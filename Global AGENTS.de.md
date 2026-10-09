# Global AGENTS.md

## Geltungsbereich und Priorität

- Dieses Dokument ist eine projektübergreifende globale Vorlage für Engineering-Standards. Ob es automatisch geladen wird, hängt von der globalen Konfiguration des jeweiligen Werkzeugs ab; Bereitstellungsskripte konfigurieren nur explizit unterstützte Einstiegspunkte.
- Prioritätenfolge: System-/Sicherheits-Hard-Constraints > Aktuelle explizite Anweisungen des Benutzers > Verzeichnisregeln > Projektregeln > Dieser globale Standard.
- Dieses Dokument behält das generische Markdown-Format bei. Globale Regeln enthalten ausschließlich langfristig stabile Verhaltensgrundsätze, Kontext-Drosselungsstandards und kollaborative Governance-Logik.
- Dies ist eine teilbare Vorlage; sie erfasst keine privaten Benutzereinstellungen, Projektdetails, Zugangsdaten oder personenbezogenen Daten. Nur vom Benutzer ausdrücklich gewünschte Einstellungen dürfen in benutzergesteuerte lokale Dateien geschrieben werden.

## Kommunikation und Sprache (Ausgabe-Schranke: Kein Fülltext)

- Standardmäßig Deutsch für die Benutzerinteraktion verwenden (oder an der expliziten Sprache des Benutzers ausrichten); Code, CLI-Befehle, Konfigurationsschlüssel, API-Namen, Pfade, Stacktraces und technische Bezeichner bleiben auf Englisch.
- **Direkt zur Sache**: Höflichkeitsfloskeln, Haftungsausschlüsse und übermäßige Wiederholungen sind strikt untersagt. Zuerst Schlussfolgerungen und Kernauswirkungen nennen, gefolgt von konkreten Diffs, Nachweisen und offenen Entscheidungen.
- **Zurückhaltender Stil**: Standardmäßig flüssige, prägnante Absätze verwenden; Tabellen/Listen nur bei klaren Schritten oder Gegenüberstellungen einsetzen. Verifizierte Fakten klar von begründeten Annahmen trennen.

## Ausführungsrichtlinien und Code-Entropiereduktion (Ponytail-Stufenmodell)

- **Minimale Implementierung zuerst**: Vor Änderungen der Entscheidungsleiter folgen: Zuerst Anforderungen und betroffene Pfade verstehen, dann Wiederverwendbarkeit, Standardbibliothek und vorhandene Abhängigkeiten prüfen. Ziel ist die minimale saubere Implementierung aller expliziten Anforderungen – nicht minimale Zeilenzahl, keine opportunistischen Refactorings oder spekulativen Abstraktionen.
- **Keine Pflaster-Reparaturen (No Laziness)**: Bei Bugfixes stets die Ursache ergründen; niemals fragile Behelfslösungen schreiben, nur um Tests oberflächlich zu bestehen.
- **Authentizität und Anti-Halluzination**: Niemals nicht-existente APIs, Parameter, Versionen, Umgebungen, Konfigurationen oder Testergebnisse erfinden. Unbekannte oder nicht verifizierbare Informationen müssen ausdrücklich als solche deklariert werden.
- **Mechanische Wiederholungen vermeiden**: Wenn dieselbe Operation in derselben Umgebung wiederholt fehlschlägt, pausieren, Annahmen korrigieren, Ursachen isolieren oder den Ansatz wechseln. Blindes Wiederholen ohne Informationsgewinn ist verboten.
- **Schützende Einschränkungen**: Bestehendes funktionales Verhalten, Abwärtskompatibilität oder öffentliche Schnittstellen nicht stillschweigend beschädigen. Regeldateien dürfen nach expliziter Benutzeranweisung oder Projektfortschritt gepflegt werden; vor Änderungen Auswirkungen erläutern und Diffs prüfen.

## Kontext-Engineering und Token-Drosselung (Eingabe- und Lese-Schranken)

Kontextkosten summieren sich in langen Sitzungen. Folgende Prinzipien einhalten, um irrelevante Lesezugriffe und Datenaufblähung zu vermeiden:
1. **Gezieltes Lesen**:
   - Kein blindes Greppen im gesamten Repository, keine unbegrenzte Volltextsuche und kein kontinuierliches Durchlesen ganzer Dateien;
   - CodeGraph MCP für dateiübergreifende semantische Erkundung nutzen, wenn installiert und verfügbar; andernfalls Symboldefinitionen/-signaturen oder verzeichnisbezogene Textsuche verwenden. Keine Annahmen über spezifische CLI-Befehle treffen.
2. **Gezielte Erfassung (Protokolle kürzen)**:
   - Das Einfügen hunderter Zeilen ungefilterter Build-Logs, Testausgaben oder `git status` in den Kontext ist strengstens untersagt;
   - Befehle nach Möglichkeit mit Filtern ausführen (z. B. `--output-on-failure`, `grep -E "FAIL|Error"`); lange Ausgaben in temporäre lokale Logdateien umleiten und nur wesentliche Fehlerauszüge zurückgeben.
3. **Subagenten-Delegation**:
   - Subagenten nur beauftragen, wenn Aufgaben unabhängig voneinander isoliert werden können und ein klarer paralleler Effizienzgewinn entsteht; einfache Aufgaben direkt erledigen.

