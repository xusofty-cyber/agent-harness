# Guide d'utilisation des compétences (Skills)

> **Language / 语言**: [English](Skills%20Usage%20Guide.md) | [简体中文](Skills%20Usage%20Guide.zh.md) | [繁體中文](Skills%20Usage%20Guide.zh-tw.md) | **Français** | [Deutsch](Skills%20Usage%20Guide.de.md)

Fonctionnement pratique des 43 compétences intégrées : lesquelles se déclenchent automatiquement, lesquelles nécessitent une invocation explicite et quand les utiliser.

## Mécanismes de déclenchement des compétences

Claude Code détermine le chargement d'une compétence de deux manières :

| Mode | Méthode | Exemple |
|---|---|---|
| **Auto** | Claude lit la `description` de la compétence et l'invoque lorsque votre demande correspond | Vous dites "corrige ce bug" → `systematic-debugging` se charge automatiquement |
| **Explicite** | Vous tapez la commande slash ou nommez directement la compétence | Vous tapez `/comet` ou dites "utilise comet pour cette tâche" |
| **Hybride** | Les deux fonctionnent — auto-déclenchement selon le contexte ou invocation directe | Vous dites "revue de cette PR" → `open-code-review` se charge ; ou tapez `/open-code-review` |

**Point clé :** Le déclenchement automatique dépend du champ `description` dans le fichier `SKILL.md` de chaque compétence.
Si Claude ne charge pas une compétence comme prévu, nommez-la simplement de manière explicite.

## Catalogue des compétences par catégorie

> **Domaines de skills** (espaces de noms pour chargement ciblé) : chaque skill appartient à un domaine,
> enregistré dans `skills-lock.json` et vérifié par la CI. Pour les agents à besoin partiel, charger par domaine plutôt que le catalogue complet.
>
> | Domaine | Skills | Objet |
> |---|---|---|
> | `openspec` | 17 | Famille du workflow OpenSpec |
> | `superpowers` | 16 | Famille méthodologique obra/superpowers |
> | `local` | 5 | Créés dans le repo (engineering-docs, living-documentation, open-code-review, option-review, cross-tool-memory) |
> | `document` | 2 | Traitement documentaire (docx, pdf) |
> | `integration` | 2 | Intégrations d'outils externes (comet, codegraph) |
> | `utility` | 3 | Utilitaires à usage unique (caveman, ponytail, rtk) |
>
> **Note sur les comptes** : `skills-lock.json` contient 45 entrées mais ce catalogue liste 43 skills.
> Les 2 entrées supplémentaires (`openspec`, `superpowers`) sont des méta-entrées des dépôts sources —
> des marqueurs de provenance, pas des skills installables.

### 1. Contrôle des flux et processus

| Compétence | Déclencheur | Commande | Description | Quand l'utiliser |
|---|---|---|---|---|
| `comet` | Explicite | `/comet` | Machine à états de flux de travail versionnée (phases, gardes, archives). Nécessite le CLI Comet installé + `.comet/config.yaml` dans le projet. | Lorsque le projet utilise Comet pour une exécution par étapes. Exécutez `/comet init` une fois par projet, puis `/comet` pour entrer en mode flux. Sans le CLI, la compétence explique les limites et revient au flux normal. |
| `openspec-new-change` | Auto | — | Démarre une nouvelle modification OpenSpec (développement piloté par les spécifications). | Au début d'une fonctionnalité/correctif nécessitant des artefacts de spécification préalables. Dites "use openspec" ou décrivez la fonctionnalité. |
| `openspec-propose` | Auto | — | Génère tous les artefacts OpenSpec en une seule étape. | Pour obtenir une ébauche rapide de spécification sans le cycle complet d'exploration. |
| `openspec-explore` | Hybride | — | Mode partenaire de réflexion pour explorer les idées avant de spécifier. | Lorsque les exigences sont floues. Dites "explorons cela avec openspec". |
| `openspec-apply-change` | Auto | — | Implémente les tâches d'une modification OpenSpec existante. | Une fois la spécification validée : "implement the openspec change". |
| `openspec-continue-change` | Auto | — | Crée l'artefact suivant dans une modification en cours. | Lors de la reprise du travail OpenSpec : "continue the openspec change". |
| `openspec-update-change` | Hybride | — | Révise les artefacts OpenSpec existants. | Lorsqu'une révision de spécification est nécessaire en cours d'implémentation. |
| `openspec-verify-change` | Auto | — | Valide la conformité de l'implémentation avec les spécifications. | Avant de finaliser : "verify against the openspec". |
| `openspec-sync-specs` | Auto | — | Synchronise les spécifications delta vers les spécifications principales. | Une fois la modification terminée et fusionnée. |
| `openspec-archive-change` | Auto | — | Archive une modification terminée. | Nettoyage final après fusion. |
| `openspec-bulk-archive-change` | Auto | — | Archive plusieurs modifications terminées à la fois. | Nettoyage par lots. |
| `openspec-ff-change` | Auto | — | Avance rapide pour contourner la création d'artefacts. | Pour sauter le cérémonial et passer directement à l'implémentation. |
| `openspec-onboard` | Hybride | — | Intégration guidée au flux de travail OpenSpec. | Première utilisation d'OpenSpec : "onboard me to openspec". |
| `draft-openspec-docs` | Hybride | — | Mode collaboratif de rédaction pour la documentation OpenSpec. | Lors de la rédaction de pages de documentation OpenSpec. |
| `write-openspec-docs` | Hybride | — | Mode rédaction OpenSpec avec guide de style. | Lors de l'écriture de documentation utilisateur OpenSpec. |
| `verify-openspec-docs` | Hybride | — | Vérifie la documentation OpenSpec avec un contexte frais. | Lors de la validation des affirmations de la documentation OpenSpec. |
| `release-openspec` | Hybride | — | Audite le travail fusionné pour les versions OpenSpec. | Lors d'une version OpenSpec. |
| `living-documentation` | Hybride | — | Maintient spécifications/architecture/références/guides avec traçabilité. | En continu. S'active pour les tâches de documentation ; dites "update living docs" pour forcer. |

