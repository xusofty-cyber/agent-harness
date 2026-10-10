# Contexte et faits durables du projet (PROJECT_CONTEXT.md)

> **Rôle & Objectif** : Ce document consigne les faits d'architecture fondamentaux et les contraintes durables pour `<PROJECT_NAME>`, servant de source unique de vérité (SSOT) lors du démarrage de session et des prises de décisions techniques des agents IA. À maintenir uniquement lors de modifications majeures d'architecture, de choix de stack ou de règles globales. L'état transitoire et les points d'arrêt de session doivent être consignés dans `SESSION_STATE.md`.

---

## 1. Présentation du projet et domaine fonctionnel

- **Nom du système** : `<PROJECT_NAME>`
- **Domaine métier** : <Description succincte du domaine et des problèmes résolus>
- **Matrice des fonctionnalités clés** :
  1. **<Module/Fonctionnalité clé 1>** : <Description des responsabilités et des flux>
  2. **<Module/Fonctionnalité clé 2>** : <Description des responsabilités et des flux>

---

## 2. Dépôt de code et stack technique

### 1. Environnement et branches
- **Dépôt Git** : `<GIT_REPO_URL>`
- **Branche principale / développement** : `main` / `develop`
- **Environnement d'exécution** : <Développement local / Docker / Kubernetes / Cloud production>

### 2. Choix techniques

| Couche / Domaine | Technologies & Versions | Notes & Bibliothèques clés |
|---|---|---|
| **Langage principal / Runtime** | <ex. TypeScript 5.x / Python 3.11 / Go 1.22> | <Langage principal et runtime> |
| **Frameworks et build** | <ex. Next.js / FastAPI / Spring Boot / Vite> | <Framework d'application et outils de build> |
| **Persistance et cache** | <ex. PostgreSQL 16 / Redis 7 / SQLite> | <Bases de données et couches de cache> |
| **API et messagerie** | <ex. gRPC / RESTful / Kafka / RabbitMQ> | <Protocoles de communication et bus d'événements> |

---

## 3. Architecture et conception structurelle

- **Patron d'architecture** : <ex. Monolithe en couches / Microservices DDD / Architecture modulaire>
- **Responsabilités des répertoires** :
  - `src/` : <Code source métier principal>
  - `tests/` : <Suites de tests unitaires et d'intégration>
  - `docs/` : <Dossiers de décisions d'architecture et spécifications techniques>

---

## 4. Contraintes techniques et lignes rouges globales

1. **Implémentation minimale et refus du gonflement (Échelle Ponytail)** :
   - Suivre l'échelle de décision : privilégier les outils existants et la bibliothèque standard avant d'introduire des abstractions spéculatives ou de nouvelles dépendances.
2. **Gestion unifiée des erreurs et anonymisation des logs** :
   - Utiliser des structures d'erreurs standardisées ; ne jamais étouffer silencieusement une erreur.
   - Interdiction formelle d'écrire en clair des clés d'API, tokens, mots de passe, clés privées ou chaînes de connexion dans les logs ou le code.
3. **Isolation Git et protection des branches** :
   - Aucun commit direct sur les branches protégées (`main`, `develop`, `master`) ; passer impérativement par une branche de fonctionnalité.
   - Interdiction d'utiliser `git add .` ou `git add -A` ; indexer uniquement des chemins explicites. Le push forcé (`git push --force`) est strictement interdit.

---

## 5. Registre des décisions d'architecture (ADR / Journal des décisions)

- **<AAAA-MM-JJ>** : [Initialisation de la mémoire du projet]
  - **Contexte** : Établir une norme de mémoire partagée inter-sessions et inter-outils.
  - **Décision** : Adopter `PROJECT_CONTEXT.md` pour les faits durables et `SESSION_STATE.md` pour les points d'arrêt.
  - **Impact** : Tous les agents chargent ce contexte au démarrage de session pour garantir la cohérence technique.
