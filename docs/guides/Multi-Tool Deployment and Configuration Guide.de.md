# Multi-Tool (Codex / Claude Code / Antigravity 2.0 / CLI / IDE / Zed) AI Engineering Deployment & Configuration Guide

> **Language / Sprache**: [English](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md) | [简体中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | [繁體中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh-tw.md) | [Français](Multi-Tool%20Deployment%20and%20Configuration%20Guide.fr.md) | **Deutsch**

Diese Anleitung bietet eine End-to-End-Spezifikation für die Bereitstellung, Konfiguration und kollaborative Nutzung der **dreistufigen AGENTS.md-Architektur** (Global-, Projekt- und Verzeichnisebene) über **OpenAI Codex / GitHub Copilot**, **Claude Code**, **Google Antigravity IDE** und **Zed IDE**, zugeschnitten auf reale Szenarien mit Schwerpunkt Softwareentwicklung bei gleichzeitiger Unterstützung professioneller technischer Dokumentation.

---

## Inhaltsverzeichnis

1. [Architektur & Schichtenpositionierung (Harness + Progressive Disclosure)](#1-architektur--schichtenpositionierung-harness--progressive-disclosure)
2. [Konfigurationsumfang pro Tool](#2-konfigurationsumfang-pro-tool)
3. [Claude Code Client-Hooks: PreToolUse (.claude/settings.json)](#3-claude-code-client-hooks-pretooluse-claudesettingsjson)
4. [Toolübergreifende Bereitstellung & Template-Updates (deploy-agents)](#4-toolübergreifende-bereitstellung--template-updates-deploy-agents)
   - 4.1 Kernarchitektur & Pipeline des Skripts
   - 4.2 Windows-Bereitstellung (`deploy-agents.ps1`)
   - 4.3 Linux- / macOS-Bereitstellung (`deploy-agents.sh`)
   - 4.4 Symlink- vs. Verzeichnis-Junction-Mechanik
5. Vertiefung in die vier Regelebenen
   - 5.1 Globale Verfassung: `Global AGENTS.md`
   - 5.2 Projekt-Router: `Project AGENTS.md`
   - 5.3 Modulare Unterregeln: `.agents/rules/`
   - 5.4 Mikro-Grenz-Patch: `Directory AGENTS.md`
6. Zweigleisiger Praxis-Workflow: „Engineering zuerst, Dokumentation danach"
7. Häufig gestellte Fragen & Best Practices (FAQ)
8. Referenz: Praxis- & Skills-Panorama-Anleitung

---

## 1. Architektur & Schichtenpositionierung (Harness + Progressive Disclosure)

Dieses Repository organisiert wiederverwendbare Regeln als **Projekteinstiegspunkt plus bedarfsgesteuerte Unterregeln**, damit Teams die Basislinie anpassen können, ohne irrelevante Anleitungen zu laden. Die tatsächliche Erkennung und die Kontextkosten hängen vom Host-Tool ab:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Globale Ebene (Global AGENTS.md)                                    │
│    - Rolle: Projektübergreifende Engineering-Verfassung & Sicherheitsbasis │
│    - Inhalt: Wiederverwendbare Engineering-Basis, Git-Sicherheit, präzise Kommunikation │
│    - Umfang: Systemweit resident über alle Benutzerprojekte (~1000 Tok) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Vererbt (nicht redundant)
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. Projekt-Root-Ebene (Project AGENTS.md)                              │
│    - Rolle: Deterministischer Engineering-Kontext & Unterregel-/Skill-Router │
│    - Inhalt: Konkrete CLI-Slots, Tech-Stack, rote Linien, Zustandsmemory │
│    - Umfang: Repository-weit; Laden hängt vom Host-Tool ab             │
│    - Bridges: CLAUDE.md / .github/copilot-instructions.md              │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ Progressive On-Demand-Lesung    │ Nur bei Bedarf in Submodulen
┌──────────────────▼───────────────┐ ┌───────────────▼───────────────────┐
│ 3. Unterregeln (.agents/rules/)  │ │ 4. Verzeichnisebene (Directory AGENTS.md)│
│  - token-discipline.md           │ │    - Rolle: Mikro-Grenz-Patch     │
│  - engineering-spec.md (SDD/TDD) │ │    - Inhalt: In/Out-Umfang, isolierte│
│  - security-boundary.md          │ │            Abhängigkeiten, schnelle Tests│
│  - git-workflow.md (Auth-Modell) │ └───────────────────────────────────┘
└──────────────────────────────────┘
```

### Kernvorteile
1. **Gemeinsame Basislinie**: Wiederverwendbare Regeln in Markdown-Templates halten und tool-spezifische Bridges verwenden, wo unterstützt; das Erkennungsverhalten jedes Hosts verifizieren, statt anzunehmen, dass jedes Tool dieselbe Datei lädt.
2. **Progressive Disclosure**:
   - Regeln werden dynamisch geladen, wenn bestimmte Szenarien ausgelöst werden.
   - Skill-Erkennung, -Laden und Prompt-Cache-Verhalten hängen vom Host-Tool und seiner Konfiguration ab; das Bereitstellen von Dateien garantiert kein automatisches Laden.
3. **Clientseitige Risiko-Leitplanken**: Claude Code-Hooks können ausgewählte passende Tool-Aufrufe ablehnen oder Warnungen ausgeben. Es handelt sich um clientseitige Prüfungen, nicht um Betriebssystem- oder serverseitige Sicherheitskontrollen.

---

## 2. Konfigurationsumfang pro Tool

Regelerkennung, Vererbung, globale Einstellungen und Memory-Mechanismen variieren je nach Produkt und Version. Diese Tabelle trennt Pfade, die von den Skripten geschrieben werden, von der Host-Erkennung; die Dateibereitstellung ist keine Ladeverifizierung.

| Tool/Oberfläche | Von diesem Repository bereitgestellt oder geschrieben | Ladehinweise |
| :--- | :--- | :--- |
| Codex (lokale App / IDE / CLI) | Globales `$CODEX_HOME/AGENTS.md` (Standard `~/.codex/AGENTS.md`); Projekt- und Verzeichnis-`AGENTS.md` | `-Global` erstellt die globale Datei; `-Global -Update` sichert und ersetzt die aktive globale Anweisungsdatei. Codex bevorzugt eine nicht leere `AGENTS.override.md` im Codex-Home gegenüber `AGENTS.md` |
| Claude Code | `CLAUDE.md`-Bridge, `~/.claude/CLAUDE.md`, Projekt-Hooks/Skills | `CLAUDE.md` ist ein Anweisungseinstiegspunkt; Claude Auto Memory ist ein separates optionales maschinenlokales Projekt-Memory, das nicht toolübergreifend geteilt wird |
| Antigravity 2.0 | Projekt-`AGENTS.md` / `GEMINI.md` / `.agents/rules/`; globales `~/.gemini/AGENTS.md` und `GEMINI.md`-Kompatibilitätszeiger | Aktuelle Docs listen beide globale Namen; ältere Releases können dem Zeiger zur kanonischen Datei folgen |
| Antigravity CLI | Projekt-/Verzeichnisregeln; globales `~/.gemini/AGENTS.md` und `GEMINI.md`-Kompatibilitätszeiger; optional `~/.gemini/antigravity-cli/rules/*.md` | Gemeinsame Regeln nutzen den kanonischen Einstieg; CLI-spezifische Regeln separat konfigurieren |
| Antigravity IDE / Extensions | Projekt-/Verzeichnisregeln; globales `~/.gemini/AGENTS.md` und `GEMINI.md`-Kompatibilitätszeiger | Aktuelle IDE unterstützt beide globale Namen; ältere IDE-Generationen können dem Zeiger folgen |
| GitHub Copilot | `.github/copilot-instructions.md`-Bridge | Laden in den aktuellen Copilot-Produkteinstellungen/Dokumentation bestätigen |
| Zed / Pi / OpenCode | Nur wiederverwendbares Markdown; kein dediziertes Setup aus diesem Repository | Keine automatische Erkennung oder globales Laden aus der Dateiexistenz ableiten |

Referenzen: [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [Claude Code memory](https://code.claude.com/docs/en/memory), [Antigravity rules](https://www.antigravity.google/docs/rules/).

---

## 3. Claude Code Client-Hooks: PreToolUse (.claude/settings.json)

### Fähigkeitsgrenzen
Die Hooks in `.claude/settings.json` sind Claude Code-spezifisch und laufen nur vor passenden Tool-Aufrufen. `guard.mjs` lehnt ausgewählte Befehlsmuster ab; viele andere Fälle geben nur eine Warnung aus. Regex-Matching kann nicht jede Shell-Wrapper-, Alias- oder Befehlsform identifizieren, daher ist dies keine vollständige Sicherheitsgrenze. Die Hooks sammeln oder übertragen keine Memory-Daten. Claude Code Auto Memory ist ein separates maschinenlokales Projekt-Feature, das Benutzer mit `/memory` einsehen/verwalten können; dieses Repository konfiguriert es nicht. Serverseitigen Branch-Schutz und Least-Privilege-Credentials für geteilte Repositories verwenden.

### Konfiguration und Implementierung

Der Installer kopiert [`.claude/settings.json`](../../.claude/settings.json) und stellt [`.claude/hooks/guard.mjs`](../../.claude/hooks/guard.mjs) plus [`guard-write.mjs`](../../.claude/hooks/guard-write.mjs) bereit. Diese Quelldateien direkt prüfen; keine Hook-Beispiele aus älteren Anleitungsversionen kopieren, da sich Protokoll und Implementierung ändern können.

### Entsprechungen bei anderen Tools (Erweiterungspunkt)

PreToolUse-Hooks sind Claude Code-spezifisch; der Installer installiert keine Interceptors für andere Tools. Für gleichwertigen Schutz den eigenen Hook-/Genehmigungsmechanismus jedes Tools verdrahten: Die Entscheidungslogik in `guard.mjs` (geschützte Branches, gefährliche Befehlsmuster) ist reines Node.js — ihre Regexes und Branch-Tabelle wiederverwenden und an den Hook-Einstiegspunkt des Ziel-Tools anpassen. Unabhängig von der gehookten Schicht ersetzt sie niemals serverseitigen Branch-Schutz; clientseitiges Abfangen ist nur eine Schicht der Defense in Depth.

---

## 4. Toolübergreifende Bereitstellung & Template-Updates (deploy-agents)

Die Skripte stellen Dateien an konfigurierten Pfaden bereit. Tool-spezifisches Ladeverhalten wird durch die Dateibereitstellung nicht garantiert. `-Global` initialisiert fehlende globale Regeldateien und erhält vorhandene. Die Kombination `-Global -Update` erstellt zuerst ein zeitgestempeltes Backup und ersetzt dann die aktive globale Regel durch das aktuelle Template. Antigravity erhält das kanonische `~/.gemini/AGENTS.md` plus einen kleinen `GEMINI.md`-Kompatibilitätszeiger statt eines doppelten vollständigen Regelsatzes. Codex verwendet `$CODEX_HOME`, wenn gesetzt (sonst `~/.codex`); existiert dort eine nicht leere `AGENTS.override.md`, wird diese aktive Datei gesichert und aktualisiert statt `AGENTS.md`:
- **Windows PowerShell**: [`deploy-agents.ps1`](../../deploy-agents.ps1)
- **Linux / macOS Bash**: [`deploy-agents.sh`](../../deploy-agents.sh)

### 4.1 Kernarchitektur & Pipeline des Skripts

```text
[ Deployment-Skript ausführen ]
       │
       ├─ [Keine Argumente im Terminal ODER mit -Interactive / --interactive]
       │       ▼
       │  Phase 0: Interaktiver Schritt-für-Schritt-Terminal-Assistent (TUI Pfeiltasten & Checkboxen)
       │    ├─ [1/5] Template-Sprache wählen (English / 简体中文 / 繁體中文 / Français / Deutsch)
       │    ├─ [2/5] Bereitstellungsumfang wählen (Nur Zielprojekt / Nur globale Regeln / Beides)
       │    ├─ [3/5] Zielprojektpfad eingeben (Standard: aktuelles Verzeichnis [.])
       │    │        (Hinweis: Codex, Antigravity, Zed lesen AGENTS.md nativ ohne Bridges)
       │    ├─ [4/5] Agent-Bridge-Dateien mehrfach wählen (Claude, Copilot, Cursor, Gemini, Windsurf, Cline, Roo, Qwen, Kiro, Continue, Trae, CodeBuddy)
       │    └─ [5/5] Optionale Workflows mehrfach wählen (Update-Modus / Projektfaktenscan / ai-memory / Comet)
       │
       ▼
 Phase 1: Template-Repository-Update (-Update)
   └─ Fast-Forward-Update dieses Template-Repositorys (`git pull --ff-only`); kein globales CLI-Upgrade oder Drittanbieter-Updater im Aufruferverzeichnis
       │
       ▼
 Phase 2: Globale Benutzerregeln (-Global)
   ├─ Claude Code initialisieren (~/.claude/CLAUDE.md) nur wenn Ziel fehlt
   ├─ Antigravity initialisieren (~/.gemini/AGENTS.md) nur wenn Ziel fehlt
   └─ Vorhandene Dateien erhalten; mit -Update benachbarte *.template.md-Dateien zum manuellen Mergen schreiben
       │
       ▼
 Phase 3: Projektregeln & Toolübergreifende Bridges
   ├─ Root AGENTS.md (generiert AGENTS.template.md wenn bereits vorhanden)
   ├─ CLAUDE.md -> AGENTS.md (Symlink/Referenz)
   ├─ .github/copilot-instructions.md -> ../AGENTS.md
   ├─ Zed nutzt das bereitgestellte AGENTS.md; keine Zed-spezifische Konfiguration wird erstellt
   └─ Claude Code PreToolUse Client-Hooks: .claude/settings.json
       │
       ▼
 Phase 4: Unterregeln (.agents/rules/*.md)
       │
       ▼
 Phase 5: Skills-Bibliothek (.agents/skills/ & .claude/skills/)
   ├─ Skills nach .agents/skills/ kopieren
   ├─ Nach .claude/skills/ verlinken (Windows: Junction, Linux/macOS: Symlink)
   └─ skills-lock.json-Metadaten kopieren
       │
       ▼
 Phase 6: Dynamisches Task-Tracking-Gerüst
   ├─ tasks/lessons.md (Fehlernotizbuch)
   └─ tasks/todo.md (Checkliste)
       │
       ▼
 Phase 7: OpenSpec-Gerüst (docs/openspec/changes/)
       │
       ▼
 Phase 8: Optionaler Comet CLI Init (-CometInit)
   └─ Führt `comet init` nur bei expliziter Anforderung aus
       │
       ▼
 Phase 9: Optionaler ai-memory Init (-AiMemoryInit)
   └─ Initialisiert .ai-memory.toml für toolübergreifendes Memory bei expliziter Anforderung
       │
       ▼
 Phase 10: Optionale CLIs prüfen & interaktive Prompts
   ├─ CodeGraph / RTK / Open Code Review (ocr) / Comet-Installation anbieten falls fehlend
   ├─ Fragen ob CodeGraph-Agents verdrahtet / Projekt indexiert werden soll
   ├─ Fragen ob rtk init ausgeführt werden soll; im nicht-interaktiven Modus übersprungen
   ├─ ocr-Installation ermöglicht Tier-A-Delegations-Review; Tier B funktioniert offline ohne
   └─ Comet CLI-Installation ermöglicht anschließende Workflow-Initialisierung via --comet-init
```

---

### 4.2 Windows-Bereitstellung (`deploy-agents.ps1`)

**Verwendung**:
```powershell
.\deploy-agents.ps1 [[-ProjectPath] <target-path>] [-Global] [-Update] [-Interactive] [-CometInit] [-AiMemoryInit] [-Pipeline]
```

**Parameter**:
- `-ProjectPath` (Position 0): Pfad zum Zielprojekt. Wenn mit `-Global` weggelassen, werden nur globale Benutzerregeln aktualisiert.
- `-Global` (`-g`): Initialisiert fehlende `~/.claude/CLAUDE.md`, `~/.gemini/AGENTS.md` und Codex `$CODEX_HOME/AGENTS.md` (Standard `~/.codex/AGENTS.md`). Vorhandene Dateien bleiben ohne `-Update` erhalten.
- `-Language` (`-l`): Wählt Template-Sprache (`en`, `zh`, `zh-tw`, `fr`, `de`; Standard `en`).
- `-Interactive` (`-i`): Startet den interaktiven Schritt-für-Schritt-Auswahlassistenten (Einfachauswahl Sprache & Umfang, Mehrfachauswahl Agent-Bridges und Optionen). Wird automatisch ausgelöst bei argumentloser Ausführung in einem interaktiven Terminal.
- `-Update` (`-u`): Aktualisiert das Template-Repository per Fast-Forward, ruft automatisch `tools/sync-skills.py --check` auf, um externe Skills mit interaktiver Bestätigung auf Upstream-Updates zu prüfen, und synchronisiert Dateien zum Ziel. Kombiniert mit `-Global` werden vorhandene globale Regeldateien gesichert und ersetzt. Codex' nicht leere `$CODEX_HOME/AGENTS.override.md` hat Vorrang und wird als aktive Datei aktualisiert. Vorhandene projektverwaltete Regeln, Hooks, Skills und Lock-Metadaten folgen ihrem dokumentierten Backup-/Update-Verhalten. Es werden keine globalen CLIs upgegradet.
- `-CometInit` (`-c`): Führt automatisch `comet init` im Zielprojekt aus, wenn Comet CLI installiert ist.
- `-AiMemoryInit` (`-m`): Initialisiert automatisch `.ai-memory.toml` im Zielprojekt (leitet `workspace` und `project` ab) für toolübergreifende ai-memory-Integration.
- `-Pipeline`: Delegiert die Ausführung direkt an den einheitlichen Pipeline-Runner ([`run-pipeline.ps1`](../../run-pipeline.ps1)).

**Einheitlicher Pipeline-Runner (Windows)**:
```powershell
# Interaktiver Schritt-für-Schritt-Assistent (Sprache, Projekt, Phasen, Modus):
.\run-pipeline.ps1

# Unbeaufsichtigte vollständige Pipeline-Ausführung in einem Durchgang:
.\run-pipeline.ps1 -All -Yes

# Bestimmte Phasen ausführen:
.\run-pipeline.ps1 -Stages "deploy,skills,docs"
```

**Beispiele**:
```powershell
# Szenario 0: Interaktiver Assistent (argumentlose Ausführung)
.\deploy-agents.ps1

# In einem neuen Projekt bereitstellen
.\deploy-agents.ps1 "D:\Projects\my-project"

# Projekt bereitstellen und globale Regeln aktualisieren
.\deploy-agents.ps1 "D:\Projects\my-project" -Global

# Skills und Unterregeln online aktualisieren
.\deploy-agents.ps1 "D:\Projects\my-project" -Global -Update

# Mit Comet-Terminal-Hooks initialisieren
.\deploy-agents.ps1 "D:\Projects\my-project" -CometInit

# Mit toolübergreifender ai-memory-Konfiguration initialisieren
.\deploy-agents.ps1 "D:\Projects\my-project" -AiMemoryInit

# Einheitliche Pipeline direkt starten
.\deploy-agents.ps1 -Pipeline

# Nur globale Regeln aktualisieren
.\deploy-agents.ps1 -Global -Update
```

---

### 4.3 Linux- / macOS-Bereitstellung (`deploy-agents.sh`)

```bash
chmod +x ./deploy-agents.sh ./run-pipeline.sh

# Szenario 0: Interaktiver Assistent (argumentlose Ausführung)
./deploy-agents.sh

# In Projekt bereitstellen
./deploy-agents.sh /path/to/my-project

# Bereitstellen und globale Regeln aktualisieren
./deploy-agents.sh /path/to/my-project --global

# Online-Update
./deploy-agents.sh /path/to/my-project --global --update

# Mit Comet CLI-Init bereitstellen
./deploy-agents.sh /path/to/my-project --comet-init

# Einheitliche Pipeline direkt starten
./deploy-agents.sh --pipeline
```

**Einheitlicher Pipeline-Runner (Linux / macOS)**:
```bash
# Interaktiver Schritt-für-Schritt-Assistent (Sprache, Projekt, Phasen, Modus):
./run-pipeline.sh

# Unbeaufsichtigte vollständige Pipeline-Ausführung in einem Durchgang:
./run-pipeline.sh --all -y

# Bestimmte Phasen ausführen:
./run-pipeline.sh --stages deploy,skills,docs
```

### Bereitstellung mit ai-memory-Init
```bash
./deploy-agents.sh /path/to/my-project --ai-memory-init
```

---

### 4.4 Symlink- vs. Verzeichnis-Junction-Mechanik

Damit Claude Code Skills in `.agents/skills/` entdecken kann:
- **Linux / macOS**: Verwendet standardmäßige relative symbolische Links:
  `ln -sf "../../.agents/skills/${name}" ".claude/skills/${name}"`
- **Windows**: Normale Benutzerkonten können keine Verzeichnis-Symboliklinks ohne Entwicklermodus oder Administratorrechte erstellen. `deploy-agents.ps1` löst dies durch **NTFS-Verzeichnis-Junctions**:
  `New-Item -ItemType Junction -Path ".claude\skills\$name" -Target ".agents\skills\$name"`
  - Funktioniert ohne erhöhte Rechte;
  - Echtzeit-Verzeichnisspiegelung ohne Dateiduplizierung;
  - Automatischer Fallback auf rekursives Kopieren, wenn Junctions nicht unterstützt werden.

---

## 5. Vertiefung in die vier Regelebenen

### 5.1 Globale Regelvorlage: `Global AGENTS.md`
- **Zweck:** Eine wiederverwendbare projektübergreifende Engineering-Basislinie. Ob ein Host sie lädt und mit welcher Priorität, hängt vom Host und der Benutzerkonfiguration ab.
- **Teilungsgrenze:** Die geteilte Vorlage generisch halten; keine persönlichen Präferenzen, Projektfakten oder sensiblen Informationen hineinlegen. Persönliche Präferenzen nur an einem benutzerkontrollierten maschinenlokalen Ort speichern, wenn explizit angefordert.
- **Memory-Schichten:**
  1. Bei Task-Start `PROJECT_CONTEXT.md` (verifizierte dauerhafte Projektfakten) und `SESSION_STATE.md` (aktueller Checkpoint) lesen, wenn relevant, dann Fakten verifizieren, die die Arbeit betreffen.
  2. An einer sinnvollen Task-/Sitzungsgrenze `SESSION_STATE.md` aktualisieren und veralteten Status entfernen. `PROJECT_CONTEXT.md` nur aktualisieren, wenn sich dauerhaftes Projektwissen ändert; No-op-Sitzungen brauchen keine leeren Updates.
  3. `PROJECT_CONTEXT.md` ist eine Projektzusammenfassung und Navigationshilfe, keine Single Source of Truth über Code, Konfiguration oder gepflegte Dokumentation. Aktuelle Benutzeranweisungen und reproduzierbare Evidenz haben Vorrang vor Memory.
  4. Unsicherheit kennzeichnen und Fakten mit Datum/Quelle versehen, die sich wahrscheinlich ändern. Niemals Credentials, private Schlüssel, rohe persönliche Daten, vollständige Konversations-/Tool-Logs oder unnötige persönliche Informationen speichern.

**Ausgewähltes optionales Backend: [ai-memory](https://github.com/akitaonrails/ai-memory).** Sein lokaler Modus bietet Markdown-basiertes Projekt-Memory, Volltext-Retrieval und toolübergreifende Handoffs ohne LLM oder API-Key. Für den normalen Gebrauch nicht erforderlich. Dieses Repository liefert einen expliziten Setup-Helfer, installiert oder startet das Backend aber niemals, erstellt keinen lokalen Opt-in-Marker und ändert keine Tool-Konfiguration während der normalen Bereitstellung.

> **Supply-Chain-Hinweis**: ai-memory ist eine native Drittanbieter-Binärdatei mit Prompt-lesenden Hooks. Nur von der offiziellen Releases-Seite herunterladen und die veröffentlichten SHA256-Prüfsummen verifizieren (bei `cargo install` den Crate-Namen `ai-memory` bestätigen). `setup-ai-memory.*` lädt es bewusst niemals für Sie herunter, verifiziert vor jeder Konfiguration, dass es eine native ausführbare Datei ist (lehnt Wrapper-Skripte ab), und pinnt die validierte Version (aktuell **v2.6.0** — eine Abweichung verweigert die Konfiguration). Vor Upgrades die Upstream-Release-Notes prüfen und vor dem Bump des Pins die Install-Flags erneut verifizieren.

#### Explizites Projekt-Opt-in und Setup

1. ai-memory separat installieren und starten gemäß seiner [offiziellen Installationsanleitung](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md). LLM- und Embedding-Provider für den kostenlosen Zero-Key-Pfad unkonfiguriert lassen.
2. `.ai-memory.toml.example` prüfen, nach `.ai-memory.toml` kopieren und beide Namen ersetzen. `.ai-memory.toml` wird von Git ignoriert; ein Commit dieses Opt-ins wird bewusst vermieden.
3. `./setup-ai-memory.sh <claude-code|codex|antigravity|antigravity-ide|antigravity-cli>` unter Linux/macOS/WSL2 ausführen, oder den entsprechenden `-Agent`-Wert in PowerShell. `antigravity` für Antigravity 2.0 und `antigravity-ide` für die IDE verwenden; beide konfigurieren MCP und verwaltete Anweisungen. Das CLI-Target installiert zusätzlich Allowlist-Hooks. Nativer Executable- und Hook-Mode-Preflight gilt für Hook-Targets; MCP-only-Targets brauchen ihn nicht. Der Helfer lädt keine Software herunter und startet keinen Server.
4. Den Server für Same-Machine-Nutzung an Loopback binden. Standard-Datenorte sind `~/.local/share/ai-memory` unter Linux, `~/Library/Application Support/ai-memory` unter macOS und typischerweise `%LOCALAPPDATA%\ai-memory` unter Windows; `AI_MEMORY_DATA_DIR` kann sie überschreiben.
   - **Docker-Bereitstellung (für Antigravity IDE HTTP MCP)**:
     ```bash
     # In-Container-Speicherpfad muss /data sein; bindet an Loopback 127.0.0.1
     mkdir -p "${HOME}/env/ai-memory-data"
     docker run -d --name ai-memory \
       --restart unless-stopped \
       -p 127.0.0.1:49374:49374 \
       -v "${HOME}/env/ai-memory-data:/data" \
       docker.io/akitaonrails/ai-memory:latest
     ```
     *Hinweis: Der Docker-Container muss keine Repository-Bäume oder `.ai-memory.toml` mounten. Antigravity IDE übergibt Projektkontext (`workspace`/`project`) über MCP-Tool-Aufrufe.*
   - Sichern mit `ai-memory --data-dir <data-dir> backup --to <archive-path>` (für Docker-Bereitstellungen den Upstream-Container-Befehl verwenden). `ai-memory uninstall --apply` entfernt verwaltete Client-Integrationen, löscht aber keine Daten. Zum Löschen von Memory den Dienst stoppen und erst nach Bestätigung von Backup und Ziel das konfigurierte Datenverzeichnis entfernen. Siehe die [offizielle Installations-/Betriebsanleitung](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md).

#### Host-Grenzen

- **Claude Code:** Upstream-MCP/Hooks; ai-memory besitzt nur seine Einträge und erhält unzugehörige Hooks. Der vorhandene Claude-`PreToolUse`-Sicherheits-Hook bleibt separat. Claude Codes Standard-Auto-Memory ist ebenfalls separat und maschinenlokal.
- **Codex CLI:** Upstream-`--client codex`-/`--agent codex`-Integration. **Codex Desktop:** nutzt die lokale Codex-Konfigurationsoberfläche, wo unterstützt; die Hook-/MCP-Verfügbarkeit der installierten App verifizieren, statt anzunehmen, dass jede CLI-Version sich identisch verhält.
- **Antigravity CLI:** Upstream-`antigravity-cli`-MCP/Hooks. Unter Windows das Setup in derselben Umgebung ausführen, die den Agent startet.
- **Antigravity 2.0 und IDE:** Der Helfer nutzt den Upstream-Antigravity-MCP-Installer, um die gemeinsame `~/.gemini/config/mcp_config.json` und verwaltete Projektanweisungen zu schreiben. Das aktuelle ai-memory-Upstream hat kein dediziertes 2.0/IDE-Lifecycle-Hook-Target, daher ist dies MCP-only und erfasst Sitzungsereignisse nicht automatisch. Manuelles MCP-Setup nutzt `serverUrl=http://127.0.0.1:49374/mcp`; siehe [Antigravity MCP-Docs](https://www.antigravity.google/docs/mcp).
- **ChatGPT Web:** Das No-Key-Loopback-Setup hat keine direkte Verbindung zu einem Remote-Web-Chat. Einen prägnanten Markdown-Handoff manuell verwenden. Remote-MCP-/Schreibzugriff liegt außerhalb dieses kostenlosen lokalen Setups.
- **Windows:** Upstream dokumentiert sowohl WSL2 als auch natives Windows. ai-memory in derselben Umgebung installieren und konfigurieren, die jeden Agent startet; WSL- und Windows-Hook-Pfade nicht mischen. Die [Windows-Anleitung](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md) für client-spezifischen Support prüfen.

Der ai-memory-Allowlist-Modus garantiert nur dann keine Erfassung für Repositories ohne Marker, wenn der installierte native Hook die Capture-Policy durchsetzt. Seine Pfadausschlüsse redigieren keinen beliebigen Prompt-Text; niemals Secrets in Prompts aufnehmen. Siehe die [Marker-File-Referenz](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md).

### 5.2 Projekt-Router: `Project AGENTS.md`
- Anpassbare Template auf Repository-Ebene.
- `-Initialize` / `--initialize` zur Bereitstellung hinzufügen, um einen Entwurf aus verifizierbaren lokalen Fakten und einer Checkliste offener Punkte zu generieren. `-DirectoryPath <relative-path>` / `--directory <relative-path>` initialisiert zusätzlich ein vorhandenes Modulverzeichnis. Die Skripte erraten weder Projektzweck, Owner noch Modulgrenzen. Vorhandene `AGENTS.md`-Dateien bleiben erhalten; generierte Review-Kopien nutzen `AGENTS.generated.md`.
- Erkannte `package.json`-Skripte und gängige Framework-/Storage-Abhängigkeiten erscheinen als Review-Vorschläge, nicht als verifizierte Fakten; vor Verlass auf diese Befehle oder Grenzen bestätigen.
- `-Check` / `--check` ausführen (optional mit Verzeichnisparameter), um vor Übernahme der generierten Regeln auf ungelöste Template-Felder zu prüfen; der Befehl gibt einen Nonzero-Exit-Status zurück, wenn er welche findet.
- Bietet Standard-CLI-Befehlsslots (install, dev, build, gezielter Test, lint, format, migration), Architektur-Rote-Linien, die **Regel- & Skill-Dispatching-Matrix**, selektive Markdown-Memory-Regeln und optionale ai-memory-Integrationsanleitung.

---

### 5.3 Modulare Unterregeln: `.agents/rules/`
Werden progressiv bei Bedarf geladen:
- **`token-discipline.md`**: Beschränkt Lesen, Abrufen und Sprechen; schreibt AST-Index statt blindem grep vor;
- **`engineering-spec.md`**: SDD Spec-first (In/Out-Umfang), TDD-Verifikationsgate (physischer Nachweis erforderlich);
- **`security-boundary.md`**: 8 Hochrisiko-Operationen-Bestätigungsmatrix, null Credentials-Leak, Sicherheit großer Dateien;
- **`git-workflow.md`**: Geschützte-Branch-Isolation (null direkte Commits), obligatorische Autorisierung für Remote-Push, Commit-Format `{type}: {description}`.

---

### 5.4 Mikro-Grenz-Patch: `Directory AGENTS.md`
- Wird **nur bei Bedarf** in Monorepo-Paketen (`packages/*`) oder isolierten Submodulen erstellt.
- Eines generieren mit `-Initialize -DirectoryPath <relative-path>` (PowerShell) oder `--initialize --directory <relative-path>` (Bash); das Ziel muss bereits innerhalb des Projekt-Roots existieren. Modulpfad/-name werden erkannt, während Verantwortung und Grenzen explizite Review-Punkte bleiben.
- Definiert In/Out-Umfang, erlaubte/verbotene Abhängigkeiten und gezielte lokale Testbefehle (z. B. `pytest tests/submodule -q`).

---

## 6. Zweigleisiger Praxis-Workflow: „Engineering zuerst, Dokumentation danach"

### 1. Software-Engineering-Track (striktes Gate)
- Umfang: APIs, Features, Bugfixes, Refactoring.
- Regeln:
  - `PROJECT_CONTEXT.md` und `SESSION_STATE.md` bei Task-Start nur lesen, wenn vorhanden und relevant, dann materielle Fakten verifizieren;
  - Immer auf temporären Branches arbeiten (`feature/*`, `fix/*`);
  - TDD-Red-Green-Zyklus, mit tatsächlichen Testläufen verifizieren;
  - Git-Autorisierungsmodell befolgen;
  - **Selektive Memory-Updates**: `SESSION_STATE.md` bei sinnvollem Abschluss aktualisieren; `PROJECT_CONTEXT.md` nur aktualisieren, wenn sich dauerhafte Projektfakten ändern.

### 2. Technische-Dokumentation-Track (leichtgewichtiger Bypass)
- Umfang: Markdown-Dokumentation, READMEs, API-Spezifikationen, Word-/PDF-Berichte.
- Regeln: **Befreit vom Ausführen von Test-Suites**; spezialisierte Skills nutzen (`docx`, `pdf`, `write-openspec-docs`); GitHub Flavored Markdown-Standards einhalten.

---

## 7. Häufig gestellte Fragen & Best Practices (FAQ)

### Q1: Warum nicht alle Projektbefehle in `Global AGENTS.md` legen?
> **Antwort**: Globale Regeln sind maschinenweit über alle Sitzungen resident. Projektspezifische Befehle erzeugen toolübergreifende Kontextverschmutzung und verschwenden Prompt-Tokens.

### Q2: Wie schützt das Online-Update (`-Update`) angepasste Projektkonfigurationen?
> **Antwort**: Vorhandenes Projekt-`AGENTS.md` bleibt erhalten und ein `AGENTS.template.md` wird zur Review generiert. `-Global` initialisiert fehlende Claude Code-, Antigravity- und Codex-globale Anweisungen und erhält vorhandene Dateien. Die Kombination `-Global -Update` erstellt zeitgestempelte Backups und ersetzt diese globalen Dateien durch das aktuelle Template; Codex' aktive nicht leere `AGENTS.override.md` wird anstelle von `AGENTS.md` aktualisiert.

### Q3: Wie vermeiden 40+ Skills das Sprengen des Kontextfensters?
> **Antwort**: Es hängt davon ab, wie der Host Skills erkennt und lädt. Keine festen Metadatenkosten oder Cache-Rabatte annehmen; nur nützliche Skills aktiviert lassen und Verhalten im Ziel-Host verifizieren.

### Q4: Was ist die 8-Hochrisiko-Operationen-Schutzmatrix?
> **Antwort**: Definiert in `security-boundary.md`, erfordert menschliche Bestätigung vor:
> 1. Ändern von Build-Konfigurationen (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`);
> 2. Einführen neuer Drittanbieter-Abhängigkeiten;
> 3. Ändern globaler öffentlicher Datenstrukturen (`public_struct.h`, `types.ts`);
> 4. Ändern von Core-Dispatch-Singletons oder öffentlichen Service-Schnittstellen;
> 5. Ändern von Kommunikationsprotokollen oder Wire-Contracts (`protofile/`);
> 6. Ändern von Lizenz-, Kryptografie- oder Auth-Code;
> 7. Ändern von `.gitignore` oder CI/CD-Pipelines;
> 8. Hochwirksame modulübergreifende Änderungen, die geteilte Contracts betreffen oder breite Koordination erfordern; allein die Dateianzahl ist kein Risiko-Trigger.

### Q5: Wann sollten `PROJECT_CONTEXT.md` und `SESSION_STATE.md` aktualisiert werden?
> An sinnvollen Task-/Sitzungsgrenzen `SESSION_STATE.md` mit abgeschlossener Arbeit, tatsächlicher Verifikationsevidenz, verbleibenden Schritten und noch relevanten Risiken aktualisieren. `PROJECT_CONTEXT.md` nur aktualisieren, wenn sich dauerhafte Architektur, Constraints oder bestätigte Entscheidungen ändern. Keine No-op-Updates erstellen. Beide Dateien fassen Projekt-Memory zusammen; sie überschreiben nicht aktuelle Benutzeranweisungen, Code, Konfiguration oder reproduzierbare Evidenz. Niemals Credentials, rohe persönliche Daten oder vollständige Konversations-/Tool-Logs speichern.

---

## 8. Referenz: Praxis- & Skills-Panorama-Anleitung

Für detaillierte Tutorials zu Slash Commands (`/comet`, `/plan`, `/opsx`), CodeGraph, TDD und vollständigen End-to-End-Ausführungs-Walkthroughs siehe:
👉 [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [中文说明](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md)
