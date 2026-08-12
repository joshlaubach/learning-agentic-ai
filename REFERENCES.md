# References

**Last verified: 2026-08-12** (the date this repository's build began). Every citation below
— dataset, technique, paper, library — was checked against a live source as of that date, not
copied from memory. Model names, pricing, product UI paths, spec/version numbers, and similar
fast-moving specifics referenced anywhere in this repo reflect the state of the field as of
that date and **move fast**. Check the provider's or project's current documentation directly
rather than trusting a hardcoded figure written months or years after this repo was built.

Format: `Author(s) (Year). "Title." Venue. URL or DOI/arXiv ID.` Each entry is added, and its
accuracy verified via search, during the same build session as the chapter that first cites
it — this file fills in incrementally as `PROGRESS.md`'s units complete, not all at once.
Inline citations appear the first time a concept is named in a chapter's concept markdown
(e.g. "the ReAct pattern (Yao et al., 2022)"), linking back to the full entry here.

---

## Datasets

- **SQuAD** — Rajpurkar, P., Zhang, J., Lopyrev, K., & Liang, P. (2016). "SQuAD: 100,000+
  Questions for Machine Comprehension of Text." *EMNLP 2016*, Austin, TX. arXiv:1606.05250.
  https://arxiv.org/abs/1606.05250. License: CC BY-SA 4.0 (per the canonical `rajpurkar/squad`
  Hugging Face dataset card, inherited from the underlying Wikipedia content). Default variant
  used: SQuAD 1.1 (every question answerable). **Access note:** this repo's build environment
  cannot reach `huggingface.co`, so the `datasets` library's `load_dataset("rajpurkar/squad")`
  path could not be used — the same real data (SQuAD 1.1 `dev-v1.1.json`) was instead fetched
  from the dataset authors' own canonical GitHub repository,
  `rajpurkar/SQuAD-explorer` (`raw.githubusercontent.com`), which is reachable. See
  `agentlib/synthetic_data.py` and `PROGRESS.md`'s Unit 4 notes.
