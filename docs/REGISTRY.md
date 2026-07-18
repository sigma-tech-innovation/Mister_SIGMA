# 🗂️ Mister_SIGMA — Registres et propriété des actifs

> **Statut :** référence documentaire canonique du domaine Registre.
>
> Ce document décrit les représentations réellement présentes, leur propriétaire
> technique, leur statut transitoire et les conditions de leur consolidation.
> Il ne fusionne, ne migre et ne supprime aucune donnée.

---

## 1. Situation actuelle

Mister_SIGMA possède plusieurs représentations distinctes du registre.

| Représentation | Rôle observé | Statut |
|---|---|---|
| `docs/REGISTRY.md` | Référence documentaire de propriété et de consolidation | Canonique |
| `MASTER_REGISTRY.md` | Inventaire initial lisible par un humain | Historique |
| `sigma-core/registry/registry.json` | Registre lu directement par la CLI historique | Transition active |
| `.sigma-workspace/database/registry.json` | Registre local utilisé par `RegistryManager` via `DatabaseManager` | Runtime local |
| `sigma-db/registry.json` | Jeu de données JSON versionné de développement | Héritage transitoire |

Ces représentations n’utilisent ni le même schéma, ni les mêmes identifiants,
ni le même stockage.

Elles ne doivent pas être présentées comme une base unique déjà synchronisée.

---

## 2. Propriétaire documentaire

Le propriétaire documentaire du domaine est :

```text
docs/REGISTRY.md
```

Ce document définit :

- la fonction de chaque registre ;
- le statut canonique, historique ou transitoire de chaque représentation ;
- les règles d’identification ;
- les règles de statut ;
- les contraintes de validation ;
- les conditions préalables à toute consolidation ;
- la distinction entre déclaration et preuve opérationnelle.

`MASTER_REGISTRY.md` reste conservé pour l’historique. Il ne doit pas être
utilisé seul pour déterminer la source technique active.

---

## 3. Inventaire historique racine

Le fichier :

```text
MASTER_REGISTRY.md
```

contient l’inventaire initial de plusieurs actifs de l’écosystème, notamment :

- le dépôt Mister_SIGMA ;
- le téléphone Android Termux ;
- le PC Windows ;
- l’environnement WSL2 ;
- Docker Desktop ;
- Home Assistant ;
- ESPHome ;
- Mosquitto MQTT ;
- des documents de gestion.

Ses familles d’identifiants comprennent notamment :

```text
SIG-PC
SIG-PHONE
SIG-WSL
SIG-VPS
SIG-RPI
SIG-GIT
SIG-DOC
SIG-SCRIPT
SIG-DB
SIG-SERVICE
SIG-ESP
SIG-IOT
SIG-LAB
SIG-AI
```

### Limite de preuve

Un statut `Actif` dans ce fichier représente une déclaration documentaire.

Il ne prouve pas à lui seul que :

- le service est démarré ;
- la machine est accessible ;
- l’intégration au dépôt est terminée ;
- une communication réseau a été testée ;
- une supervision automatique existe.

Les services Windows déclarés actifs doivent donc rester qualifiés comme
**déclarés par le propriétaire, preuve opérationnelle en attente** lorsque la
machine concernée est indisponible.

---

## 4. Registre lu par la CLI

La configuration CLI définit actuellement le chemin suivant :

```text
sigma-core/registry/registry.json
```

La commande :

```bash
./sigma-cli/sigma.py registry list
```

lit directement ce fichier, sans passer par `RegistryManager`.

### Structure observée

- version : `0.1.0` ;
- type racine : objet JSON ;
- collection : `objects` ;
- objets : `5`.

Identifiants observés :

```text
SIG-GIT-001
SIG-PHONE-001
SIG-PC-001
SIG-NODE-3B880B85A99F
SIG-NODE-A102D3D0BA7E
```

### Validation CLI

La commande :

```bash
./sigma-cli/sigma.py registry validate
```

vérifie actuellement la présence des champs :

```text
id
name
type
status
```

Cette validation est structurelle et limitée.

Elle ne vérifie pas notamment :

- l’unicité globale des identifiants ;
- l’existence réelle de l’actif ;
- l’accessibilité réseau ;
- la cohérence avec `local.json` ;
- la cohérence avec `RegistryManager` ;
- la présence d’un propriétaire ;
- la date de dernière vérification ;
- la provenance de la déclaration.

### Dette constatée

Le fichier contient deux identifiants de nœud décrivant un environnement
Android avec le hostname `localhost`.

Cette coexistence correspond au problème de doublons déjà documenté par
ADR-001. Elle ne doit pas être corrigée sans migration contrôlée.

---

