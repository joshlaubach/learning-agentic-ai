# Chapter 3: RAG and Retrieval Evaluation - Model Answers

Open this file only after you've attempted `curriculum/03_rag_evaluation.ipynb`'s cold
diagnosis exercise and further exercises from memory.

---

## Cold-diagnosis exercise

### 1. A RAG system gives a confident, detailed, entirely wrong answer. Offline precision@k on this query is 0.

Retrieval problem. Precision@k of 0 means none of the top-k retrieved documents were actually
relevant, so the model never had a chance to be right, because it was never given the right
material. This is this chapter's break-it #1 (a corrupted retriever): the generator is doing
exactly what it should with the context it received; the context itself was wrong. The fix
lives in retrieval or indexing, not in the prompt or the model. No amount of "answer more
carefully" instruction to the generator would fix a retrieval bug.

### 2. A RAG system gives a confident, fluent answer that doesn't match the source material at all - but precision@k and recall@k are both 1.0.

Generation problem. This is the important, counter-intuitive case: retrieval metrics being
perfect proves the right material was retrieved, which means the fault is entirely in
generation. The model had the right context and didn't use it (break-it #2). This is exactly
why faithfulness or groundedness has to be measured as its own metric, separate from
retrieval quality, since a system can pass every retrieval check and still hallucinate. If you
only ever monitor precision@k and recall@k in production, this failure mode is invisible to
you.

### 3. A RAG system's answer is half-right - it has the entity but not the date, or vice versa.

