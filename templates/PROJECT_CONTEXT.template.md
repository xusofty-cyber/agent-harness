# Project Context & Durable Facts (PROJECT_CONTEXT.md)

> **Role & Purpose**: This document records core architectural facts and durable engineering constraints for `<PROJECT_NAME>`, serving as the single source of truth (SSOT) when AI Agents start sessions and make technical decisions. Maintain only when system architecture, stack choices, persistence designs, or global guardrails change significantly. Session-specific transient status and breakpoints belong in `SESSION_STATE.md`.

---

## 1. Project Overview & Core Domain

- **System Name**: `<PROJECT_NAME>`
- **Domain**: <Brief description of domain, purpose, and key problems solved>
- **Core Feature Matrix**:
  1. **<Core Module/Feature 1>**: <Description of responsibilities and workflow>
  2. **<Core Module/Feature 2>**: <Description of responsibilities and workflow>

---

## 2. Repository & Technology Stack

### 1. Environment & Branches
- **Repository**: `<GIT_REPO_URL>`
- **Primary / Working Branch**: `main` / `develop`
- **Runtime & Deployment**: <Local dev / Docker / Kubernetes / Production cloud>

### 2. Stack Choices

| Layer / Domain | Tech & Version | Notes & Key Libraries |
|---|---|---|
| **Core Language / Runtime** | <e.g., TypeScript 5.x / Python 3.11 / Go 1.22> | <Main language and execution environment> |
| **Frameworks & Build** | <e.g., Next.js / FastAPI / Spring Boot / Vite> | <Application framework & build tools> |
| **Persistence & Cache** | <e.g., PostgreSQL 16 / Redis 7 / SQLite> | <Primary databases and caching layer> |
| **API & Messaging** | <e.g., gRPC / RESTful / Kafka / RabbitMQ> | <Protocols and event buses> |

---

## 3. Architecture & Structural Design

- **Architecture Pattern**: <e.g., Layered Monolith / Domain-Driven Microservices / Modular Plugin>
- **Directory & Module Responsibilities**:
  - `src/`: <Core business source code>
  - `tests/`: <Unit and integration test suites>
  - `docs/`: <Architecture decision records and technical specs>

---

## 4. Key Constraints & Global Red Lines

1. **Minimal Implementations & Zero Bloat (Ponytail Ladder)**:
   - Always follow the decision ladder: prefer existing code, standard libraries, and existing dependencies before introducing speculative abstractions or new packages.
2. **Unified Error Handling & Secret Sanitization**:
   - Use standard error structures; never swallow errors silently.
   - Never log or commit API keys, tokens, passwords, private keys, or internal connection strings.
3. **Git Isolation & Branch Protection**:
   - Never commit directly to protected branches (`main`, `develop`, `master`); use feature branches.
   - Never run `git add .` or `git add -A`; stage explicit paths only. Force-push (`git push --force`) is permanently prohibited.

---

## 5. Architectural & Technical Decision Records (ADR / Decision Log)

- **<YYYY-MM-DD>**: [Project Memory Initialization]
  - **Context**: Establish a cross-session, cross-tool standard for project memory.
  - **Decision**: Adopt `PROJECT_CONTEXT.md` for durable facts and `SESSION_STATE.md` for transient checkpoints.
  - **Impact**: All agents load this context at session start to maintain technical consistency.
