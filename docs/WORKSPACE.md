# 🧭 Mister_SIGMA — Workspace local et WorkspaceManager V2

> **Statut :** référence documentaire canonique du domaine Workspace.
>
> Ce document distingue le workspace local de l’installation, la commande CLI
> historique et le modèle métier `WorkspaceManager V2`.
>
> Il décrit uniquement les comportements réellement observés dans le dépôt.

---

## 1. Trois notions distinctes

Le mot *workspace* désigne actuellement trois réalités différentes dans
Mister_SIGMA.

| Notion | Représentation | Rôle |
|---|---|---|
| Workspace local | `.sigma-workspace/` | Données locales de l’installation |
| CLI workspace | `sigma-cli/sigma/workspace.py` | Création et affichage de répertoires historiques |
| Workspace métier V2 | `sigma-core/managers/workspace_manager.py` | Gestion de records de workspace via `DatabaseManager` |

Ces notions ne doivent pas être confondues.

La présence d’un répertoire `.sigma-workspace` ne prouve pas qu’un record
métier Workspace V2 existe.

---

## 2. Propriétaire documentaire

Le propriétaire documentaire du domaine est :

```text
docs/WORKSPACE.md
```

Ce document définit :

- la frontière entre données locales et données partagées ;
- le rôle de `.sigma-workspace/` ;
- le contrat observé de la commande CLI ;
- le contrat observé de `WorkspaceManager V2` ;
- les champs et statuts du modèle métier ;
- les limites de couverture de test ;
- les dettes de code et de documentation ;
- les prérequis d’une future synchronisation multi-machine.

---

## 3. Workspace local de l’installation

Le workspace local se trouve dans :

```text
.sigma-workspace/
```

Ce répertoire est ignoré par Git.

La règle actuelle est définie dans `.gitignore` :

```text
.sigma-workspace/
```

Les fichiers locaux de ce répertoire ne doivent donc pas être considérés comme
des données partagées par le dépôt.

### Contenu observé

L’installation inspectée contient notamment :

```text
.sigma-workspace/backups/
.sigma-workspace/cache/
.sigma-workspace/configs/
.sigma-workspace/database/
.sigma-workspace/logs/
.sigma-workspace/projects/
.sigma-workspace/registry/
.sigma-workspace/temp/
```

Des sauvegardes locales, fichiers de configuration, bases JSON locales et
journaux sont également présents.

Ces éléments appartiennent à l’installation locale.

---

## 4. Configuration locale

Les fichiers observés sont :

```text
.sigma-workspace/configs/config.json
.sigma-workspace/configs/local.json
```

### `config.json`

Le fichier contient actuellement :

- le chemin du workspace ;
- la version du format local.

Il reste local car son chemin absolu dépend de l’installation.

### `local.json`

Ce fichier contient notamment :

- `machine_id` ;
- `node_id` ;
- `hostname` ;
- `device_type` ;
- `local_profile` ;
- `local_environment` ;
- `last_sync` ;
- `installation_id`.

Conformément à ADR-001 et ADR-002, ces valeurs appartiennent à l’installation
locale et ne doivent pas être partagées directement par Git.

---

## 5. Bases locales du workspace

Le répertoire observé est :

```text
.sigma-workspace/database/
```

Il contient actuellement :

```text
nodes.json
packages.json
projects.json
registry.json
releases.json
templates.json
```

Aucun fichier `workspaces.json` n’a été observé lors de l’inspection.

Cela signifie qu’aucune base Workspace V2 locale n’est encore matérialisée dans
cette installation, ou qu’elle n’a pas encore été créée par le backend actif.

L’absence du fichier ne signifie pas que le manager est absent du code.

---

## 6. Commande CLI historique

La route publique est :

```bash
./sigma-cli/sigma.py workspace
```

Les syntaxes observées sont :

```bash
./sigma-cli/sigma.py workspace
./sigma-cli/sigma.py workspace show
./sigma-cli/sigma.py workspace init
```

Le comportement par défaut est `show`.

### Répertoires gérés

La commande CLI historique utilise la liste suivante :

```text
projects
registry
logs
backups
configs
cache
temp
```

### `show`

La commande affiche pour chaque répertoire :

- `OK` si le chemin existe ;
- `MISSING` sinon.

### `init`

La commande crée les répertoires manquants avec `mkdir(parents=True,
exist_ok=True)`, puis affiche leur état.

### Limite

Cette commande ne crée pas de record Workspace V2 dans une base de données.

Elle initialise uniquement une structure locale historique.

---

## 7. WorkspaceManager V2

Le manager métier est défini dans :

```text
sigma-core/managers/workspace_manager.py
```

Il est :

- chargé par `SigmaEngine` ;
- instancié dans `self.workspace` ;
- enregistré dans `self.managers` sous la clé `workspace`.

Le manager mélange actuellement deux contrats :

1. une compatibilité V1 orientée système de fichiers ;
2. un modèle V2 orienté records métier.

---

## 8. Compatibilité V1

