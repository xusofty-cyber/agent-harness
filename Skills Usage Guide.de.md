# Skills-Nutzungsleitfaden

> **Language / 语言**: [English](Skills%20Usage%20Guide.md) | [简体中文](Skills%20Usage%20Guide.zh.md) | [繁體中文](Skills%20Usage%20Guide.zh-tw.md) | [Français](Skills%20Usage%20Guide.fr.md) | **Deutsch**

Wie die 43 gebündelten Skills in der Praxis funktionieren: welche automatisch auslösen, welche explizit aufgerufen werden und wann man welche einsetzt.

## Funktionsweise der Skill-Trigger

Claude Code entscheidet auf zwei Arten über das Laden eines Skills:

| Modus | Methode | Beispiel |
|---|---|---|
| **Auto** | Claude liest die `description` des Skills und ruft ihn auf, wenn die Anfrage übereinstimmt | Sie sagen "fix this bug" → `systematic-debugging` lädt automatisch |
| **Explizit** | Sie geben den Slash-Befehl ein oder benennen den Skill direkt | Sie tippen `/comet` oder sagen "nutze comet für diese Aufgabe" |
| **Hybrid** | Beides funktioniert — automatisches Auslösen bei passendem Kontext oder direkter Aufruf | Sie sagen "review this PR" → `open-code-review` lädt; oder tippen `/open-code-review` |

**Wichtige Erkenntnis:** Das automatische Auslösen hängt vom Feld `description` in der Datei `SKILL.md` jedes Skills ab.
Wenn Claude einen Skill nicht wie erwartet lädt, benennen Sie ihn einfach explizit.

## Skill-Katalog

> **Skill-Domänen** (Namespaces für gezieltes Laden): Jeder Skill gehört zu einer Domäne,
> in `skills-lock.json` erfasst und per CI erzwungen. Bei Agents mit Teilbedarf pro Domäne laden statt Vollkatalog.
>
> | Domäne | Skills | Zweck |
> |---|---|---|
> | `openspec` | 17 | OpenSpec-Workflow-Familie |
> | `superpowers` | 16 | obra/superpowers-Methodenfamilie |
> | `local` | 5 | Im Repo erstellt (engineering-docs, living-documentation, open-code-review, option-review, cross-tool-memory) |
> | `document` | 2 | Dokumentenverarbeitung (docx, pdf) |
> | `integration` | 2 | Externe Tool-Integrationen (comet, codegraph) |
> | `utility` | 3 | Einzelzweck-Utilities (caveman, ponytail, rtk) |
>
> **Hinweis zur Zählung**: `skills-lock.json` hat 45 Einträge, dieser Katalog listet 43 Skills.
> Die 2 zusätzlichen Einträge (`openspec`, `superpowers`) sind Meta-Einträge der Quell-Repos —
> Provenienz-Platzhalter, keine installierbaren Skills. nach Kategorien

### 1. Workflow- und Ablaufsteuerung

