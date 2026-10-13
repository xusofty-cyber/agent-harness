# Directory AGENTS.md

> **Notice d'utilisation** : Ce document est un correctif micromodule créé à la demande, utilisé **uniquement** dans les sous-paquets de monorepos (`packages/*`), les répertoires frontend/backend indépendants ou les sous-modules dotés de frontières d'isolation strictes. Les sous-répertoires classiques héritent par défaut des règles de la racine ; ne jamais créer ce fichier de manière inconsidérée.

## Mission du module

- **Nom du module** : `<MODULE_NAME>`
- **Chemin du répertoire** : `<DIRECTORY_PATH>`
- **Responsabilité centrale** : `<RESPONSIBILITY>` (une phrase définissant le rôle principal de ce répertoire)

## Définition des frontières (In / Out Scope)

- **Dans le périmètre (In-Scope)** :
  - `<IN_SCOPE_ITEM_1>`
  - `<IN_SCOPE_ITEM_2>`
- **Hors périmètre (Out-of-Scope)** :
  - `<OUT_OF_SCOPE_ITEM_1>` (si un besoin touche ce point, le confier au module dédié ou à la racine)
  - `<OUT_OF_SCOPE_ITEM_2>`

## Contraintes de dépendances et d'isolation

- **Dépendances autorisées** : `<ALLOWED_DEPENDENCIES>` uniquement (socle commun ou contrats publics).
- **Dépendances interdites** : Référencer directement `<FORBIDDEN_DEPENDENCIES>` est strictement proscrit (pour éviter les ruptures de couches ou les dépendances cycliques).
- **Exposition externe** : Toutes les méthodes et types publics doivent être exportés via un point d'entrée unique (ex. `index.ts` / `__init__.py` / `mod.rs` / `include/`) ; les imports directs d'implémentations privées internes sont interdits.

## Commandes de vérification locale ultra-rapide (Évite l'inflation de tokens)

> Après modification de ce module, exécuter en priorité les vérifications légères ciblées ; étendre la portée uniquement si les changements affectent le comportement inter-modules.

```bash
# Tests unitaires et vérification rapide du module (avec flags de sortie concise)
<LOCAL_TEST_COMMAND>           # ex. : npm test -- packages/core --reporter=dot / pytest tests/core -q

# Vérification Lint du module
<LOCAL_LINT_COMMAND>           # ex. : npm run lint --filter core
```

## Frontières de la mémoire locale

- Consigner uniquement les limites, dépendances, commandes et règles de maintenance propres à ce répertoire et toujours valides ; le reste hérite du projet racine.
- Ne pas créer de fichier `MEMORY.md` local ni copier l'historique du projet par défaut. Les faits durables vont dans `PROJECT_CONTEXT.md` à la racine ; les points d'étape courants dans `SESSION_STATE.md`.
- Lors de la modification des règles de ce répertoire, vérifier leur conformité avec le code actif ; supprimer ou corriger les contraintes obsolètes.
- Ne jamais stocker d'identifiants, clés privées, données personnelles brutes ou journaux d'outils complets dans les mémoires locales.
- Tout service de mémoire multi-outils utilise l'espace de noms du projet racine ; les règles normatives de ce répertoire résident uniquement ici.

## Maintenance sécurisée des très grands fichiers / fichiers patrimoniaux (> 100 Ko)

- **Localisation précise** : Pour les fichiers volumineux, cibler exactement les fonctions et plages de lignes ; interdiction de réécrire ou reformater globalement le fichier ;
- **Cohérence de style prioritaire** : Le nouveau code doit respecter strictement le style existant du fichier (nommage, indentation, gestion des erreurs) ;
- **Zéro exposition involontaire** : Les fonctions d'aide privées et structures internes ne doivent jamais être intégrées directement aux en-têtes publics.

## Liste de contrôle des modifications

- [ ] Les modifications restent strictement dans le périmètre du module (In-Scope), sans dépendance interdite.
- [ ] Retouches ciblées et localisées pour les fichiers volumineux, dans le respect du style existant.
- [ ] Nouvelles capacités exposées exclusivement via le point d'entrée public du module.
- [ ] Vérifications exécutées proportionnellement aux risques encourus ; motifs des éléments non exécutés consignés.
