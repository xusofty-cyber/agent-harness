# Guide pratique de l'outillage IA et panorama des compétences (Claude Code / Codex / Antigravity IDE / Zed IDE)

> **Language / Langue**: [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [简体中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | [繁體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh-tw.md) | **Français** | [Deutsch](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.de.md)

Ce guide fournit un manuel complet pour l'ingénierie logicielle et la documentation technique avec des agents IA : **quelles compétences et quels outils du Harness installer, l'économie sous-jacente des tokens, la configuration et le câblage des outils, quand et comment invoquer les commandes slash principales (p. ex. `/comet`, `/plan`, `/opsx`, `codegraph`), et un parcours pratique complet de bout en bout.**

---

## Table des matières

1. [Architecture centrale et matrice des outils (qui gère quoi)](#1-architecture-centrale-et-matrice-des-outils-qui-gère-quoi)
2. [Inventaire des compétences et outils de l'écosystème](#2-inventaire-des-compétences-et-outils-de-lécosystème)
   - 2.1 40 compétences natives intégrées par catégorie
   - 2.2 Verrouillage de version, mises à jour en ligne et synchronisation des compétences (`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`)
   - 2.3 Outils CLI optionnels du Harness
   - 2.4 Économie des tokens des compétences (pourquoi plus de 40 compétences n'explosent PAS le contexte)
   - 2.5 Matrice de dispatching des compétences d'ingénierie et des règles
3. [Plongée dans les outils centraux du Harness et les commandes slash](#3-plongée-dans-les-outils-centraux-du-harness-et-les-commandes-slash)
   - 3.1 Comet : point d'entrée du flux versionné
   - 3.2 OpenSpec : développement piloté par les spécifications (`/opsx:propose`, `/opsx:apply`, etc.)
   - 3.3 Superpowers : TDD, débogage systématique et porte de vérification
   - 3.4 CodeGraph : intégration optionnelle du graphe de code MCP
   - 3.5 Ponytail : échelle d'implémentation minimale (porte de génération)
   - 3.6 Caveman : sortie ultra-compressée (porte de communication)
   - 3.7 RTK : troncature de sortie et blindage des journaux (porte d'exécution)
   - 3.8 Modèle d'autorisation Git et flux des branches protégées
   - 3.9 Cérémonie de session en 3 étapes et boucle de mémoire dynamique
   - 3.10 Matrice de protection des 8 opérations à haut risque
4. [Commandes natives spécifiques aux plateformes et bonnes pratiques](#4-commandes-natives-spécifiques-aux-plateformes-et-bonnes-pratiques)
   - 4.1 Google Antigravity IDE
   - 4.2 Claude Code et crochets PreToolUse
   - 4.3 OpenAI Codex / GitHub Copilot
   - 4.4 Zed IDE
5. [Parcours pratique de bout en bout (développement réel d'une fonctionnalité)](#5-parcours-pratique-de-bout-en-bout-développement-réel-dune-fonctionnalité)
6. [Contrôles de santé quotidiens et dépannage](#6-contrôles-de-santé-quotidiens-et-dépannage)

---

## 1. Architecture centrale et matrice des outils (qui gère quoi)

Sans frontières physiques, le développement assisté par IA dérive fréquemment, sur-conçoit ou casse la compatibilité descendante. Notre architecture Harness impose cinq portes consécutives :

```text
       [ Demande de l'utilisateur ]
              │
       ┌──────▼─────────────────────────────────────────────────┐
       │ 1. Porte processus et état : Comet (/comet) + OpenSpec SDD │
       └──────┬─────────────────────────────────────────────────┘
              │ Portée verrouillée ; début de l'exploration et de la découverte
       ┌──────▼─────────────────────────────────────────────────┐
       │ 2. Récupération sémantique optionnelle : CodeGraph MCP, si configuré │
       └──────┬─────────────────────────────────────────────────┘
              │ Dépendances de symboles claires ; conception et code
       ┌──────▼─────────────────────────────────────────────────┐
       │ 3. Porte du code : Superpowers (TDD rouge-vert) + Ponytail   │
       └──────┬─────────────────────────────────────────────────┘
              │ Exécuter les tests et les commandes de build
       ┌──────▼─────────────────────────────────────────────────┐
       │ 4. Filtrage de commandes optionnel : CLI RTK + crochet d'agent          │
       └──────┬─────────────────────────────────────────────────┘
              │ Livrer et committer
       ┌──────▼─────────────────────────────────────────────────┐
       │ 5. Communication et Git : directives Caveman (si chargées) + Git  │
       └────────────────────────────────────────────────────────┘
```

### Matrice des responsabilités

| Composant | Responsabilité centrale | Point de douleur résolu | Interface |
|---|---|---|---|
| **Comet** | Flux versionnés natifs/classiques | Flux de tâches reprenables et vérifiables | Suivez la version installée et `.comet/config.yaml` |
| **OpenSpec** | Développement piloté par les spécifications (SDD) | Amnésie des exigences, changements delta non suivis | `/opsx:propose`, docs vivantes `docs/openspec/` |
| **Superpowers** | TDD et porte de preuves de vérification | Achèvement de tâche halluciné, preuve physique manquante | Test rouge $\rightarrow$ test vert $\rightarrow$ rapport de vérification |
| **CodeGraph** | Intégration optionnelle de recherche sémantique de code | Nécessite le CLI, le câblage MCP de l'agent et un index de projet | Interrogez via les outils MCP CodeGraph configurés |
| **Ponytail** | Compétence de directives d'implémentation minimale | Dépendances et abstractions inutiles | Directives uniquement lorsque l'hôte charge la compétence |
| **Caveman** | Compétence de directives de communication concise | Réponses trop longues | Directives de style au chargement ; préserver la clarté et les détails de sécurité |
| **RTK** | CLI optionnel Rust Token Killer | Sortie terminal verbeuse | Nécessite l'installation du CLI et un crochet d'agent pris en charge |
| **Git Auth** | Directives de branche protégée plus vérifications limitées du crochet client | Prévention des opérations accidentelles sur branches partagées | Règles, crochet client Claude Code et protection de branche côté serveur |

### Portée des règles et de la mémoire par outil de programmation

| Outil/surface | Point d'entrée d'instructions | Portée de la mémoire |
|---|---|---|
| App desktop Codex | `AGENTS.md` de projet ; ai-memory peut utiliser l'intégration Codex locale lorsque l'application installée expose les MCP/crochets configurés | Vérifiez la version exacte du desktop ; la mémoire de conversation web ChatGPT est distincte |
| Codex CLI | Répertoire Codex et fichiers `AGENTS.md` de la racine du dépôt jusqu'au répertoire courant ; l'installateur amont ai-memory prend en charge MCP/crochets | Les fichiers de contexte/point de contrôle du projet restent gérés par le dépôt |
| Claude Code | `CLAUDE.md` utilisateur/projet/répertoire ou `AGENTS.md` pris en charge | La mémoire Auto optionnelle est machine-locale et spécifique à Claude ; `/memory` ouvre ses contrôles |
| Antigravity CLI | `AGENTS.md` global, workspace et répertoire / `.agents/rules/*.md` ; l'amont ai-memory prend en charge MCP/crochets | Exécutez la configuration dans le même environnement que le CLI |
| Antigravity IDE | Règles/compétences Markdown de projet plus un serveur MCP ai-memory configuré manuellement | MCP fournit des outils explicites de récupération/écriture ; aucune capture automatique du cycle de vie n'est revendiquée |

Les scripts de déploiement écrivent des chemins ; vérifiez la documentation actuelle de chaque hôte et le contexte chargé avant de supposer qu'un fichier a été consommé.

---
## 2. Inventaire des compétences et outils de l'écosystème

### 2.1 40 compétences natives intégrées par catégorie

L'installateur copie les répertoires de compétences du dépôt dans `.agents/skills/` ; la découverte réelle dépend de l'outil hôte et de sa configuration.

#### 1. Point d'entrée du flux versionné
- **`comet`** : le CLI Comet fournit des flux versionnés natifs et classiques. Ce dépôt ne livre qu'un guide de point d'entrée ; il n'implémente pas les gardes de phase Comet.

#### 2. Suite pilotée par les spécifications OpenSpec (12 compétences)
- **`openspec`** : architecture centrale.
- **`openspec-propose`** : propose des changements avec conception, spécifications et tâches en une étape.
- **`openspec-new-change`** : création d'artefacts pas à pas.
- **`openspec-continue-change`** : fait avancer le changement vers l'artefact suivant.
- **`openspec-ff-change`** : avance rapide dans la génération d'artefacts.
- **`openspec-apply-change`** : implémente les tâches d'un changement actif.
- **`openspec-verify-change`** : vérifie le code par rapport aux spécifications delta.
- **`openspec-sync-specs`** : synchronise les spécifications delta dans les spécifications principales.
- **`openspec-archive-change`** : archive un changement terminé.
- **`openspec-bulk-archive-change`** : archive plusieurs changements en parallèle.
- **`openspec-explore`** : partenaire de réflexion interactif avant de créer des changements.
- **`openspec-onboard`** : visite guidée interactive.
- **`write-openspec-docs`** : rédige la documentation dans le style maison.
- **`draft-openspec-docs`** : rédaction collaborative section par section.
- **`verify-openspec-docs`** : vérifie factuellement les affirmations de la documentation.
- **`release-openspec`** : audit de release et gestion des changesets.

#### 3. Suite qualité d'ingénierie Superpowers (15 compétences)
- **`superpowers`** : constitution qualité.
- **`using-superpowers`** : découverte des compétences et garde d'invocation.
- **`brainstorming`** : exploration de conception avant implémentation.
- **`writing-plans`** : planification d'exécution pas à pas.
- **`executing-plans`** : exécution stricte du plan.
- **`test-driven-development`** : cycle TDD rouge-vert.
- **`systematic-debugging`** : analyse de cause racine avant modification du code.
- **`verification-before-completion`** : preuve obligatoire avant de déclarer l'achèvement.
- **`dispatching-parallel-agents`** : lance des sous-agents concurrents isolés.
- **`subagent-driven-development`** : harnais d'exécution de plans par sous-agents.
- **`using-git-worktrees`** : espaces de travail physiques isolés.
- **`finishing-a-development-branch`** : décisions de fusion et d'intégration.
- **`requesting-code-review`** : vérification de revue avant fusion.
- **`open-code-review`** : revue de code déterministe — règles d'abord, ancrage par ligne, couverture imposée. Niveau A via délégation CLI `ocr`, méthodologie de niveau B sans.
- **`receiving-code-review`** : évaluation technique des commentaires de revue humains.
- **`writing-skills`** : créateur et validateur de compétences.
- **`diagnosing-superpowers`** : audite la dérive de session ou le coût.

#### 4. Code minimal et graphe de syntaxe
- **`ponytail`** : échelle d'implémentation minimale (stdlib d'abord, YAGNI).
- **`codegraph`** : directives optionnelles de configuration CLI/MCP CodeGraph ; l'installation et le câblage de l'agent sont distincts.

#### 5. Filtrage de sortie et livraison concise
- **`rtk`** : directives optionnelles du CLI Rust Token Killer ; la réécriture de commandes nécessite un crochet d'agent configuré.
- **`caveman`** : sortie télégraphique ultra-compressée.

#### 6. Traitement professionnel des documents
- **`docx`** : génération, édition et mise en forme de documents Word.
- **`pdf`** : extraction et traitement de texte/tableaux PDF.

#### 7. Revue pré-décision, mémoire inter-outils et documentation vivante (compétences du dépôt)
- **`cross-tool-memory`** : aide à la navigation et au rappel de la mémoire de projet inter-outils (s'associe au backend ai-memory local).
- **`option-review`** : revue multi-options pré-décision générant une matrice de décision isolée à 5 dimensions.
- **`living-documentation`** : suite de documentation vivante à 4 niveaux (specs/architecture/référence/guides) avec traçabilité bidirectionnelle code-doc basée sur le frontmatter, prenant en charge les seuils d'impact de changement L0/L1/L2.
- **`engineering-docs`** : modèles de documents du cycle de vie R&D (31 types de documents, 15 modèles bilingues de portes de phase) garantissant une sortie cohérente entre les agents IA et une intégration transparente avec les portes de phase Comet et la documentation vivante.

---

### 2.2 Verrouillage de version, mises à jour en ligne et synchronisation des compétences (`skills-lock.json` + `deploy-agents` + `tools/sync-skills.py`)

1. **`skills-lock.json`** :
   - Enregistre les sources amont et les hachages d'intégrité SHA256 normalisés LF pour les compétences externes vendorisées ;
   - Distingue les compétences centrales rédigées localement (`sourceType: local`) des compétences amont externes (`sourceType: github`).
2. **Synchronisation amont des compétences externes (`tools/sync-skills.py`)** :
   - Programme de mise à jour intégré pour les compétences externes vendorisées ;
   - **Mode vérification** : `python3 tools/sync-skills.py --check` (lecture seule, compare les hachages `SKILL.md` locaux et amont, rapporte 🟢 en synchronisation / 🟡 périmé) ;
   - **Mode application** : `python3 tools/sync-skills.py --apply` (met à jour les fichiers `SKILL.md` périmés sur place et actualise les hachages de verrouillage ; les compétences rédigées localement sont strictement protégées) ;
   - Interface terminal interactive alimentée par `tools/tui.py` lors d'une invocation sans arguments ;
   - Prend en charge `--skill <name>` pour les mises à jour ciblées et `--json` pour l'automatisation.
3. **Analyse d'impact de la documentation vivante (`tools/doc-impact.py`)** :
   - Analyse les changements de code par rapport aux métadonnées de traçabilité de la documentation vivante (`docs/{specs,architecture,reference,guides,adr}/`) ;
   - Prend en charge l'inspection de l'arbre de travail, les bases de commit (`--since`), les listes de fichiers explicites et le mode assistant interactif (`--interactive`).
4. **Exécuteur de pipeline unifié (`run-pipeline.sh` / `run-pipeline.ps1`)** :
   - Enchaîne le flux complet en une seule exécution par OS (Déploiement → Mémoire IA → Synchronisation des compétences → Impact doc vivante) ;
   - Assistant interactif : `./run-pipeline.sh` (Linux/macOS) ou `.\run-pipeline.ps1` (Windows) ;
   - Automatisation sans surveillance : `./run-pipeline.sh --all -y` ou `.\run-pipeline.ps1 -All -Yes`.
5. **Composant TUI interactif de terminal (`tools/tui.py`)** :
   - Fournit des menus interactifs pilotés au clavier : sélection unique (touches fléchées + Entrée) et sélection multiple (touches fléchées + bascule par case à cocher avec la barre d'espace + Entrée pour confirmer) ;
   - Détection intégrée de la compatibilité TTY et ANSI avec repli gracieux vers des invites textuelles numérotées dans les pipelines non interactifs ou non ANSI, servant de fondation à tous les outils de déploiement et de maintenance.
6. **Flux de mise à jour en ligne intégré** :
   ```powershell
   # Windows
   .\deploy-agents.ps1 -ProjectPath "." -Update

   # Linux / macOS
   ./deploy-agents.sh . --update
   ```
   - Les scripts de déploiement mettent en avance rapide le dépôt de modèles, proposent de vérifier/appliquer les mises à jour des compétences externes, et synchronisent les fichiers gérés vers les projets cibles avec des sauvegardes `.bak.<horodatage>`.

---

### 2.3 Outils CLI optionnels du Harness

La disponibilité des compétences dépend de l'outil hôte et de sa configuration. Les outils CLI de niveau terminal sont optionnels :
- **Comet CLI** : installez via `npm install -g @rpamis/comet` ; fournit l'exécution des flux natifs/classiques et l'initialisation `--comet-init`.
- **CodeGraph CLI** : macOS/Linux : `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh` ; Windows PowerShell : `irm https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.ps1 | iex`. Exécutez `codegraph install` pour câbler les agents et `codegraph init` dans le projet.
- **RTK (Rust Token Killer) CLI** : macOS/Linux : `curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh` ; Windows : `winget install rtk-ai.rtk`. Vérifiez avec `rtk gain`. Exécutez `rtk init` dans le projet pour configurer les crochets d'agent.
- **Open Code Review (OCR) CLI** : installez via `npm install -g @alibaba-group/open-code-review` ; active la revue par délégation de niveau A à coût LLM nul via la compétence `open-code-review`.

Les scripts de déploiement détectent automatiquement ces CLI optionnels lors de la configuration initiale et guident l'installation le cas échéant.

---

### 2.4 Chargement des compétences et configuration optionnelle des CLI

La découverte des compétences et les coûts de contexte dépendent de l'agent hôte et de sa configuration. La seule présence de fichiers ne garantit pas qu'une compétence soit chargée. Ponytail et Caveman sont des compétences de directives copiées avec le projet ; CodeGraph et RTK nécessitent en outre leurs étapes distinctes de CLI et d'intégration d'agent. Leur efficacité dépend du projet, de l'hôte et de la configuration : ce guide n'avance donc aucune affirmation fixe d'économie de tokens.

---
### 2.5 Matrice de dispatching des compétences d'ingénierie et des règles

| Scénario | Règle / Compétence | Déclencheur / Mot-clé | Comportement attendu |
|---|---|---|---|
| **Branchement / Commit / Push** | [`git-workflow.md`](../../.agents/rules/git-workflow.md) | `git commit` / `git push` | Commit uniquement sur branches temporaires ; pas de `git add .` ; autorisation humaine requise pour le push distant |
| **Opérations à haut risque** | [`security-boundary.md`](../../.agents/rules/security-boundary.md) | Modification de configs de build, protocoles, structs publiques | Pause et confirmation de l'impact avec un humain |
| **Exigences complexes** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `comet` / `openspec` | `/comet` ou « utiliser openspec » | Proposer le changement sous `docs/openspec/changes/` ; attendre la confirmation |
| **Découverte de symboles** | [`token-discipline.md`](../../.agents/rules/token-discipline.md) + `codegraph` optionnel | CodeGraph MCP lorsque configuré ; sinon `rg` à portée limitée | Ne pas supposer que CodeGraph est installé ou disponible |
| **Implémentation de fonctionnalité** | `ponytail` + `test-driven-development` | Consulter les compétences chargées selon le cas | Comprendre le code actuel, puis choisir la plus petite implémentation correcte et la validation adaptée |
| **Investigation de bug** | `systematic-debugging` | Trace d'erreur collée | Rassembler les preuves $\rightarrow$ formuler une hypothèse $\rightarrow$ repro minimale $\rightarrow$ corriger |
| **Longue sortie terminal** | `rtk` optionnel | Uniquement installé et son crochet d'agent configuré | Sinon utiliser les drapeaux concis natifs ; conserver la validation requise et préserver les journaux pertinents |
| **Économie de tokens** | `caveman` | Uniquement lorsque l'hôte charge la compétence ou le plugin | Être concis tout en préservant le contexte nécessaire, l'exactitude technique et les détails de sécurité |
| **Traitement de documents** | `docx` / `pdf` | Mentions de `.docx` ou `.pdf` | Mise en forme professionnelle sans exécuter de suites de tests de code |
| **Docs vivantes et traçabilité** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `living-documentation` | `/living-documentation` / synchroniser les docs de traçabilité | Maintenir les docs à 4 niveaux (specs/architecture/référence/guides) via les seuils d'impact L0/L1/L2 et la traçabilité du frontmatter |
| **Docs de portes de phase / Modèles** | [`engineering-spec.md`](../../.agents/rules/engineering-spec.md) + `engineering-docs` | `/engineering-docs` / demandes SRS/HLD/spec | Standardiser les sorties des agents IA entre les phases à l'aide des 15 modèles bilingues de portes de phase, reliant les artefacts Comet à la documentation vivante |
| **Revue de code et porte qualité** | `open-code-review` + `requesting-code-review` | Avant fusion ou après achèvement de la tâche | Règles d'abord, ancrage par ligne, couverture imposée ; délégation de niveau A si le CLI `ocr` existe, sinon méthodologie de niveau B |
| **Achèvement de tâche** | `verification-before-completion` | Fin de tâche | Présenter les preuves physiques d'exécution de commandes |

---

## 3. Plongée dans les outils centraux du Harness et les commandes slash

### 3.1 Comet : point d'entrée du flux versionné

Comet est un outil de flux versionné indépendamment. Vérifiez le `.comet/config.yaml` du projet et la version CLI installée, puis suivez le flux natif ou classique pris en charge par cette version. La compétence Comet de ce dépôt est un guide de point d'entrée ; elle ne crée pas de fichiers d'état Comet ni n'impose de gardes de phase. Si Comet n'est pas installé ou configuré, utilisez le processus existant du projet ou établissez un plan adapté à la tâche. Associé à `engineering-docs`, chaque phase (Open, Design, Build, Verify, Archive) utilise des modèles de porte standardisés pour des livrables cohérents.

```text
/comet Add date-range filtered CSV export for the order service
```

Utilisez la documentation amont actuelle de Comet pour les points d'entrée spécifiques à la version, la configuration, les chemins d'artefacts et le comportement d'archivage.

---

### 3.2 OpenSpec : développement piloté par les spécifications

- `/opsx:propose <name>` : propose un nouveau changement sous `docs/openspec/changes/` ;
- `/opsx:apply` : implémente le changement approuvé ;
- `/opsx:verify` : compare l'implémentation réelle avec la spécification delta ;
- `/opsx:sync` : synchronise les spécifications delta dans les docs principales ;
- `/opsx:archive` : déplace le changement terminé vers `docs/openspec/changes/archive/`.

---

### 3.3 Superpowers : TDD, débogage systématique et porte de vérification

1. **Cycle TDD rouge-vert** :
   - Écrire un test en échec basé sur le scénario de spécification ;
   - Exécuter le test et observer l'échec attendu ;
   - Écrire le code minimal pour passer ;
   - Refactorer et exécuter la vérification.
2. **Débogage systématique** :
   - Étape 1 : collecte de traces ;
   - Étape 2 : formulation d'hypothèse ;
   - Étape 3 : test de reproduction minimale ;
   - Étape 4 : corriger la cause racine et vérifier.
3. **Porte de preuves de vérification** :
   - Aucune tâche n'est terminée sans preuve physique de sortie terminal.

---

### 3.4 CodeGraph : intégration optionnelle du graphe de code MCP

```bash
# Explorer les chaînes d'appels et l'architecture
Interrogez l'outil MCP CodeGraph configuré pour l'agent actuel : « User authentication and JWT token flow ».

# Trouver les définitions et toutes les références d'appels
Interrogez l'outil MCP CodeGraph configuré pour `OrderService::calculateDiscount`.
```

---

### 3.5 Ponytail : échelle d'implémentation minimale

1. Cette fonctionnalité doit-elle exister ? (YAGNI) ;
2. Existe-t-il un utilitaire existant à réutiliser ?
3. La bibliothèque standard du langage peut-elle le faire ?
4. Changez 1 ligne avant de réécrire 10 lignes ;
5. Jamais de refactoring opportuniste pendant les corrections de bugs.

---

### 3.6 Caveman : sortie ultra-compressée

- Élimine le superflu : « Sure, I'll do that for you », « Note that this requires caution » ;
- Livre : conclusion et impact $\rightarrow$ diff $\rightarrow$ preuves de vérification.

---

### 3.7 RTK : CLI optionnel Rust Token Killer

- RTK ne réécrit les commandes prises en charge que lorsqu'il est installé et intégré à l'agent actif. La seule compétence du dépôt ne filtre pas la sortie terminal.
- Vérifiez le bon produit avec `rtk gain` ; initialisez les crochets de projet pris en charge avec `rtk init`.
- Si RTK n'est pas configuré, utilisez les drapeaux concis natifs et la gestion bornée des journaux.

- Ne jamais exécuter de commandes verbeuses nues ;
- Toujours utiliser `git status -s`, `pytest -q`, `ctest --output-on-failure` ;
- Redirigez les journaux de plusieurs centaines de lignes vers des fichiers scratch locaux et ne découpez que les traces d'échec.

---

### 3.8 Modèle d'autorisation Git et flux des branches protégées

1. **Isolation des branches temporaires** :
   - Tout le travail se fait dans `feature/*`, `fix/*`, `refactor/*` ;
   - Ne jamais committer directement sur `develop`, `master`, `main`, `release*`, `staging`.
2. **Autorisation du push distant** :
   - L'IA peut créer des branches et committer localement ;
   - Pousser vers le distant ou fusionner dans des branches protégées nécessite une confirmation humaine explicite.
3. **Lois d'airain** :
   - `git push --force` est définitivement interdit ;
   - Rebaser des branches protégées est définitivement interdit ;
   - Le staging aveugle via `git add .` est interdit (utilisez `git add <chemin-explicite>`) ;
   - Standard de message de commit : `{type}: {description}`.

---
### 3.9 Mémoire de projet et point de contrôle de session (`PROJECT_CONTEXT.md` / `SESSION_STATE.md`)

Traitez la mémoire comme un résumé vérifiable et une aide à la navigation, pas comme un remplacement du code ou de la documentation maintenue :
1. **Début de tâche :** lisez `PROJECT_CONTEXT.md` (faits durables vérifiés du projet) et `SESSION_STATE.md` (point de contrôle actuel) uniquement lorsqu'ils sont présents et pertinents ; vérifiez la branche, la configuration et les faits d'implémentation qui affectent la tâche.
2. **Pendant le travail :** conservez les plans lorsqu'ils sont utiles pour le travail multi-étapes. N'ajoutez pas de capture automatique des prompts, entrées/sorties d'outils, fichiers sources ou commandes de terminal.
3. **Clôture significative :** mettez à jour `SESSION_STATE.md` avec le travail accompli, les preuves de vérification réelles, les étapes restantes et les risques encore pertinents ; supprimez les éléments périmés. Ne mettez à jour `PROJECT_CONTEXT.md` que lorsque l'architecture durable, les contraintes ou les décisions confirmées changent. Les sessions sans opération n'ont pas besoin de mise à jour vide.
4. **Sources et conflits :** signalez l'incertitude et datez/sourcez les faits susceptibles de changer. Les instructions actuelles de l'utilisateur et le code/la configuration/les preuves reproductibles actuels priment sur les résumés de mémoire.
5. **Confidentialité :** n'enregistrez pas d'identifiants, clés privées, données personnelles brutes, journaux complets de conversations/outils, ni d'informations personnelles inutiles. Les modèles globaux partagés ne doivent pas contenir de préférences privées de l'utilisateur.
6. **Portée de répertoire :** un `AGENTS.md` de répertoire ne contient que des frontières et contraintes locales. Ne créez pas de fichiers de mémoire de répertoire par défaut ; conservez les faits du projet et les points de contrôle dans leurs fichiers racine.

**La mémoire Auto native de Claude Code** est une mémoire de projet machine-locale distincte qui peut être inspectée, modifiée ou supprimée avec `/memory`. Elle n'est pas partagée entre outils ou machines et ne remplace pas les fichiers de projet ci-dessus. Claude Code gère cette fonctionnalité ; le déployeur de ce dépôt ne l'active pas, ne la désactive pas et ne la capture pas. Voir la [doc mémoire de Claude Code](https://code.claude.com/docs/en/memory).

#### Mémoire inter-agents optionnelle : ai-memory

Ce dépôt ne sélectionne que [ai-memory](https://github.com/akitaonrails/ai-memory) comme backend inter-agents optionnel. Son parcours local Markdown et recherche plein texte n'utilise ni LLM, ni fournisseur d'embeddings, ni clé API. Le dépôt ne l'installe ni ne le démarre automatiquement.

Pour activer un dépôt, copiez `.ai-memory.toml.example` vers le `.ai-memory.toml` ignoré, remplacez les noms de workspace/projet, puis exécutez `setup-ai-memory.ps1 -Agent <claude-code|codex|antigravity-cli>` ou `./setup-ai-memory.sh <claude-code|codex|antigravity-cli>`. L'assistant nécessite une installation ai-memory existante et délègue la configuration à ses commandes amont sensibles à la fusion. Examinez la sortie de capacité des crochets ; le mode liste d'autorisation n'est effectif que pour les crochets qui appliquent la politique de capture native.

La configuration inclut les MCP/crochets Claude Code et Codex CLI, plus les MCP/crochets Antigravity CLI. La prise en charge du desktop Codex dépend de la version desktop installée exposant l'intégration Codex locale ; vérifiez-la dans l'application. Antigravity IDE est MCP uniquement : ajoutez `http://127.0.0.1:49374/mcp` comme `serverUrl` via ses paramètres MCP ou le fichier de configuration documenté. Pour le déploiement Docker, exécutez `docker run -d --name ai-memory --restart unless-stopped -p 127.0.0.1:49374:49374 -v "${HOME}/env/ai-memory-data:/data" docker.io/akitaonrails/ai-memory:latest` (le chemin de stockage du conteneur est fixé à `/data`). ChatGPT web utilise un transfert Markdown manuel dans la configuration locale gratuite.

Windows prend en charge les modes WSL2 et natif en amont. Installez et configurez ai-memory dans le même environnement qui lance l'agent ; voir le [guide Windows](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md). Les exclusions de chemins ne expurgent pas le texte arbitraire du prompt. Sauvegardez avec `ai-memory --data-dir <data-dir> backup --to <archive-path>` ; la désinstallation supprime les intégrations mais pas les données. Arrêtez le service et vérifiez le répertoire de données configuré avant de le supprimer intentionnellement. Voir la [référence du marqueur](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md) et le [guide d'installation](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md) pour les chemins de plateforme et les commandes Docker.

### 3.10 Matrice de protection des 8 opérations à haut risque

La confirmation humaine est obligatoire avant :
- [ ] 1. Modifier les configs de build (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`) ;
- [ ] 2. Ajouter de nouvelles dépendances tierces ;
- [ ] 3. Modifier les structures de données publiques globales (`public_struct.h`, `types.ts`) ;
- [ ] 4. Modifier les singletons de dispatch centraux ou les API de services publics ;
- [ ] 5. Changer les protocoles wire ou les contrats de sérialisation (`protofile/`) ;
- [ ] 6. Altérer la licence, la cryptographie ou le code d'authentification ;
- [ ] 7. Modifier `.gitignore` ou les pipelines CI/CD ;
- [ ] 8. Changements inter-modules à fort impact affectant des contrats partagés ou nécessitant une large coordination (le seul nombre de fichiers n'est pas un déclencheur de risque).

---

## 4. Commandes natives spécifiques aux plateformes et bonnes pratiques

### 4.1 Google Antigravity CLI et IDE
- Le CLI s'exécute comme `agy` ; l'IDE desktop est une surface distincte. Les deux documentent des règles de workspace/global basées sur des fichiers, mais les commandes slash du CLI et les contrôles de l'IDE sont spécifiques à la surface.
- `/plan` : planification de tâches structurée pour $\ge 3$ étapes ;
- `/goal` : boucle autonome sans surveillance jusqu'à l'achèvement vérifié ;
- `/grill-me` : entretien de découverte interactif lorsque les exigences sont ambiguës ;
- `/learn` : capture les leçons apprises dans `tasks/lessons.md` ;
- `/schedule` : minuteurs d'arrière-plan et surveillance cron récurrente.

### 4.2 Claude Code et crochet client PreToolUse
- `/compact` : compresse l'historique de conversation lorsque le nombre de tokens est élevé ;
- `/cost` : utilisation de tokens de la session en temps réel ;
- `/review` : examine les diffs de la copie de travail ;
- `@<path>` : charge dynamiquement des règles spécifiques à la demande.
- **Crochet de sécurité** : `.claude/settings.json` exécute des vérifications côté client de Claude Code pour les appels d'outils correspondants. Il peut rejeter des motifs sélectionnés ou avertir ; ce n'est pas un contrôle du système d'exploitation ni un collecteur de mémoire.

### 4.3 Codex dans ChatGPT, Codex CLI et GitHub Copilot
- Codex CLI documente la découverte `AGENTS.md` depuis le répertoire Codex et le chemin du dépôt jusqu'au répertoire courant. Ne déduisez pas ce comportement exact pour ChatGPT/desktop ; vérifiez son comportement et sa configuration actuels du produit.
- `/hooks` : inspecte et fait confiance aux crochets de cycle de vie ;
- `$comet` : déclenche la machine à états Comet dans Codex CLI ;
- `@workspace` : analyse le contexte du workspace dans VS Code.

### 4.4 Zed IDE
- Réutilisez le `AGENTS.md` du projet ; cet installateur ne crée pas de fichier spécifique à Zed ;
- `Ctrl+Enter` (assistance en ligne) avec `follow ponytail principles` ;
- Panneau Assistant (`Ctrl+?`) pour la planification architecturale multi-tours.

---
## 5. Parcours pratique de bout en bout (développement réel d'une fonctionnalité)

**Exigence** : « Ajouter un point de terminaison d'export CSV avec filtrage par plage de dates au service de commandes. »

```text
Étape 1 : Cérémonie de session et conscience des points de reprise (début de session)
  ├─ Lire en priorité PROJECT_CONTEXT.md et SESSION_STATE.md pour restaurer l'architecture et reprendre au point d'arrêt
  ├─ Vérifier tasks/lessons.md et tasks/todo.md (si présents)
  └─ git checkout -b feature/order-csv-export

Étape 2 : Cadrage et création du changement (Comet + OpenSpec SDD)
  ├─ /comet Add date range CSV export endpoint
  ├─ Généré : docs/openspec/changes/add-csv-export/
  └─ Confirmer la proposition avec un humain

Étape 3 : Récupération sémantique optionnelle (CodeGraph, si configuré)
  ├─ Interdit : grep -rn "export" .
  └─ Interroger le MCP CodeGraph configuré ; sinon utiliser la recherche de code à portée limitée
      └─ Localisé : router.py, order_repo.py, types.ts

Étape 4 : Test rouge (Superpowers TDD)
  ├─ tests/test_export.py : écrire un test en échec avec vérification de plage de dates invalide
  └─ pytest tests/test_export.py -q -> FAILED (rouge)

Étape 5 : Implémentation minimale (Ponytail)
  ├─ Stdlib Python : import csv, datetime (pas de paquet d'export lourd)
  └─ Ajouter la condition de filtre dans order_repo.py et la route dans router.py

Étape 6 : Vérification verte (RTK)
  ├─ pytest tests/test_export.py -q -> PASSED (vert, 2 passed in 0.3s)
  └─ npm test -- packages/order --reporter=dot

Étape 7 : Livraison, commit sûr et clôture mémoire sélective (fin de session)
  ├─ Sortie : diff concis et preuves de tests passants
  ├─ git add tests/test_export.py api/router.py repo/order_repo.py
  ├─ git commit -m "feat: add date-range CSV export endpoint"
  ├─ Demander à un humain avant git push
  ├─ Clôture mémoire sélective :
  │   ├─ Mettre à jour SESSION_STATE.md aux frontières significatives de tâche avec les preuves réelles et le travail restant
  │   └─ Ne mettre à jour PROJECT_CONTEXT.md que lorsque les faits durables du projet changent ; ignorer les mises à jour vides
  ├─ Mettre à jour tasks/todo.md
  └─ Archiver le changement OpenSpec
```

---

## 6. Contrôles de santé quotidiens et dépannage

### Contrôle de santé quotidien :
```bash
Vérifiez la version Comet installée et la configuration du projet avant d'utiliser des commandes spécifiques à Comet.
Lisez `tasks/lessons.md` lorsqu'il est pertinent pour la tâche.
```

### Documentation de référence :
- Exécuteurs de pipeline unifiés :
  - Windows : [`run-pipeline.ps1`](../../run-pipeline.ps1)
  - Linux / macOS : [`run-pipeline.sh`](../../run-pipeline.sh)
- Scripts de déploiement en un clic :
  - Windows : [`deploy-agents.ps1`](../../deploy-agents.ps1)
  - Linux / macOS : [`deploy-agents.sh`](../../deploy-agents.sh)
- Outils de maintenance :
  - Bibliothèque UI de terminal : [`tools/tui.py`](../../tools/tui.py)
  - Outil de synchronisation des compétences : [`tools/sync-skills.py`](../../tools/sync-skills.py)
  - Porte d'impact de la doc vivante : [`tools/doc-impact.py`](../../tools/doc-impact.py)
- Guide de déploiement et configuration :
  - [Multi-Tool Deployment and Configuration Guide (English)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md)
  - [多工具部署配置指南 (中文)](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md)
- Architecture des règles :
  - [`Global AGENTS.md`](../../templates/agents/Global%20AGENTS.md)
  - [`Project AGENTS.md`](../../templates/agents/Project%20AGENTS.md)
  - [`Directory AGENTS.md`](../../templates/agents/Directory%20AGENTS.md)
