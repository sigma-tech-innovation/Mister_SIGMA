# 📝 Mister_SIGMA — Journal canonique des changements

> **Statut :** journal documentaire canonique des versions et évolutions
> significatives de Mister_SIGMA.
>
> Ce document synthétise l’historique Git. Il ne remplace ni les commits, ni
> les tags, ni les rapports de phase.
>
> La section **Non publié** décrit le travail présent dans l’historique après le
> tag `v1.1.0` ou encore en cours sur la branche active. Elle ne constitue pas
> une release publiée.

---

## Convention

Les catégories utilisées sont :

- **Ajouté** : nouvelle capacité ;
- **Modifié** : évolution d’un comportement existant ;
- **Corrigé** : réparation ;
- **Documentation** : clarification ou synchronisation documentaire ;
- **Sécurité et gouvernance** : propriété, validation ou règles de contrôle ;
- **Limites connues** : fonctionnalité partielle, dette ou absence de preuve.

Le détail exhaustif reste disponible dans Git :

```bash
git log --oneline
git show <commit>
git tag
```

---

## Non publié

### État de référence

- branche observée : `feature/SIG-07B-node-network-endpoints` ;
- commit observé : `203d932` ;
- version affichée par la CLI : `1.1.0` ;
- phase active : `7A` ;
- sous-étape technique `7A.3b` temporairement suspendue pendant la
  synchronisation documentaire.

Les modifications documentaires présentes dans l’arbre de travail ne sont pas
encore une release tant qu’elles ne sont pas validées, commitées et, le cas
échéant, intégrées à une branche de publication.

### Ajouté

#### NodeNetworkManager — phase 7A

Les commits observés sur la branche active ajoutent progressivement :

- les contrats de domaine du nœud ;
- le modèle de nœud et la politique réseau ;
- un dépôt en mémoire ;
- la recherche dans le dépôt ;
- une façade de manager ;
- les opérations de cycle de vie.

Commits de référence :

```text
8c44bb5 feat(node): add domain contracts
565f295 feat(node): add node model and network policy
0b3ea72 feat(node): add in-memory repository
5ffc623 feat(node): add repository search and manager facade
ee97a7c feat(node): add node lifecycle operations
```

### Modifié

#### Socle multi-entités

Après la préparation de `v1.1.0`, l’historique ajoute ou étend notamment :

- `OrganizationManager` ;
- `WorkspaceManager V2` ;
- `UserManager` ;
- `MembershipManager` ;
- `AuthenticationManager` ;
- `SessionManager` ;
- `DeviceManager` ;
- `NodeNetworkManager`.

#### Données et configuration

L’historique ajoute notamment :

- la séparation entre configuration globale et locale ;
- `LocalConfigManager` ;
- une migration contrôlée de la configuration locale ;
- la standardisation de l’accès aux données des managers ;
- des backends JSON et SQLite modulaires ;
- un backend PostgreSQL optionnel ;
- une configuration centralisée du backend ;
- des commandes CLI de configuration de base ;
- `DataProviderManager` ;
- un fournisseur Notion optionnel.

#### Contexte, identité et autorisation

L’historique ajoute ou aligne :

- `ContextManager` ;
- `IdentityManager V2` ;
- le contexte comme source d’identité de synchronisation ;
- une fondation RBAC avec `AuthorizationManager`.

#### Synchronisation

L’historique ajoute :

- une fondation `SyncManager` ;
- une commande CLI connectée au manager ;
- l’utilisation du contexte unifié comme source d’identité.

### Documentation

La synchronisation documentaire en cours établit ou rationalise :

- `docs/INDEX.md` comme index documentaire ;
- `docs/architecture/ARCHITECTURE.md` comme architecture canonique ;
- `docs/ROADMAP.md` comme roadmap canonique ;
- `docs/CLI.md` comme référence des 46 routes publiques observées ;
- `docs/REGISTRY.md` comme référence de propriété des registres ;
- `docs/WORKSPACE.md` comme référence du workspace local et du manager V2 ;
- `docs/governance/REGLES_CANONIQUES.md` comme registre normatif ;
- le registre de traçabilité des 40 parties du Dossier Maître ;
- la note maître de l’écosystème ;
- la note de synthèse documentaire active.

Les fichiers racine historiques sont conservés comme points d’entrée lorsque
cela évite de casser les chemins existants.