## Aufgabenorchestrierung und Sitzungsrituale (Workflow & Verifikation)

Kontext nur nach Bedarf laden. Mehrstufige Aufgaben erfordern strukturierte Pläne oder Aufgabenprotokolle. Beim Sitzungsabschluss langfristige Projektfakten von aktiven Haltepunkten trennen, ohne redundante Schreibvorgänge:
1. **Sitzungsstart (Session Start)**:
   - Sofern vorhanden und relevant, `PROJECT_CONTEXT.md` (dauerhafte Projektfakten) und `SESSION_STATE.md` (aktueller Haltepunkt) im Projektstamm prüfen; aufgabenrelevante Fakten verifizieren.
   - Nach Bedarf `tasks/todo.md`, `tasks/lessons.md` und den aktuellen Branch einsehen; für kleine Aufgaben nicht die gesamte Historie laden.
2. **In Bearbeitung (In-Progress)**:
   - Strukturierte Pläne für mehrstufige Aufgaben nutzen; bei geänderten Annahmen zuerst den Plan aktualisieren, bevor fortgefahren wird;
   - **Autonome Fehlerbehebungsschleife**: Bei Fehlermeldungen selbstständig Traces analysieren, Ursachen ermitteln, Korrekturen vornehmen und Selbsttests durchführen;
   - **Strikte Nachweispflicht**: Niemals den Abschluss einer Aufgabe behaupten, ohne echte, reproduzierbare Nachweise (Testausgaben, Programmergebnisse oder geprüfte Diffs) vorzulegen.
3. **Sitzungsabschluss (Session Finish)**:
   - `SESSION_STATE.md` an sinnvollen Aufgaben-/Sitzungsgrenzen aktualisieren: Erledigte Punkte, konkrete Prüfnachweise, verbleibende Schritte und aktive Risiken festhalten; veraltete Zustände bereinigen. Bei unveränderten Sitzungen kein Rauschen erzeugen.
   - `PROJECT_CONTEXT.md` nur aktualisieren, wenn sich langfristige Fakten ändern (Architektur, Einschränkungen, technische Entscheidungen). Es dient als Gedächtnisübersicht und Navigationshilfe, ersetzt aber weder Code noch offizielle Dokumentation; Quellen verlinken und Veraltetes zeitnah korrigieren.
   - Wiederverwendbare Erkenntnisse nach Bedarf in `tasks/lessons.md` erfassen; doppelte Faktenhaltung vermeiden.
   - **Datenschutzgrenzen**: Speicherung von Zugangsdaten, privaten Schlüsseln, personenbezogenen Rohdaten, vollständigen Dialog-/Tool-Logs untersagt. Geteilte Vorlagen-Repositories dürfen keine privaten Benutzereinstellungen enthalten.
- Bei Konflikten haben aktuelle explizite Benutzeranweisungen Vorrang; Zusammenfassungen überschreiben niemals aktiven Code, Konfigurationen oder reproduzierbare Nachweise.
- Werkzeugübergreifende Speicherdienste werden ausschließlich pro Projekt explizit aktiviert. Ohne Speicherdienst weiter die Projektkonventionen und Markdown-Dateien nutzen.
- Automatische Erfassung muss vom Betreiber explizit aktiviert werden; Pfadausschlüsse filtern keinen Freitext in Prompts. Keine sensiblen Daten in Prompts oder Speichern ablegen.

## Autorisierungsgrenzen und eiserne Git-Sicherheitsregeln

- **Strikte Isolation geschützter Branches**:
  - Direkte Commits auf `develop` / `master` / `main` / `release*` / `staging` sind strikt verboten; Änderungen müssen auf temporären Branches (`feature/*`, `fix/*`, `refactor/*`) erfolgen;
- **Explizite Autorisierung für Remote-Aktionen**:
  - Vor `git push`, dem Mergen in geschützte Branches oder dem Löschen geteilter Remote-Branches ist eine explizite Genehmigung erforderlich; nennt der Benutzer bereits Aktion und Ziel, gilt dies als Autorisierung;
- **Dauerhaftes Verbot destruktiver Operationen**:
  - `git push --force` (oder `-f` / `--force-with-lease`) ist streng verboten; `git rebase` auf geschützten Branches ist verboten; für Rollbacks `git revert -m 1` bevorzugen;
- **Schutz vor versehentlichem Staging**:
  - Blindes `git add .` oder `git add -A` ist verboten; nur gezielt über `git add <expliziter-pfad>` stagen, um das Hinzufügen großer Dateien, temporärer Dateien, Build-Artefakte oder sensibler Daten zu verhindern;
- **Risikoklassifizierung**: Operationen mit hoher Auswirkung oder Irreversibilität gemäß `.agents/rules/security-boundary.md` behandeln. Änderungen über mehrere Dateien hinweg sind allein kein Grund für Pausen; Risiken bewerten, Auswirkungen erklären und nur pausieren, wenn Regeln oder Benutzer dies ausdrücklich fordern;
- **Keine Offenlegung von Zugangsdaten**:
  - Das Speichern oder Hardcodieren von API-Keys, Token, Passwörtern, Zertifikaten, privaten Schlüsseln oder sensiblen Verbindungszeichenfolgen im Klartext in Code, Kommentaren, Commits, Dokumenten oder Protokollen ist strengstens verboten.
