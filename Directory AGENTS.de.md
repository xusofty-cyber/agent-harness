# Directory AGENTS.md

> **Nutzungshinweis**: Diese Datei ist ein bedarfsgesteuerter Mikromodul-Patch, der **ausschließlich** in Monorepo-Unterpaketen (`packages/*`), getrennten Frontend-/Backend-Verzeichnissen oder Submodulen mit strikten Isolationsgrenzen verwendet wird. Standard-Unterverzeichnisse erben stets die Regeln der Projektwurzel; Datei niemals wahllos erstellen.

## Modulzweck

- **Modulname**: `<MODULE_NAME>`
- **Verzeichnispfad**: `<DIRECTORY_PATH>`
- **Kernverantwortung**: `<RESPONSIBILITY>` (ein prägnanter Satz zur Hauptaufgabe dieses Verzeichnisses)

## Grenzendefinition (In / Out Scope)

- **Zuständig (In-Scope)**:
  - `<IN_SCOPE_ITEM_1>`
  - `<IN_SCOPE_ITEM_2>`
- **Nicht zuständig (Out-of-Scope)**:
  - `<OUT_OF_SCOPE_ITEM_1>` (falls Anforderungen dies betreffen, an das zuständige Modul oder die Projektwurzel übergeben)
  - `<OUT_OF_SCOPE_ITEM_2>`

## Abhängigkeiten und Isolationsregeln

- **Erlaubte Abhängigkeiten**: Nur `<ALLOWED_DEPENDENCIES>` (Basispakete oder öffentliche Verträge).
- **Verbotene Abhängigkeiten**: Direkte Bezüge auf `<FORBIDDEN_DEPENDENCIES>` sind streng verboten (verhindert Schichtdurchbrüche oder zyklische Abhängigkeiten).
- **Öffentliche Schnittstellen**: Alle exportierten Methoden und Typen müssen über einen einheitlichen Einstiegspunkt exponiert werden (z. B. `index.ts` / `__init__.py` / `mod.rs` / `include/`); direkte Tiefenimporte interner privater Implementierungen sind verboten.

## Schnelle lokale Verifikationsbefehle (Vermeidet Token-Aufblähung durch Gesamttests)

> Nach Moduländerungen vorrangig leichtgewichtige Modulprüfungen durchführen; Prüfumfang erst ausweiten, wenn modulübergreifendes Verhalten betroffen ist.

```bash
# Modulbezogene Unit-Tests und Schnellprüfungen (mit Flags für prägnante Ausgaben)
<LOCAL_TEST_COMMAND>           # z. B.: npm test -- packages/core --reporter=dot / pytest tests/core -q

# Modul-Linting
<LOCAL_LINT_COMMAND>           # z. B.: npm run lint --filter core
```

## Lokale Gedächtnisgrenzen

- Nur aktive Grenzen, Abhängigkeiten, Befehle und Wartungsregeln festhalten, die für dieses Verzeichnis spezifisch sind; Redundanzen erben die Wurzelregeln.
- Kein verzeichnisbezogenes `MEMORY.md` standardmäßig anlegen oder Projekthistorien kopieren. Dauerhafte Fakten gehören in `PROJECT_CONTEXT.md`, aktive Haltepunkte in `SESSION_STATE.md`.
- Bei Regeländerungen sicherstellen, dass sie dem aktiven Code entsprechen; veraltete Vorgaben löschen oder korrigieren.
- Niemals Zugangsdaten, Schlüssel oder ungefilterte Chat-Logs in lokalen Modulregeln speichern.
- Werkzeugübergreifende Speicherdienste verbleiben im Projekt-Namespace; normative Vorgaben dieses Moduls existieren nur hier.

## Sicherheitsleitfaden für sehr große / historische Dateien (> 100 KB)

- **Präzise Lokalisierung**: Bei übergroßen Dateien stets exakte Funktionen und Zeilenbereiche bestimmen; vollständiges Umschreiben oder globales Neuformatieren ist verboten;
- **Stilkonsistenz hat Vorrang**: Neuer Code muss sich strikt an den bestehenden Stil der Datei anpassen (Benennung, Einrückung, Fehlerbehandlung);
- **Keine ungewollte Offenlegung**: Private Hilfsfunktionen und interne Strukturen dürfen niemals direkt in öffentlichen Headern platziert werden.

## Änderungs-Checkliste

- [ ] Änderungen liegen strikt im Zuständigkeitsbereich (In-Scope) und führen keine verbotenen Abhängigkeiten ein.
- [ ] Gezielte punktuelle Änderungen bei großen Dateien unter Beibehaltung des bisherigen Stils.
- [ ] Neue Fähigkeiten nur über den öffentlichen Modul-Einstiegspunkt exponiert, Kapselung gewahrt.
- [ ] Angemessene Verifikation proportional zum Fehlerrisiko ausgeführt; Auslassungsgründe dokumentiert.