### Sécurité et gouvernance

Les ADR acceptés après la préparation de `v1.1.0` définissent :

- la séparation entre données globales, locales et secrètes ;
- les sources de vérité transitoires et cibles ;
- l’interdiction de considérer Notion, MQTT, PostgreSQL ou l’API comme sources
  opérationnelles sans preuve ;
- la conservation des données avant migration ;
- l’absence de suppression silencieuse.

### Limites connues

- `NodeNetworkManager` est présent dans le code de la branche active, mais son
  intégration complète à `SigmaEngine` n’est pas démontrée dans l’état
  documentaire observé.
- La consolidation des différents registres JSON reste à réaliser par une
  migration dédiée.
- `WorkspaceManager V2` contient deux définitions successives de
  `create_record()` et `update_record()` ; la seconde définition est celle
  retenue par Python.
- Les tests Workspace observés couvrent principalement la compatibilité V1.
- L’API reste partielle.
- Les fournisseurs externes restent optionnels ou incomplets.
- La commande CLI `help` et la commande `commands` ne sont pas encore alignées
  automatiquement sur le dispatcher.
- Le fichier global `tests/test_cli.py` est vide.
- Les rapports des phases 01 à 03 et 07 doivent rester fondés sur des preuves
  réelles avant d’être déclarés complets.

---

## Version 1.1.0 — 2026-07-14

Tag Git :

```text
v1.1.0
```

Sujet du tag observé :

```text
Mister SIGMA v1.1.0 - CRUD managers, 93 tests, Doctor OK, Health OK
```

### Ajouté

- managers de base supplémentaires ;
- registre central des managers dans `SigmaEngine` ;
- capacités CRUD pour plusieurs managers ;
- tests unitaires élargis ;
- fondations pour identité, workspace, service, journalisation, événements,
  tâches et plugins ;
- `BaseManager` et `BaseCommand`.

### Modifié

- amélioration de la recherche des managers ;
- standardisation de plusieurs contrats de liste, comptage et accès ;
- extension de la couverture de test de plusieurs managers.

### Corrigé

- restauration du comportement attendu de `PluginManager` ;
- correction de l’accès racine dans `ApiManager`.

### Publication

La préparation de la version est matérialisée par :

```text
61503a3 RELEASE: prepare Mister SIGMA v1.1.0
5e7d7a5 Merge branch 'release/v1.1.0' into develop
```

Le tag Git constitue la preuve de publication de cette version.

---

## Version 1.0.0 — 2026-07-13

Tag Git :

```text
v1.0.0
```

Sujet du tag observé :

```text
Mister SIGMA Core v1.0.0
```

### Ajouté

- moteur `SigmaEngine` ;
- chargement et enregistrement des managers ;
- managers initiaux pour projets, nœuds, packages, registre, templates,
  releases, API et base de données ;
- architecture de plugins ;
- identité persistante du nœud ;
- métadonnées de profil et de synchronisation ;
- documentation d’architecture et roadmap associée.

### CLI

La CLI modulaire comprend alors de nombreuses commandes d’inspection et de
gestion, notamment :

- moteur, informations, statistiques et santé ;
- arbre, liste, recherche, affichage et comptage ;
- export, sauvegarde, restauration et import ;
- historique et configuration ;
- initialisation, vérification et résumé ;
- commandes Git de branche, remote, statut, log et liste des branches.

### Publication

Commits de référence :

```text
5e01d37 RELEASE: snapshot v1.0.0
37a9975 release: Sigma CLI v1.0.0
```

---

## Version 0.6.0 — 2026-07-05

Cette version correspond au premier jalon CLI explicitement documenté dans
l’ancien changelog racine.

### Ajouté

- architecture CLI modulaire ;
- dispatcher ;
- moteur de workspace local ;
- registre CLI ;
- validation du registre ;
- identité du nœud ;
- enregistrement du nœud ;
- statut global ;
- journalisation ;
- diagnostic étendu ;
- aide CLI ;
- état Git et synchronisation Git ;
- commandes initiales pour projets, packages, templates, releases et base de
  données.

Commit de publication observé :

```text
49f3bd6 SIG-VERSION-BUMP: release Sigma CLI v0.6.0
```

### Limite historique

