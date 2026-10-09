# Agent Harness

> **Language / Langue**: [English](README.md) | [简体中文](README_zh.md) | [繁體中文](README.zh-tw.md) | **Français** | [Deutsch](README.de.md)

> **Modèles réutilisables de règles de programmation IA, crochets de sécurité Claude Code et scripts de déploiement multi-outils**

Ce dépôt fournit des modèles de règles aux niveaux global, projet et répertoire, des crochets PreToolUse pour Claude Code, des bibliothèques de compétences (skills) et des scripts de déploiement pour Windows/Linux/macOS. Le comportement de chargement et les fonctionnalités varient selon l'outil hôte. Les crochets sont des mécanismes côté client et ne constituent pas des barrières de sécurité côté système d'exploitation ou serveur.

---

## Fonctionnalités clés

1. **Architecture progressive à trois niveaux AGENTS.md** :
   - **Niveau global ([`Global AGENTS.fr.md`](Global%20AGENTS.fr.md))** : Constitution d'ingénierie transverse, standard de communication concise, règles d'autorisation Git et gouvernance de session.
   - **Niveau projet ([`Project AGENTS.fr.md`](Project%20AGENTS.fr.md))** : Modèle adaptable pour commandes CLI, stack technique, garde-fous d'architecture et matrice de compétences.
   - **Niveau répertoire ([`Directory AGENTS.fr.md`](Directory%20AGENTS.fr.md))** : Patch micromodule pour sous-paquets de monorepos ou sous-modules isolés (In/Out scope, isolation des dépendances et tests rapides).
   - **Sous-règles modulaires ([`.agents/rules/`](.agents/rules/))** : Règles consultées dynamiquement (`token-discipline.md`, `engineering-spec.md`, `security-boundary.md`, `git-workflow.md`).

2. **Crochets de sécurité Claude Code ([`.claude/settings.json`](.claude/settings.json) + [`.claude/hooks/`](.claude/hooks/))** :
   - Exécutés uniquement lors des appels d'outils correspondants dans Claude Code ;
   - Scripts de garde Node.js traitant les entrées JSON sur stdin pour un blocage strict (`exit 2`) ;
   - Blocages permanents : commit direct sur branche protégée (`develop`/`master`/`main`/`release*`), `git push --force`, suppression de branche distante protégée, rebase sur branche protégée.

