# ⌨️ Mister_SIGMA — Référence canonique de la CLI

> **Statut :** document propriétaire de l’interface en ligne de commande.
>
> Cette référence décrit uniquement les routes réellement présentes dans
> `sigma-cli/sigma/dispatcher.py` et les modules de `sigma-cli/sigma/commands/`.
> Le comportement réel du code et les tests exécutés restent la preuve opérationnelle.

---

## 1. Lancement

Depuis la racine du dépôt :

```bash
./sigma-cli/sigma.py <commande> [arguments]
```

Le lanceur vérifié est :

```text
sigma-cli/sigma.py
```

Il appelle `sigma.main.main()`, puis transmet :

- `sys.argv[1]` comme commande ;
- `sys.argv[2:]` comme arguments ;
- la commande et ses arguments à `sigma.dispatcher.dispatch()`.

La CLI utilise un routage Python manuel. Aucun usage d’`argparse`, Click ou Typer n’a été détecté.

### Version observée

```bash
./sigma-cli/sigma.py version
```

Sortie vérifiée :

```text
Sigma CLI v1.1.0
```

### Sans commande

```bash
./sigma-cli/sigma.py
```

Sortie actuelle :

```text
Sigma CLI
```

### Commande inconnue

Une commande inconnue affiche actuellement :

```text
Unknown command
```

Le code de sortie observé est `0`. Ce comportement ne permet donc pas encore à un script d’automatisation de distinguer une commande inconnue d’une réussite.

---

## 2. Contrat public actuel

Le routeur expose **46 commandes publiques**.

| Commande | Sous-commandes détectées | Classe statique | Test dédié |
|---|---|---|---|
| `authentication` | `audit`, `list`, `policy`, `show`, `status`, `validate` | lecture ou diagnostic | oui |
| `session` | `list`, `show`, `status`, `validate` | lecture ou diagnostic | oui |
| `device` | `list`, `status`, `validate` | lecture ou diagnostic | oui |
| `version` | aucune | lecture ou diagnostic | non |
| `doctor` | aucune | lecture ou diagnostic | non |
| `registry` | `list`, `show`, `validate` | lecture ou diagnostic | non |
| `workspace` | `init`, `show` | modificatrice | non |
| `node` | `register` | modificatrice | non |
| `status` | aucune | lecture ou diagnostic | non |
| `help` | aucune | lecture ou diagnostic | non |
| `log` | aucune | lecture ou diagnostic | non |
| `sync` | `plan`, `snapshot`, `validate` | lecture ou diagnostic | oui |
| `projects` | `create` | modificatrice | non |
| `packages` | aucune | lecture ou diagnostic | non |
| `database` | `backend`, `list`, `migrate`, `status` | modificatrice | oui |
| `templates` | aucune | lecture ou diagnostic | non |
| `releases` | aucune | lecture ou diagnostic | non |
| `roadmap` | aucune | lecture ou diagnostic | non |
| `engine` | aucune | lecture ou diagnostic | non |
| `info` | aucune | lecture ou diagnostic | non |
| `stats` | aucune | lecture ou diagnostic | non |
| `health` | aucune | lecture ou diagnostic | non |
| `tree` | aucune | lecture ou diagnostic | non |
| `list` | aucune | lecture ou diagnostic | non |
| `search` | argument texte | lecture ou diagnostic | non |
| `show` | argument base de données | lecture ou diagnostic | non |
| `count` | aucune | lecture ou diagnostic | non |
| `export` | aucune | modificatrice | non |
| `backup` | aucune | modificatrice | non |
| `restore` | aucune | destructive | non |
| `import` | aucune | modificatrice | non |
| `history` | aucune | lecture ou diagnostic | non |
| `about` | aucune | lecture ou diagnostic | non |
| `config` | aucune | modificatrice | non |
| `local-config` | `apply`, `preview`, `show` | modificatrice | oui |
| `reset` | aucune | destructive | non |
| `init` | aucune | lecture ou diagnostic | non |
| `verify` | aucune | lecture ou diagnostic | non |
| `commands` | aucune | lecture ou diagnostic | non |
| `summary` | aucune | lecture ou diagnostic | non |
| `branch` | aucune | lecture ou diagnostic | non |
| `remote` | aucune | lecture ou diagnostic | non |
| `last` | aucune | lecture ou diagnostic | non |
| `gitstatus` | aucune | lecture ou diagnostic | non |
| `gitlog` | nombre optionnel | lecture ou diagnostic | non |
| `gitbranches` | aucune | lecture ou diagnostic | non |