## 5. Registre runtime de RegistryManager

`RegistryManager` n’ouvre pas directement un chemin fixe.

Il appelle :

```python
engine.database.load("registry")
```

et :

```python
engine.database.save("registry", data)
```

`DatabaseManager` résout son stockage depuis le workspace de l’engine.

Avec l’engine actuel, la racine locale est :

```text
.sigma-workspace/database
```

Le registre runtime local correspondant est :

```text
.sigma-workspace/database/registry.json
```

### État observé

- type racine : liste JSON ;
- entrées : `0` ;
- identifiants : aucun.

Ce fichier appartient au runtime local. Il ne doit pas être considéré comme une
source Git partagée.

### Capacités de RegistryManager

Le manager fournit actuellement :

- `records()` ;
- `list()` ;
- `next_id()` ;
- `get()` ;
- `exists()` ;
- `create()` ;
- `update()` ;
- `delete()` ;
- `count()`.

Les écritures réalisées par ces méthodes concernent le backend configuré de
`DatabaseManager`.

---

## 6. Registre JSON versionné de développement

Le fichier :

```text
sigma-db/registry.json
```

contient actuellement :

- type racine : liste JSON ;
- entrées : `1` ;
- identifiant : `REG-0001`.

Il s’agit d’un jeu de données versionné de développement ou d’héritage.

Il ne correspond pas automatiquement au stockage runtime actif de
`RegistryManager`, puisque celui-ci utilise actuellement le répertoire local du
workspace.

Ce fichier ne doit pas être présenté comme une base centrale
multi-utilisateurs.

---

## 7. Schémas actuellement incompatibles

### Inventaire documentaire

`MASTER_REGISTRY.md` utilise un tableau humain comprenant notamment :

```text
ID
Nom
Catégorie
Statut
Emplacement
Projet lié
```

### Registre CLI

`sigma-core/registry/registry.json` utilise :

```text
version
objects[]
id
name
type
status
```

Certains objets de type nœud ajoutent :

```text
hostname
system
release
machine
python
uuid
workspace
```

### RegistryManager

Les enregistrements actuellement gérés peuvent contenir :

```text
id
name
version
status
```

Ces schémas ne doivent pas être fusionnés par simple copie de fichiers.

---

## 8. Sources de vérité transitoires

Conformément à ADR-001 et ADR-002 :

| Catégorie | Source transitoire |
|---|---|
| Code, tests, documentation et schémas | Git |
| Identité locale d’installation | `.sigma-workspace/configs/local.json` |
| Données runtime locales | backend de `DatabaseManager` |
| Registre affiché par la CLI historique | `sigma-core/registry/registry.json` |
| Inventaire humain historique | `MASTER_REGISTRY.md` |
| Données JSON versionnées de développement | `sigma-db/*.json` |

Aucune de ces représentations ne constitue aujourd’hui une source centrale
transactionnelle multi-utilisateurs.

PostgreSQL et l’API Sigma restent des cibles d’architecture, non une preuve de
centralisation actuellement opérationnelle.

---

## 9. Identifiants

### Identifiants d’actifs

Les actifs historiques utilisent le préfixe `SIG-` suivi d’une catégorie et
d’un numéro ou identifiant technique.

Exemples :

```text
SIG-GIT-001
SIG-PHONE-001
SIG-PC-001
SIG-NODE-...
```

### Identifiants d’enregistrements

`RegistryManager` génère actuellement des identifiants :

```text
REG-0001
REG-0002
REG-0003
```

Ces familles n’ont pas le même rôle :

- `SIG-*` désigne un actif de l’écosystème ;
- `REG-*` désigne actuellement un enregistrement géré par `RegistryManager`.

Une migration future devra décider si un enregistrement `REG-*` référence un
actif `SIG-*` ou si les deux modèles sont remplacés par un schéma commun.

---

## 10. Statuts

Les statuts historiques documentés sont :

| Statut | Sens documentaire |
|---|---|
| `Draft` | En préparation |
| `Actif` | Déclaré comme utilisé |
| `À vérifier` | Audit ou preuve nécessaire |
| `Obsolète` | À remplacer |
| `Archivé` | Conservé pour historique |

Les fichiers JSON utilisent actuellement des valeurs anglaises comme :

```text
active
```

La normalisation linguistique et sémantique reste à définir avant migration.

Un statut futur devrait distinguer au minimum :

- déclaré ;
- vérifié ;
- accessible ;
- indisponible ;
- suspendu ;
- obsolète ;
- archivé.

---

## 11. Sécurité et confidentialité

Un registre versionné ne doit pas contenir :