| Skill | Trigger | Befehl | Funktion | Wann einsetzen |
|---|---|---|---|---|
| `comet` | Explizit | `/comet` | Versionierte Workflow-Zustandsmaschine (Phasen, Guards, Archive). Erfordert installiertes Comet-CLI + `.comet/config.yaml` im Projekt. | Wenn das Projekt Comet für phasenbasierte Ausführung nutzt. Einmalig `/comet init` pro Projekt ausführen, dann `/comet` für den Workflow-Modus. Ohne CLI erklärt der Skill die Einschränkung und fällt auf den Standardablauf zurück. |
| `openspec-new-change` | Auto | — | Startet eine neue OpenSpec-Änderung (spezifikationsgetriebene Entwicklung). | Zu Beginn eines Features/Fixes, das vorab Spezifikationsartefakte benötigt. Sagen Sie "use openspec" oder beschreiben Sie das Feature. |
| `openspec-propose` | Auto | — | Erzeugt alle OpenSpec-Artefakte in einem Schritt. | Für einen schnellen Spezifikationsentwurf ohne den vollständigen Explorationszyklus. |
| `openspec-explore` | Hybrid | — | Denkpartner-Modus zur Ideenexploration vor der Spezifikation. | Bei unklaren Anforderungen. Sagen Sie "lass uns das mit openspec erkunden". |
| `openspec-apply-change` | Auto | — | Implementiert Aufgaben einer bestehenden OpenSpec-Änderung. | Nach Freigabe der Spezifikation: "implement the openspec change". |
| `openspec-continue-change` | Auto | — | Erstellt das nächste Artefakt in einer laufenden Änderung. | Bei Wiederaufnahme von OpenSpec-Arbeiten: "continue the openspec change". |
| `openspec-update-change` | Hybrid | — | Überarbeitet bestehende OpenSpec-Artefakte. | Wenn während der Implementierung Anpassungen an der Spezifikation nötig sind. |
| `openspec-verify-change` | Auto | — | Validiert die Übereinstimmung der Implementierung mit den Spezifikationen. | Vor dem Abschluss: "verify against the openspec". |
| `openspec-sync-specs` | Auto | — | Synchronisiert Delta-Spezifikationen zurück in die Hauptspezifikationen. | Nach Abschluss und Merge der Änderung. |
| `openspec-archive-change` | Auto | — | Archiviert eine abgeschlossene Änderung. | Finale Bereinigung nach dem Merge. |
| `openspec-bulk-archive-change` | Auto | — | Archiviert mehrere abgeschlossene Änderungen gleichzeitig. | Batch-Bereinigung. |
| `openspec-ff-change` | Auto | — | Schneller Vorlauf unter Umgehung der Artefakterstellung. | Um Zeremonien zu überspringen und direkt zur Implementierung überzugehen. |
| `openspec-onboard` | Hybrid | — | Geführte Einführung in den OpenSpec-Workflow. | Bei der ersten Nutzung von OpenSpec: "onboard me to openspec". |
| `draft-openspec-docs` | Hybrid | — | Kollaborativer Entwurfsmodus für OpenSpec-Dokumentation. | Beim Erstellen von OpenSpec-Dokumentseiten. |
| `write-openspec-docs` | Hybrid | — | OpenSpec-Dokmodus mit Hausstil. | Beim Schreiben von OpenSpec-Benutzerdokumentation. |
| `verify-openspec-docs` | Hybrid | — | Prüft OpenSpec-Dokumentation mit frischem Kontext. | Beim Validieren von OpenSpec-Dokumentationsaussagen. |
| `release-openspec` | Hybrid | — | Prüft zusammengeführte Arbeit für OpenSpec-Releases. | Bei einem OpenSpec-Release. |
| `living-documentation` | Hybrid | — | Pflegt Spezifikationen/Architektur/Referenzen/Leitfäden mit Rückverfolgbarkeit. | Fortlaufend. Aktiviert sich bei Dokumentationsaufgaben; "update living docs" erzwingt den Lauf. |

### 2. Codequalität und Review

| Skill | Trigger | Befehl | Funktion | Wann einsetzen |
|---|---|---|---|---|
| `requesting-code-review` | Auto | — | Entscheidet, **wann** ein Review erforderlich ist (Timing-Gate). | Löst nach Fertigstellung signifikanter Arbeiten automatisch aus. |
| `open-code-review` | Auto | — | Deterministische Review-**Methode** (Dateiauswahl, Regelabgleich, zeilenbezogene Befunde). | Löst bei Diffs/PRs automatisch aus. Explizit: "review dieses diff mit open-code-review". |
| `receiving-code-review` | Auto | — | Verarbeitet eingehendes Review-Feedback vor der Umsetzung. | Beim Einfügen von Review-Kommentaren: automatische Triage. |
| `systematic-debugging` | Auto | — | Strukturiertes Debugging: Reproduzieren → Isolieren → Hypothese → Beheben → Verifizieren. | Bei jedem Bug, Testfehlschlag oder unerwartetem Verhalten. Löst vor einem Lösungsvorschlag aus. |
| `test-driven-development` | Auto | — | Erzwingt den Rot-Grün-Refactor-Zyklus. | Bei Feature-/Bugfix-Implementierung. Tests zuerst schreiben. |
| `verification-before-completion` | Auto | — | Checkliste vor Abschluss: Tests ausführen, Behauptungen verifizieren. | Bevor "fertig" gemeldet wird — verlangt Nachweise statt reiner Behauptungen. |

### 3. Planung und Design

