# Project AGENTS.md

## Vererbung und Positionierung

- Dieses Dokument dient als Stamm-Anweisungsdatei des aktuellen Projekts und ergänzt die allgemeine Baseline aus [Global AGENTS.md] um den projektspezifischen Engineering-Kontext.
- Nach dem Prinzip der **Progressiven Offenlegung (Progressive Disclosure)** werden hochfrequente Leitplanken und Befehle hier gepflegt; detaillierte Regeln befinden sich unter `.agents/rules/` und werden vom Agenten nur bei Bedarf geladen.

## Projektübersicht

- **Projektname**: `<PROJECT_NAME>`
- **Fachlicher Zweck**: `<PROJECT_PURPOSE>` (ein prägnanter Satz zum Kern-Einsatzszenario und zur Zielgruppe)
- **Hauptverantwortliche (Maintainer)**: `<OWNERS>`
- **Repository-URL & Standard-Branch**: `<REPOSITORY_URL>`; Standard-Branch `<DEFAULT_BRANCH>` (gemäß Remote `origin/HEAD`)

## Häufige Entwicklungsbefehle (CLI-Kontext)

> Vor Ausführung stets das Arbeitsverzeichnis prüfen. Befehle müssen Filterparameter nutzen, um Log-Überflutung zu verhindern; niemals vollständige Protokolle unbegrenzt in den Kontext leiten.

```bash
# 1. Abhängigkeitsverwaltung / Build-Konfiguration
<INSTALL_COMMAND>                  # z. B.: npm ci / poetry install / cmake -B build / go mod download / cargo check

# 2. Lokale Entwicklung und Kompilierung
<DEV_COMMAND>                      # z. B.: npm run dev / python main.py / cargo run
<BUILD_COMMAND>                    # z. B.: npm run build / cmake --build build / go build ./... / cargo build --release

# 3. Gezielte Unit-Tests & Verifikation (nach Änderungen zwingend; prägnante Ausgabe erforderlich)
<UNIT_TEST_COMMAND>                # z. B.: npm test -- --reporter=dot / pytest -q / ctest --output-on-failure
<TARGETED_TEST_COMMAND>            # Einzeldatei-Tests: npm test -- <path> / pytest <path> -q / ctest -R <test_name>
<INTEGRATION_TEST_COMMAND>         # Integrationstests: npm run test:e2e

# 4. Codequalität, Linting und statische Analyse
<LINT_COMMAND>                     # z. B.: npm run lint / ruff check . / clang-tidy / golangci-lint run / cargo clippy
<FORMAT_COMMAND>                   # z. B.: npm run format / black . / clang-format -i / gofmt -w . / cargo fmt
<TYPE_CHECK_COMMAND>               # z. B.: npm run typecheck / mypy .

# 5. Datenbankmigrationen und Releases (Hochrisiko-Aktionen erfordern Bestätigung)
<MIGRATION_COMMAND>                # z. B.: npm run db:migrate / alembic upgrade head
```

## Technologie-Stack und Laufzeitumgebung

| Kategorie | Technologieauswahl & Version | Ergänzende Hinweise |
|---|---|---|
| **Sprache & Standard/Laufzeit** | `<LANGUAGE_AND_VERSION>` | z. B.: C++20 / Python 3.11 / TypeScript 5.4 (Node 20) / Go 1.22 / Rust 1.78 |
| **Paketmanager / Build-Tool** | `<PACKAGE_MANAGER>` | z. B.: CMake+Ninja / Conan / Poetry / pnpm / Cargo / Go Modules |
| **Kernframeworks / Bibliotheken** | `<FRAMEWORK>` | z. B.: Qt 6 / Boost / FastAPI / Next.js / Gin / Tokio |
| **Persistenzschicht & Speicher** | `<DATABASE_AND_CACHE>` | z. B.: PostgreSQL 16 / SQLite 3 / Redis 7 |
| **CI/CD-Konfiguration** | `<CI_PATH>` | z. B.: `.github/workflows/ci.yml` / `.gitlab-ci.yml` |

## Architektonische Kern-Leitplanken

1. **Unidirektionale Schichtenabhängigkeit**: Höhere Schichten rufen tiefere Schichten auf; tiefere Schichten dürfen keinesfalls auf übergeordnete Geschäftslogik zugreifen. Zyklische Abhängigkeiten sind verboten.
2. **Einheitliche Ausnahmebehandlung**: Fachliche Fehler müssen standardisierte Business-Exceptions werfen; stillschweigendes Schlucken von Ausnahmen ist untersagt. Asynchrone Abläufe müssen Fehler abfangen.
3. **Konfigurationsisolation**: Sämtliche Konfigurationen müssen über zentrale Umgebungsvariablen oder Konfigurationsmodule eingelesen werden; kein Hardcoding im Code.
4. **Log-Anonymisierung**: Alle vertraulichen Werte in Konsolenausgaben oder Logs (PII, Tokens, Passwörter) müssen maskiert werden.
5. **Risikoklassifizierung**: Unterscheidung von Hinweisen, Benachrichtigungen und zwingenden Freigaben gemäß `.agents/rules/security-boundary.md`; Dateianzahl allein rechtfertigt kein Anhalten.
6. **Isolation geschützter Git-Branches**: Direkte Codeänderungen auf geschützten Branches (develop/master/main) sind verboten. Änderungen erfolgen auf temporären Branches.

## Matrix für Teilregeln und Engineering-Skills (Bedarfsgesteuerte Aktivierung)

Um Kontextaufblähung zu vermeiden, befinden sich spezifische Vorgaben in `.agents/rules/` und `.agents/skills/`. Skills mit externen CLI/MCP-Werkzeugen arbeiten nur bei vorliegender Installation:

