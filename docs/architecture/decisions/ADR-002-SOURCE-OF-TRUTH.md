# ADR-002 — Sources de vérité de la plateforme Sigma

- Statut : Accepté
- Date : 2026-07-14
- Projet : Mister SIGMA
- Version de départ : v1.1.0
- Dépendance : ADR-001

## Contexte

Mister SIGMA doit fonctionner sur plusieurs machines et pour plusieurs
utilisateurs sans créer de doublons, de conflits ou de copies divergentes.

Une même donnée ne doit pas être administrée simultanément par plusieurs
fichiers ou services concurrents.

## Principe fondamental

Chaque catégorie de données possède une seule source de vérité officielle.

Les autres systèmes peuvent conserver :

- une copie locale ;
- un cache ;
- une vue ;
- un export ;
- une projection ;
- une sauvegarde.

Ils ne deviennent pas pour autant propriétaires de la donnée.

## Sources de vérité transitoires

### Git

Git est la source de vérité pour :

- code source ;
- tests ;
- documentation ;
- décisions d’architecture ;
- modèles de configuration ;
- schémas de données ;
- scripts de migration ;
- fichiers de release ;
- fichiers de déploiement.

Git ne doit pas contenir :

- identités locales de machines ;
- chemins absolus locaux ;
- journaux ;
- caches ;
- états de synchronisation ;
- secrets.

### Configuration globale

Le fichier partagé `sigma-config.json` doit contenir uniquement des valeurs
communes et non sensibles, par exemple :

- project ;
- organization_id ;
- workspace_id par défaut ;
- environnement logique ;
- URL publique du registre ;
- configuration fonctionnelle commune.

Il ne doit plus contenir :

- machine_id ;
- node_id ;
- hostname ;
- chemin local ;
- last_sync ;
- secrets ;
- identité personnelle générée localement.

### Configuration locale

Le fichier suivant devient la source de vérité locale de l’installation :

`.sigma-workspace/configs/local.json`

Il contiendra notamment :

- installation_id ;
- machine_id ;
- node_id ;
- hostname ;
- device_type ;
- operating_system ;
- workspace_path ;
- local_profile ;
- last_sync ;
- local_environment.

Ce fichier est ignoré par Git.

### Secrets locaux

Les secrets doivent être chargés depuis un stockage local non versionné :

- variables d’environnement ;
- fichier `.env` ignoré ;
- gestionnaire de secrets du système ;
- coffre de secrets futur.

### JSON Sigma

Pendant la phase transitoire, les fichiers `sigma-db/*.json` servent de base
de développement locale.

Ils ne constituent pas encore une base multi-utilisateurs transactionnelle.

### PostgreSQL

PostgreSQL deviendra la source de vérité centrale pour :

- organisations ;
- utilisateurs ;
- appartenances ;
- équipes ;
- rôles ;
- permissions ;
- machines déclarées ;
- nœuds enregistrés ;
- workspaces ;
- projets ;
- actifs du registre ;
- synchronisations ;
- événements métier ;
- audits.

### API Sigma

L’API Sigma sera l’unique interface d’écriture distante vers PostgreSQL.

Les clients ne devront pas modifier directement la base centrale.

### Notion

Notion sera utilisé pour :

- documentation ;
- tableaux de pilotage ;
- vues de gestion ;
- procédures ;
- décisions ;
- formation.

Notion ne sera pas la source de vérité transactionnelle des identités,
permissions, machines ou synchronisations.

### MQTT

MQTT sera utilisé pour :

- événements ;
- états temporaires ;
- commandes ;
- télémétrie ;
- présence des nœuds.

MQTT ne sera pas une base de données permanente.

### GitHub

GitHub héberge le dépôt Git, les branches, les tags, les releases et les
workflows CI/CD.

GitHub ne stocke pas les états locaux d’une installation Sigma.

## Matrice de propriété

| Donnée | Source de vérité | Copie autorisée |
|---|---|---|
| Code | Git | Machines de développement |
| Documentation versionnée | Git | Notion |
| Organisation | PostgreSQL | Cache local, Notion |
| Utilisateur | PostgreSQL | Cache local |
| Rôle et permission | PostgreSQL | Cache local |
| Machine | PostgreSQL après enrôlement | local.json |
| Installation | local.json puis PostgreSQL | Cache serveur |
| Node | PostgreSQL | local.json, MQTT |
| Workspace partagé | PostgreSQL | Cache local |
| Chemin local du workspace | local.json | Aucun partage |
| Projet | PostgreSQL | Git, cache local |
| Secret | Coffre local ou serveur | Mémoire temporaire |
| Télémétrie | MQTT | PostgreSQL selon politique |
| Release | Git et GitHub | PostgreSQL, Notion |
| Dernière synchronisation locale | local.json | PostgreSQL |
| Journal local | Workspace local | Agrégateur futur |

## Règles de synchronisation

1. Une donnée possède un propriétaire unique.
2. Une copie locale doit indiquer sa version ou sa date de synchronisation.
3. Les écritures distantes passent par l’API.
4. Les conflits ne sont jamais résolus silencieusement.
5. Les identités ne sont jamais régénérées automatiquement si elles existent.
6. Une machine peut héberger plusieurs installations.
7. Un utilisateur conserve le même user_id sur toutes ses machines.
8. Un node_id désigne une instance Sigma, pas une personne.
9. Un hostname est descriptif et non identifiant.
10. Les suppressions doivent être auditées.

## Situation actuelle à migrer

Les représentations suivantes sont temporaires et doivent être rationalisées :

- `sigma-config.json` ;
- `.sigma-workspace/configs/config.json` ;
- `sigma-core/registry/registry.json` ;
- `sigma-db/nodes.json` ;
- `sigma-db/registry.json`.

Aucune suppression ne sera réalisée avant :

- sauvegarde ;
- définition du schéma cible ;
- script de migration ;
- tests automatisés ;
- validation du résultat.

## Première migration autorisée

La première migration technique sera limitée à :

1. créer le modèle de configuration locale ;
2. créer un gestionnaire de configuration locale ;
3. migrer sans supprimer les valeurs existantes ;
4. ajouter les tests ;
5. vérifier la rétrocompatibilité.

La consolidation des registres sera traitée séparément.