3. **42 compétences réutilisables ([`.agents/skills/`](.agents/skills/))** :
   - **Guide Comet** : point d'entrée pour les flux Comet ;
   - **Documentation vivante & Traçabilité** : `living-documentation` (modèle à 4 niveaux, traçabilité bidirectionnelle code-doc, seuils d'impact L0/L1/L2) ;
   - **Spec-Driven Development (SDD)** : suite de 16 compétences `openspec` ;
   - **Test-Driven Development (TDD)** : suite de 15 compétences `superpowers` ;
   - **Orientation implémentation** : `ponytail` (échelle de solution minimale) et `codegraph` (graphe de code via MCP) ;
   - **Sortie et communication** : `rtk` (troncature et limitation de tokens) et `caveman` (mode ultra-concis) ;
   - **Revue avant décision & mémoire partagée** : `option-review` et `cross-tool-memory` ;
   - **Documents professionnels** : compétences `docx` et `pdf`.

4. **Déploiement en un clic & synchronisation (`deploy-agents`)** :
   - Scripts automatisés pour PowerShell ([`deploy-agents.ps1`](deploy-agents.ps1)) et Bash ([`deploy-agents.sh`](deploy-agents.sh)) avec support multilingue (`--lang` / `-Language`) ;
   - Génération de `AGENTS.md`, ponts vers `CLAUDE.md` et Copilot, et crochets Claude Code ;
   - Sauvegarde préalable avec horodatage lors de `--global --update` ;
   - Détection et invite d'installation pour les CLI optionnels (CodeGraph, RTK, Open Code Review, Comet).

5. **Mémoire partagée inter-outils optionnelle (`ai-memory`)** :
   - Approche locale sans frais d'API, sans LLM obligatoire ;
   - Activation explicite via `.ai-memory.toml` et crochets amont en mode liste blanche.

### Périmètre de prise en charge

| Outil | Configuration fournie | Statut |
|---|---|---|
| Claude Code | Pont `CLAUDE.md`, liens `.claude/skills/`, crochets `.claude/settings.json` | Configuré par script ; crochets actifs côté client |
| Antigravity 2.0 / CLI / IDE | Règles/compétences du projet ; `--global` écrit `~/.gemini/AGENTS.md` et le pointeur `GEMINI.md` | Prise en charge des deux noms globaux |
| Codex | Global `$CODEX_HOME/AGENTS.md`, `AGENTS.md` du projet et `.agents/skills/` | `-Global` initialise le fichier global ; `-Global -Update` sauvegarde et remplace |
| ai-memory | MCP/crochets optionnels pour Claude Code, Codex CLI, Antigravity CLI ; MCP seul pour IDE | Activation explicite par projet |
| GitHub Copilot | Pont `.github/copilot-instructions.md` | Configuré par script |
| Zed | Fichier `AGENTS.md` | Fichiers réutilisables uniquement |
| Pi / OpenCode | Aucun point d'entrée spécifique | Non adapté formellement |

---

## Structure du répertoire

```text
agent-harness/
├── .agents/
│   ├── rules/                       # Sous-règles d'ingénierie modulaires
│   └── skills/                      # 42 compétences d'ingénierie
├── .claude/
│   ├── settings.json                # Configuration PreToolUse Claude Code
│   └── hooks/                       # Scripts de garde et interception
├── Global AGENTS.md                 # Modèle de règles globales
├── Project AGENTS.md                # Modèle racine du projet & routeur
├── Directory AGENTS.md              # Patch de frontière pour sous-modules
├── Multi-Tool Deployment and Configuration Guide.fr.md # Guide de déploiement (Français)
├── Multi-Tool Deployment and Configuration Guide.md    # Guide de déploiement (Anglais)
├── Tools Practical Usage and Skills Panorama Guide.fr.md # Panorama des outils (Français)
├── Tools Practical Usage and Skills Panorama Guide.md    # Panorama des outils (Anglais)
├── deploy-agents.ps1                # Script Windows PowerShell
├── deploy-agents.sh                 # Script Linux / macOS Bash
├── setup-ai-memory.ps1              # Script de configuration ai-memory (Windows)
├── setup-ai-memory.sh               # Script de configuration ai-memory (Unix)
├── .ai-memory.toml.example          # Exemple de marqueur d'activation locale
├── skills-lock.json                 # Métadonnées d'intégrité et sources
├── README.md                        # Présentation (English)
└── README_zh.md                     # Présentation (Chinois simplifié)
```

---

## Démarrage rapide

### 1. Déployer les règles et compétences sur un projet

- **Windows (PowerShell)** :
  ```powershell
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Global -Language fr -Initialize -DirectoryPath "packages/core"
  .\deploy-agents.ps1 -ProjectPath "D:\Projects\my-project" -Check -DirectoryPath "packages/core"
  ```

- **Linux / macOS (Bash)** :
  ```bash
  chmod +x ./deploy-agents.sh
  ./deploy-agents.sh /path/to/my-project --global --lang fr --initialize --directory packages/core
  ./deploy-agents.sh /path/to/my-project --check --directory packages/core
  ```

### 2. Mémoire partagée optionnelle (ai-memory)

```bash
cargo install ai-memory
cp .ai-memory.toml.example .ai-memory.toml
sed -i 's/replace-with-workspace-name/default/g; s/replace-with-project-name/agent-harness/g' .ai-memory.toml
./setup-ai-memory.sh antigravity-ide
ai-memory serve --transport http
```

### 3. Mise à jour en ligne

```bash
./deploy-agents.sh . --update
```

---

## Index documentaire

- 📖 **Déploiement & Configuration** :
  - [Français](Multi-Tool%20Deployment%20and%20Configuration%20Guide.fr.md) | [English](Multi-Tool%20Deployment%20and%20Configuration%20Guide.md) | [简体中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh.md) | [繁體中文](Multi-Tool%20Deployment%20and%20Configuration%20Guide.zh-tw.md) | [Deutsch](Multi-Tool%20Deployment%20and%20Configuration%20Guide.de.md)
- 📖 **Usage pratique & Panorama des compétences** :
  - [Français](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.fr.md) | [English](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.md) | [简体中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh.md) | [繁體中文](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.zh-tw.md) | [Deutsch](Tools%20Practical%20Usage%20and%20Skills%20Panorama%20Guide.de.md)
- 📜 **Architecture des règles à trois niveaux** :
  - **Règles globales** : [`Global AGENTS.fr.md`](Global%20AGENTS.fr.md) (Français) | [`English`](Global%20AGENTS.en.md) | [`简体中文`](Global%20AGENTS.md) | [`繁體中文`](Global%20AGENTS.zh-tw.md) | [`Deutsch`](Global%20AGENTS.de.md)
  - **Règles de projet** : [`Project AGENTS.fr.md`](Project%20AGENTS.fr.md) (Français) | [`English`](Project%20AGENTS.en.md) | [`简体中文`](Project%20AGENTS.md) | [`繁體中文`](Project%20AGENTS.zh-tw.md) | [`Deutsch`](Project%20AGENTS.de.md)
  - **Règles de répertoire** : [`Directory AGENTS.fr.md`](Directory%20AGENTS.fr.md) (Français) | [`English`](Directory%20AGENTS.en.md) | [`简体中文`](Directory%20AGENTS.md) | [`繁體中文`](Directory%20AGENTS.zh-tw.md) | [`Deutsch`](Directory%20AGENTS.de.md)

---

## Licence

Ce projet est distribué sous licence MIT. Les compétences tierces intégrées conservent leurs licences d'origine respectives.