Le fichier racine `CHANGELOG.md` ne décrivait que ce jalon CLI. Il devient un
point d’entrée historique vers le présent journal afin d’éviter deux sources
concurrentes.

---

## Initialisation — 2026-06-30

Premiers commits observés :

```text
123c242 Initialise Mister SIGMA repository
d56b444 Add Mister SIGMA V1 splash screen
```

Ils établissent :

- le dépôt initial ;
- un premier écran de démarrage Mister SIGMA.

---

## Jalons historiques intermédiaires

### 2026-07-05 — Structure et CLI initiale

L’historique comprend notamment :

- structure officielle du projet ;
- roadmap initiale ;
- registre maître initial ;
- CLI MVP ;
- commandes de registre ;
- dispatcher modulaire ;
- configuration CLI centrale ;
- workspace local ;
- journalisation ;
- identité et enregistrement du nœud ;
- diagnostic, statut et aide ;
- structure documentaire, tests et contribution ;
- couche API initiale ;
- base JSON initiale ;
- commandes de gestion des données.

### 2026-07-06 et 2026-07-07 — Moteur et commandes étendues

L’historique ajoute :

- le moteur central ;
- les managers initiaux ;
- l’enregistrement automatique des managers ;
- les commandes d’inspection globales ;
- les opérations d’export, sauvegarde, restauration et import ;
- les commandes de configuration et d’initialisation ;
- les commandes Git supplémentaires.

### 2026-07-11 à 2026-07-13 — Système de plugins

L’historique ajoute progressivement :

- enregistrement et suppression ;
- activation et désactivation ;
- recherche, découverte et chargement ;
- déchargement et rechargement ;
- création et suppression ;
- import et export ;
- sauvegarde et restauration ;
- validation, installation et désinstallation ;
- opérations globales et opérations par identifiant.

### 2026-07-14 — Managers, CRUD, tests et architecture

L’historique ajoute :

- plusieurs managers de plateforme ;
- des contrats CRUD ;
- une couverture de test élargie ;
- la release `v1.1.0` ;
- les ADR sur la propriété des données et les sources de vérité ;
- la configuration locale ;
- la fondation de synchronisation ;
- le contexte unifié ;
- l’autorisation RBAC.

### 2026-07-15 — Plateforme multi-entités et phases 04 à 07

L’historique ajoute :

- organisations, utilisateurs, memberships et workspaces V2 ;
- backends de données modulaires ;
- fournisseur Notion optionnel ;
- phase 04 AuthenticationManager ;
- phase 05 SessionManager ;
- phase 06 DeviceManager ;
- début de la phase 07 NodeNetworkManager.

---

## Sources de version actuelles

Les sources observées ne jouent pas toutes le même rôle.

| Source | Valeur ou état observé | Statut |
|---|---|---|
| `sigma-cli/sigma/config.py` | `1.1.0` | version affichée par la CLI |
| commande `version` | `Sigma CLI v1.1.0` | preuve d’exécution |
| tag Git `v1.1.0` | présent | release publiée |
| tag Git `v1.0.0` | présent | release publiée |
| `releases/latest.json` | `1.1.0` | métadonnée de release |
| `sigma-db/releases.json` | record `0.6.0` | héritage de développement |
| `.sigma-workspace/database/releases.json` | liste vide | runtime local |
| ancien `CHANGELOG.md` racine | uniquement `0.6.0` | historique |

Une version présente dans un fichier JSON ne constitue pas automatiquement une
release publiée.

Les tags Git restent la preuve principale des releases `v1.0.0` et `v1.1.0`.

---

## Règles de maintenance

Toute mise à jour de ce journal doit :

1. distinguer **Non publié** d’une release taguée ;
2. s’appuyer sur des commits, tags ou rapports vérifiables ;
3. ne pas transformer une cible d’architecture en fonctionnalité livrée ;
4. mentionner les migrations et incompatibilités importantes ;
5. signaler les limites de test significatives ;
6. conserver les anciennes versions sans réécrire leur histoire ;
7. utiliser une date de publication seulement lorsqu’elle est prouvée ;
8. éviter la copie exhaustive de tous les commits ;
9. conserver Git comme historique détaillé ;
10. actualiser les points d’entrée documentaires associés.

Le nombre de commits observé au moment de la synchronisation était de `281`.
Ce nombre est un instantané, pas un identifiant de version.