Les méthodes de compatibilité système de fichiers sont :

```text
root()
path()
exists()
list()
count()
create()
update()
delete()
```

### Lecture

- `root()` retourne `engine.root` ;
- `path(*parts)` construit un chemin sous la racine ;
- `exists(*parts)` vérifie l’existence ;
- `list(*parts)` liste un répertoire ;
- `count(*parts)` compte les entrées.

### Écriture

`create()` peut :

- créer un répertoire ;
- créer un fichier ;
- écrire un contenu UTF-8.

`update()` peut remplacer le contenu d’un fichier existant.

`delete()` peut :

- supprimer un fichier avec `unlink()` ;
- supprimer récursivement un répertoire avec `shutil.rmtree()`.

Ces opérations peuvent être destructives.

Elles doivent être utilisées uniquement avec des chemins contrôlés.

---

## 9. Modèle métier V2

Le nom logique de la base est :

```text
workspaces
```

Le manager appelle :

```python
engine.database.load("workspaces")
```

et :

```python
engine.database.save("workspaces", records)
```

Le stockage concret dépend donc du backend actif de `DatabaseManager`.

### Champs obligatoires

Le manager exige actuellement :

```text
id
organization_id
name
slug
owner_user_id
status
root_path
```

### Champs ajoutés par défaut

La création peut ajouter :

```text
description
metadata
created_at
updated_at
```

### Identifiant

La méthode `next_id()` génère un identifiant sous la forme :

```text
WS-<uuid>
```

### Slug

Le slug est :

- converti en chaîne ;
- nettoyé avec `strip()` ;
- converti en minuscules ;
- transformé en remplaçant les espaces par des tirets.

Cette normalisation ne traite pas encore toutes les collisions possibles,
accents, séparateurs ou caractères spéciaux.

---

## 10. Statuts Workspace V2

Les statuts acceptés sont :

```text
active
archived
suspended
```

Tout autre statut rend le record invalide.

La méthode `archive()` ne supprime pas le record.

Elle appelle :

```python
update_record(workspace_id, status="archived")
```

Cette approche préserve l’historique logique du workspace.

---

## 11. Contexte et propriétés automatiques

Lors de la création d’un record, le manager peut obtenir automatiquement :

```text
organization_id
owner_user_id
root_path
created_at
updated_at
```

Les sources observées sont :

```python
engine.context.organization_id()
engine.context.user_id()
engine.root
engine.now()
```

Le manager dépend donc de plusieurs services de `SigmaEngine`.

Un test complet du modèle V2 doit fournir ces dépendances.

---

## 12. Création d’un record

La méthode publique observée est :

```python
create_record(data)
```

Elle :

1. copie les données reçues ;
2. génère un identifiant si nécessaire ;
3. complète l’organisation et le propriétaire ;
4. normalise le slug ;
5. applique le statut `active` par défaut ;
6. applique le chemin racine ;
7. ajoute les métadonnées temporelles ;
8. valide le record ;
9. refuse un identifiant déjà présent ;
10. refuse un slug déjà présent ;
11. sauvegarde la liste ;
12. émet l’événement `workspace.created`.

La méthode `create()` délègue également à `create_record()` lorsque son premier
argument est un dictionnaire.

---

## 13. Mise à jour d’un record

La méthode publique observée est :

```python
update_record(workspace_id, **fields)
```

Elle :

1. charge les records ;
2. trouve le workspace par identifiant ;
3. applique les champs reçus ;
4. actualise `updated_at` ;
5. valide le résultat ;
6. sauvegarde la liste ;
7. émet l’événement `workspace.updated`.

La méthode `update()` délègue à `update_record()` lorsqu’elle reçoit un seul
identifiant et des champs nommés.

### Limite actuelle

La mise à jour ne vérifie pas explicitement qu’un nouveau slug n’entre pas en
collision avec un autre record existant.

---

## 14. Lecture et validation

Les méthodes métier de lecture sont :

```text
records()
get()
get_by_slug()
exists_record()
current()
validate()
snapshot()
```

### `current()`

Cette méthode recherche un workspace dont le slug correspond à :

```python
engine.context.workspace_id()
```

Le contrat suppose donc que `workspace_id()` peut être utilisé comme slug.

Cette hypothèse doit être documentée ou corrigée si `workspace_id` devient un
identifiant `WS-*`.

### `validate()`

La validation globale :

- vérifie chaque record ;
- agrège les erreurs ;
- retourne le nombre de records ;
- fournit un booléen `valid`.

### `snapshot()`

Le snapshot expose :

- l’organisation courante ;
- le workspace courant du contexte ;
- l’utilisateur courant ;
- la validation ;
- la liste des workspaces.

---

## 15. Événements

Les événements émis sont :

```text
workspace.created
workspace.updated
```

Aucun événement distinct `workspace.archived` n’est actuellement émis.

L’archivage produit donc un événement `workspace.updated`.

---

## 16. Dette de code constatée

Le fichier contient deux définitions successives de :

