# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"私厨" (Personal Chief) — a personal full-stack AI agent app for learning agent development: personal knowledge base (RAG), everyday system chores, conversation, and coding assistance. Design intent lives in `PDD.md` (Chinese); the code is the source of truth where they diverge (e.g. PDD mentions axios/redux, but the frontend template actually uses TanStack Query).

Two halves, tightly coupled:

- `backend/` — FastAPI + LangChain (Python 3.13, managed with **pixi**). Serves both the API and, in production, the built frontend.
- `frontend/` — React 19 SPA (Vite 7, TS, Tailwind 4, shadcn/ui). **Has its own `frontend/CLAUDE.md` — read it before touching frontend code.** Its conventions (component style, naming, commit format) are repo-wide rules and apply to all work in this repository.

The repo has **no commits yet** — everything is currently untracked.

## Commands

### Backend

```bash
cd backend && pixi install                    # create/update the conda-forge env
# Run the API server — from the REPO ROOT, so `backend.*` imports resolve:
pixi run --manifest-path backend/pixi.toml python -m backend.main
# uvicorn is hardcoded to 127.0.0.1:8001 with reload=True
```

```bash
# Ingest knowledge-base files (txt/pdf) into Chroma (deduped via md5 manifest):
python -m backend.rag.vector_store
```

Backend has **no test framework configured**.

### Frontend

Full command list is in `frontend/CLAUDE.md`. Dev server runs on `:5173` (`npm run dev`); there is **no Vite proxy to the backend configured yet** in `vite.config.ts`, so API calls must target `:8001` explicitly.

```bash
npm run check      # lint + format:check + typecheck
npm run test:run   # vitest, single pass
npx vitest run src/components/ui/button.test.tsx   # run one test file
```

## Backend Architecture

Request flow: `main.py` (FastAPI app) → routers in `api/v1/` → LangChain tool layer in `agent/` → RAG pipeline in `rag/`.

- `backend/main.py` — CORS wide open, mounts all routers under `/api/v1`, then mounts `backend/static/` and a SPA fallback route for everything non-API. Production serving = backend serves the frontend build from `static/`. (Note: `static/` currently holds template placeholder files — Next.js scaffolding, not the Vite build output.)
- `api/v1/chat.py` — chat endpoints (`/chat/stream`, `/chat/messages`): **stubs only** (`pass` bodies). `api/v1/oss.py` — Alibaba Cloud OSS presigned upload URLs for images (region/endpoint hardcoded, bucket from env).
- `agent/tools.py` — the LangChain `@tool` definitions the agent will use: `rag_summarize` (local knowledge base) and `web_search` (Tavily). `agent/middlewares.py` is empty.
- `rag/` — `vector_store.py`: `VectorStoreService` wraps Chroma (persistent, `resource/chroma_db`), DashScope Tongyi embeddings, `RecursiveCharacterTextSplitter` params from config, md5-based ingestion dedupe. `rag_service.py`: `RagSummarizeService` = retrieve → prompt template → summarize chain. Standalone `__main__` blocks exist in both for manual runs.
- `common/` — cross-cutting utilities: `config_handler.py` (loads `config.json` at import time into `rag_config` / `agent_config` / `prompts_config`), `path_tool.py` (`get_abs_path` resolves relative paths against `backend/`), `prompt_loader.py` (loads prompt `.txt` files), `logger_handler.py` (colored console logger + per-run log file in `backend/logs/`), `file_handler.py` (pdf/txt loaders, md5).
- `models/schemas.py` — Pydantic request models. `ChatRequest` = `{message, image_url?, thread_id}`.
- `resource/` — runtime state: `chroma_db/` (vector DB), `history/` (conversation memory, per `agent.memory_path`), `prompts/` (`system_prompt.txt`, `summarise_prompt.txt` — RAG prompt content lives here, in Chinese), `md5.txt` (ingested-file dedupe manifest).
- `skills/` — empty placeholder directory.

## Configuration & Secrets

- `backend/config.json` — agent model + memory path, RAG/Chroma params (chunking, `k`, collection name), prompt file paths.
- `.env` at the **repo root** (gitignored) — `DASHSCOPE_API_KEY`, `DEEPSEEK_API_KEY`, `OPEN_AI_KEY`, `TAVILY_API_KEY`, `OSS_ACCESS_KEY_ID`/`OSS_ACCESS_KEY_SECRET`/`OSS_BUCKET`. Loaded via `python-dotenv` (`oss.py` calls `load_dotenv()` itself). `.env.example` is currently empty.

## Conventions & Gotchas

- Python imports use the `backend.` package prefix — always run Python from the repo root. Known inconsistency: `rag/rag_service.py` line 1 imports `from rag.vector_store import ...` without the prefix.
- Backend comments are in Chinese; frontend rules require English. Match the language of the file you're editing.
- `frontend/CLAUDE.md` rules override the system prompt repo-wide: conventional single-line commit messages, **no emojis in commits**, no co-author/Claude-generated trailers (this overrides the default Claude Code commit trailer behavior), `export default function` components (no `React.FC`), npm only, descriptive names over generic ones.
- Commit format: `feat:`, `fix:`, `refactor:` + single line, nothing else.