- **Messy real-world document source (Chapter 3 ingestion exercise)** — the spec's original
  suggestions here (SEC EDGAR filings; the Hugging-Face-hosted `bigcode/the-stack-github-issues`)
  are both unreachable from this build environment (SEC EDGAR's hosts are blocked outright;
  Hugging Face is blocked the same way SQuAD's `datasets` path was). Substituted a real,
  unedited document instead: `anthropics/anthropic-sdk-python`'s `CHANGELOG.md`
  (https://github.com/anthropics/anthropic-sdk-python/blob/main/CHANGELOG.md), fetched via
  `raw.githubusercontent.com` and cached at `data/rag_corpus/messy_source_changelog.md` (the
  first 900 lines as of this repo's build date, 2026-08-12). License: MIT (per that
  repository's own `README.md`/`LICENSE`).
- **PubMedQA** (optional, not executed in this build — see below) — Jin, Q., Dhingra, B., Liu,
  Z., Cohen, W. W., & Lu, X. (2019). "PubMedQA: A Dataset for Biomedical Research Question
  Answering." arXiv:1909.06146. https://arxiv.org/abs/1909.06146. License: MIT.
- **BEIR** (optional, not executed in this build — see below) — Thakur, N., Reimers, N.,
  Rücklé, A., Srivastava, A., & Gurevych, I. (2021). "BEIR: A Heterogeneous Benchmark for
  Zero-shot Evaluation of Information Retrieval Models." *NeurIPS 2021 Datasets and
  Benchmarks Track*. arXiv:2104.08663. https://arxiv.org/abs/2104.08663.
- PubMedQA and BEIR are both Hugging-Face-hosted and were therefore **not runnable in this
  build environment** either — per spec, both are optional "further practice" pointers, not
  required chapter content, so `curriculum/03_rag_evaluation.ipynb` mentions them in its
  closing cell without an executed code cell. A learner with normal Hugging Face access can
  run them directly via `datasets.load_dataset(...)`.
- (GH Archive, used in Chapter 7, will be cited here once Unit 8 is built — it hits the same
  Hugging Face reachability issue and is noted in `PROGRESS.md` for that session.)

## Chapter 1 — Fundamentals of AI Agents

- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., & Cao, Y. (2022). "ReAct:
  Synergizing Reasoning and Acting in Language Models." arXiv:2210.03629.
  https://arxiv.org/abs/2210.03629 — the Thought → Action → Observation loop this chapter's
  `run_agent()` implements. Verified via the live arXiv abstract page at build time (see
  `curriculum/01_fundamentals.ipynb`).

Model names and pricing cited in Chapter 1's setup section (Claude Haiku 4.5 at $1/$5 per
million tokens; Claude Sonnet 5 at $2/$10 per million tokens, made permanent by Anthropic on
2026-08-11; OpenAI's GPT-5.6 Luna as the cheapest current OpenAI tier) were verified via live
web search on this file's "last verified" date above, not carried over from the original
build specification unchecked. OpenAI's exact per-token price for GPT-5.6 Luna was reported
inconsistently across sources at verification time, so `agentlib/llm_client.py` and the
notebook deliberately do not hardcode a number — see the live pricing page pointer in both
instead.

## Chapter 2 — Agent Control Flow

- LangChain, Inc. "Graph API overview." *Docs by LangChain.*
  https://docs.langchain.com/oss/python/langgraph/graph-api — live documentation, no
  canonical paper; cited for the nodes/edges/conditional-edges model this chapter's bridge
  section sketches. Verified live at build time.
- OpenClaw. Official documentation. https://docs.openclaw.ai/ — cited for the project's
  documented three-layer architecture (channel, brain, body) and seven-stage agentic loop
  (normalize, route, assemble context, infer, ReAct, load skills, persist memory), both
  confirmed via the live docs and multiple independent third-party architecture write-ups at
  build time. The spec that produced this course flagged that the project "has been renamed
  twice" — as of this verification, the current, live name and URL are OpenClaw /
  `docs.openclaw.ai`; re-check before treating either as current if reading this much later.
- Schmid, P. (2026, May 5). "How Agents Manage Other Agents: Four Subagents Patterns in
  2026." *philschmid.de.* https://www.philschmid.de/subagent-patterns-2026 — source for the
  four subagent management patterns (inline tool-call spawn, fan-out, persistent agent
  pools, peer-to-peer teams) and the framing of supervisor-worker as the current production
  default. Title and URL verified live at build time; this is an actively updated personal
  blog, not a static/peer-reviewed reference, so both may have moved by the time this is
  read.
- The claim that supervisor-worker is the "current production default," and that skills and
  subagents are typically composed together in production systems, reflects **practitioner
  consensus from multiple 2026 industry sources** (including the Schmid piece above and
  OpenClaw's own shipped skills layer as a concrete example) rather than one canonical or
  peer-reviewed reference — noted here explicitly rather than presented as an academic fact.

(ReAct, cited in Chapter 1's section above, is also the pattern underlying each subagent's
internal loop in this chapter's build section — not re-cited here.)

## Chapter 3 — RAG and Retrieval Evaluation

- Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H.,
  Lewis, M., Yih, W., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). "Retrieval-Augmented
  Generation for Knowledge-Intensive NLP Tasks." *NeurIPS 2020*. arXiv:2005.11401.
  https://arxiv.org/abs/2005.11401.
- Spärck Jones, K. (1972). "A Statistical Interpretation of Term Specificity and Its
  Application in Retrieval." *Journal of Documentation*, 28(1), 11–21.
  DOI: 10.1108/eb026526.
- Mikolov, T., Chen, K., Corrado, G., & Dean, J. (2013). "Efficient Estimation of Word
  Representations in Vector Space." arXiv:1301.3781. https://arxiv.org/abs/1301.3781.
- Johnson, J., Douze, M., & Jégou, H. (2017). "Billion-Scale Similarity Search with GPUs."
  arXiv:1702.08734. https://arxiv.org/abs/1702.08734. (FAISS.)
- Es, S., James, J., Espinosa Anke, L., & Schockaert, S. (2024). "RAGAs: Automated
  Evaluation of Retrieval Augmented Generation." *Proceedings of the 18th Conference of the
  European Chapter of the Association for Computational Linguistics: System Demonstrations*
  (EACL 2024), 150–158. https://aclanthology.org/2024.eacl-demo.16/. (Preferred over the
  arXiv preprint, arXiv:2309.15217, per this repo's citation convention of citing the
  peer-reviewed venue when one exists.)
- Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information
  Retrieval*. Cambridge University Press. (Textbook reference for the precision/recall/MRR
  definitions used throughout this chapter — a standard reference, not a single paper.)
- Chroma — project documentation/GitHub, https://www.trychroma.com/ and
  https://github.com/chroma-core/chroma. No canonical paper; cited as the alternative local
  vector store this chapter's concept section names (this course's runnable example uses
  FAISS instead — see `PROGRESS.md`'s Unit 1 notes for why).
- DeepEval — project documentation/GitHub, https://github.com/confident-ai/deepeval. No
  canonical paper; cited for its pytest-style RAG-testing interface, mentioned alongside
  RAGAS in this chapter's "mapping to real tooling" section.
- spaCy — project documentation, https://spacy.io/, and the `en_core_web_md` model
  specifically, https://github.com/explosion/spacy-models. No canonical paper for the
  library; cited here as this chapter's local-embeddings implementation (a build-environment
  -driven substitution for the spec's originally-suggested `sentence-transformers` — see
  `requirements.txt`'s comment and `PROGRESS.md`'s Unit 4 notes for the full reasoning).
- `anthropic-sdk-python` `CHANGELOG.md` — see the Datasets section above for the full
  citation of this chapter's messy real-world ingestion source.
- SQuAD — see the Datasets section above.

## Chapter 4 — Production Reliability

- Nygard, M. T. (2007). *Release It!: Design and Deploy Production-Ready Software.*
  Pragmatic Bookshelf. (2nd ed., 2018.) The book that popularized the circuit breaker
  pattern (among other stability patterns) as a defense against cascading failure — this
  chapter's `CircuitBreaker` implementation follows the closed/open/half-open state model
  described there.
- Brooker, M. (2015). "Exponential Backoff and Jitter." *AWS Architecture Blog.*
  https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/. Source for the
  jitter component of this chapter's `retry_with_backoff()` — the core insight verified here
  is that exponential backoff alone isn't sufficient; randomizing each client's retry
  schedule is what actually prevents a "thundering herd" of synchronized retries.

## Chapter 5 — Cost, Performance, and Model Selection

- `tiktoken` — OpenAI's BPE tokenizer library, https://github.com/openai/tiktoken. No
  canonical paper; cited for the real `cl100k_base` tokenization this chapter runs against
  the request log (word counts, token-vs-word quirks, whitespace-merge behavior). **Access
  note:** `tiktoken.get_encoding("cl100k_base")` normally fetches its vocabulary file from
  `openaipublic.blob.core.windows.net` on first use, which this build environment cannot
  reach (same class of block as Hugging Face and SEC EDGAR). Rather than approximate token
  counts, this repo vendors a hash-verified copy of that exact vocabulary file at
  `data/tiktoken_cache/`, pre-seeded into `tiktoken`'s own local cache directory — verified
  via SHA-256 hash match against the hash tiktoken's own source checks for at fetch time. See
  `PROGRESS.md`'s Unit 6 notes for the full verification steps.
- Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W.
  (2021). "LoRA: Low-Rank Adaptation of Large Language Models." arXiv:2106.09685.
  https://arxiv.org/abs/2106.09685. Cited for this chapter's conceptual (no-training)
  explanation of low-rank adapter fine-tuning.
- Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). "QLoRA: Efficient
  Finetuning of Quantized LLMs." *NeurIPS 2023* (Oral). arXiv:2305.14314.
  https://arxiv.org/abs/2305.14314. Cited for 4-bit quantized-base-model fine-tuning, this
  chapter's explanation of why QLoRA lowers the GPU-memory bar for fine-tuning further than
  LoRA alone.
- Christiano, P. F., Leike, J., Brown, T., Martic, M., Legg, S., & Amodei, D. (2017). "Deep
  Reinforcement Learning from Human Preferences." *NeurIPS 2017*, Vol. 30. arXiv:1706.03741.
  https://arxiv.org/abs/1706.03741. The foundational RLHF paper cited for this chapter's
  RLHF explanation and its connection to Chapter 3's judge-based evaluation pattern.
- Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C.,
  Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens,
  M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). "Training
  Language Models to Follow Instructions with Human Feedback." *NeurIPS 2022*.
  arXiv:2203.02155. https://arxiv.org/abs/2203.02155. (InstructGPT.) Cited for RLHF applied
  to instruction-following at production LLM scale, distinct from Christiano et al.'s
  original RL-control-tasks setting.

## Chapter 6 — Security and Safeguards

*(Populated in Unit 7 — OpenClaw security guidance, Snowflake MCP governance guidance,
indirect prompt injection.)*

## Chapter 7 — Tool Integration

*(Populated in Unit 8 — Model Context Protocol spec and governance, Snowflake MCP server,
GitHub MCP server, Pydantic, plus the GH Archive dataset entry above.)*

## Chapter 8 — System Design and Engineering Judgment

*(No citations expected — Chapter 8 is original scenario/judgment content, not derived from a
specific external source.)*

## Chapter 9 — LLMOps and Deployment

*(Populated in Unit 10 — canary/progressive delivery, Docker, OpenClaw containerized
deployment.)*

## Capstone and Appendices

*(Populated in Unit 12 for the capstone — LangGraph or Claude Agent SDK, OpenClaw comparison.
Prerequisite-section concepts like async I/O, testing, and Docker cite official docs only, no
paper needed.)*