La classification est statique : elle repose sur les appels détectés dans les modules. Elle ne remplace pas une exécution contrôlée ni une revue des effets réels.

---

## 3. Commandes couvertes par des tests dédiés

Six familles disposent de tests de commande dédiés.

### `authentication`

```bash
./sigma-cli/sigma.py authentication
./sigma-cli/sigma.py authentication status
./sigma-cli/sigma.py authentication validate
./sigma-cli/sigma.py authentication list
./sigma-cli/sigma.py authentication show <credential-id>
./sigma-cli/sigma.py authentication audit [--credential <id>] [--user <id>]
./sigma-cli/sigma.py authentication policy
```

Le comportement par défaut est `status`.

Cette commande est actuellement en lecture seule. Le contrat testé ne prend pas de mot de passe en argument.

### `session`

```bash
./sigma-cli/sigma.py session
./sigma-cli/sigma.py session status
./sigma-cli/sigma.py session validate
./sigma-cli/sigma.py session list
./sigma-cli/sigma.py session show <session-id>
```

Le comportement par défaut est `status`.

### `device`

```bash
./sigma-cli/sigma.py device
./sigma-cli/sigma.py device status
./sigma-cli/sigma.py device validate
./sigma-cli/sigma.py device list
```

Les tests dédiés couvrent les fonctions de statut, validation et liste.

### `sync`

```bash
./sigma-cli/sigma.py sync
./sigma-cli/sigma.py sync snapshot
./sigma-cli/sigma.py sync validate
./sigma-cli/sigma.py sync plan
```

Le comportement par défaut est `snapshot`.

`sync validate` affiche notamment l’état `ready` retourné par `SyncManager`. Cette commande valide un état ; elle ne constitue pas une preuve qu’une synchronisation distante complète a été exécutée.

### `database`

```bash
./sigma-cli/sigma.py database
./sigma-cli/sigma.py database status
./sigma-cli/sigma.py database backend
./sigma-cli/sigma.py database backend <backend> [url]
./sigma-cli/sigma.py database migrate <backend-cible> [base ...]
./sigma-cli/sigma.py database list
```

Le comportement par défaut est `status`.

Les opérations `backend <backend>` et `migrate` peuvent modifier la configuration ou les données. Elles doivent être exécutées après sauvegarde et contrôle de la cible.

### `local-config`

```bash
./sigma-cli/sigma.py local-config
./sigma-cli/sigma.py local-config preview
./sigma-cli/sigma.py local-config show
./sigma-cli/sigma.py local-config apply
```

Le comportement par défaut est `preview`.

`preview` effectue une simulation. `apply` écrit la migration de configuration locale et peut créer une sauvegarde.

---

## 4. Autres syntaxes explicitement détectées

### Registre

```bash
./sigma-cli/sigma.py registry
./sigma-cli/sigma.py registry list
./sigma-cli/sigma.py registry show <object-id>
./sigma-cli/sigma.py registry validate
```

Le comportement par défaut ou `list` affiche les objets du registre.

### Workspace

```bash
./sigma-cli/sigma.py workspace
./sigma-cli/sigma.py workspace show
./sigma-cli/sigma.py workspace init
```

Le comportement par défaut est `show`. `init` crée ou complète `.sigma-workspace`.

### Nœud

```bash
./sigma-cli/sigma.py node register
```

Cette route appelle une opération d’enregistrement de nœud et doit être considérée comme modificatrice.

### Projets

```bash
./sigma-cli/sigma.py projects
./sigma-cli/sigma.py projects create <nom>
```

`create` crée des fichiers ou répertoires de projet.

### Recherche

```bash
./sigma-cli/sigma.py search <texte>
```

La recherche inspecte les bases `projects`, `packages` et `nodes`.

### Affichage d’une base

```bash
./sigma-cli/sigma.py show <database>
```

### Journal Git

```bash
./sigma-cli/sigma.py gitlog [nombre]
```

---

## 5. Commandes modificatrices

Les routes suivantes contiennent des appels susceptibles d’écrire, créer, migrer ou enregistrer des données :

