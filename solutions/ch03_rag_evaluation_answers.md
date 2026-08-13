# Chapter 3: RAG and Retrieval Evaluation — Model Answers

Open this file only after you've attempted `curriculum/03_rag_evaluation.ipynb`'s cold
diagnosis exercise and further exercises from memory.

---

## Cold-diagnosis exercise

### 1. A RAG system gives a confident, detailed, entirely wrong answer. Offline precision@k on this query is 0.

**Retrieval problem.** Precision@k of 0 means none of the top-k retrieved documents were
actually relevant — the model never had a chance to be right, because it was never given the
right material. This is this chapter's break-it #1 (a corrupted retriever): the generator is
doing exactly what it should with the context it received, the context itself was wrong. The
fix lives in retrieval/indexing, not in the prompt or the model — no amount of "answer more
carefully" instruction to the generator would fix a retrieval bug.

### 2. A RAG system gives a confident, fluent answer that doesn't match the source material at all — but precision@k and recall@k are both 1.0.

**Generation problem.** This is the important, counter-intuitive case: retrieval metrics
being perfect *proves* the right material was retrieved, which means the fault is entirely in
generation — the model had the right context and didn't use it (break-it #2). This is
exactly why faithfulness/groundedness has to be measured as its own metric, separate from
retrieval quality — a system can pass every retrieval check and still hallucinate. If you only
ever monitor precision@k/recall@k in production, this failure mode is invisible to you.

### 3. A RAG system's answer is half-right — it has the entity but not the date, or vice versa.

**A retrieval problem, specifically a retrieval-breadth problem** — not generation, and not
exactly the same failure as #1. The signature (a partially-correct answer with a specific,
consistent gap) points to the answer being split across multiple source chunks, only some of
which were retrieved (break-it #3). MRR can look fine here (the *first* relevant chunk found
was ranked well), which is the tell that this isn't a ranking problem — the ranking of what
was found is fine, the set of what was found is incomplete. The practical fix is raising k, a
reranker, or chunk-linking at ingestion time — not touching generation at all.

### 4. A RAG system gives a plausible answer that's subtly wrong in one specific fact, and the source documents contain a near-identical passage with a different value for that fact.

**A retrieval problem, specifically a disambiguation failure** — near-duplicate documents
(break-it #4). Precision@k can look deceptively reasonable here too, if you're only checking
"was *a* relevant-looking document retrieved" rather than "was *the correct one of two very
similar* documents retrieved" — which is exactly why this failure mode is easy to miss in a
coarse eval setup and why deduplication at ingestion time (not hoping the retriever always
breaks the tie right) is the real fix.

---

## Further exercises

### 5. How would you chunk a messy real-world corpus, and how would you catch near-duplicate chunks before they hurt retrieval?

From what this chapter actually built: start by respecting document structure rather than
cutting on a raw character count — this chapter's semantic/section-boundary chunker (splitting
on Markdown headers) never cuts a sentence or a code block in half, where the fixed-size
chunker demonstrably does. The tradeoff is real, though: fixed-size chunking is trivial to
implement and gives predictable chunk sizes for embedding-model context limits; semantic
chunking requires the document to actually have detectable structure to split on, and section
sizes end up uneven. In practice I'd default to semantic chunking whenever the source format
has real structure to exploit (Markdown headers, HTML tags, code file boundaries) and fall
back to fixed-size only for genuinely unstructured plain text.

For near-duplicates: compute pairwise similarity (this chapter used TF-IDF cosine similarity,
cheap and effective at this scale; a real system at larger scale would use approximate
nearest-neighbor search over embeddings, e.g. via the same FAISS index used for retrieval, to
avoid an O(n²) pairwise comparison) and drop or merge chunks above a similarity threshold
*before* they enter the index — not after, and not by hoping retrieval sorts it out at query
time. The chapter's dedup step removed real near-duplicate release-note sections from a real
changelog this way, and separately, the confusable-document break-it scenario showed
concretely what happens when that step is skipped: a near-duplicate can outrank the original
at query time with no warning.

### 6. Explain, in plain language, why an AI system that uses RAG can still hallucinate.

Giving the system access to real documents doesn't force it to actually *use* them — it's
more like handing someone the right reference book open to the right page, but they can still
answer from memory instead of reading the page in front of them, and you can't always tell
which one they did just from how confident they sound. Grounding a system in real source
material makes it *less likely* to make things up, but there's no built-in mechanism that
guarantees it only says things the source material actually supports. That enforcement —
checking that the answer is actually traceable back to what was retrieved — has to be built
and checked deliberately; it doesn't come free just because retrieval happened.
