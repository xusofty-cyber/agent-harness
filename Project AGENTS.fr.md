# Project AGENTS.md

## Héritage et positionnement

- Ce document constitue le fichier d'instructions racine du projet actuel, complétant les règles générales de [Global AGENTS.md] par le contexte d'ingénierie propre à ce projet.
- Adoptant une architecture de **divulgation progressive (Progressive Disclosure)**, les garde-fous essentiels et les commandes fréquentes du projet sont maintenus ici ; les règles granulaires résident dans `.agents/rules/`, consultées à la demande par l'Agent.

## Vue d'ensemble du projet

- **Nom du projet** : `<PROJECT_NAME>`
- **Mission métier** : `<PROJECT_PURPOSE>` (une phrase définissant le scénario opérationnel cible et les utilisateurs)
- **Mainteneurs principaux** : `<OWNERS>`
- **Dépôt de code et branche par défaut** : `<REPOSITORY_URL>` ; branche par défaut `<DEFAULT_BRANCH>` (alignée sur `origin/HEAD`)

## Commandes de développement courantes (Contexte CLI)

> Vérifier le répertoire de travail avant toute exécution. Utiliser systématiquement des filtres pour éviter la saturation des logs ; ne jamais déverser de logs bruts intégraux dans le contexte.

```bash
# 1. Gestion des dépendances / configuration de build
<INSTALL_COMMAND>                  # ex. : npm ci / poetry install / cmake -B build / go mod download / cargo check

# 2. Développement local et compilation
<DEV_COMMAND>                      # ex. : npm run dev / python main.py / cargo run
<BUILD_COMMAND>                    # ex. : npm run build / cmake --build build / go build ./... / cargo build --release

# 3. Tests unitaires ciblés et vérifications (obligatoire après modifications ; sortie concise requise)
<UNIT_TEST_COMMAND>                # ex. : npm test -- --reporter=dot / pytest -q / ctest --output-on-failure
<TARGETED_TEST_COMMAND>            # Test de fichier unique : npm test -- <path> / pytest <path> -q / ctest -R <test_name>
<INTEGRATION_TEST_COMMAND>         # Tests d'intégration : npm run test:e2e

# 4. Qualité du code, Linting et analyse statique
<LINT_COMMAND>                     # ex. : npm run lint / ruff check . / clang-tidy / golangci-lint run / cargo clippy
<FORMAT_COMMAND>                   # ex. : npm run format / black . / clang-format -i / gofmt -w . / cargo fmt
<TYPE_CHECK_COMMAND>               # ex. : npm run typecheck / mypy .

# 5. Migrations de données et publication (opérations critiques soumises à confirmation)
<MIGRATION_COMMAND>                # ex. : npm run db:migrate / alembic upgrade head
```

## Stack technique et environnement d'exécution

| Catégorie | Choix technique & Version | Remarques complémentaires |
|---|---|---|
| **Langage & Standard/Runtime** | `<LANGUAGE_AND_VERSION>` | ex. : C++20 / Python 3.11 / TypeScript 5.4 (Node 20) / Go 1.22 / Rust 1.78 |
| **Gestionnaire de paquets / Outil de build** | `<PACKAGE_MANAGER>` | ex. : CMake+Ninja / Conan / Poetry / pnpm / Cargo / Go Modules |
| **Frameworks majeurs / Bibliothèques** | `<FRAMEWORK>` | ex. : Qt 6 / Boost / FastAPI / Next.js / Gin / Tokio |
| **Couche de persistance & Stockage** | `<DATABASE_AND_CACHE>` | ex. : PostgreSQL 16 / SQLite 3 / Redis 7 |
| **Configuration CI/CD** | `<CI_PATH>` | ex. : `.github/workflows/ci.yml` / `.gitlab-ci.yml` |

## Garde-fous architecturaux stricts

1. **Dépendances en couches unidirectionnelles** : Les couches supérieures appellent les couches inférieures ; interdiction formelle pour les couches basses de référencer la logique métier des couches hautes. Aucune dépendance cyclique entre modules.
2. **Gestion unifiée des exceptions** : Les erreurs métier doivent lever des exceptions métier standardisées ; interdiction de masquer silencieusement les exceptions. Tout traitement asynchrone doit capturer les erreurs.
3. **Isolation de la configuration** : Toute configuration doit être lue via des variables d'environnement ou un module centralisé ; interdiction formelle de coder en dur des valeurs dans le code.
4. **Anonymisation des logs** : Tout champ sensible envoyé à la console ou consigné dans les logs (PII, tokens, mots de passe) doit être masqué.
5. **Classification des risques** : Différencier rappels, notifications simples et autorisations obligatoires selon `.agents/rules/security-boundary.md` ; le nombre de fichiers modifiés ne constitue pas en soi un motif de blocage.
6. **Isolation des branches Git protégées** : Interdiction absolue de modifier le code directement sur les branches protégées (develop/master/main). Toute modification s'opère sur une branche temporaire.

## Matrice de routage des règles secondaires et compétences (Activation à la demande)

Afin d'éviter la saturation du contexte, les spécifications fines et compétences résident dans `.agents/rules/` et `.agents/skills/`. Les compétences nécessitant des CLI/MCP externes ne fonctionnent que si elles sont installées et configurées :

