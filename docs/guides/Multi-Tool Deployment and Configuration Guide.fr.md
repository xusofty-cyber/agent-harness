# Guide de déploiement et de configuration multi-outils (Codex / Claude Code / Antigravity 2.0 / CLI / IDE / Zed) pour l'ingénierie IA

> **Language / Langue**: [English](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md) | [简体中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | [繁體中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh-tw.md) | **Français** | [Deutsch](Multi-Tool%20Deployment%20and%20Configuration%20Guide.de.md)

Ce guide fournit une spécification de bout en bout sur la manière de déployer, configurer et utiliser en collaboration l'**architecture AGENTS.md à trois niveaux** (niveaux global, projet et répertoire) avec **OpenAI Codex / GitHub Copilot**, **Claude Code**, **Google Antigravity IDE** et **Zed IDE**, adaptée à des scénarios réels mettant l'accent sur l'ingénierie logicielle tout en prenant en charge la documentation technique professionnelle.

---

## Table des matières

1. [Architecture et positionnement par couches (Harness + divulgation progressive)](#1-architecture-et-positionnement-par-couches-harness--divulgation-progressive)
2. [Périmètre de configuration par outil](#2-périmètre-de-configuration-par-outil)
3. [Crochets client Claude Code : PreToolUse (.claude/settings.json)](#3-crochets-client-claude-code--pretooluse-claudesettingsjson)
4. [Déploiement multi-outils et mises à jour des modèles (deploy-agents)](#4-déploiement-multi-outils-et-mises-à-jour-des-modèles-deploy-agents)
   - 4.1 Architecture centrale du script et pipeline
   - 4.2 Déploiement Windows (`deploy-agents.ps1`)
   - 4.3 Déploiement Linux / macOS (`deploy-agents.sh`)
   - 4.4 Mécanique des liens symboliques vs jonctions de répertoire
5. Plongée dans les quatre couches de règles
   - 5.1 Constitution globale : `Global AGENTS.md`
   - 5.2 Routeur de projet : `Project AGENTS.md`
   - 5.3 Sous-règles modulaires : `.agents/rules/`
   - 5.4 Correctif de micro-périmètre : `Directory AGENTS.md`
6. Flux de travail pratique à double voie : « l'ingénierie d'abord, la documentation ensuite »
7. Foire aux questions et bonnes pratiques (FAQ)
8. Référence du guide d'utilisation pratique et panorama des compétences

---

## 1. Architecture et positionnement par couches (Harness + divulgation progressive)

Ce dépôt organise les règles réutilisables comme un **point d'entrée de projet plus des sous-règles à la demande**, afin que les équipes puissent adapter la base et éviter de charger des directives sans rapport. La découverte réelle et le coût du contexte dépendent de l'outil hôte :

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Niveau global (Global AGENTS.md)                                    │
│    - Rôle : constitution d'ingénierie inter-projets et base de sécurité│
│    - Contenu : base d'ingénierie réutilisable, sécurité Git, communication concise │
│    - Portée : résident à l'échelle du système pour tous les projets (~1000 Tok) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Hérité (non redondant)
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. Niveau racine du projet (Project AGENTS.md)                         │
│    - Rôle : contexte d'ingénierie déterministe et routeur sous-règles/compétences │
│    - Contenu : emplacements CLI concrets, stack technique, lignes rouges, mémoire d'état │
│    - Portée : à l'échelle du dépôt ; le chargement dépend de l'outil hôte │
│    - Ponts : CLAUDE.md / .github/copilot-instructions.md               │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │ Lecture progressive à la demande│ Uniquement si besoin dans les sous-modules
┌──────────────────▼───────────────┐ ┌───────────────▼───────────────────┐
│ 3. Sous-règles (.agents/rules/)  │ │ 4. Niveau répertoire (Directory AGENTS.md)│
│  - token-discipline.md           │ │    - Rôle : correctif de micro-périmètre │
│  - engineering-spec.md (SDD/TDD) │ │    - Contenu : périmètre In/Out, dépendances│
│  - security-boundary.md          │ │            isolées, tests rapides  │
│  - git-workflow.md (modèle d'autorisation) │ └───────────────────────────────────┘
└──────────────────────────────────┘
```

### Avantages clés
1. **Base partagée** : conservez les règles réutilisables dans des modèles Markdown et utilisez des ponts spécifiques à l'outil lorsque c'est pris en charge ; vérifiez le comportement de découverte de chaque hôte au lieu de supposer que chaque outil charge le même fichier.
2. **Divulgation progressive** :
   - Les règles sont chargées dynamiquement lorsque des scénarios spécifiques sont déclenchés.
   - La découverte des compétences, leur chargement et le comportement du cache de prompt dépendent de l'outil hôte et de sa configuration ; déployer des fichiers ne garantit pas un chargement automatique.
3. **Garde-fous client contre les risques** : les crochets Claude Code peuvent rejeter des appels d'outils correspondants sélectionnés ou émettre des avertissements. Ce sont des vérifications côté client, pas des contrôles de sécurité côté système d'exploitation ou serveur.

---
## 2. Périmètre de configuration par outil

La découverte des règles, l'héritage, les paramètres globaux et les mécanismes de mémoire varient selon le produit et la version. Ce tableau distingue les chemins écrits par les scripts de la découverte de l'hôte ; le déploiement de fichiers n'est pas une vérification de chargement.

| Outil/surface | Fourni ou écrit par ce dépôt | Notes de chargement |
| :--- | :--- | :--- |
| Codex (app locale / IDE / CLI) | `AGENTS.md` global `$CODEX_HOME/AGENTS.md` (défaut `~/.codex/AGENTS.md`) ; `AGENTS.md` de projet et de répertoire | `-Global` crée le fichier global ; `-Global -Update` sauvegarde et remplace le fichier d'instructions global actif. Codex utilise un `AGENTS.override.md` non vide dans le répertoire Codex de préférence à `AGENTS.md` |
| Claude Code | Pont `CLAUDE.md`, `~/.claude/CLAUDE.md`, crochets/compétences de projet | `CLAUDE.md` est un point d'entrée d'instructions ; la mémoire Claude Auto est une mémoire de projet machine-locale optionnelle distincte, non partagée entre outils |
| Antigravity 2.0 | `AGENTS.md` / `GEMINI.md` de projet / `.agents/rules/` ; `~/.gemini/AGENTS.md` global et pointeur de compatibilité `GEMINI.md` | La documentation actuelle liste les deux noms globaux ; les anciennes versions peuvent suivre le pointeur vers le fichier canonique |
| Antigravity CLI | Règles de projet/répertoire ; `~/.gemini/AGENTS.md` global et pointeur de compatibilité `GEMINI.md` ; optionnel `~/.gemini/antigravity-cli/rules/*.md` | Les règles communes utilisent l'entrée canonique ; configurez les règles réservées au CLI séparément |
| Antigravity IDE / extensions | Règles de projet/répertoire ; `~/.gemini/AGENTS.md` global et pointeur de compatibilité `GEMINI.md` | L'IDE actuel prend en charge les deux noms globaux ; les anciennes générations d'IDE peuvent suivre le pointeur |
| GitHub Copilot | Pont `.github/copilot-instructions.md` | Confirmez le chargement dans les paramètres/docs actuels du produit Copilot |
| Zed / Pi / OpenCode | Markdown réutilisable uniquement ; aucune configuration dédiée fournie par ce dépôt | Ne déduisez pas une découverte automatique ou un chargement global de la simple présence de fichiers |

Références : [Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md), [Claude Code memory](https://code.claude.com/docs/en/memory), [Antigravity rules](https://www.antigravity.google/docs/rules/).

---

## 3. Crochets client Claude Code : PreToolUse (.claude/settings.json)

### Limites de capacité
Les crochets de `.claude/settings.json` sont spécifiques à Claude Code et ne s'exécutent qu'avant les appels d'outils correspondants. `guard.mjs` rejette des motifs de commandes sélectionnés ; de nombreux autres cas n'émettent qu'un avertissement. La correspondance par expressions régulières ne peut pas identifier tous les wrappers shell, alias ou formes de commandes : ce n'est donc pas une frontière de sécurité complète. Les crochets ne collectent ni ne transmettent de données de mémoire. La mémoire Claude Code Auto est une fonctionnalité de projet machine-locale distincte que les utilisateurs peuvent inspecter/gérer avec `/memory` ; ce dépôt ne la configure pas. Utilisez la protection de branche côté serveur et des identifiants à moindre privilège pour les dépôts partagés.

### Configuration et implémentation

L'installateur copie [`.claude/settings.json`](../../.claude/settings.json) et déploie [`.claude/hooks/guard.mjs`](../../.claude/hooks/guard.mjs) plus [`guard-write.mjs`](../../.claude/hooks/guard-write.mjs). Inspectez directement ces fichiers sources ; ne copiez pas d'exemples de crochets issus d'anciennes versions du guide, car le protocole et l'implémentation peuvent changer.

### Équivalents sur d'autres outils (point d'extension)

Les crochets PreToolUse sont spécifiques à Claude Code ; l'installateur n'installe pas d'intercepteurs pour d'autres outils. Pour une protection équivalente, branchez le mécanisme de crochet/approbation propre à chaque outil : la logique de décision de `guard.mjs` (branches protégées, motifs de commandes dangereuses) est du Node.js simple — réutilisez ses expressions régulières et sa table de branches et adaptez-les au point d'entrée de crochet de l'outil cible. Quelle que soit la couche branchée, elle ne remplace jamais la protection de branche côté serveur ; l'interception côté client n'est qu'une couche de la défense en profondeur.

---
## 4. Déploiement multi-outils et mises à jour des modèles (deploy-agents)

Les scripts déploient les fichiers vers les chemins configurés. Le comportement de chargement spécifique à l'outil n'est pas garanti par le déploiement de fichiers. `-Global` initialise les fichiers de règles globaux manquants et préserve les existants. La combinaison `-Global -Update` crée d'abord une sauvegarde horodatée, puis remplace la règle globale active par le modèle actuel. Antigravity reçoit le `~/.gemini/AGENTS.md` canonique plus un petit pointeur de compatibilité `GEMINI.md` au lieu d'un jeu de règles complet dupliqué. Codex utilise `$CODEX_HOME` lorsqu'il est défini (sinon `~/.codex`) ; si un `AGENTS.override.md` non vide existe à cet endroit, ce fichier actif est sauvegardé et mis à jour à la place de `AGENTS.md` :
- **Windows PowerShell** : [`deploy-agents.ps1`](../../deploy-agents.ps1)
- **Linux / macOS Bash** : [`deploy-agents.sh`](../../deploy-agents.sh)

### 4.1 Architecture centrale du script et pipeline

```text
[ Exécuter le script de déploiement ]
       │
       ├─ [Zéro argument en terminal OU avec -Interactive / --interactive]
       │       ▼
       │  Phase 0 : Assistant interactif pas à pas en terminal (TUI touches fléchées et cases à cocher)
       │    ├─ [1/5] Sélectionner la langue du modèle (English / 简体中文 / 繁體中文 / Français / Deutsch)
       │    ├─ [2/5] Sélectionner la portée du déploiement (projet cible uniquement / règles globales uniquement / les deux)
       │    ├─ [3/5] Saisir le chemin du projet cible (défaut : répertoire courant [.])
       │    │        (Note : Codex, Antigravity, Zed lisent nativement AGENTS.md sans ponts)
       │    ├─ [4/5] Sélection multiple des fichiers ponts d'agents (Claude, Copilot, Cursor, Gemini, Windsurf, Cline, Roo, Qwen, Kiro, Continue, Trae, CodeBuddy)
       │    └─ [5/5] Sélection multiple des flux optionnels (mode mise à jour / analyse des faits du projet / ai-memory / Comet)
       │
       ▼
 Phase 1 : Mise à jour du dépôt de modèles (-Update)
   └─ Mise à jour en avance rapide du dépôt de modèles (`git pull --ff-only`) ; aucune mise à niveau de CLI global ni programme de mise à jour tiers dans le répertoire appelant
       │
       ▼
 Phase 2 : Règles globales de l'utilisateur (-Global)
   ├─ Initialiser Claude Code (~/.claude/CLAUDE.md) uniquement si la cible est absente
   ├─ Initialiser Antigravity (~/.gemini/AGENTS.md) uniquement si la cible est absente
   └─ Préserver les fichiers existants ; avec -Update, écrire des fichiers *.template.md adjacents pour fusion manuelle
       │
       ▼
 Phase 3 : Règles de projet et ponts multi-outils
   ├─ AGENTS.md racine (génère AGENTS.template.md s'il existe déjà)
   ├─ CLAUDE.md -> AGENTS.md (lien symbolique/référence)
   ├─ .github/copilot-instructions.md -> ../AGENTS.md
   ├─ Zed utilise le AGENTS.md fourni ; aucune configuration spécifique à Zed n'est créée
   └─ Crochets client PreToolUse Claude Code : .claude/settings.json
       │
       ▼
 Phase 4 : Sous-règles (.agents/rules/*.md)
       │
       ▼
 Phase 5 : Bibliothèque de compétences (.agents/skills/ & .claude/skills/)
   ├─ Copier les compétences vers .agents/skills/
   ├─ Lier vers .claude/skills/ (Windows : jonction, Linux/macOS : lien symbolique)
   └─ Copier les métadonnées skills-lock.json
       │
       ▼
 Phase 6 : Échafaudage de suivi dynamique des tâches
   ├─ tasks/lessons.md (carnet d'erreurs)
   └─ tasks/todo.md (liste de contrôle)
       │
       ▼
 Phase 7 : Échafaudage OpenSpec (docs/openspec/changes/)
       │
       ▼
 Phase 8 : Init Comet CLI optionnelle (-CometInit)
   └─ Exécute `comet init` uniquement sur demande explicite
       │
       ▼
 Phase 9 : Init ai-memory optionnelle (-AiMemoryInit)
   └─ Initialise .ai-memory.toml pour la mémoire inter-outils sur demande explicite
       │
       ▼
 Phase 10 : Détection des CLI optionnels et invites interactives
   ├─ Proposer l'installation de CodeGraph / RTK / Open Code Review (ocr) / Comet si manquant
   ├─ Demander s'il faut câbler les agents CodeGraph / indexer le projet
   ├─ Demander s'il faut exécuter rtk init ; ignoré en mode non interactif
   ├─ Installer ocr active la revue par délégation de niveau A ; le niveau B fonctionne hors ligne sans
   └─ Installer Comet CLI active l'initialisation ultérieure du flux via --comet-init
```

---
### 4.2 Déploiement Windows (`deploy-agents.ps1`)

**Utilisation** :
```powershell
.\deploy-agents.ps1 [[-ProjectPath] <chemin-cible>] [-Global] [-Update] [-Interactive] [-CometInit] [-AiMemoryInit] [-Pipeline]
```

**Paramètres** :
- `-ProjectPath` (positionnel 0) : chemin vers le projet cible. Si omis avec `-Global`, met uniquement à jour les règles globales de l'utilisateur.
- `-Global` (`-g`) : initialise les `~/.claude/CLAUDE.md`, `~/.gemini/AGENTS.md` et Codex `$CODEX_HOME/AGENTS.md` (défaut `~/.codex/AGENTS.md`) manquants. Les fichiers existants sont préservés sans `-Update`.
- `-Language` (`-l`) : sélectionne la langue du modèle (`en`, `zh`, `zh-tw`, `fr`, `de` ; défaut `en`).
- `-Interactive` (`-i`) : lance l'assistant interactif de sélection pas à pas (sélection unique de langue et portée, sélection multiple des ponts d'agents et options). Déclenché automatiquement à l'exécution sans argument dans un terminal interactif.
- `-Update` (`-u`) : met en avance rapide le dépôt de modèles, invoque automatiquement `tools/sync-skills.py --check` pour analyser les mises à jour amont des compétences externes avec confirmation interactive, et synchronise les fichiers vers la cible. Combiné avec `-Global`, sauvegarde et remplace les fichiers de règles globaux existants. Le `$CODEX_HOME/AGENTS.override.md` non vide de Codex est prioritaire et mis à jour comme fichier actif. Les règles de projet existantes, crochets, compétences et métadonnées de verrouillage suivent leur comportement documenté de sauvegarde/mise à jour. Ne met pas à niveau les CLI globaux.
- `-CometInit` (`-c`) : exécute automatiquement `comet init` dans le projet cible si Comet CLI est installé.
- `-AiMemoryInit` (`-m`) : initialise automatiquement `.ai-memory.toml` dans le projet cible (en déduisant `workspace` et `project`) pour l'intégration ai-memory inter-outils.
- `-Pipeline` : délègue l'exécution directement à l'exécuteur de pipeline unifié ([`run-pipeline.ps1`](../../run-pipeline.ps1)).

**Exécuteur de pipeline unifié (Windows)** :
```powershell
# Assistant interactif pas à pas (sélectionner langue, projet, étapes, mode détaillé) :
.\run-pipeline.ps1

# Exécution complète sans surveillance en une fois :
.\run-pipeline.ps1 -All -Yes

# Exécuter des étapes spécifiques :
.\run-pipeline.ps1 -Stages "deploy,skills,docs"
```

**Exemples** :
```powershell
# Scénario 0 : assistant interactif (exécution sans argument)
.\deploy-agents.ps1

# Déployer vers un nouveau projet
.\deploy-agents.ps1 "D:\Projects\my-project"

# Déployer le projet et mettre à jour les règles globales
.\deploy-agents.ps1 "D:\Projects\my-project" -Global

# Mettre à jour en ligne les compétences et sous-règles
.\deploy-agents.ps1 "D:\Projects\my-project" -Global -Update

# Initialiser avec les crochets de terminal Comet
.\deploy-agents.ps1 "D:\Projects\my-project" -CometInit

# Initialiser avec la configuration ai-memory inter-outils
.\deploy-agents.ps1 "D:\Projects\my-project" -AiMemoryInit

# Lancer directement le pipeline unifié
.\deploy-agents.ps1 -Pipeline

# Mettre à jour uniquement les règles globales
.\deploy-agents.ps1 -Global -Update
```

---

### 4.3 Déploiement Linux / macOS (`deploy-agents.sh`)

```bash
chmod +x ./deploy-agents.sh ./run-pipeline.sh

# Scénario 0 : assistant interactif (exécution sans argument)
./deploy-agents.sh

# Déployer vers un projet
./deploy-agents.sh /path/to/my-project

# Déployer et mettre à jour les règles globales
./deploy-agents.sh /path/to/my-project --global

# Mise à jour en ligne
./deploy-agents.sh /path/to/my-project --global --update

# Déployer avec init Comet CLI
./deploy-agents.sh /path/to/my-project --comet-init

# Lancer directement le pipeline unifié
./deploy-agents.sh --pipeline
```

**Exécuteur de pipeline unifié (Linux / macOS)** :
```bash
# Assistant interactif pas à pas (langue, projet, étapes, mode) :
./run-pipeline.sh

# Exécution complète sans surveillance en une fois :
./run-pipeline.sh --all -y

# Exécuter des étapes spécifiques :
./run-pipeline.sh --stages deploy,skills,docs
```

### Déployer avec init ai-memory
```bash
./deploy-agents.sh /path/to/my-project --ai-memory-init
```

---

### 4.4 Mécanique des liens symboliques vs jonctions de répertoire

Pour permettre à Claude Code de découvrir les compétences situées dans `.agents/skills/` :
- **Linux / macOS** : utilise des liens symboliques relatifs standard :
  `ln -sf "../../.agents/skills/${name}" ".claude/skills/${name}"`
- **Windows** : les comptes utilisateurs normaux ne peuvent pas créer de liens symboliques de répertoire sans le mode développeur ni les privilèges administrateur. `deploy-agents.ps1` résout cela en utilisant des **jonctions de répertoire NTFS** :
  `New-Item -ItemType Junction -Path ".claude\skills\$name" -Target ".agents\skills\$name"`
  - Fonctionne sans élévation ;
  - Réflexion du répertoire en temps réel sans duplication de fichiers ;
  - Repli automatique vers la copie récursive si les jonctions ne sont pas prises en charge.

---
## 5. Plongée dans les quatre couches de règles

### 5.1 Modèle de règles globales : `Global AGENTS.md`
- **Objectif :** une base d'ingénierie réutilisable inter-projets. Qu'un hôte la charge, et avec quelle priorité, dépend de cet hôte et de la configuration de l'utilisateur.
- **Frontière de partage :** gardez le modèle partagé générique ; n'y mettez ni préférences personnelles, ni faits de projet, ni informations sensibles. Enregistrez les préférences personnelles uniquement dans un emplacement machine-local contrôlé par l'utilisateur sur demande explicite.
- **Couches de mémoire :**
  1. Au début d'une tâche, lisez `PROJECT_CONTEXT.md` (faits durables vérifiés du projet) et `SESSION_STATE.md` (point de contrôle actuel) lorsque c'est pertinent, puis vérifiez les faits qui affectent le travail.
  2. À une frontière significative de tâche/session, mettez à jour `SESSION_STATE.md` et supprimez les statuts périmés. Ne mettez à jour `PROJECT_CONTEXT.md` que lorsque les connaissances durables du projet changent ; les sessions sans opération n'ont pas besoin de mises à jour vides.
  3. `PROJECT_CONTEXT.md` est un résumé et une aide à la navigation du projet, pas une source unique de vérité sur le code, la configuration ou la documentation maintenue. Les instructions actuelles de l'utilisateur et les preuves reproductibles priment sur la mémoire.
  4. Signalez l'incertitude et datez/sourcez les faits susceptibles de changer. Ne stockez jamais d'identifiants, clés privées, données personnelles brutes, journaux complets de conversations/outils, ni d'informations personnelles inutiles.

**Backend optionnel sélectionné : [ai-memory](https://github.com/akitaonrails/ai-memory).** Son mode local fournit une mémoire de projet basée sur Markdown, une recherche plein texte et un transfert inter-agents sans LLM ni clé API. Il n'est pas requis pour un usage ordinaire. Ce dépôt fournit un assistant de configuration explicite mais n'installe ni ne démarre jamais le backend, ne crée pas de marqueur d'activation local, ni ne modifie la configuration des outils lors d'un déploiement normal.

> **Note sur la chaîne d'approvisionnement** : ai-memory est un binaire natif tiers avec des crochets de lecture de prompt. Téléchargez-le uniquement depuis la page officielle des Releases et vérifiez les sommes de contrôle SHA256 publiées (pour `cargo install`, confirmez que le nom du crate est `ai-memory`). `setup-ai-memory.*` ne le télécharge délibérément jamais pour vous, vérifie qu'il s'agit d'un exécutable natif (en rejetant les scripts wrappers) avant de configurer quoi que ce soit, et épingle la version validée (actuellement **v2.6.0** — une incompatibilité refuse de configurer). Consultez les notes de version amont avant de mettre à niveau, et revérifiez les drapeaux d'installation avant de changer l'épingle.

#### Activation explicite du projet et configuration

1. Installez et démarrez ai-memory séparément en suivant son [guide d'installation officiel](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md). Laissez les fournisseurs LLM et d'embeddings non configurés pour le parcours gratuit sans clé.
2. Examinez `.ai-memory.toml.example`, copiez-le vers `.ai-memory.toml` et remplacez les deux noms. `.ai-memory.toml` est ignoré par Git ; committer cette activation est intentionnellement évité.
3. Exécutez `./setup-ai-memory.sh <claude-code|codex|antigravity|antigravity-ide|antigravity-cli>` sous Linux/macOS/WSL2, ou la valeur `-Agent` équivalente en PowerShell. Utilisez `antigravity` pour Antigravity 2.0 et `antigravity-ide` pour l'IDE ; les deux configurent MCP et les instructions gérées. La cible CLI installe en outre des crochets d'autorisation. Le pré-contrôle d'exécutable natif et de mode crochet s'applique aux cibles à crochets ; les cibles MCP uniquement n'en ont pas besoin. L'assistant ne télécharge pas de logiciel ni ne démarre le serveur.
4. Gardez le serveur lié au loopback pour un usage sur la même machine. Les emplacements de données par défaut sont `~/.local/share/ai-memory` sous Linux, `~/Library/Application Support/ai-memory` sous macOS, et généralement `%LOCALAPPDATA%\ai-memory` sous Windows ; `AI_MEMORY_DATA_DIR` peut les remplacer.
   - **Déploiement Docker (pour Antigravity IDE HTTP MCP)** :
     ```bash
     # Le chemin de stockage dans le conteneur doit être /data ; lié au loopback 127.0.0.1
     mkdir -p "${HOME}/env/ai-memory-data"
     docker run -d --name ai-memory \
       --restart unless-stopped \
       -p 127.0.0.1:49374:49374 \
       -v "${HOME}/env/ai-memory-data:/data" \
       docker.io/akitaonrails/ai-memory:latest
     ```
     *Note : le conteneur Docker n'a pas besoin de monter les arborescences du dépôt ni `.ai-memory.toml`. Antigravity IDE transmet le contexte du projet (`workspace`/`project`) via les appels d'outils MCP.*
   - Sauvegardez avec `ai-memory --data-dir <data-dir> backup --to <archive-path>` (pour les déploiements Docker, utilisez la commande conteneur amont). `ai-memory uninstall --apply` supprime les intégrations client gérées mais ne supprime pas les données. Pour effacer la mémoire, arrêtez le service et supprimez son répertoire de données configuré uniquement après avoir confirmé la sauvegarde et la cible. Voir le [guide officiel d'installation/exploitation](https://github.com/akitaonrails/ai-memory/blob/main/docs/install.md).

#### Frontières des hôtes

- **Claude Code :** MCP/crochets amont ; ai-memory ne possède que ses entrées et préserve les crochets non liés. Le crochet de sécurité `PreToolUse` Claude existant reste distinct. La mémoire automatique par défaut de Claude Code est également distincte et machine-locale.
- **Codex CLI :** intégration amont `--client codex` / `--agent codex`. **Codex desktop :** utilise la surface de configuration Codex locale lorsqu'elle est prise en charge ; vérifiez la disponibilité crochet/MCP de l'application installée au lieu de supposer que chaque version CLI se comporte identiquement.
- **Antigravity CLI :** MCP/crochets amont `antigravity-cli`. Sous Windows, exécutez la configuration dans le même environnement qui lance l'agent.
- **Antigravity 2.0 et IDE :** l'assistant utilise l'installateur MCP amont d'Antigravity pour écrire le `~/.gemini/config/mcp_config.json` partagé et les instructions de projet gérées. L'amont ai-memory actuel n'a pas de cible dédiée de crochet de cycle de vie 2.0/IDE, c'est donc MCP uniquement et ne capture pas automatiquement les événements de session. La configuration MCP manuelle utilise `serverUrl=http://127.0.0.1:49374/mcp` ; voir la [doc MCP d'Antigravity](https://www.antigravity.google/docs/mcp).
- **ChatGPT web :** la configuration locale sans clé et en loopback n'a pas de connexion directe vers un chat web distant. Utilisez un transfert Markdown concis manuellement. L'accès MCP/écriture distant est hors du cadre de cette configuration locale gratuite.
- **Windows :** l'amont documente à la fois WSL2 et Windows natif. Installez et configurez ai-memory dans le même environnement qui lance chaque agent ; ne mélangez pas les chemins de crochets WSL et Windows. Consultez le [guide Windows](https://github.com/akitaonrails/ai-memory/blob/main/docs/windows.md) pour la prise en charge spécifique au client.

Le mode liste d'autorisation d'ai-memory ne garantit l'absence de capture pour les dépôts sans marqueur que lorsque le crochet natif installé applique la politique de capture. Ses exclusions de chemins ne expurgent pas le texte arbitraire du prompt ; n'incluez jamais de secrets dans les prompts. Voir la [référence du fichier marqueur](https://github.com/akitaonrails/ai-memory/blob/main/docs/marker-file.md).

### 5.2 Routeur de projet : `Project AGENTS.md`
- Modèle adaptable au niveau du dépôt.
- Ajoutez `-Initialize` / `--initialize` au déploiement pour générer un brouillon à partir de faits locaux vérifiables et une liste de contrôle des éléments en attente. `-DirectoryPath <chemin-relatif>` / `--directory <chemin-relatif>` initialise également un répertoire de module existant. Les scripts ne devinent ni l'objet du projet, ni les propriétaires, ni les frontières des modules. Les `AGENTS.md` existants sont préservés ; les copies de révision générées utilisent `AGENTS.generated.md`.
- Les scripts `package.json` détectés et les dépendances courantes de framework/stockage apparaissent comme suggestions de révision, pas comme faits vérifiés ; confirmez-les avant de vous fier à ces commandes ou frontières.
- Exécutez `-Check` / `--check` (optionnellement avec le paramètre de répertoire) pour analyser les champs de modèle non résolus avant d'adopter les règles générées ; la commande renvoie un statut de sortie non nul lorsqu'elle en trouve.
- Fournit des emplacements standard de commandes CLI (install, dev, build, test ciblé, lint, format, migration), des lignes rouges d'architecture, la **matrice de dispatching règles et compétences**, des règles de mémoire Markdown sélectives et des conseils d'intégration ai-memory optionnels.

---

### 5.3 Sous-règles modulaires : `.agents/rules/`
Chargées progressivement à la demande :
- **`token-discipline.md`** : restreint la lecture, la récupération et la parole ; impose l'index AST plutôt que le grep aveugle ;
- **`engineering-spec.md`** : SDD spec-first (périmètre In/Out), porte de vérification TDD (preuve physique requise) ;
- **`security-boundary.md`** : matrice de confirmation des 8 opérations à haut risque, zéro fuite d'identifiants, sécurité des gros fichiers ;
- **`git-workflow.md`** : isolation des branches protégées (zéro commit direct), autorisation obligatoire pour le push distant, format de commit `{type}: {description}`.

---

### 5.4 Correctif de micro-périmètre : `Directory AGENTS.md`
- Créé **uniquement si nécessaire** dans les packages de monorepo (`packages/*`) ou les sous-modules isolés.
- Générez-en un avec `-Initialize -DirectoryPath <chemin-relatif>` (PowerShell) ou `--initialize --directory <chemin-relatif>` (Bash) ; la cible doit déjà exister à l'intérieur de la racine du projet. Le chemin/nom du module est détecté, tandis que la responsabilité et les frontières restent des éléments de révision explicites.
- Définit le périmètre In/Out, les dépendances autorisées/interdites et les commandes de test locales ciblées (p. ex. `pytest tests/submodule -q`).

---
## 6. Flux de travail pratique à double voie : « l'ingénierie d'abord, la documentation ensuite »

### 1. Voie ingénierie logicielle (porte stricte)
- Portée : API, fonctionnalités, corrections de bugs, refactoring.
- Règles :
  - Lisez `PROJECT_CONTEXT.md` et `SESSION_STATE.md` au début de la tâche uniquement lorsqu'ils sont présents et pertinents, puis vérifiez les faits matériels ;
  - Travaillez toujours sur des branches temporaires (`feature/*`, `fix/*`) ;
  - Cycle TDD rouge-vert, vérifiez avec des exécutions de tests réelles ;
  - Suivez le modèle d'autorisation Git ;
  - **Mises à jour mémoire sélectives** : mettez à jour `SESSION_STATE.md` à la clôture significative ; ne mettez à jour `PROJECT_CONTEXT.md` que lorsque les faits durables du projet changent.

### 2. Voie documentation technique (dérivation légère)
- Portée : documentation Markdown, READMEs, spécifications d'API, rapports Word/PDF.
- Règles : **exemptée de l'exécution des suites de tests** ; tirez parti des compétences spécialisées (`docx`, `pdf`, `write-openspec-docs`) ; maintenez les standards GitHub Flavored Markdown.

---

## 7. Foire aux questions et bonnes pratiques (FAQ)

### Q1 : Pourquoi ne pas mettre toutes les commandes du projet dans `Global AGENTS.md` ?
> **Réponse** : les règles globales résident dans toutes les sessions de la machine. Ajouter des commandes spécifiques au projet crée une pollution de contexte inter-projets et gaspille les tokens de prompt.

### Q2 : Comment la mise à jour en ligne (`-Update`) protège-t-elle les configurations de projet personnalisées ?
> **Réponse** : le `AGENTS.md` de projet existant est préservé et un `AGENTS.template.md` est généré pour révision. `-Global` initialise les instructions globales Claude Code, Antigravity et Codex manquantes tout en préservant les fichiers existants. La combinaison `-Global -Update` effectue des sauvegardes horodatées et remplace ces fichiers globaux par le modèle actuel ; le `AGENTS.override.md` actif non vide de Codex est mis à jour à la place de `AGENTS.md`.

### Q3 : Comment plus de 40 compétences évitent-elles d'exploser la fenêtre de contexte ?
> **Réponse** : cela dépend de la manière dont l'hôte découvre et charge les compétences. Ne supposez pas de coûts de métadonnées fixes ni de remises de cache ; ne gardez activées que les compétences utiles et vérifiez le comportement dans l'hôte cible.

### Q4 : Qu'est-ce que la matrice de protection des 8 opérations à haut risque ?
> **Réponse** : définie dans `security-boundary.md`, exigeant une confirmation humaine avant :
> 1. Modifier les configurations de build (`package.json`, `CMakeLists.txt`, `.pro`, `Cargo.toml`) ;
> 2. Introduire de nouvelles dépendances tierces ;
> 3. Modifier les structures de données publiques globales (`public_struct.h`, `types.ts`) ;
> 4. Changer les singletons de dispatch centraux ou les interfaces de services publics ;
> 5. Modifier les protocoles de communication ou les contrats wire (`protofile/`) ;
> 6. Altérer la licence, la cryptographie ou le code d'authentification ;
> 7. Modifier `.gitignore` ou les pipelines CI/CD ;
> 8. Changements inter-modules à fort impact affectant des contrats partagés ou nécessitant une large coordination ; le seul nombre de fichiers n'est pas un déclencheur de risque.

### Q5 : Quand `PROJECT_CONTEXT.md` et `SESSION_STATE.md` doivent-ils être mis à jour ?
> À des frontières significatives de tâche/session, mettez à jour `SESSION_STATE.md` avec le travail accompli, les preuves de vérification réelles, les étapes restantes et les risques encore pertinents. Ne mettez à jour `PROJECT_CONTEXT.md` que lorsque l'architecture durable, les contraintes ou les décisions confirmées changent. Ne créez pas de mises à jour sans opération. Les deux fichiers résument la mémoire du projet ; ils ne prévalent pas sur les instructions actuelles de l'utilisateur, le code, la configuration ou les preuves reproductibles. Ne stockez jamais d'identifiants, de données personnelles brutes ni de journaux complets de conversations/outils.

---

## 8. Référence du guide d'utilisation pratique et panorama des compétences

Pour des tutoriels détaillés sur les commandes Slash (`/comet`, `/plan`, `/opsx`), CodeGraph, TDD et des parcours d'exécution complets de bout en bout, voir :
👉 [Tools Practical Usage and Skills Panorama Guide (English)](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [中文说明](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md)