### 2. Qualité du code et revue

| Compétence | Déclencheur | Commande | Description | Quand l'utiliser |
|---|---|---|---|---|
| `requesting-code-review` | Auto | — | Détermine **quand** une revue est nécessaire (porte de temporisation). | Se déclenche automatiquement lors de l'achèvement d'un travail important. |
| `open-code-review` | Auto | — | Méthode déterministe de revue (sélection de fichiers, règles, observations par ligne). | Se déclenche automatiquement sur diffs/PRs. Explicite : "utilise open-code-review pour ce diff". |
| `receiving-code-review` | Auto | — | Traite les retours de revue entrants avant implémentation. | Lors du collage de commentaires de revue : triage automatique. |
| `systematic-debugging` | Auto | — | Débogage structuré : reproduire → isoler → hypothèse → corriger → vérifier. | Tout bug, échec de test ou comportement inattendu. Se déclenche avant de proposer un correctif. |
| `test-driven-development` | Auto | — | Impose le cycle rouge-vert-refactorisation. | Lors de l'implémentation de fonctionnalités/bugs. Écrire les tests d'abord. |
| `verification-before-completion` | Auto | — | Liste de contrôle avant achèvement : tests, assertions et preuves. | Avant de déclarer "c'est fait" — impose des preuves concrètes. |

### 3. Planification et conception

| Compétence | Déclencheur | Commande | Description | Quand l'utiliser |
|---|---|---|---|---|
| `brainstorming` | Auto | — | Explore l'intention, les exigences et la conception avant l'implémentation. **Indispensable avant tout travail créatif.** | Toute nouvelle fonctionnalité, composant ou changement de comportement. Si Claude code directement, dites "brainstorm d'abord". |
| `writing-plans` | Auto | — | Crée des plans d'implémentation structurés à partir de spécifications. | Tâches en plusieurs étapes. Se déclenche avec des exigences sans plan. |
| `executing-plans` | Auto | — | Exécute un plan en tant qu'implémenteur. | Après approbation du plan : "execute the plan". |
| `option-review` | Auto | — | Compare 2+ approches viables avec une matrice de décision. | En cas d'hésitation : "devrais-je choisir A ou B ?". |
| `dispatching-parallel-agents` | Auto | — | Répartit les tâches indépendantes sur des sous-agents parallèles. | 2+ tâches indépendantes. Dites "fais cela en parallèle". |
| `subagent-driven-development` | Auto | — | Orchestre l'implémentation via des sous-agents. | Grands plans avec des composants indépendants. |
| `using-git-worktrees` | Auto | — | Isole le travail de fonctionnalité dans des worktrees git. | Avant de démarrer un travail nécessitant une isolation de la branche courante. |
| `finishing-a-development-branch` | Auto | — | Décide de la stratégie d'intégration (merge/rebase/squash). | Lorsque l'implémentation est terminée et que les tests passent. |

### 4. Mémoire et contexte

| Compétence | Déclencheur | Commande | Description | Quand l'utiliser |
|---|---|---|---|---|
| `cross-tool-memory` | Auto | — | Charge/enregistre la mémoire durable du projet entre outils. Repli sur `PROJECT_CONTEXT.md` / `SESSION_STATE.md` si ai-memory MCP est absent. | Lors de la reprise d'un travail. Charge automatiquement le contexte ; dites explicitement "mémorise ceci" pour enregistrer. Voir [Configuration de la mémoire de projet](#configuration-de-la-mémoire-de-projet) ci-dessous. |
| `using-superpowers` | Auto | — | Établit le protocole de découverte des compétences au début de la session. | Se déclenche automatiquement au début. Assure que Claude vérifie les compétences disponibles avant de répondre. |

### 5. Outils de développement

