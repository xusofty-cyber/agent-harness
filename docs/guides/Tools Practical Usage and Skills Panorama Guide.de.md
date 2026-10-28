# Praktische Anleitung zu AI-Tooling und Skills-Panorama (Claude Code / Codex / Antigravity IDE / Zed IDE)

> **Language / Sprache**: [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [简体中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | [繁體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh-tw.md) | [Français](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.fr.md) | **Deutsch**

Diese Anleitung bietet ein umfassendes Handbuch für Softwareentwicklung und technische Dokumentation mit AI-Agents: **welche Skills und Harness-Tools zu installieren sind, zugrundeliegende Token-Ökonomie, Tool-Konfiguration und -Verdrahtung, wann und wie zentrale Slash Commands aufzurufen sind (z. B. `/comet`, `/plan`, `/opsx`, `codegraph`), sowie ein End-to-End-Praxis-Walkthrough.**

---

## Inhaltsverzeichnis

1. [Kernarchitektur & Tool-Matrix (wer verwaltet was)](#1-kernarchitektur--tool-matrix-wer-verwaltet-was)
2. [Skills- & Ökosystem-Tool-Inventar](#2-skills---ökosystem-tool-inventar)
   - 2.1 44 integrierte native Skills kategorisiert
   - 2.2 Versions-Locking, Online-Updates & Skill-Sync (`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`)
   - 2.3 Optionale Harness-CLI-Tools
   - 2.4 Token-Ökonomie der Skills (warum 40+ Skills den Kontext NICHT sprengen)
   - 2.5 Engineering-Skills- & Regel-Dispatching-Matrix
3. [Vertiefung in zentrale Harness-Tools & Slash Commands](#3-vertiefung-in-zentrale-harness-tools--slash-commands)
   - 3.1 Comet: Versionierter Workflow-Einstiegspunkt
   - 3.2 OpenSpec: Spezifikationsgetriebene Entwicklung (`/opsx:propose`, `/opsx:apply`, etc.)
   - 3.3 Superpowers: TDD, systematisches Debugging & Verifikations-Gate
   - 3.4 CodeGraph: Optionale MCP-Code-Graph-Integration
   - 3.5 Ponytail: Minimale Implementierungsleiter (Generierungs-Gate)
   - 3.6 Caveman: Ultra-komprimierte Ausgabe (Kommunikations-Gate)
   - 3.7 RTK: Ausgabe-Kürzung & Log-Abschirmung (Ausführungs-Gate)
   - 3.8 Git-Autorisierungsmodell & Protected-Branch-Workflow
   - 3.9 3-Schritte-Sitzungszeremonie & dynamische Memory-Schleife
   - 3.10 8-Hochrisiko-Operationen-Schutzmatrix
4. [Plattformspezifische native Befehle & Best Practices](#4-plattformspezifische-native-befehle--best-practices)
   - 4.1 Google Antigravity IDE
   - 4.2 Claude Code & PreToolUse-Hooks
   - 4.3 OpenAI Codex / GitHub Copilot
   - 4.4 Zed IDE
5. [End-to-End-Praxis-Walkthrough (reale Feature-Entwicklung)](#5-end-to-end-praxis-walkthrough-reale-feature-entwicklung)
6. [Tägliche Health Checks & Troubleshooting](#6-tägliche-health-checks--troubleshooting)

---

## 1. Kernarchitektur & Tool-Matrix (wer verwaltet was)

Ohne physische Grenzen driftet AI-unterstützte Entwicklung häufig, over-engineered oder bricht die Rückwärtskompatibilität. Unsere Harness-Architektur setzt fünf aufeinanderfolgende Gates durch:

```text
       [ Benutzeranfrage ]
              │
       ┌──────▼─────────────────────────────────────────────────┐
       │ 1. Prozess- & Zustands-Gate: Comet (/comet) + OpenSpec SDD │
       └──────┬─────────────────────────────────────────────────┘
              │ Umfang fixiert; Exploration & Discovery beginnen
       ┌──────▼─────────────────────────────────────────────────┐
       │ 2. Optionales semantisches Retrieval: CodeGraph MCP, falls konfiguriert │
       └──────┬─────────────────────────────────────────────────┘
              │ Symbolabhängigkeiten klar; Design & Code
       ┌──────▼─────────────────────────────────────────────────┐
       │ 3. Code-Gate: Superpowers (TDD Red-Green) + Ponytail   │
       └──────┬─────────────────────────────────────────────────┘
              │ Tests & Build-Befehle ausführen
       ┌──────▼─────────────────────────────────────────────────┐
       │ 4. Optionale Befehlsfilterung: RTK CLI + Agent-Hook          │
       └──────┬─────────────────────────────────────────────────┘
              │ Liefern & Committen
       ┌──────▼─────────────────────────────────────────────────┐
       │ 5. Kommunikation & Git: Caveman-Anleitung (falls geladen) + Git  │
       └────────────────────────────────────────────────────────┘
```

### Verantwortungsmatrix

| Komponente | Kernverantwortung | Gelöster Schmerzpunkt | Schnittstelle |
|---|---|---|---|
| **Comet** | Versionierte Native/Classic-Workflows | Fortsetzbare, verifizierbare Task-Workflows | Installierter Version und `.comet/config.yaml` folgen |
| **OpenSpec** | Spezifikationsgetriebene Entwicklung (SDD) | Anforderungsamnesie, ungetrackte Delta-Änderungen | `/opsx:propose`, `docs/openspec/` Live-Docs |
| **Superpowers** | TDD- & Verifikationsevidenz-Gate | Halluzinierte Task-Fertigstellung, fehlender physischer Nachweis | Roter Test $\rightarrow$ Grüner Test $\rightarrow$ Verifikationsbericht |
| **CodeGraph** | Optionale semantische Code-Such-Integration | Erfordert CLI, Agent-MCP-Verdrahtung und Projektindex | Abfrage über konfigurierte CodeGraph-MCP-Tools |
| **Ponytail** | Minimal-Implementierungs-Anleitungs-Skill | Unnötige Abhängigkeiten und Abstraktionen | Nur Anleitung, wenn der Host den Skill lädt |
| **Caveman** | Prägnanz-Anleitungs-Skill | Überlange Antworten | Stilanleitung bei Laden; Klarheit und Sicherheitsdetails erhalten |
| **RTK** | Optionale Rust Token Killer CLI | Wortreiche Terminal-Ausgabe | Erfordert CLI-Installation und unterstützten Agent-Hook |
| **Git Auth** | Protected-Branch-Anleitung plus begrenzte Client-Hook-Prüfungen | Verhindern versehentlicher Shared-Branch-Operationen | Regeln, Claude Code Client-Hook und serverseitiger Branch-Schutz |

### Regel- und Memory-Umfang pro Coding-Tool

| Tool/Oberfläche | Anweisungseinstiegspunkt | Memory-Umfang |
|---|---|---|
| Codex Desktop-App | Projekt-`AGENTS.md`; ai-memory kann die lokale Codex-Integration nutzen, wo die installierte App konfigurierte MCP/Hooks exponiert | Exakte Desktop-Version verifizieren; ChatGPT-Web-Konversationsmemory ist separat |
| Codex CLI | Codex-Home und `AGENTS.md`-Dateien vom Repository-Root bis zum aktuellen Verzeichnis; ai-memory-Upstream-Installer unterstützt MCP/Hooks | Projektkontext-/Checkpoint-Dateien bleiben repository-verwaltet |
| Claude Code | Benutzer-/Projekt-/Verzeichnis-`CLAUDE.md` oder unterstütztes `AGENTS.md` | Optionales Auto-Memory ist maschinenlokal und Claude-spezifisch; `/memory` öffnet seine Controls |
| Antigravity CLI | Globale, Workspace- und Verzeichnis-`AGENTS.md` / `.agents/rules/*.md`; ai-memory-Upstream unterstützt MCP/Hooks | Setup in derselben Umgebung wie die CLI ausführen |
| Antigravity IDE | Projekt-Markdown-Regeln/Skills plus manuell konfigurierter ai-memory-MCP-Server | MCP bietet explizite Retrieval-/Schreib-Tools; keine automatische Lifecycle-Erfassung wird behauptet |

Die Deployment-Skripte schreiben Pfade; vor der Annahme, dass eine Datei konsumiert wurde, die aktuelle Dokumentation und den geladenen Kontext jedes Hosts prüfen.

---

## 2. Skills- & Ökosystem-Tool-Inventar

### 2.1 44 integrierte native Skills kategorisiert

Der Installer kopiert die Skill-Verzeichnisse des Repositorys nach `.agents/skills/`; die tatsächliche Erkennung hängt vom Host-Tool und seiner Konfiguration ab.

#### 1. Versionierter Workflow-Einstiegspunkt
- **`comet`**: Die Comet CLI bietet versionierte Native- und Classic-Workflows. Dieses Repository liefert nur eine Einstiegspunkt-Anleitung; es implementiert keine Comet-Phase-Guards.

#### 2. OpenSpec-Spezifikationsgetriebene Suite (16 Skills)
- **`openspec`**: Kernarchitektur.
- **`openspec-propose`**: Schlägt Änderungen mit Design, Specs und Tasks in einem Schritt vor.
- **`openspec-new-change`**: Schrittweise Artefakterstellung.
- **`openspec-continue-change`**: Führt Change zum nächsten Artefakt fort.
- **`openspec-ff-change`**: Fast-Forward durch Artefaktgenerierung.
- **`openspec-apply-change`**: Implementiert Tasks aus einem aktiven Change.
- **`openspec-verify-change`**: Verifiziert Code gegen Delta-Spezifikationen.
- **`openspec-sync-specs`**: Synct Delta-Specs in Haupt-Specs.
- **`openspec-archive-change`**: Archiviert abgeschlossenen Change.
- **`openspec-bulk-archive-change`**: Archiviert mehrere Changes parallel.
- **`openspec-explore`**: Interaktiver Denkpartner vor Change-Erstellung.
- **`openspec-onboard`**: Geführter interaktiver Walkthrough.
- **`write-openspec-docs`**: Schreibt Docs im Hausstil.
- **`draft-openspec-docs`**: Kollaboratives abschnittsweises Drafting.
- **`verify-openspec-docs`**: Faktencheck von Dokumentationsbehauptungen.
- **`release-openspec`**: Release-Audit und Changeset-Management.

#### 3. Superpowers-Engineering-Qualitätssuite (15 Skills)
- **`superpowers`**: Qualitätsverfassung.
- **`using-superpowers`**: Skill-Erkennung und Aufruf-Guard.
- **`brainstorming`**: Design-Exploration vor Implementierung.
- **`writing-plans`**: Schrittweise Ausführungsplanung.
- **`executing-plans`**: Strikte Planausführung.
- **`test-driven-development`**: TDD-Red-Green-Zyklus.
- **`systematic-debugging`**: Root-Cause-Analyse vor Codemodifikation.
- **`verification-before-completion`**: Obligatorischer Nachweis vor Fertigstellungsbehauptung.
- **`dispatching-parallel-agents`**: Spawnt isolierte konkurrierende Subagents.
- **`subagent-driven-development`**: Subagent-Plan-Ausführungsharness.
- **`using-git-worktrees`**: Isolierte physische Workspaces.
- **`finishing-a-development-branch`**: Merge- und Integrationsentscheidungen.
- **`requesting-code-review`**: Pre-Merge-Review-Verifizierung.
- **`open-code-review`**: Deterministisches Code-Review — regelzuerst, zeilenverankert, coverage-verpflichtend. Tier A via `ocr`-CLI-Delegation, Tier-B-Methodik ohne.
- **`receiving-code-review`**: Technische Bewertung menschlicher Review-Kommentare.
- **`writing-skills`**: Skill-Ersteller und -Validator.
- **`diagnosing-superpowers`**: Auditiert Sitzungsdrift oder Kosten.

#### 4. Minimaler Code & Syntaxgraph
- **`ponytail`**: Minimale Implementierungsleiter (Stdlib zuerst, YAGNI).
- **`codegraph`**: Optionale CodeGraph-CLI/MCP-Setup-Anleitung; Installation und Agent-Verdrahtung sind separat.

#### 5. Ausgabefilterung & prägnante Lieferung
- **`rtk`**: Optionale Rust-Token-Killer-CLI-Anleitung; Befehls-Rewriting erfordert einen konfigurierten Agent-Hook.
- **`caveman`**: Ultra-komprimierte telegrafische Ausgabe.

#### 6. Professionelle Dokumentenverarbeitung
- **`docx`**: Word-Dokumentenerzeugung, -bearbeitung und -styling.
- **`pdf`**: PDF-Text-/Tabellenextraktion und -verarbeitung.

#### 7. Pre-Decision-Review, toolübergreifendes Memory & Living Documentation (In-Repo-Skills)
- **`cross-tool-memory`**: Toolübergreifende projektspezifische Memory-Navigations- und Recall-Hilfe (paart mit lokalem ai-memory-Backend).
- **`option-review`**: Pre-Decision-Multi-Options-Review generiert eine isolierte 5-Dimensionen-Entscheidungsmatrix.
- **`living-documentation`**: 4-stufige Living-Documentation-Suite (specs/architecture/reference/guides) mit Frontmatter-basierter Code-Doc-bidirektionaler Traceability, unterstützt L0/L1/L2-Change-Impact-Schwellen.
- **`engineering-docs`**: F&E-Lebenszyklus-Dokumententemplates (31 Dokumenttypen, 15 bilinguale Phase-Gate-Templates) gewährleisten konsistente Ausgabe über AI-Agents und nahtlose Integration mit Comet-Phase-Gates und Living Documentation.

---

### 2.2 Versions-Locking, Online-Updates & Skill-Sync (`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`)

1. **`skills-lock.json`**:
   - Zeichnet Upstream-Quellen und LF-normalisierte SHA256-Integritätshashes für vendored externe Skills auf;
   - Unterscheidet lokal verfasste Core-Skills (`sourceType: local`) von externen Upstream-Skills (`sourceType: github`).
2. **Externer Skill-Upstream-Sync (`tools/sync-skills.py`)**:
   - Eingebauter Updater für vendored externe Skills;
   - **Check-Modus**: `python3 tools/sync-skills.py --check` (read-only, vergleicht lokale und Upstream-`SKILL.md`-Hashes, meldet 🟢 in-sync / 🟡 outdated);
   - **Apply-Modus**: `python3 tools/sync-skills.py --apply` (aktualisiert veraltete `SKILL.md`-Dateien in-place und refresht Lock-Hashes; lokal verfasste Skills sind strikt geschützt);
   - Interaktive Terminal-UI powered by `tools/tui.py` bei argumentlosem Aufruf;
   - Unterstützt `--skill <name>` für gezielte Updates und `--json` für Automatisierung.
3. **Living-Documentation-Impact-Analyse (`tools/doc-impact.py`)**:
   - Analysiert Code-Änderungen gegen Living-Documentation-Traceability-Metadaten (`docs/{specs,architecture,reference,guides,adr}/`);
   - Unterstützt Working-Tree-Inspektion, Commit-Baselines (`--since`), explizite Dateilisten und interaktiven Wizard-Modus (`--interactive`).
4. **Einheitlicher Pipeline-Runner (`run-pipeline.sh` / `run-pipeline.ps1`)**:
   - Verkettet den vollständigen Workflow zu einer einzigen Ausführung pro OS (Deploy → AI Memory → Skills Sync → Living Doc Impact);
   - Interaktiver Assistent: `./run-pipeline.sh` (Linux/macOS) oder `.\run-pipeline.ps1` (Windows);
   - Unbeaufsichtigte Automatisierung: `./run-pipeline.sh --all -y` oder `.\run-pipeline.ps1 -All -Yes`.
5. **Terminal-interaktive TUI-Komponente (`tools/tui.py`)**:
   - Bietet tastaturgesteuerte Einfachauswahl (Pfeiltasten + Enter) und Mehrfachauswahl (Pfeiltasten + Leertaste-Checkbox-Toggle + Enter zur Bestätigung) interaktive Menüs;
   - Features eingebaute TTY- und ANSI-Kompatibilitätserkennung mit graceful Fallback auf nummerierte Text-Prompts in nicht-interaktiven oder nicht-ANSI-Pipelines, als Grundlage aller Deployment- und Wartungstools.
6. **Integrierter Online-Update-Flow**:
   ```powershell
   # Windows
   .\deploy-agents.ps1 -ProjectPath "." -Update

   # Linux / macOS
   ./deploy-agents.sh . --update
   ```
   - Die Deployment-Skripte aktualisieren das Template-Repository per Fast-Forward, fragen zum Prüfen/Anwenden externer Skill-Updates und synchronisieren verwaltete Dateien zu Zielprojekten mit `.bak.<timestamp>`-Backups.

---

### 2.3 Optionale Harness-CLI-Tools

Die Skill-Verfügbarkeit hängt vom Host-Tool und seiner Konfiguration ab. Terminal-Level-CLI-Tools sind optional:
- **Comet CLI**: Installieren via `npm install -g @rpamis/comet`; bietet Native/Classic-Workflow-Ausführung und `--comet-init`-Initialisierung.
- **CodeGraph CLI**: macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh`; Windows PowerShell: `irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex`. `codegraph install` ausführen, um Agents zu verdrahten, und `codegraph init` im Projekt.
- **RTK (Rust Token Killer) CLI**: macOS/Linux: `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh`; Windows: `winget install rtk-ai.rtk`. Mit `rtk gain` verifizieren. `rtk init` im Projekt ausführen, um Agent-Hooks zu konfigurieren.
- **Open Code Review (OCR) CLI**: Installieren via `npm install -g @alibaba-group/open-code-review`; ermöglicht Tier-A-Zero-LLM-Cost-Delegations-Review via dem `open-code-review`-Skill.

Die Deployment-Skripte erkennen diese optionalen CLIs während des initialen Setups automatisch und leiten die Installation an, wo angemessen.

---

### 2.4 Skill-Laden und optionales CLI-Setup

Skill-Erkennung und Kontextkosten hängen vom Host-Agent und seiner Konfiguration ab. Allein die Dateiexistenz garantiert nicht, dass ein Skill geladen wird. Ponytail und Caveman sind Anleitungs-Skills, die mit dem Projekt kopiert werden; CodeGraph und RTK brauchen zusätzlich ihre separaten CLI- und Agent-Integrationsschritte. Ihre Effektivität hängt von Projekt, Host und Setup ab, daher macht diese Anleitung keine festen Token-Einsparungsbehauptungen.

---

### 2.5 Engineering-Skills- & Regel-Dispatching-Matrix

| Szenario | Regel / Skill | Trigger / Keyword | Erwartetes Verhalten |
|---|---|---|---|
| **Branching / Commit / Push** | [`git-workflow.md`](../../.agents/rules/git-workflow.md) | `git commit` / `git push` | Nur auf temporären Branches committen; kein `git add .`; menschliche Autorisierung für Remote-Push erforderlich |
| **Hochrisiko-Operationen** | [`security-boundary.md`](../../.agents/rules/security-boundary.md) | Ändern von Build-Konfigurationen, Protokollen, öffentlichen Structs | Pausieren und Impact mit Mensch bestätigen |
| **Komplexe Anforderungen** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `comet` / `openspec` | `/comet` oder "use openspec" | Change unter `docs/openspec/changes/` vorschlagen; auf Bestätigung warten |
| **Symbol-Discovery** | [`token-discipline.md`](../../.agents/rules/token-discipline.md) + optionales `codegraph` | CodeGraph MCP wenn konfiguriert; sonst scoped `rg` | Nicht annehmen, dass CodeGraph installiert oder verfügbar ist |
| **Feature-Implementierung** | `ponytail` + `test-driven-development` | Geladene Skills nach Bedarf konsultieren | Aktuellen Code verstehen, dann kleinste korrekte Implementierung und geeignete Validierung wählen |
| **Bug-Untersuchung** | `systematic-debugging` | Error-Trace eingefügt | Evidenz sammeln $\rightarrow$ Hypothese bilden $\rightarrow$ minimales Repro $\rightarrow$ fixen |
| **Lange Terminal-Ausgabe** | optionales `rtk` | Nur wenn installiert und sein Agent-Hook konfiguriert | Sonst native prägnante Flags nutzen; erforderliche Validierung beibehalten und relevante Logs erhalten |
| **Token-Schonung** | `caveman` | Nur wenn der Host den Skill oder das Plugin lädt | Prägnant sein unter Erhalt notwendigen Kontexts, technischer Genauigkeit und Sicherheitsdetails |
| **Dokumentenverarbeitung** | `docx` / `pdf` | Erwähnt `.docx` oder `.pdf` | Professionelle Formatierung ohne Ausführen von Code-Test-Suites |
| **Living Docs & Traceability** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `living-documentation` | `/living-documentation` / Trace-Docs syncen | 4-stufige Docs (specs/architecture/reference/guides) via L0/L1/L2-Impact-Schwellen und Frontmatter-Traceability pflegen |
| **Phase-Gate-Docs / Templates** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `engineering-docs` | `/engineering-docs` / SRS/HLD/Spec-Anfragen | AI-Agent-Ausgaben über Phasen standardisieren mit 15 bilingualen Phase-Gate-Templates, Comet-Artefakte mit Living Documentation verbinden |
| **Code-Review & Qualitäts-Gate** | `open-code-review` + `requesting-code-review` | Vor Merge oder nach Task-Abschluss | Regel-zuerst, zeilenverankert, coverage-verpflichtend; Tier-A-Delegation wenn `ocr`-CLI existiert, sonst Tier-B-Methodik |
| **Task-Abschluss** | `verification-before-completion` | Task-Ende | Physische Befehlsausführungs-Evidenz präsentieren |

---

## 3. Vertiefung in zentrale Harness-Tools & Slash Commands

### 3.1 Comet: Versionierter Workflow-Einstiegspunkt

Comet ist ein unabhängig versioniertes Workflow-Tool. Die `.comet/config.yaml` des Projekts und die installierte CLI-Version prüfen, dann dem von dieser Version unterstützten Native- oder Classic-Workflow folgen. Der Comet-Skill dieses Repositorys ist eine Einstiegspunkt-Anleitung; er erstellt keine Comet-State-Dateien und setzt keine Phase-Guards durch. Wenn Comet nicht installiert oder konfiguriert ist, den vorhandenen Projektprozess nutzen oder einen task-angemessenen Plan erstellen. Gepaart mit `engineering-docs` nutzt jede Phase (Open, Design, Build, Verify, Archive) standardisierte Gate-Templates für konsistente Deliverables.

```text
/comet Add date-range filtered CSV export for the order service
```

Die aktuelle Upstream-Dokumentation von Comet für versionsspezifische Einstiegspunkte, Konfiguration, Artefaktpfade und Archivverhalten nutzen.

---

### 3.2 OpenSpec: Spezifikationsgetriebene Entwicklung

- `/opsx:propose <name>`: Schlägt neuen Change unter `docs/openspec/changes/` vor;
- `/opsx:apply`: Implementiert genehmigten Change;
- `/opsx:verify`: Vergleicht tatsächliche Implementierung mit Delta-Spezifikation;
- `/opsx:sync`: Synct Delta-Spezifikationen in Haupt-Docs;
- `/opsx:archive`: Verschiebt fertigen Change nach `docs/openspec/changes/archive/`.

---

### 3.3 Superpowers: TDD, systematisches Debugging & Verifikations-Gate

1. **TDD-Red-Green-Zyklus**:
   - Fehlschlagenden Test basierend auf Spezifikationsszenario schreiben;
   - Test ausführen und erwarteten Fehlschlag beobachten;
   - Minimalen Code schreiben, um zu bestehen;
   - Refactoren und Verifikation ausführen.
2. **Systematisches Debugging**:
   - Schritt 1: Trace-Sammlung;
   - Schritt 2: Hypothese bilden;
   - Schritt 3: Minimaler Reproduktionstest;
   - Schritt 4: Root Cause fixen und verifizieren.
3. **Verifikationsevidenz-Gate**:
   - Kein Task ist ohne physische Terminal-Ausgabe-Evidenz abgeschlossen.

---

### 3.4 CodeGraph: Optionale MCP-Code-Graph-Integration

```bash
# Call-Chains und Architektur explorieren
Das für den aktuellen Agent konfigurierte CodeGraph-MCP-Tool abfragen: „User authentication and JWT token flow".

# Definitionen und alle Aufruf-referenzen finden
Das konfigurierte CodeGraph-MCP-Tool für `OrderService::calculateDiscount` abfragen.
```

---

### 3.5 Ponytail: Minimale Implementierungsleiter

1. Muss dieses Feature existieren? (YAGNI);
2. Gibt es ein vorhandenes Utility zur Wiederverwendung?
3. Kann die Sprach-Standardbibliothek das?
4. 1 Zeile ändern, bevor 10 Zeilen rewritten werden;
5. Niemals opportunistisches Refactoring während Bugfixes.

---

### 3.6 Caveman: Ultra-komprimierte Ausgabe

- Eliminiert Fluff: "Sure, I'll do that for you", "Note that this requires caution";
- Liefert: Fazit & Impact $\rightarrow$ Diff $\rightarrow$ Verifikationsevidenz.

---

### 3.7 RTK: Optionale Rust-Token-Killer-CLI

- RTK rewritet unterstützte Befehle nur, wenn installiert und mit dem aktiven Agent integriert. Der Repository-Skill allein filtert keine Terminal-Ausgabe.
- Das korrekte Produkt mit `rtk gain` verifizieren; unterstützte Projekt-Hooks mit `rtk init` initialisieren.
- Wenn RTK nicht konfiguriert ist, native prägnante Flags und begrenztes Log-Handling nutzen.

- Niemals bloße verbose Befehle ausführen;
- Immer `git status -s`, `pytest -q`, `ctest --output-on-failure` nutzen;
- Mehrere hundert Zeilen Logs in lokale Scratch-Dateien umleiten und nur die Failure-Traces slicen.

---

### 3.8 Git-Autorisierungsmodell & Protected-Branch-Workflow

1. **Temporäre-Branch-Isolation**:
   - Alle Arbeit findet in `feature/*`, `fix/*`, `refactor/*` statt;
   - Niemals direkt auf `develop`, `master`, `main`, `release*`, `staging` committen.
2. **Remote-Push-Autorisierung**:
   - AI kann Branches erstellen und lokal committen;
   - Push zu Remote oder Merge in geschützte Branches erfordert explizite menschliche Bestätigung.
3. **Eiserne Gesetze**:
   - `git push --force` ist permanent verboten;
   - Rebase geschützter Branches ist permanent verboten;
   - Blindes Staging via `git add .` ist verboten (`git add <explicit-path>` nutzen);
   - Commit-Message-Standard: `{type}: {description}`.

---

### 3.9 Projekt-Memory und Sitzungs-Checkpoint (`PROJECT_CONTEXT.md` / `SESSION_STATE.md`)

Memory als verifizierbare Zusammenfassung und Navigationshilfe behandeln, nicht als Ersatz für Code oder gepflegte Dokumentation:
1. **Task-Start:** `PROJECT_CONTEXT.md` (verifizierte dauerhafte Projektfakten) und `SESSION_STATE.md` (aktueller Checkpoint) nur lesen, wenn vorhanden und relevant; Branch, Konfiguration und Implementierungsfakten verifizieren, die den Task betreffen.
2. **Während der Arbeit:** Pläne bei Bedarf für mehrstufige Arbeit behalten. Keine automatische Erfassung von Prompts, Tool-Inputs/Outputs, Quelldateien oder Terminal-Befehlen hinzufügen.
3. **Sinnvoller Abschluss:** `SESSION_STATE.md` mit abgeschlossener Arbeit, tatsächlicher Verifikationsevidenz, verbleibenden Schritten und noch relevanten Risiken aktualisieren; veraltete Items entfernen. `PROJECT_CONTEXT.md` nur aktualisieren, wenn sich dauerhafte Architektur, Constraints oder bestätigte Entscheidungen ändern. No-op-Sitzungen brauchen kein leeres Update.
4. **Quellen und Konflikte:** Unsicherheit kennzeichnen und Fakten mit Datum/Quelle versehen, die sich wahrscheinlich ändern. Aktuelle Benutzeranweisungen und aktueller Code/Konfiguration/reproduzierbare Evidenz haben Vorrang vor Memory-Zusammenfassungen.
5. **Privatsphäre:** Keine Credentials, privaten Schlüssel, rohen persönlichen Daten, vollständigen Konversations-/Tool-Logs oder unnötigen persönlichen Informationen aufzeichnen. Geteilte globale Templates dürfen keine privaten Benutzerpräferenzen enthalten.
6. **Verzeichnisumfang:** Ein Verzeichnis-`AGENTS.md` enthält nur lokale Grenzen und Constraints. Standardmäßig keine Verzeichnis-Memory-Dateien erstellen; Projektfakten und Checkpoints in ihren Root-Dateien halten.

**Claude Code natives Auto-Memory** ist ein separates maschinenlokales Projekt-Memory, das mit `/memory` eingesehen, editiert oder gelöscht werden kann. Es wird nicht tool- oder maschinenübergreifend geteilt und ersetzt nicht die obigen Projektdateien. Claude Code verwaltet dieses Feature; der Deployer dieses Repositorys aktiviert, deaktiviert oder erfasst es nicht. Siehe die [Claude Code Memory-Docs](https://code.claude.com/docs/en/memory).

#### Optionales toolübergreifendes Memory: ai-memory

Dieses Repository wählt nur [ai-memory](https://github.com/akitaonrails/ai-memory) als optionales toolübergreifendes Backend. Sein lokaler Markdown- und Volltextsuchpfad nutzt kein LLM, keinen Embedding-Provider und keinen API-Key. Das Repository installiert oder startet es nicht automatisch.

Zum Opt-in eines Repositorys `.ai-memory.toml.example` nach dem ignorierten `.ai-memory.toml` kopieren, die Workspace-/Projektnamen ersetzen, dann `setup-ai-memory.ps1 -Agent <claude-code|codex|antigravity-cli>` oder `./setup-ai-memory.sh <claude-code|codex|antigravity-cli>` ausführen. Der Helfer erfordert eine vorhandene ai-memory-Installation und delegiert die Konfiguration an seine Upstream-merge-bewussten Befehle. Die Hook-Fähigkeitsausgabe prüfen; der Allowlist-Modus ist nur für Hooks wirksam, die native Capture-Policy durchsetzen.

Das Setup umfasst Claude Code- und Codex-CLI-MCP/Hooks plus Antigravity-CLI-MCP/Hooks. Codex-Desktop-Support hängt von der installierten Desktop-Version ab, die die lokale Codex-Integration exponiert; in der App verifizieren. Antigravity IDE ist MCP-only: `http://127.0.0.1:49374/mcp` als `serverUrl` über seine MCP-Einstellungen oder die dokumentierte Konfigurationsdatei hinzufügen. Für Docker-Bereitstellung `docker run -d --name ai-memory --restart unless-stopped -p 127.0.0.1:49374:49374 -v "${HOME}/env/ai-memory-data:/data" docker.io/akitaonrails/ai-memory:latest` ausführen (der Container-Speicherpfad ist fix `/data`). ChatGPT Web nutzt manuellen Markdown-Handoff im kostenlosen lokalen Setup.

Windows unterstützt sowohl WSL2- als auch native Modi upstream. ai-memory in derselben Umgebung installieren und konfigurieren, die den Agent startet; siehe die [Windows-Anleitung](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md). Pfadausschlüsse redigieren keinen beliebigen Prompt-Text. Sichern mit `ai-memory --data-dir <data-dir> backup --to <archive-path>`; Deinstallation entfernt Integrationen, aber keine Daten. Den Dienst stoppen und das konfigurierte Datenverzeichnis verifizieren, bevor es absichtlich gelöscht wird. Siehe die [Marker-Referenz](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md) und [Installationsanleitung](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md) für Plattformpfade und Docker-Befehle.

### 3.10 8-Hochrisiko-Operationen-Schutzmatrix

Menschliche Bestätigung ist obligatorisch vor:
- [ ] 1. Ändern von Build-Konfigurationen (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`);
- [ ] 2. Hinzufügen neuer Drittanbieter-Abhängigkeiten;
- [ ] 3. Ändern globaler öffentlicher Datenstrukturen (`public_struct.h`, `types.ts`);
- [ ] 4. Ändern von Core-Dispatch-Singletons oder öffentlichen Service-APIs;
- [ ] 5. Ändern von Wire-Protokollen oder Serialisierungs-Contracts (`protofile/`);
- [ ] 6. Ändern von Lizenz-, Kryptografie- oder Auth-Code;
- [ ] 7. Ändern von `.gitignore` oder CI/CD-Pipelines;
- [ ] 8. Hochwirksame modulübergreifende Änderungen, die geteilte Contracts betreffen oder breite Koordination erfordern (allein die Dateianzahl ist kein Risiko-Trigger).

---

## 4. Plattformspezifische native Befehle & Best Practices

### 4.1 Google Antigravity CLI und IDE
- Die CLI läuft als `agy`; die Desktop-IDE ist eine separate Oberfläche. Beide dokumentieren dateibasierte Workspace-/globale Regeln, aber CLI-Slash-Commands und IDE-Controls sind oberflächenspezifisch.
- `/plan`: Strukturierte Task-Planung für $\ge 3$ Schritte;
- `/goal`: Unbeaufsichtigte autonome Schleife bis zur verifizierten Fertigstellung;
- `/grill-me`: Interaktives Discovery-Interview bei unklaren Anforderungen;
- `/learn`: Erfasst gelernte Lektionen in `tasks/lessons.md`;
- `/schedule`: Hintergrund-Timer und wiederkehrendes Cron-Monitoring.

### 4.2 Claude Code und PreToolUse-Client-Hook
- `/compact`: Komprimiert Konversationshistorie bei hoher Token-Anzahl;
- `/cost`: Echtzeit-Sitzungs-Token-Nutzung;
- `/review`: Reviewed Working-Copy-Diffs;
- `@<path>`: Lädt spezifische Regeln dynamisch bei Bedarf.
- **Sicherheits-Hook**: `.claude/settings.json` führt Claude Code-clientseitige Prüfungen für passende Tool-Aufrufe aus. Er kann ausgewählte Muster ablehnen oder warnen; er ist keine Betriebssystemkontrolle und kein Memory-Collector.

### 4.3 Codex in ChatGPT, Codex CLI und GitHub Copilot
- Codex CLI dokumentiert `AGENTS.md`-Erkennung vom Codex-Home und dem Repository-Pfad bis zum aktuellen Verzeichnis. Nicht auf exaktes Verhalten für ChatGPT/Desktop schließen; dessen aktuelles Produktverhalten und Konfiguration prüfen.
- `/hooks`: Inspiziert und vertraut Lifecycle-Hooks;
- `$comet`: Triggert Comet-State-Machine in Codex CLI;
- `@workspace`: Scannt Workspace-Kontext in VS Code.

### 4.4 Zed IDE
- Projekt-`AGENTS.md` wiederverwenden; dieser Installer erstellt keine Zed-spezifische Datei;
- `Ctrl+Enter` (Inline Assist) mit `follow ponytail principles`;
- Assistant Panel (`Ctrl+?`) für mehrstufige Architekturplanung.

---

## 5. End-to-End-Praxis-Walkthrough (reale Feature-Entwicklung)

**Anforderung**: „Einen CSV-Export-Endpunkt mit Datumsbereichsfilterung zum Order-Service hinzufügen."

```text
Schritt 1: Sitzungszeremonie & Breakpoint-Awareness (Sitzungsstart)
  ├─ Prioritär PROJECT_CONTEXT.md & SESSION_STATE.md lesen, um Architektur wiederherzustellen & vom Breakpoint fortzusetzen
  ├─ tasks/lessons.md und tasks/todo.md prüfen (falls vorhanden)
  └─ git checkout -b feature/order-csv-export

Schritt 2: Scoping & Change-Erstellung (Comet + OpenSpec SDD)
  ├─ /comet Add date range CSV export endpoint
  ├─ Generiert: docs/openspec/changes/add-csv-export/
  └─ Proposal mit Mensch bestätigen

Schritt 3: Optionales semantisches Retrieval (CodeGraph, falls konfiguriert)
  ├─ Verboten: grep -rn "export" .
  └─ Konfiguriertes CodeGraph-MCP abfragen; sonst scoped Code-Suche nutzen
      └─ Gefunden: router.py, order_repo.py, types.ts

Schritt 4: Roter Test (Superpowers TDD)
  ├─ tests/test_export.py: Fehlschlagenden Test mit ungültiger Datumsbereichsprüfung schreiben
  └─ pytest tests/test_export.py -q -> FAILED (Rot)

Schritt 5: Minimale Implementierung (Ponytail)
  ├─ Python-Stdlib: import csv, datetime (kein schweres Export-Paket)
  └─ Filterbedingung in order_repo.py und Route in router.py hinzufügen

Schritt 6: Grüne Verifikation (RTK)
  ├─ pytest tests/test_export.py -q -> PASSED (Grün, 2 passed in 0.3s)
  └─ npm test -- packages/order --reporter=dot

Schritt 7: Lieferung, sicherer Commit & selektiver Memory-Abschluss (Sitzungsende)
  ├─ Ausgabe: Prägnanter Diff und bestandene Testevidenz
  ├─ git add tests/test_export.py api/router.py repo/order_repo.py
  ├─ git commit -m "feat: add date-range CSV export endpoint"
  ├─ Mensch vor git push fragen
  ├─ Selektiver Memory-Abschluss:
  │   ├─ SESSION_STATE.md an sinnvollen Task-Grenzen mit tatsächlicher Evidenz und verbleibender Arbeit aktualisieren
  │   └─ PROJECT_CONTEXT.md nur aktualisieren, wenn sich dauerhafte Projektfakten ändern; leere Updates überspringen
  ├─ tasks/todo.md aktualisieren
  └─ OpenSpec-Change archivieren
```

---

## 6. Tägliche Health Checks & Troubleshooting

### Täglicher Health Check:
```bash
Die installierte Comet-Version und Projektkonfiguration vor Nutzung Comet-spezifischer Befehle prüfen.
`tasks/lessons.md` lesen, wenn es für den Task relevant ist.
```

### Referenzdokumentation:
- Einheitliche Pipeline-Runner:
  - Windows: [`run-pipeline.ps1`](../../run-pipeline.ps1)
  - Linux / macOS: [`run-pipeline.sh`](../../run-pipeline.sh)
- One-Click-Deployment-Skripte:
  - Windows: [`deploy-agents.ps1`](../../deploy-agents.ps1)
  - Linux / macOS: [`deploy-agents.sh`](../../deploy-agents.sh)
- Wartungstools:
  - Terminal-UI-Bibliothek: [`tools/tui.py`](../../tools/tui.py)
  - Skill-Sync-Tool: [`tools/sync-skills.py`](../../tools/sync-skills.py)
  - Living-Doc-Impact-Gate: [`tools/doc-impact.py`](../../tools/doc-impact.py)
- Bereitstellungs- & Konfigurationsanleitung:
  - [Multi-Tool Deployment and Configuration Guide (English)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)
  - [多工具部署配置指南 (中文)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md)
- Regelarchitektur:
  - [`Global AGENTS.md`](../../templates/agents/Global%20AGENTS.md)
  - [`Project AGENTS.md`](../../templates/agents/Project%20AGENTS.md)
  - [`Directory AGENTS.md`](../../templates/agents/Directory%20AGENTS.md)
