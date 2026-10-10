# Projektkontext & dauerhafte Fakten (PROJECT_CONTEXT.md)

> **Rolle & Zweck**: Dieses Dokument erfasst die Kernarchitekturfakten und dauerhaften technischen Vorgaben für `<PROJECT_NAME>` als einzige verlässliche Quelle (Single Source of Truth) beim Start von KI-Agentensitzungen und bei technischen Entscheidungen. Nur bei wesentlichen Änderungen an Architektur, Stack, Persistenz oder globalen Leitplanken aktualisieren. Sitzungsspezifische Übergangszustände und Haltepunkte gehören in `SESSION_STATE.md`.

---

## 1. Projektübersicht & Fachdomäne

- **Systemname**: `<PROJECT_NAME>`
- **Fachdomäne**: <Kurzbeschreibung der Domäne und der gelösten Kernprobleme>
- **Kernfunktionsmatrix**:
  1. **<Kernmodul/Funktion 1>**: <Beschreibung von Verantwortlichkeiten und Abläufen>
  2. **<Kernmodul/Funktion 2>**: <Beschreibung von Verantwortlichkeiten und Abläufen>

---

## 2. Code-Repository & Technologie-Stack

### 1. Umgebung & Branches
- **Repository**: `<GIT_REPO_URL>`
- **Haupt-/Entwicklungs-Branch**: `main` / `develop`
- **Laufzeit- und Bereitstellungsumgebung**: <Lokale Entwicklung / Docker / Kubernetes / Cloud-Produktion>

### 2. Technologieauswahl

| Schicht / Bereich | Technologie & Version | Hinweise & Kernbibliotheken |
|---|---|---|
| **Kernsprache / Laufzeit** | <z. B. TypeScript 5.x / Python 3.11 / Go 1.22> | <Hauptprogrammiersprache und Laufzeitumgebung> |
| **Frameworks & Build** | <z. B. Next.js / FastAPI / Spring Boot / Vite> | <Anwendungs-Framework & Build-Tools> |
| **Persistenz & Cache** | <z. B. PostgreSQL 16 / Redis 7 / SQLite> | <Datenbanken und Caching-Schichten> |
| **API & Messaging** | <z. B. gRPC / RESTful / Kafka / RabbitMQ> | <Kommunikationsprotokolle und Event-Busse> |

---

## 3. Architektur & strukturelles Design

- **Architekturmuster**: <z. B. Schichten-Monolith / Domain-Driven Microservices / Modulare Architektur>
- **Verzeichnis- und Modulzuständigkeiten**:
  - `src/`: <Kernquellcode der Geschäftslogik>
  - `tests/`: <Unit- und Integrationstests>
  - `docs/`: <Architekturentscheidungen und technische Spezifikationen>

---

## 4. Wichtige Vorgaben & globale rote Linien

1. **Minimale Implementierung & kein Bloat (Ponytail-Entscheidungsleiter)**:
   - Der Entscheidungsleiter folgen: Vor neuen Abstraktionen oder Abhängigkeiten stets vorhandenen Code und die Standardbibliothek bevorzugen.
2. **Einheitliche Fehlerbehandlung & Log-Bereinigung**:
   - Standardisierte Fehlerstrukturen nutzen; Fehler niemals stillschweigend unterdrücken.
   - API-Keys, Tokens, Passwörter, private Schlüssel oder interne Verbindungszeichenfolgen dürfen niemals im Klartext geloggt oder committet werden.
3. **Git-Isolation & Branch-Schutz**:
   - Niemals direkt auf geschützte Branches (`main`, `develop`, `master`) committen; temporäre Feature-Branches nutzen.
   - `git add .` und `git add -A` sind untersagt; nur explizite Dateipfade stagen. Force-Push (`git push --force`) ist dauerhaft verboten.

---

## 5. Architektonische & technische Entscheidungsaufzeichnungen (ADR / Decision Log)

- **<JJJJ-MM-TT>**: [Initialisierung des Projektgedächtnisses]
  - **Kontext**: Etablierung eines sitzungs- und werkzeugübergreifenden Standards für Projektgedächtnis.
  - **Entscheidung**: Einführung von `PROJECT_CONTEXT.md` für dauerhafte Fakten und `SESSION_STATE.md` für temporäre Haltepunkte.
  - **Auswirkung**: Alle Agenten laden diesen Kontext zu Beginn der Sitzung, um technische Konsistenz zu gewährleisten.