| Commande | Effets statiquement détectés |
|---|---|
| `workspace` | création du workspace |
| `node` | enregistrement d’un nœud |
| `projects` | création de projet, répertoires et fichiers |
| `database` | configuration ou migration |
| `export` | écriture d’un fichier |
| `backup` | création d’un répertoire et copie d’arborescence |
| `import` | sauvegarde de données importées |
| `config` | création de répertoire et écriture de configuration |
| `local-config` | application d’une migration |

Avant leur exécution :

1. se placer à la racine du dépôt ;
2. vérifier les chemins utilisés par le module ;
3. sauvegarder les données concernées ;
4. exécuter une simulation lorsqu’elle existe ;
5. examiner `git status --short` après l’opération.

---

## 6. Commandes destructives

### `restore`

Le module supprime le répertoire `sigma-db` existant avant de recopier la sauvegarde la plus récente trouvée dans `backups`.

```bash
./sigma-cli/sigma.py restore
```

Cette commande doit être précédée d’une sauvegarde distincte et d’une vérification du contenu de `backups`.

### `reset`

Le module supprime entièrement `sigma-db`, puis recrée un répertoire vide.

```bash
./sigma-cli/sigma.py reset
```

Cette commande entraîne une perte locale des données présentes dans `sigma-db` si aucune sauvegarde exploitable n’existe.

---

## 7. Diagnostics et inspection

Les commandes suivantes sont principalement destinées à la lecture, au diagnostic ou à l’inspection :

```text
about
authentication
branch
commands
count
device
doctor
engine
gitbranches
gitlog
gitstatus
health
help
history
info
init
last
list
log
packages
registry
releases
remote
roadmap
search
session
show
stats
status
summary
sync
templates
tree
verify
version
```

Certaines dépendent du répertoire courant, de Git, de fichiers JSON ou du chargement de `SigmaEngine`. Leur absence d’écriture détectée ne garantit pas l’absence de tout effet indirect.

---

## 8. Défaut actuel de `help` et `commands`

Les commandes :

```bash
./sigma-cli/sigma.py help
./sigma-cli/sigma.py commands
```

parcourent actuellement les fichiers `sigma-cli/sigma/commands/*.py` au lieu d’interroger le routeur public.

Conséquences observées :

- elles affichent `base_command`, qui n’est pas une route publique ;
- elles affichent `importdb`, alors que la route publique est `import` ;
- elles affichent `local_config`, alors que la route publique est `local-config`.

Ces sorties ne doivent pas être utilisées comme contrat public exhaustif tant que l’aide n’est pas reliée au dispatcher.

Le contrat public de référence est la liste des 46 routes de ce document, dérivée de `sigma-cli/sigma/dispatcher.py`.

---

## 9. Couverture de test

Tests dédiés présents :

```text
sigma-core/tests/test_authentication_command.py
sigma-core/tests/test_database_command.py
sigma-core/tests/test_device_command.py
sigma-core/tests/test_local_config_command.py
sigma-core/tests/test_session_command.py
sigma-core/tests/test_sync_command.py
```

Le fichier suivant existe mais est vide :

```text
tests/test_cli.py
```

La présence d’une route dans le dispatcher ne signifie donc pas qu’elle est couverte par un test d’intégration du lanceur.

---

## 10. Sources de vérité

| Sujet | Propriétaire |
|---|---|
| Routes publiques | `sigma-cli/sigma/dispatcher.py` |
| Lanceur | `sigma-cli/sigma.py` |
| Lecture de `sys.argv` | `sigma-cli/sigma/main.py` |
| Implémentation des commandes | `sigma-cli/sigma/commands/*.py` |
| Tests dédiés | `sigma-core/tests/test_*_command.py` |
| Référence utilisateur | ce document |
| Architecture générale | [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) |
| Roadmap active | [`ROADMAP.md`](ROADMAP.md) |
| Règles communes | [`governance/REGLES_CANONIQUES.md`](governance/REGLES_CANONIQUES.md) |

---

## 11. Règles de maintenance

Toute modification de la CLI doit :

1. mettre à jour le dispatcher ;
2. maintenir un nom public stable et distinct du nom interne du module ;
3. fournir un message d’usage exact ;
4. retourner un code non nul en cas de commande inconnue ou d’échec ;
5. documenter clairement les commandes modificatrices et destructives ;
6. ajouter ou actualiser les tests dédiés ;
7. mettre à jour ce document lorsque le contrat public change.

Une commande ne doit pas être présentée comme opérationnelle uniquement parce qu’un fichier Python portant son nom existe.
