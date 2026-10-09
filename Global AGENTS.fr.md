# Global AGENTS.md

## Champ d'application et priorité

- Ce document est un modèle global de standards d'ingénierie transversal aux projets. Le chargement automatique dépend de la configuration globale de chaque outil ; les scripts de déploiement ne configurent que les points d'entrée explicitement pris en charge.
- Ordre de priorité : Contraintes dures du système/sécurité > Instructions explicites actuelles de l'utilisateur > Règles au niveau du répertoire > Règles au niveau du projet > Ce défaut global.
- Ce document conserve un format Markdown générique. Les règles globales ne conservent que les lignes de conduite stables à long terme, les normes de limitation de contexte et la gouvernance collaborative.
- Il s'agit d'un modèle générique partageable ; il n'enregistre pas les préférences privées de l'utilisateur, les faits spécifiques au projet, les identifiants ou les informations personnelles. Seules les préférences expressément demandées par l'utilisateur peuvent être inscrites dans les fichiers globaux locaux de la machine contrôlés par celui-ci.

## Communication et langue (Filtre de sortie : Zéro superflu)

- Utiliser le français par défaut pour interagir avec l'utilisateur (ou s'aligner sur sa langue explicite) ; conserver en anglais le code, les commandes CLI, les clés de configuration, les noms d'API, les chemins, les traces d'erreur et les identifiants techniques.
- **Droit au but** : Éviter formellement les civilités, les clauses de non-responsabilité ou les paraphrases excessives. Donner d'abord les conclusions et impacts majeurs, suivis des diffs concrets, des preuves de vérification et des décisions en attente.
- **Style sobre** : Privilégier des paragraphes concis et cohérents ; n'utiliser des tableaux/listes que lorsque les étapes sont explicites ou pour comparer des éléments. Distinguer les faits vérifiés des déductions raisonnables.

## Principes d'exécution et réduction de l'entropie du code (Échelle Ponytail)

- **Implémentation minimale d'abord** : Suivre l'échelle de décision avant modification : comprendre d'abord le besoin et les chemins affectés, puis vérifier la réutilisation, la bibliothèque standard et les dépendances existantes. Viser l'implémentation minimale et propre répondant à toutes les exigences explicites, sans chercher à minimiser artificiellement le nombre de lignes, ni procéder à des refactorisations opportunistes ou des abstractions spéculatives.
- **Refus des pansements temporaires (No Laziness)** : Rechercher systématiquement la cause racine des bugs ; ne jamais écrire de hacks fragiles juste pour passer les tests en surface.
- **Authenticité et anti-hallucination** : Ne jamais inventer d'API, de paramètres, de versions, d'environnements, de configurations ou de résultats de tests inexistants. Déclarer explicitement toute information inconnue ou invérifiable.
- **Éviter les tentatives répétitives mécaniques** : En cas d'échecs consécutifs d'une même opération dans un environnement identique, marquer une pause pour corriger les hypothèses, isoler la cause racine ou changer d'approche. Les répétitions aveugles sans gain d'information sont proscrites.
- **Contraintes de protection** : Ne pas altérer silencieusement les comportements existants, la rétrocompatibilité ou les interfaces publiques. Les fichiers de règles peuvent être maintenus selon les instructions explicites de l'utilisateur ou l'évolution du projet ; expliquer l'impact et examiner les diffs avant toute modification.

## Ingénierie du contexte et économie de jetons (Filtres d'entrée et de lecture)

Le coût du contexte s'accumule avec les entrées au fil des longues sessions. Respecter les principes suivants pour éviter les lectures superflues et les sorties volumineuses :
1. **Contrôler la « lecture » (Recherche ciblée)** :
   - Éviter le grep aveugle sur tout le dépôt, les recherches en texte intégral sans limites ou la lecture continue de fichiers entiers ;
   - Utiliser le MCP CodeGraph pour l'exploration sémantique entre fichiers lorsqu'il est installé, configuré et disponible ; sinon, utiliser les définitions/signatures de symboles ou une recherche textuelle délimitée au répertoire pertinent. Ne pas présumer de l'existence de sous-commandes CLI de graphe.