| Szenario | Zugeordnete Regel / Skill | Auslösesyntax & Aktion | Erwartetes Standardverhalten |
|---|---|---|---|
| **Branching / Commits / Pushes** | `git-workflow.md` | Jede `git commit`- / `git push`- / Branch-Aktion | Commits nur auf Feature-Branches; `git add .` verboten; Freigabe für Remote-Aktionen erforderlich; kein Force-Push |
| **Hochrisiko-Aktionen / Strukturänderungen** | `security-boundary.md` | Erreichen des definierten Autorisierungsschwellenwerts | Auswirkungen risikogerecht erläutern; nur pausieren, wenn Autorisierung zwingend ist |
| **Komplexe Features / Architekturumbau** | `engineering-spec.md` + optional `comet` / `openspec` | Benutzerdefiniert oder im Projekt konfiguriert | Zustandsdateien des gewählten Tools beachten; bei Fehlen eigenständig nach Bedarf planen |
| **Code-Abhängigkeiten / Symbolsuche** | `token-discipline.md` + optional `codegraph` | Semantische Suche über CodeGraph MCP; sonst begrenztes `rg` | Keine Annahmen über MCP-Verfügbarkeit; Suchbereich strikt auf das Problem eingrenzen |
| **Implementierung / Coding-Phase** | `engineering-spec.md` + `ponytail` + `test-driven-development` | Skills nach Bedarf einsehen; Tests risikogerecht durchführen | Bestehenden Code verstehen, minimale valide Lösung wählen, nach Ponytail-Leiter prüfen |
| **Schwierige Bugs / Sporadische Fehler** | `engineering-spec.md` + `systematic-debugging` | Vollständigen Trace einfügen | Keine blinden Behelfslösungen; Nachweise sammeln, Hypothesen aufstellen, Ursache ermitteln |
| **Lange Ausgaben / Testläufe** | `token-discipline.md` + optional `rtk` | RTK-Hook schreibt Befehle um falls aktiv; sonst native prägnante CLI-Optionen | Keine automatische Umschreibung voraussetzen; lange Logs lokal speichern, nur Zusammenfassung liefern |
| **Token-Knappheit / Prägnante Ausgabe** | `Global AGENTS.md` + optional `caveman` | Aktivierung bei geladenem Skill | Prägnanter Ausdruck unter Wahrung von Sicherheitshinweisen und technischer Präzision |
| **Dokumentation / Architektursynchronisation** | `engineering-spec.md` + optional `living-documentation` | `/living-documentation` / Specs & Architektur-Sync | Vierstufige Dokumente nach L0/L1/L2 abgleichen; Frontmatter-Rückverfolgbarkeit pflegen |
| **Code-Review / Qualitäts-Gate vor Merge** | `open-code-review` + `requesting-code-review` | Nach Feature-Fertigstellung oder vor dem Merge | Regelbasiert, zeilenverankert; Tier A über `ocr` CLI falls vorhanden, sonst Tier B |

---

## Dynamisches Gedächtnis und Aufgabenverfolgung

- **Sitzungsstart**: Vorhandene `PROJECT_CONTEXT.md` und `SESSION_STATE.md` bei Aufgabenbezug prüfen; Einflussfaktoren auf die aktuelle Arbeit verifizieren.
- **Langfristiges Projektgedächtnis**: `PROJECT_CONTEXT.md` dokumentiert bewährte, übergreifende Architekturentscheidungen und Rahmenbedingungen. Es ersetzt keinen Quellcode; Pfade oder Nachweise verlinken.
- **Sitzungs-Haltepunkte**: `SESSION_STATE.md` an Meilensteinen mit erledigten Punkten, Nachweisen, nächsten Schritten und Risiken aktualisieren; Veraltetes bereinigen.
- **Änderungsumfang**: `PROJECT_CONTEXT.md` nur bei dauerhaften Faktenänderungen anpassen; für Zwischenstände nur `SESSION_STATE.md` fortschreiben.
- **Wiederverwendbare Erfahrungen**: In `tasks/lessons.md` nur Erkenntnisse aufnehmen, die noch nicht in Regeln übernommen wurden.
- **Quellen und Gültigkeit**: Annahmen kennzeichnen. Bei Widersprüchen zwischen Gedächtnis und reproduzierbaren Nachweisen im Code gelten stets die aktuellen Nachweise.
- **Datenschutz & Sicherheit**: Keine Zugangsdaten, Schlüssel oder ungefilterte Chat-Logs ablegen; keine privaten Benutzereinstellungen in geteilten Repositories speichern.
- **Optionales Langzeitgedächtnis**: Werkzeugübergreifendes Gedächtnis nutzt ausschließlich lokales ai-memory (keine Cloud-Pflicht, keine API-Keys). Bei Nichtverfügbarkeit niemals Aufgaben blockieren.
- **Geteilter Memory-Skill**: `.agents/skills/cross-tool-memory/SKILL.md` bei sitzungsübergreifenden Fortsetzungen oder Grundsatzentscheidungen nutzen.
- **Lebendige Dokumentation & Quellcode-Rückverfolgbarkeit**: Dokumentation wird unter `docs/` gepflegt. `modules` und `depends_on` im Frontmatter deklarieren. Siehe `.agents/skills/living-documentation/SKILL.md`.

## Verzeichnisbezogener Regelindex

In Monorepos oder Projekten mit stark isolierten Submodulen Verzeichnis-`AGENTS.md` nur dort anlegen, wo nötig:
- Eigene `AGENTS.md` nur in Modulen mit klaren Grenzen erstellen, um In/Out Scope und Schnellprüfungen zu definieren; Standardverzeichnisse erben direkt diese Stammdatei.