A retrieval problem, specifically a retrieval-breadth problem, and not exactly the same
failure as #1. The signature (a partially-correct answer with a specific, consistent gap)
points to the answer being split across multiple source chunks, only some of which were
retrieved (break-it #3). MRR can look fine here, because the first relevant chunk found was
ranked well, which is the tell that this isn't a ranking problem: the ranking of what was
found is fine, the set of what was found is incomplete. The practical fix is raising k, a
reranker, or chunk-linking at ingestion time, not touching generation at all.

### 4. A RAG system gives a plausible answer that's subtly wrong in one specific fact, and the source documents contain a near-identical passage with a different value for that fact.

A retrieval problem, specifically a disambiguation failure caused by near-duplicate documents
(break-it #4). Precision@k can look deceptively reasonable here too, if you're only checking
"was a relevant-looking document retrieved" rather than "was the correct one of two very
similar documents retrieved." That's exactly why this failure mode is easy to miss in a
coarse eval setup, and why deduplication at ingestion time, rather than hoping the retriever
always breaks the tie right, is the real fix.

---

## Further exercises

### 5. How would you chunk a messy real-world corpus, and how would you catch near-duplicate chunks before they hurt retrieval?

From what this chapter actually built: start by respecting document structure rather than
cutting on a raw character count. This chapter's semantic/section-boundary chunker (splitting
on Markdown headers) never cuts a sentence or a code block in half, where the fixed-size
chunker demonstrably does. The tradeoff is real, though. Fixed-size chunking is trivial to
implement and gives predictable chunk sizes for embedding-model context limits, while semantic
chunking requires the document to actually have detectable structure to split on, and its
section sizes end up uneven. In practice I'd default to semantic chunking whenever the source
format has real structure to exploit (Markdown headers, HTML tags, code file boundaries) and
fall back to fixed-size only for genuinely unstructured plain text.

For near-duplicates: compute pairwise similarity (this chapter used TF-IDF cosine similarity,
cheap and effective at this scale; a real system at larger scale would use approximate
nearest-neighbor search over embeddings, for example via the same FAISS index used for
retrieval, to avoid an O(n²) pairwise comparison), then drop or merge chunks above a
similarity threshold before they enter the index, not after, and not by hoping retrieval
sorts it out at query time. The chapter's dedup step removed real near-duplicate release-note
sections from a real changelog this way, and separately, the confusable-document break-it
scenario showed concretely what happens when that step is skipped: a near-duplicate can
outrank the original at query time with no warning.

### 6. Explain, in plain language, why an AI system that uses RAG can still hallucinate.

Giving the system access to real documents doesn't force it to actually use them. It's more
like handing someone the right reference book open to the right page: they can still answer
from memory instead of reading the page in front of them, and you can't always tell which one
they did just from how confident they sound. Grounding a system in real source material makes
it less likely to make things up, but there's no built-in mechanism that guarantees it only
says things the source material actually supports. That enforcement, checking that the answer
is actually traceable back to what was retrieved, has to be built and checked deliberately. It
doesn't come free just because retrieval happened.

---

## 7. Cold diagnosis: exact part numbers return neighbours, not the part

**What's wrong:** the pipeline is dense-only, and an arbitrary part number is the one kind of
string a dense retriever structurally cannot handle.

An embedding model places text in a space it learned from a training corpus. `SKU-6690` was
minted by a database. It appeared in no training corpus, carries no distributional meaning,
and the tokenizer breaks it into fragments (`sku`, `66`, `90`) whose vectors reflect other
contexts entirely. The nearest neighbours of that improvised vector are other catalogue
entries that look superficially similar — which is exactly the reported symptom: three
plausible neighbours, not the part.

Note the diagnosis is sharper than "embeddings are bad at exact match". This chapter measured
the split directly: on the parts catalogue, dense retrieval ranks `MERV 13`, `GFCI`, `ERV` and
`RO cartridge` at **#1**, the same as BM25. Those are *words* — they occur in real text, so the
model has representations for them. It ranks `SKU-6690` at **#15 of 20**. The dividing line is
not "exact vs. semantic", it is **whether the string existed in the training distribution at
all.**

**Why fine-tuning won't fix it:** fine-tuning adjusts the geometry of a learned space. There is
no signal to learn from — the relationship between `SKU-6690` and a foam pipe sleeve is
arbitrary and carries zero distributional evidence. Worse, it doesn't generalise: every new SKU
added tomorrow is unseen again, so you would be retraining on every catalogue update to solve a
problem that lookup solves for free. It is expensive, slow to roll back, and structurally
incapable of covering new identifiers.

**What to do instead:** add a lexical index (BM25 or plain inverted-index lookup) and route or
fuse. Two details matter in the answer:

- **The identifier has to be in the indexed text**, not only the record key. An identifier you
  never indexed is a missing field, not a retrieval failure — and this is a real bug worth
  checking for first, because it presents identically.
- **Tokenization has to preserve it.** A tokenizer that strips punctuation and digits, or stems
  aggressively, destroys the thing you are trying to match. `SKU-6690` must survive as
  something searchable.

If the query is *recognisably* an identifier (it matches a known SKU pattern), the cleanest
design is not even search — detect the pattern and do a direct lookup, falling back to the
retrieval path only when it misses.

---

## 8. Judgment call: overlap raised from 0 to 50%

**What it cost:** index size, roughly doubled. Overlap works by sliding the window less than
its own width, so halving the step halves the distance between chunk starts and roughly doubles
the chunk count. Each extra chunk is another vector to embed, store, index, and search. This
chapter's measurement shows the shape: going from overlap 0 to 160 on a 200-character chunk
took the index from ~4.3 chunks per document to ~15.2, about 3.5x, while boundary-split
recovery went from under half to over 95%.

So the honest framing is that recall did not "go up" for free — it was bought, and the receipt
is storage, embedding cost at ingest, and a slightly slower search over a bigger index.

**What I'd want measured before shipping:**

- **Which recall.** Recovery of boundary-split facts is the thing overlap actually fixes. If
  the reported gain is on a metric that overlap shouldn't affect, something else changed too,
  or the eval set is small enough to be noise.
- **Precision, and duplicate results.** Overlapping chunks mean the same sentence lives in
  several chunks, so top-k can fill with near-identical passages — real recall gain, worse
  context. Check whether retrieved sets got more redundant, and whether deduplication at
  retrieval time is now needed.
- **Cost deltas**: index size, ingest time, p95 query latency.
- **Whether `k` should now come down.** Overlap and a larger `k` are two fixes for the same
  failure. If chunks are self-contained more often, you may be able to retrieve fewer of them
  and win back context window — which is the compounding benefit people forget to claim.
- **The eval set's provenance.** If the gain was measured on queries chosen after seeing the
  failure, it is not evidence.

50% is a common default and not obviously wrong. The reason to push back on "recall went up" as
a shipping argument is that it is a one-sided report of a two-sided trade.

---

## 9. Design judgment: adding hybrid search to a dense-only pipeline

**The argument for it:** lexical and semantic retrieval fail on genuinely different queries.
Dense retrieval handles paraphrase, where the user's words and the document's words differ.
Lexical retrieval handles exact strings — identifiers, error codes, rare proper nouns — that
have no useful embedding. A pipeline with only one of them has a whole class of query it cannot
serve, and on a mixed real workload that class is usually larger than anyone estimated. Fusing
the two ranked lists (reciprocal-rank fusion is the standard default, and needs no score
calibration between systems) covers both.

**The precondition, and when it backfires:** fusion is an averaging operation. It helps when
both retrievers are *individually competent* and fail *independently*. If one side is
substantially weaker, fusion drags the strong retriever toward the weak one and the combined
result is worse than the better component alone.

That is not hypothetical — it is what happens in this chapter. The dense retriever here
averages spaCy word vectors, which cannot compose meaning, so it loses to BM25 on paraphrase
queries as well as identifier ones. Reciprocal-rank fusion of the two lands *below* BM25 alone.
The same thing happens in production whenever a team bolts a poorly-tuned BM25 index onto a
strong embedding pipeline and reports that "hybrid didn't help".

**What I'd measure, before and after:**

- **Per-slice, not aggregate.** Split the eval set by query type — identifier-bearing,
  paraphrase, mixed — and report each separately. A single aggregate MRR hides the entire
  effect, because hybrid's gain on one slice can cancel its loss on another.
- **Each component alone, on the same set.** You cannot interpret the fused number without
  both baselines. The decision rule is simple: if fusion does not beat `max(dense, lexical)`
  on the slices you care about, you have a component-quality problem, not a fusion opportunity.
- **The query mix itself**, from real logs. Hybrid's value is proportional to how much of your
  traffic is the type your current retriever fails. If 2% of queries carry identifiers, this is
  a small win; if 40% do, it is the whole ballgame.
- **Latency and cost**, since you are now running two retrievers per query plus a fusion step.

**The honest summary:** "add hybrid search" is good default advice and a bad substitute for
measurement. The failure mode is not that fusion is wrong, it is that fusion is assumed to be
free — and the only way to know which case you are in is to measure both components separately
on your own corpus and query mix.