```text
create_record()
update_record()
```

En Python, la seconde définition remplace la première lors de la création de la
classe.

Dans l’état observé, les deux copies sont identiques, mais cette duplication
reste une dette réelle :

- elle augmente le risque de divergence ;
- une modification de la première copie serait sans effet ;
- la lecture du contrat devient ambiguë ;
- les outils d’inventaire peuvent compter deux méthodes alors qu’une seule est
  active.

Cette duplication doit être supprimée lors d’une modification technique
dédiée, avec tests avant et après.

Elle ne doit pas être corrigée pendant la synchronisation documentaire.

---

## 17. Couverture de test actuelle

Le fichier :

```text
sigma-core/tests/test_workspace_manager.py
```

exécute cinq tests.

Ils couvrent principalement la compatibilité V1 :

- existence du manager ;
- résolution des chemins ;
- création de fichiers ;
- mise à jour de fichiers ;
- suppression de fichiers ;
- création de répertoires ;
- suppression récursive de répertoires ;
- liste et comptage local.

### Non couvert actuellement

Les tests observés ne couvrent pas directement :

- `records()` ;
- `save_records()` ;
- `normalize_slug()` ;
- `next_id()` ;
- `get()` ;
- `get_by_slug()` ;
- `exists_record()` ;
- `validate_record()` ;
- `create_record()` ;
- `update_record()` ;
- `archive()` ;
- `current()` ;
- `validate()` ;
- `snapshot()` ;
- les événements ;
- les collisions de slug ;
- l’intégration avec `DatabaseManager`.

Le fichier global suivant existe mais est vide :

```text
tests/test_workspace.py
```

La mention « WorkspaceManager V2 réalisé » doit donc être comprise comme un
socle de code présent, pas comme une couverture fonctionnelle complète.

---

## 18. Frontières de propriété

| Donnée | Propriétaire transitoire |
|---|---|
| Code du manager | Git |
| Documentation du domaine | `docs/WORKSPACE.md` |
| Identité locale de l’installation | `.sigma-workspace/configs/local.json` |
| Fichiers runtime locaux | `.sigma-workspace/` |
| Records Workspace V2 | backend actif de `DatabaseManager` |
| Contexte courant | `ContextManager` |
| Cible centralisée future | PostgreSQL via API Sigma |

Le chemin local d’un workspace ne doit pas devenir une donnée partagée sans
politique explicite.

---

## 19. Sécurité

Les opérations système de fichiers doivent empêcher :

- les chemins sortant de la racine autorisée ;
- les suppressions accidentelles ;
- l’écrasement silencieux ;
- la création de fichiers sensibles ;
- l’exposition de secrets ;
- la copie de chemins absolus locaux dans une source partagée.

Le code observé construit actuellement les chemins avec :

```python
self.engine.root.joinpath(*parts)
```

Il ne valide pas explicitement que le chemin résolu reste sous la racine.

Cette protection doit être ajoutée avant toute exposition distante ou
multi-utilisateur des opérations de fichiers.

---

## 20. Synchronisation multi-machine

La cible décrite par les ADR prévoit :

- PostgreSQL pour les workspaces partagés ;
- l’API Sigma comme interface d’écriture distante ;
- un cache ou backend local ;
- `local.json` pour les propriétés d’installation ;
- une résolution explicite des conflits ;
- aucune suppression silencieuse.

Cette cible n’est pas démontrée comme entièrement opérationnelle dans l’état
actuel du dépôt.

---

## 21. Sources de vérité documentaire

| Sujet | Propriétaire |
|---|---|
| Domaine Workspace | ce document |
| Architecture générale | [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) |
| Séparation des données | [`architecture/decisions/ADR-001-DATA-OWNERSHIP.md`](architecture/decisions/ADR-001-DATA-OWNERSHIP.md) |
| Sources de vérité | [`architecture/decisions/ADR-002-SOURCE-OF-TRUTH.md`](architecture/decisions/ADR-002-SOURCE-OF-TRUTH.md) |
| Référence CLI | [`CLI.md`](CLI.md) |
| Domaine Registre | [`REGISTRY.md`](REGISTRY.md) |
| Règles canoniques | [`governance/REGLES_CANONIQUES.md`](governance/REGLES_CANONIQUES.md) |

---

## 22. Règles de maintenance

Toute modification du domaine Workspace doit :

1. préciser si elle concerne le filesystem local ou les records V2 ;
2. identifier le backend réellement lu ou écrit ;
3. conserver les données avant toute suppression ;
4. empêcher les chemins sortant de la racine ;
5. préserver la séparation entre données locales et partagées ;
6. ajouter les tests du contrat V2 ;
7. vérifier l’unicité des identifiants et slugs ;
8. documenter les événements émis ;
9. mettre à jour ce document ;
10. ne pas présenter une cible PostgreSQL ou API comme déjà opérationnelle sans
    preuve.

Le répertoire `.sigma-workspace/`, la commande CLI historique et un record
Workspace V2 sont trois objets différents.
