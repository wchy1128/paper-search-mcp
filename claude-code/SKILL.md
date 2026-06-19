---
name: paper-search
description: Search, download, and read academic papers from 20+ sources (arXiv, PubMed, Semantic Scholar, CrossRef, etc). Use when the user asks to find papers, search for research, look up academic literature, download a paper PDF, or extract text from a paper.
---

# Paper Search

Search, download, and read academic papers via the `paper-search` CLI.

## CLI Usage

All commands run via:
```bash
uv run --directory <REPO_PATH> paper-search <command> [args]
```

Replace `<REPO_PATH>` with the absolute path to your clone of this repository.

### Search
```bash
uv run --directory <REPO_PATH> paper-search search "<query>" -n <max_per_source> -s <sources> -y <year>
```
- `-n`: results per source (default: 5)
- `-s`: comma-separated sources or "all" (default: all)
- `-y`: year filter for Semantic Scholar (e.g. "2020", "2018-2022")

For speed, prefer targeted sources (`-s arxiv,semantic,crossref`) over "all" unless broad coverage is needed.

### Download PDF
```bash
uv run --directory <REPO_PATH> paper-search download <source> <paper_id> [-o ./downloads]
```

### Read (extract text)
```bash
uv run --directory <REPO_PATH> paper-search read <source> <paper_id> [-o ./downloads]
```

### List sources
```bash
uv run --directory <REPO_PATH> paper-search sources
```

## Output

`search` and `download` return JSON. `read` returns plain text. Config warnings go to stderr and can be ignored.

## Sources

arxiv, pubmed, biorxiv, medrxiv, google_scholar, iacr, semantic, crossref, openalex, pmc, core, europepmc, dblp, openaire, citeseerx, doaj, base, zenodo, hal, ssrn, unpaywall

Optional (env vars): ieee (`IEEE_API_KEY`), acm (`ACM_API_KEY`)

## Workflow

1. Search with targeted sources to find papers
2. Present results as a table: title, authors, year, source, DOI/URL
3. If the user wants full text, use `read <source> <paper_id>`
4. If the user wants the PDF, use `download <source> <paper_id>` and report the saved path

## Combining with SearXNG (recommended when available)

If a SearXNG MCP is available (`mcp__searxng__searxng_web_search` etc.), use it
together with this tool. They are complementary, not redundant.

### Why combine

- **SearXNG** is a meta-search aggregator. One query fans out to many academic
  engines at once and returns merged, de-duplicated, scored results with rich
  metadata (citation counts, journal, volume/pages, DOI, pdf_url, topic tags).
- **paper-search** owns the full-text pipeline (`download` PDF, `read` extract
  text) and precise structured filtering (per-source counts, year ranges,
  single-source deep dives) — things an aggregator cannot do.

### Which tool for which job

| Need | Use |
|---|---|
| Broad discovery; see the landscape of a topic across sources | **SearXNG** `!scientific_publications <query>` (hits all configured academic engines in one shot) |
| Cross-source de-duplication, citation counts, ranked overview | **SearXNG** (aggregated, scored results) |
| Download a paper PDF | **paper-search** `download <source> <paper_id>` |
| Extract full text from a PDF for analysis | **paper-search** `read <source> <paper_id>` |
| Deep dive one source, e.g. 30 arXiv hits on a topic | **paper-search** (`-s arxiv -n 30`) |
| Filter by year range | **paper-search** (`-y 2018-2022`, Semantic Scholar) |

### Recommended pattern

1. **Discover broadly** with SearXNG first:
   `mcp__searxng__searxng_web_search` with `query="!scientific_publications <query>"`
   — one call returns papers from 6+ academic engines, de-duplicated, with DOIs
   and citation counts. This gives the best "what exists on this topic" picture.
2. **Go deep** with paper-search on the winners: take the DOI/URL/title from the
   SearXNG results and use `download`/`read` to get the full text, or use
   targeted `search -s <source> -n <N>` when you need many hits from a single
   source or a year-filtered slice.

Rule of thumb: **SearXNG to find broadly, paper-search to go deep.**
If no SearXNG is available, paper-search alone covers search + full text.