| Scénario de dev | Règle / Compétence associée | Syntaxe de déclenchement & Action | Standard comportemental attendu |
|---|---|---|---|
| **Cycle de branches / Commits / Push** | `git-workflow.md` | Toute opération `git commit` / `git push` / changement de branche | Commits sur branche temporaire ; `git add .` interdit ; autorisation formelle pour les opérations distantes ; force push interdit |
| **Opérations à haut risque / Changements structurels** | `security-boundary.md` | Atteinte du seuil d'autorisation défini | Expliquer les impacts selon le niveau de risque ; ne marquer de pause que si l'autorisation est obligatoire |
| **Fonctionnalités complexes / Évolution d'architecture** | `engineering-spec.md` + option `comet` / `openspec` | Flux demandé par l'utilisateur ou configuré sur le projet | Respecter les fichiers d'état de l'outil choisi ; planifier selon les besoins en l'absence de configuration |
| **Dépendances de code / Recherche de symboles** | `token-discipline.md` + option `codegraph` | Exploration sémantique si le MCP CodeGraph est disponible ; sinon `rg` délimité | Ne pas présumer de la disponibilité du MCP ; restreindre la portée de recherche au problème posé |
| **Implémentation / Phase de codage** | `engineering-spec.md` + `ponytail` + `test-driven-development` | Consulter les compétences à la demande ; tests selon les risques et standards | Comprendre l'existant avant de choisir la solution minimale valide ; vérifier selon l'échelle Ponytail |
| **Bugs complexes / Pannes intermittentes** | `engineering-spec.md` + `systematic-debugging` | Coller la trace d'erreur complète | Zéro bricolage aveugle ; recueillir les preuves, poser des hypothèses et trouver la cause racine avant d'écrire le correctif |
| **Sorties volumineuses / Séries de tests** | `token-discipline.md` + option `rtk` | Hook RTK réécrit les commandes si configuré ; sinon flags concis natifs du CLI | Ne pas présumer de réécriture automatique ; enregistrer les longs logs localement et ne restituer que les synthèses |
| **Saturation de tokens / Sortie concise** | `Global AGENTS.md` + option `caveman` | Activer à la demande si l'hôte charge la compétence | Expression concise tout en préservant les avertissements de sécurité et l'exactitude technique |
| **Documentation / Synchronisation d'architecture** | `engineering-spec.md` + option `living-documentation` | `/living-documentation` / Archivage specs et architecture | Synchroniser les documents selon les seuils L0/L1/L2 ; maintenir la traçabilité bidirectionnelle Frontmatter |
| **Docs R&D formels / Modèles** | `engineering-docs` | Lors de la rédaction de PRD/SRS/HLD/LLD/plans de test | Choisir le modèle via l'arbre 31→15 ; suivre rendering-spec.md |
| **Revue de code / Porte de validation avant merge** | `open-code-review` + `requesting-code-review` | Fin de développement ou avant fusion | Revue guidée par les règles, ancrée aux lignes de code ; Tier A via CLI `ocr` si présent, sinon Tier B |

---

## Mémoire dynamique et suivi des tâches

- **Démarrage de session** : Consulter `PROJECT_CONTEXT.md` et `SESSION_STATE.md` s'ils existent et sont pertinents pour la tâche ; vérifier les faits impactant le travail en cours.
- **Mémoire durable du projet** : `PROJECT_CONTEXT.md` consigne les choix d'architecture, contraintes fermes et décisions techniques validés et utiles entre plusieurs tâches. Il sert d'index et de boussole sans se substituer au code ; inclure les chemins sources.
- **Points d'arrêt de session** : Mettre à jour `SESSION_STATE.md` aux jalons significatifs en enregistrant le travail accompli, les preuves de validation, les étapes restantes et les risques d'environnement ; nettoyer les états périmés.
- **Périmètre des mises à jour** : Ne modifier `PROJECT_CONTEXT.md` que si les faits durables évoluent ; ne mettre à jour que `SESSION_STATE.md` pour les points d'étape courants.
- **Capitalisation d'expérience** : Utiliser `tasks/lessons.md` pour consigner les enseignements réutilisables non encore formalisés dans les règles.
- **Preuves et exactitude** : Distinguer déductions et faits avérés. En cas de contradiction avec le code actif ou des preuves reproductibles, ces dernières prévalent.
- **Confidentialité et sécurité** : Ne jamais stocker de mots de passe, clés privées, données personnelles brutes ou historiques d'échange superflus ; les dépôts partagés ne conservent aucune préférence individuelle privée.
- **Mémoire inter-outils optionnelle** : La mémoire partagée s'appuie uniquement sur la solution locale ai-memory ; ni déployée ni démarrée par défaut, zéro clé API requise. Ne jamais bloquer les tâches si elle est indisponible.
- **Compétence de mémoire partagée** : Utiliser `.agents/skills/cross-tool-memory/SKILL.md` pour poursuivre un travail d'une session à l'autre ou valider des décisions durables.
- **Documentation vivante & Traçabilité du code** : La documentation long terme réside sous `docs/` (`docs/specs/`, `docs/architecture/`, `docs/reference/`, `docs/guides/`). Déclarer `modules` et `depends_on` dans le Frontmatter. Voir `.agents/skills/living-documentation/SKILL.md`.

## Index des règles au niveau répertoire

Dans les monorépôts ou les projets comportant des sous-modules hautement isolés, créer des fichiers `AGENTS.md` de répertoire uniquement lorsque nécessaire :
- Ajouter un fichier `AGENTS.md` dédié dans les sous-modules aux frontières nettes afin de définir leur périmètre spécifique et leurs commandes de vérification rapide ; les répertoires standards héritent directement du présent fichier.