| Skill | Trigger | Befehl | Funktion | Wann einsetzen |
|---|---|---|---|---|
| `brainstorming` | Auto | — | Erkundet Absichten, Anforderungen und Design vor der Implementierung. **Pflicht vor kreativer Arbeit.** | Bei jedem neuen Feature, jeder Komponente oder Verhaltensänderung. Wenn Claude direkt codet: "erst brainstormen". |
| `writing-plans` | Auto | — | Erstellt strukturierte Implementierungspläne aus Spezifikationen. | Mehrschrittige Aufgaben. Löst aus, wenn Anforderungen ohne Plan vorliegen. |
| `executing-plans` | Auto | — | Führt Pläne als Implementierer aus. | Nach Planfreigabe: "execute the plan". |
| `option-review` | Auto | — | Vergleicht 2+ gangbare Ansätze mit einer Entscheidungsmatrix. | Bei Unentschlossenheit: "sollte ich A oder B wählen?". |
| `dispatching-parallel-agents` | Auto | — | Verteilt unabhängige Aufgaben auf parallele Subagents. | 2+ unabhängige Aufgaben. Sagen Sie "das parallel erledigen". |
| `subagent-driven-development` | Auto | — | Orchestriert die Implementierung über Subagents. | Umfangreiche Pläne mit unabhängigen Komponenten. |
| `using-git-worktrees` | Auto | — | Isoliert Feature-Arbeiten in Git Worktrees. | Vor Arbeiten, die Isolation vom aktuellen Branch erfordern. |
| `finishing-a-development-branch` | Auto | — | Entscheidet über die Integrationsstrategie (merge/rebase/squash). | Wenn die Implementierung abgeschlossen ist und Tests bestehen. |

### 4. Gedächtnis und Kontext