- de mot de passe ;
- de token ;
- de clé API ;
- de clé privée ;
- de secret MQTT ;
- d’identifiant PostgreSQL sensible ;
- de donnée personnelle non nécessaire ;
- de chemin local lorsqu’il s’agit d’une donnée partagée.

Les informations propres à une installation doivent être stockées dans les
données locales prévues par ADR-001.

La présence actuelle de chemins locaux dans une représentation transitoire doit
être traitée par migration, pas par suppression manuelle isolée.

---

## 12. Consolidation future

La consolidation des registres est autorisée uniquement après :

1. sauvegarde de chaque représentation ;
2. définition d’un schéma cible ;
3. définition du propriétaire de chaque champ ;
4. correspondance entre identifiants historiques ;
5. détection des doublons de nœuds et machines ;
6. conservation de la provenance des données ;
7. script de migration réversible ;
8. tests unitaires et d’intégration ;
9. validation des volumes et identifiants ;
10. approbation documentaire ;
11. absence de suppression silencieuse.

Aucune migration ne doit déduire automatiquement que deux nœuds ayant le même
hostname sont identiques.

---

## 13. Cible d’architecture

La cible décrite par ADR-002 prévoit :

- PostgreSQL comme source centrale des actifs partagés ;
- l’API Sigma comme interface d’écriture distante ;
- un cache ou backend local pour le fonctionnement hors ligne ;
- une identité locale séparée dans `local.json` ;
- MQTT pour les événements et états temporaires ;
- Git pour le code, la documentation et les schémas ;
- Notion comme vue documentaire et de pilotage.

Cette cible reste partiellement non implémentée.

Elle ne doit pas être présentée comme état courant.

---

## 14. Commandes de lecture actuelles

```bash
./sigma-cli/sigma.py registry
./sigma-cli/sigma.py registry list
./sigma-cli/sigma.py registry show <object-id>
./sigma-cli/sigma.py registry validate
```

Ces commandes lisent uniquement :

```text
sigma-core/registry/registry.json
```

Elles ne montrent pas le contenu runtime de `RegistryManager`.

La sortie CLI ne constitue donc pas un inventaire exhaustif de toutes les
représentations existantes.

---

## 15. Tests actuels

Le test :

```text
sigma-core/tests/test_registry_manager.py
```

couvre :

- l’existence du manager ;
- la liste ;
- le comptage ;
- la génération d’identifiant ;
- la recherche ;
- la création ;
- la mise à jour ;
- la suppression.

Il ne teste pas l’alignement entre :

- `RegistryManager` ;
- la commande CLI `registry` ;
- `MASTER_REGISTRY.md` ;
- `sigma-core/registry/registry.json` ;
- `sigma-db/registry.json`.

---

## 16. Empreintes observées

| Fichier | SHA-256 |
|---|---|
| `sigma-core/registry/registry.json` | `21805cb2b034b8fb4a9a6a3b7b758ae0aae37ee80ee24f3cc5a5b6244e2fb3b5` |
| `sigma-db/registry.json` | `e9ab25320bf9486df086624ba06bcf284685fb0c27f9f1c9ac19239455edfb04` |
| `.sigma-workspace/database/registry.json` | `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` |

Ces empreintes documentent l’état observé avant consolidation. Elles ne
désignent pas des versions canoniques définitives.

---

## 17. Sources de vérité documentaire

| Sujet | Propriétaire |
|---|---|
| Propriété et consolidation des registres | ce document |
| Séparation des données | [`architecture/decisions/ADR-001-DATA-OWNERSHIP.md`](architecture/decisions/ADR-001-DATA-OWNERSHIP.md) |
| Sources de vérité | [`architecture/decisions/ADR-002-SOURCE-OF-TRUTH.md`](architecture/decisions/ADR-002-SOURCE-OF-TRUTH.md) |
| Référence CLI | [`CLI.md`](CLI.md) |
| Architecture générale | [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) |
| Règles canoniques | [`governance/REGLES_CANONIQUES.md`](governance/REGLES_CANONIQUES.md) |
| Inventaire initial historique | [`../MASTER_REGISTRY.md`](../MASTER_REGISTRY.md) |

---

## 18. Règles de maintenance

Toute modification du domaine Registre doit :

1. identifier le fichier réellement lu ou écrit ;
2. distinguer données documentaires, locales et partagées ;
3. conserver la provenance des actifs ;
4. ne jamais transformer une déclaration en preuve ;
5. vérifier l’unicité des identifiants ;
6. documenter les changements de schéma ;
7. ajouter des tests de migration ;
8. actualiser ce document ;
9. préserver les données avant toute suppression ;
10. signaler explicitement les représentations encore transitoires.

Un fichier appelé `registry.json` ne devient pas automatiquement la source de
vérité du domaine.