| Compétence | Déclencheur | Commande | Description | Quand l'utiliser |
|---|---|---|---|---|
| `codegraph` | Auto | — | Exploration sémantique du code via CodeGraph MCP. Nécessite le CLI CodeGraph installé. | "Où X est-il utilisé ?" / "affiche les appelants de Y". Repli sur grep si le CLI manque. |
| `rtk` | Auto | — | Rust Token Killer : réécrit les sorties CLI verbeuses en format concis. Nécessite le CLI RTK. | Compresse automatiquement les sorties bruyantes. Dites "disable rtk" pour la sortie brute. |
| `docx` | Hybride | — | Crée, lit et modifie des documents Word. | "Génère un rapport .docx" ou "lis ce fichier Word". |
| `pdf` | Hybride | — | Lit et extrait du texte/tableaux de fichiers PDF. | "Résume ce PDF" ou "extrais les tableaux...". |
| `caveman` | Hybride | — | Mode de sortie ultra-compressé (économise les tokens). | "Sois concis" / "caveman mode". Niveaux : lite, full, ultra. |
| `ponytail` | Hybride | — | Impose la solution fonctionnelle la plus simple (anti-suringénierie). | "Reste simple" / lorsque Claude sur-ingénie. |

### 6. Méta-compétences

| Compétence | Déclencheur | Commande | Description | Quand l'utiliser |
|---|---|---|---|---|
| `writing-skills` | Auto | — | Guide la création, l'édition et la vérification de compétences. | Lors de la création ou modification de compétences dans `.agents/skills/`. |
| `diagnosing-superpowers` | Auto | — | Diagnostique les anomalies dans le flux de travail superpowers. | Lorsque Claude ignore les plans ou répète des tâches. Dites "diagnostique ce qui ne va pas". |

### 7. Documentation d'ingénierie

| Compétence | Déclencheur | Commande | Description | Quand l'utiliser |
|---|---|---|---|---|
| `engineering-docs` | Hybride | — | 15 modèles bilingues couvrant 31 types de documents de R&D (proposition → exigences → conception → test → livraison). Inclut des spécifications de rendu pour garantir un format uniforme. | Pour rédiger tout document officiel de R&D. Dites "rédige un PRD" / "rédige la conception générale" pour activer le bon modèle. |

## Configuration de la mémoire de projet

### `PROJECT_CONTEXT.md` et `SESSION_STATE.md`

Ce mécanisme constitue la solution de repli basée sur des fichiers lorsque le service MCP ai-memory est indisponible.
La compétence `cross-tool-memory` les lit automatiquement. Lors de l'exécution de `deploy-agents.sh / .ps1` ou `run-pipeline.sh / .ps1` (et `pipeline.sh / .ps1`), s'ils sont absents du projet cible, les scripts **les initialisent automatiquement à partir de modèles**. Vous pouvez également les initialiser ou les personnaliser manuellement via les modèles ci-dessous.

**Quand les créer :**
- `PROJECT_CONTEXT.md` : Une fois par projet, quand l'architecture est stable. Mettre à jour uniquement lorsque les faits durables changent (stack, contraintes, décisions clés).
- `SESSION_STATE.md` : À la fin de chaque session de travail importante ou lors d'un passage de relais. Mettre à jour avec le travail achevé, les preuves de vérification et les étapes suivantes.

**Comment créer les versions initiales :**

Demandez directement à Claude :
```text
Crée PROJECT_CONTEXT.md pour ce projet selon le format de la compétence cross-tool-memory.
```

Ou copiez ces modèles :

#### Modèle `PROJECT_CONTEXT.md`

```markdown
# PROJECT_CONTEXT.md

> Faits durables du projet. Mettre à jour uniquement en cas de changement d'architecture, de contraintes ou de décisions confirmées.
> Ne placez pas l'état spécifique de session ici — cela va dans SESSION_STATE.md.

## Stack technique
- Langage / framework :
- Build :
- Test :

## Architecture
- (Composants clés et leurs responsabilités)

## Contraintes
- (Contraintes techniques ou de politique non négociables)

## Décisions clés
- AAAA-MM-JJ : (Décision et justification)
```

#### Modèle `SESSION_STATE.md`

```markdown
# SESSION_STATE.md

> Point de contrôle courant. Mettre à jour aux frontières significatives de tâches.
> Supprimer les éléments obsolètes ; conserver un format facile à parcourir.

## Dernière mise à jour
- AAAA-MM-JJ : (bref résumé de session)

## Terminé
- (Ce qui a été fait, avec preuves de vérification)

## En cours
- (Ce qui est actuellement en cours de traitement)

## Prochaines étapes
- (Ce qui reste à faire, par ordre de priorité)

## Risques ouverts / Questions
- (Problèmes non résolus ou décisions nécessaires)
```

**Emplacement :** Racine du projet. La compétence `cross-tool-memory` les recherche à cet endroit.

**Portée de répertoire :** Ne créez pas de fichiers de mémoire par sous-répertoire. Conservez les faits du projet dans les fichiers racine ; les fichiers `AGENTS.md` de sous-répertoire contiennent uniquement des limites et contraintes locales.