2. **Contrôler la « capture » (Tronquer les logs d'outils)** :
   - Interdire formellement le déversement de centaines de lignes de journaux de build non filtrés, de traces de tests ou de `git status` dans le contexte ;
   - Exécuter les commandes avec des filtres dans la mesure du possible (ex. `--output-on-failure`, `grep -E "FAIL|Error"`) ; rediriger les sorties volumineuses vers des fichiers journaux locaux temporaires en ne renvoyant que les résumés critiques d'échec.
3. **Délégation aux sous-agents** :
   - Ne déléguer à des sous-agents que si les tâches peuvent être isolées de manière indépendante avec un gain évident d'exécution parallèle ; réaliser directement les tâches simples.

## Orchestration des tâches et rituels de session (Workflow & Vérification)

Charger le contexte selon les besoins de la tâche. Les tâches en plusieurs étapes doivent s'appuyer sur des plans structurés ou des journaux de tâches. La clôture de session doit distinguer les faits durables du projet des points d'arrêt actifs sans écritures répétitives :
1. **Démarrage de session (Session Start)** :
   - Lorsque les fichiers existent et concernent la tâche, consulter `PROJECT_CONTEXT.md` (faits durables du projet) et `SESSION_STATE.md` (point d'arrêt actuel) à la racine du projet ; vérifier les faits influençant cette tâche.
   - Consulter au besoin `tasks/todo.md`, `tasks/lessons.md` et la branche active ; ne pas charger indistinctement tout l'historique pour une tâche mineure.
2. **En cours (In-Progress)** :
   - Utiliser des plans structurés/suivis de tâches pour les opérations complexes ou de longue durée ; mettre à jour le plan dès que les hypothèses changent avant de continuer ;
   - **Boucle autonome de résolution de pannes** : À la réception de traces d'erreur, analyser les piles d'appels, identifier la cause racine, rédiger le correctif et effectuer les tests de validation de manière autonome ;
   - **Exigence stricte de preuves de vérification** : Ne jamais prétendre qu'une tâche est terminée sans présenter de preuves de vérification authentiques et reproductibles (sorties de tests, résultats d'exécution ou diffs validés).
3. **Clôture de session (Session Finish)** :
   - Mettre à jour `SESSION_STATE.md` aux frontières logiques de tâches ou de session : consigner les éléments terminés, les preuves concrètes de vérification, les étapes restantes et les risques d'environnement actifs ; nettoyer les états obsolètes. Ne pas créer de bruit inutile sans changement effectif.
   - Mettre à jour `PROJECT_CONTEXT.md` uniquement lorsque les faits à long terme évoluent (architecture, contraintes ou choix techniques confirmés). Il sert de résumé mémoriel et d'index de navigation, sans remplacer le code ou la documentation officielle ; mentionner les chemins sources et corriger rapidement les informations obsolètes.
   - Les enseignements réutilisables non encore consolidés en règles peuvent être consignés dans `tasks/lessons.md` ; éviter de dupliquer les mêmes faits.
   - **Frontières de confidentialité de la mémoire** : Interdiction stricte d'enregistrer des identifiants, clés privées, données personnelles brutes, journaux complets de conversation/outils ou informations personnelles superflues. Les dépôts partagés ne doivent pas contenir de préférences utilisateur privées.
- En cas de conflit, les instructions explicites actuelles de l'utilisateur prévalent ; les résumés mémoriels ne sauraient primer sur le code actif, les configurations ou les preuves reproductibles. Rectifier les éléments obsolètes lors de la phase de clôture.
- Les services de mémoire multi-outils ne sont activés qu'explicitement par projet ; les règles globales ne configurent ni n'activent la collecte automatique personnelle. Sans service de mémoire, continuer avec les conventions du projet et les fichiers Markdown.
- La collecte automatique doit être explicitement activée par l'opérateur avec validation du périmètre des données ; l'exclusion de chemins ne filtre pas le texte arbitre des invites. Interdiction d'inclure des identifiants et données privées dans les invites ou mémoires.

## Frontières d'autorisation et règles d'or de sécurité Git

- **Isolation stricte des branches protégées** :
  - Les commits directs sur `develop` / `master` / `main` / `release*` / `staging` sont formellement interdits ; tout changement doit être effectué sur une branche temporaire (`feature/*`, `fix/*`, `refactor/*`) ;
- **Autorisation formelle pour toute interaction distante** :
  - Une autorisation explicite est requise avant d'exécuter `git push`, de fusionner sur une branche protégée ou de supprimer des branches distantes partagées ; si la commande de l'utilisateur précise déjà l'action et la cible, cela vaut autorisation ;
- **Interdiction permanente des opérations destructrices** :
  - Interdiction absolue de `git push --force` (ou `-f` / `--force-with-lease`) ; interdiction absolue de `git rebase` sur les branches protégées ; privilégier `git revert -m 1` pour annuler des modifications ;
- **Garde-fou contre l'indexation accidentelle** :
  - Interdiction stricte de recourir aveuglément à `git add .` ou `git add -A` ; indexer uniquement via `git add <chemin-explicite>` pour éviter d'embarquer de gros fichiers, des fichiers temporaires, des artefacts de build ou des données sensibles ;
- **Classification des risques** : Traiter les opérations à fort impact ou irréversibles selon `.agents/rules/security-boundary.md`. Le simple fait de modifier plusieurs fichiers ne justifie pas une interruption ; évaluer les risques, expliquer les impacts et ne solliciter une confirmation que lorsque les règles ou l'utilisateur l'exigent explicitement ;
- **Zéro fuite d'identifiants** :
  - Interdiction absolue d'inscrire en clair ou de coder en dur des clés API, jetons, mots de passe, certificats, clés privées ou chaînes de connexion sensibles dans le code, les commentaires, l'historique des commits, la documentation ou les journaux d'exécution.