| Skill | Trigger | Befehl | Funktion | Wann einsetzen |
|---|---|---|---|---|
| `cross-tool-memory` | Auto | — | Lädt/speichert dauerhaftes Projektgedächtnis über Werkzeuge hinweg. Fällt auf `PROJECT_CONTEXT.md` / `SESSION_STATE.md` zurück, wenn ai-memory MCP fehlt. | Bei Weiterarbeit an bestehenden Projekten. Lädt Kontext automatisch; "merke dir das" speichert explizit. Siehe [Projektgedächtnis-Einrichtung](#projektgedächtnis-einrichtung) unten. |
| `using-superpowers` | Auto | — | Etabliert das Skill-Discovery-Protokoll zu Sitzungsbeginn. | Löst zu Sitzungsbeginn automatisch aus. Stellt sicher, dass Claude verfügbare Skills vor der Antwort prüft. |

### 5. Entwicklungswerkzeuge

| Skill | Trigger | Befehl | Funktion | Wann einsetzen |
|---|---|---|---|---|
| `codegraph` | Auto | — | Semantische Code-Exploration über CodeGraph MCP. Erfordert installiertes CodeGraph-CLI. | "Wo wird X verwendet?" / "zeige Aufrufer von Y". Fällt ohne CLI auf grep zurück. |
| `rtk` | Auto | — | Rust Token Killer: schreibt geschwätzige Terminalausgaben kompakt um. Erfordert RTK-CLI. | Komprimiert laute Befehlsausgaben automatisch. "disable rtk" für Rohausgabe. |
| `docx` | Hybrid | — | Erstellt, liest und bearbeitet Word-Dokumente. | "Erstelle einen .docx-Bericht" oder "lies diese Word-Datei". |
| `pdf` | Hybrid | — | Liest und extrahiert Text/Tabellen aus PDFs. | "Fasse dieses PDF zusammen" oder "extrahiere Tabellen...". |
| `caveman` | Hybrid | — | Stark komprimierter Ausgabemodus (spart Tokens). | "Sei prägnant" / "caveman mode". Stufen: lite, full, ultra. |
| `ponytail` | Hybrid | — | Erzwingt die einfachste funktionierende Lösung (Anti-Overengineering). | "Halte es einfach" / wenn Claude überdimensioniert. |

### 6. Meta-Skills

| Skill | Trigger | Befehl | Funktion | Wann einsetzen |
|---|---|---|---|---|
| `writing-skills` | Auto | — | Leitet die Erstellung, Bearbeitung und Verifizierung von Skills an. | Beim Erstellen oder Ändern von Skills in `.agents/skills/`. |
| `diagnosing-superpowers` | Auto | — | Diagnostiziert Fehler im Superpowers-Workflow. | Wenn Claude Pläne ignoriert oder Arbeiten wiederholt. Sagen Sie "diagnostiziere, was schiefgelaufen ist". |

### 7. Engineering-Dokumentation

| Skill | Trigger | Befehl | Funktion | Wann einsetzen |
|---|---|---|---|---|
| `engineering-docs` | Hybrid | — | 15 zweisprachige Vorlagen für 31 F&E-Dokumenttypen (Projektantrag → Anforderungen → Entwurf → Test → Übergabe). Inklusive Rendering-Spezifikation für einheitliche Formatierung. | Beim Verfassen formeller F&E-Dokumente. Sagen Sie „erstelle ein PRD“ / „schreibe einen Grobentwurf“, um die passende Vorlage zu aktivieren. |

## Projektgedächtnis-Einrichtung

### `PROJECT_CONTEXT.md` und `SESSION_STATE.md`

Dies ist die dateibasierte Ausweichlösung, wenn der ai-memory MCP-Dienst nicht verfügbar ist.
Der Skill `cross-tool-memory` liest diese Dateien automatisch. Beim Ausführen von `deploy-agents.sh / .ps1` oder `run-pipeline.sh / .ps1` (und `pipeline.sh / .ps1`) werden fehlende Dateien im Zielprojekt **automatisch aus Vorlagen initialisiert**. Sie können sie auch manuell anhand der folgenden Vorlagen erstellen oder anpassen.

**Wann erstellen:**
- `PROJECT_CONTEXT.md`: Einmal pro Projekt, sobald die Architektur stabil ist. Nur aktualisieren, wenn sich dauerhafte Fakten ändern (Stack, Constraints, Schlüsselentscheidungen).
- `SESSION_STATE.md`: Am Ende jeder wichtigen Arbeitssitzung oder bei Übergaben. Mit erledigten Aufgaben, Verifizierungsnachweisen und nächsten Schritten aktualisieren.

**Wie initiale Versionen erstellt werden:**

Fragen Sie Claude direkt:
```text
Erstelle PROJECT_CONTEXT.md für dieses Projekt im Format des cross-tool-memory Skills.
```

Oder kopieren Sie diese Vorlagen:

#### Vorlage `PROJECT_CONTEXT.md`

```markdown
# PROJECT_CONTEXT.md

> Dauerhafte Projektfakten. Nur aktualisieren, wenn sich Architektur, Einschränkungen oder bestätigte Entscheidungen ändern.
> Keine sitzungsspezifischen Zustände hier ablegen — diese gehören in SESSION_STATE.md.

## Tech-Stack
- Sprache/Framework:
- Build:
- Test:

## Architektur
- (Schlüsselkomponenten und deren Verantwortlichkeiten)

## Einschränkungen
- (Nicht verhandelbare technische oder organisatorische Vorgaben)

## Wichtige Entscheidungen
- JJJJ-MM-TT: (Entscheidung und Begründung)
```

#### Vorlage `SESSION_STATE.md`

```markdown
# SESSION_STATE.md

> Aktueller Kontrollpunkt. An bedeutungsvollen Aufgabengrenzen aktualisieren.
> Veraltete Punkte entfernen; übersichtlich halten.

## Zuletzt aktualisiert
- JJJJ-MM-TT: (kurze Sitzungszusammenfassung)

## Abgeschlossen
- (Was wurde getan, mit Verifizierungsnachweisen)

## In Bearbeitung
- (Woran wird aktuell gearbeitet)

## Nächste Schritte
- (Was bleibt zu tun, nach Priorität geordnet)

## Offene Risiken / Fragen
- (Ungelöste Probleme oder ausstehende Entscheidungen)
```

**Ablageort:** Projektstammverzeichnis. Der Skill `cross-tool-memory` sucht dort nach den Dateien.

**Verzeichnisbereich:** Keine Gedächtnisdateien pro Unterverzeichnis erstellen. Projektfakten gehören in die Stammdateien;
verzeichnisbezogene `AGENTS.md`-Dateien enthalten nur lokale Grenzen und Einschränkungen.
