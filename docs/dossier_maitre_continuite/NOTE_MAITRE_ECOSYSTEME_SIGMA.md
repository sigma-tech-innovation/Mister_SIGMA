# 🧭 Mister_SIGMA — Note maître de continuité de l’écosystème

> **Statut documentaire :** référence consolidée
> **État observé :** 15 juillet 2026
> **Branche active observée :** `feature/SIG-07-node-network-manager`
> **Commit observé :** `ee97a7c` — `feat(node): add node lifecycle operations`

---

## 1. 🎯 Finalité de cette note

Cette note fournit un point d’entrée unique vers l’ensemble de l’écosystème Sigma. Elle ne remplace pas le dépôt Git, le Guide technique maître, les 40 parties du Dossier Maître de Continuité, les ADR, les rapports de phases ni le Master Backlog.

Elle centralise uniquement la hiérarchie des sources de vérité, l’état réel observé, l’organisation de l’écosystème, les responsabilités documentaires, la tâche active, les règles de reprise et les références vers les documents détaillés.

Une information générale n’est écrite qu’une seule fois. Les détails restent dans leur document propriétaire.

---

## 2. 🏛️ Hiérarchie des sources de vérité

| Priorité | Source | Responsabilité |
|---:|---|---|
| 1 | 💻 Dépôt Git et tests | État réellement implémenté |
| 2 | 🧾 ADR acceptés | Décisions d’architecture durables |
| 3 | ✅ Rapports de phases | Preuves de validation et de clôture |
| 4 | 📝 Note de phase active | État opérationnel immédiat |
| 5 | 📕 Guide technique maître | Spécification d’exécution des phases |
| 6 | 📚 Dossier Maître en 40 parties | Continuité, architecture et cible détaillée |
| 7 | 📋 SIGMA FORCE Master Backlog | Gouvernance, epics et règles globales |
| 8 | 🗺️ Roadmaps | Planification, jamais preuve d’implémentation |
| 9 | 🔗 Notion et vues externes | Présentation et pilotage |

### Règle d’arbitrage

En cas de contradiction :

1. le code et les résultats réellement exécutés prévalent ;
2. les ADR déterminent l’architecture acceptée ;
3. les rapports validés prouvent les jalons terminés ;
4. la documentation prospective reste marquée **prévue** ou **cible**.

---

## 3. 🌍 Vision de l’écosystème Sigma

Mister_SIGMA vise une plateforme d’ingénierie distribuée, multi-utilisateur, multi-organisation, multi-workspace, multi-machine, multi-plateforme, modulaire, réutilisable, observable et synchronisable.

### Plateformes cibles

- 🪟 Windows
- 🐧 Linux
- 📱 Android
- ⌨️ Termux
- 🍓 Raspberry Pi
- 🐳 Docker
- ☁️ Cloud et VPS
- 🔌 ESP32 et systèmes embarqués, comme cibles optionnelles ou expérimentales

Cette liste décrit des plateformes possibles. Elle ne rend obligatoire aucun matériel, écran, format d’affichage ou environnement d’exécution précis.

Le cœur métier doit rester indépendant de l’interface. Les interfaces CLI, API, web, mobile ou embarquées sont des adaptateurs remplaçables.

ESP32 CYD peut servir de prototype ou de cible expérimentale, sans garantie qu’il devienne la plateforme d’interface définitive.

### Services et technologies cibles

- PostgreSQL
- API
- CLI
- MQTT
- Notion
- Home Assistant
- ESPHome
- n8n
- intelligence artificielle
- monitoring
- automatisations Platinum Scripts

### Devise

> **Write once. Reuse everywhere.**

---

## 4. 🔄 Workflow officiel

```text
IDEA
  → ANALYZE
  → DESIGN
  → BUILD
  → TEST
  → VALIDATE
  → DOCUMENT
  → SYNC
  → RELEASE
  → MONITOR
  → IMPROVE
```

### Cycle d’une tâche

```text
Analyze → Develop → Test → Validate → Document → Synchronize → Close
```

Une tâche n’est clôturée que lorsque son résultat est explicitement **OK**.

---

## 5. 🔒 Règles absolues de développement

1. Une seule tâche active à la fois.
2. Ne jamais commencer la tâche suivante avant validation de la tâche courante.
3. Une seule source de vérité par catégorie de données.
4. Réutiliser et étendre avant de créer un nouveau composant.
5. Aucun changement d’architecture pendant une tâche active.
6. Toute décision durable doit être documentée.
7. Les scripts répétitifs doivent être automatisés et idempotents.
8. Les secrets ne doivent jamais être versionnés ou affichés dans les logs.
9. Aucune fonctionnalité future ne doit être présentée comme implémentée.
10. Aucun commit ni merge ne doit être proposé avec un contrôle obligatoire en échec.

---

## 6. 🧪 Pipeline obligatoire de validation

Après toute modification fonctionnelle :

1. inspection ciblée avec `grep` ;
2. lecture de la zone avec `sed` ;
3. vérification d’une ancre unique ;
4. patch localisé ;
5. compilation avec `py_compile` ;
6. tests ciblés ;
7. suite globale `pytest` ;
8. Sigma Doctor ;
9. Sigma Health ;
10. Sigma Sync Validate ;
11. `git diff --check` ;
12. revue du diff ;
13. commit atomique uniquement après validation.

Les remplacements globaux sur des ancres ambiguës sont interdits.

---

## 7. 📍 État réel observé du projet

### Référence Git

| Élément | Valeur observée |
|---|---|
| Branche | `feature/SIG-07-node-network-manager` |
| Commit | `ee97a7c` |
| Dernier jalon | opérations de cycle de vie des nœuds |
| Working tree | documentation non suivie dans `docs/dossier_maitre_continuite/` |

### Phases

| Phase | Manager | État |
|---:|---|---|
| 01 | OrganizationManager | ✅ Socle réalisé |
| 02 | WorkspaceManager V2 | ✅ Socle réalisé |
| 03 | MembershipManager | ✅ Socle réalisé |
| 04 | AuthenticationManager | ✅ Rapport présent |
| 05 | SessionManager | ✅ Rapport présent |
| 06 | DeviceManager | ✅ Rapport présent |
| 07A | NodeNetworkManager — fondations | 🚧 En cours |
| 07B | Découverte et heartbeat | ⏳ Prévue |
| 07C | Sécurité transport | ⏳ Prévue |
| 07D | Routage | ⏳ Prévue |
| 07E | Tests réseau | ⏳ Prévue |
| 07F | Validation et intégration | ⏳ Prévue |
| 08 | ReplicationManager | ⏳ Prévue |
| 09 | ConflictManager | ⏳ Prévue |
| 10 | SynchronizationEngine | ⏳ Prévue |

### Phase active : 07A

Éléments présents dans le socle actuel :

- modèle `Node` ;
- politique réseau ;
- repository mémoire ;
- façade `NodeNetworkManager` ;
- création et recherche ;
- cycle de vie de base ;
- validation ;
- snapshot.

Éléments restant dans le périmètre 7A :

- endpoints structurés ;
- capacités ;
- zones ;
- régions ;
- liens logiques ;
- coût et latence ;
- recherches étendues ;
- invariants de topologie ;
- tests associés.

### Limite de phase

Ne pas introduire dans 7A : découverte automatique, heartbeat, TTL, TLS ou mTLS, routage actif, réplication, résolution de conflits ou synchronisation distribuée.

---

## 8. 🧠 Architecture fonctionnelle

```text
Context
  → Identity
  → Authentication
  → Authorization
  → Organization
  → Workspace
  → Membership
  → Session
  → Device
  → Node
  → Replication
  → Conflict
  → Synchronization
```

### Principes

- modèles métier immuables lorsque le domaine l’exige ;
- responsabilités séparées ;
- repositories spécialisés ;
- façades publiques stables ;
- composition avant héritage ;
- persistance découplée des interfaces ;
- moteur métier indépendant du matériel et de la résolution d’affichage ;
- interfaces traitées comme des adaptateurs remplaçables ;
- sérialisation explicite ;
- validation centralisée ;
- préparation à la distribution sans implémentation prématurée.

---

## 9. 🧩 État des composants du dépôt

### 🧠 Sigma Core

Le dépôt contient notamment les managers d’authentification, autorisation, configuration, contexte, fournisseurs de données, base de données, appareils, identité, configuration locale, memberships, nœuds, réseau de nœuds, organisations, packages, plugins, projets, registre, releases, services, sessions, synchronisation, tâches, templates, utilisateurs et workspaces.

Des backends JSON, SQLite et PostgreSQL sont présents derrière une abstraction de persistance.

### ⌨️ CLI

La CLI est la couche d’interface la plus développée. Elle couvre notamment l’authentification, les appareils, les sessions, la base de données, les projets, les packages, le registre, les templates, les releases, la configuration locale, la sauvegarde, la restauration, Doctor, Health, Sync Validate, les diagnostics Git, la recherche, les statistiques et les résumés.

### 🌐 API

Éléments non vides observés : `auth.py`, `devices.py`, `sessions.py`.

Éléments encore vides observés : `server.py`, `router.py`, `nodes.py`, `packages.py`, `projects.py`, `registry.py`, `__init__.py`.

L’API ne doit donc pas être décrite comme un service complet déjà opérationnel.

### 🔌 Plugins

Le socle comprend un `PluginManager`, un plugin `core-engine` minimal et un plugin `demo` minimal. L’écosystème de plugins reste embryonnaire.

### 🗄️ Persistance

Le dépôt contient des fichiers JSON pour plusieurs registres, des backends JSON, SQLite et PostgreSQL, ainsi qu’une stratégie d’évolution vers PostgreSQL comme source transactionnelle partagée.

### 🏠 Intégrations et plateformes

| Domaine | État observé |
|---|---|
| Home Assistant | ⚪ Placeholder |
| ESPHome | ⚪ Placeholder |
| Firmware | ⚪ Placeholder |
| Hardware | ⚪ Placeholder |
| Raspberry Pi | ⚪ Placeholder |
| Intégrations génériques | ❌ Répertoire absent |
| Plugins | 🟡 Socle minimal |
| Notion | 🟡 Provider présent |
| PostgreSQL | 🟡 Backend présent |
| API | 🟡 Partielle |
| CLI | 🟢 Développée |

---

## 10. 🗃️ Stratégie des données et sources de vérité

### Données globales

Doivent être versionnées lorsqu’elles décrivent le code, les schémas, les modèles de configuration, la documentation, les décisions d’architecture et les scripts réutilisables.

### Données locales

Doivent rester hors Git lorsqu’elles décrivent la machine, l’installation, l’identité locale, les chemins locaux ou la configuration propre à un poste.

### Secrets

Ne doivent apparaître ni dans Git, ni dans les documents, ni dans les commandes, ni dans les logs, ni dans les rapports de validation.

### Cible des systèmes

| Système | Responsabilité cible |
|---|---|
| Git | code, documentation, schémas et modèles |
| Fichiers locaux ignorés | identité locale et secrets |
| JSON | développement local et compatibilité transitoire |
| PostgreSQL | données transactionnelles partagées |
| API | interface contrôlée d’écriture distante |
| Notion | documentation et vues de gestion |
| MQTT | événements et télémétrie |
| VPS | hébergement des services |

Notion, MQTT et les fichiers JSON ne doivent pas être traités comme des bases transactionnelles maîtres partagées.

---

## 11. 📋 SIGMA FORCE — Carte des epics

| Epic | Domaine |
|---:|---|
| 01 | Mister Sigma ESP32 |
| 02 | Sigma Desktop |
| 03 | Sigma Core |
| 04 | PostgreSQL |
| 05 | Notion |
| 06 | PowerShell Platinum |
| 07 | WSL |
| 08 | Linux |
| 09 | Android |
| 10 | Termux |
| 11 | Raspberry Pi |
| 12 | Cloud / VPS |
| 13 | Intelligence artificielle |
| 14 | Laboratory |
| 15 | Documentation |
| 16 | Testing & QA |
| 17 | Deployment |
| 18 | Monitoring |
| 19 | Cybersecurity |
| 20 | Business & Administration |

### Catégories d’objets

- Asset
- Object
- Action
- Platform
- Automation
- Data
- Project

---

## 12. 🗺️ Roadmap distribuée

### Phase 7 — Réseau de nœuds

- **7A** : modèle et topologie
- **7B** : découverte, heartbeat et TTL
- **7C** : sécurité transport et confiance
- **7D** : routage et sélection de chemin
- **7E** : tests réseau et résilience
- **7F** : clôture, documentation et fusion

### Phase 8 — Réplication

Objectif : propager des unités versionnées de manière fiable, idempotente et traçable.

### Phase 9 — Conflits

Objectif : détecter les écritures concurrentes et appliquer une politique explicite et déterministe.

### Phase 10 — Synchronisation

Objectif : orchestrer réplication, résolution de conflits, fonctionnement hors ligne, reprise et convergence globale.

Aucune phase future ne doit être commencée avant validation complète de ses prérequis.

---

## 13. 📚 Architecture documentaire canonique

| Sujet | Document propriétaire |
|---|---|
| Vision et gouvernance | Cette note maître |
| Règles normatives communes | `../governance/REGLES_CANONIQUES.md` |
| État opérationnel immédiat | `sources/NOTE_CONTINUITE_PHASE_07.md` |
| Exécution des phases 1 à 10 | `sources/GUIDE_TECHNIQUE_MAITRE.docx` |
| Epics et gouvernance | `sources/SIGMA_FORCE_MASTER_BACKLOG_v1.0.txt` |
| Sources détaillées d’architecture | Dossier Maître, parties 01 à 40, avec traçabilité dans `REGISTRE_TRACABILITE_40_PARTIES.md` |
| Propriété des données | `ADR-001-DATA-OWNERSHIP.md` |
| Sources de vérité | `ADR-002-SOURCE-OF-TRUTH.md` |
| Résultats de phases | `docs/development/phase_XX/RESULT.md` |
| Architecture synthétique | `docs/architecture/ARCHITECTURE.md` |
| Roadmap active | `docs/ROADMAP.md` |
| Changements publiés | `docs/CHANGELOG.md` |
| Utilisation CLI | `docs/CLI.md` |

### Politique anti-duplication

- cette note contient les synthèses ;
- le Guide contient les procédures exécutables ;
- les parties 19 à 37 contiennent les détails des managers et phases ;
- les ADR contiennent les décisions ;
- les rapports contiennent les preuves ;
- les roadmaps contiennent uniquement les travaux prévus ;
- les documents vides ne doivent pas recevoir de copie brute d’un autre document.

---

## 14. 📖 Classement des 40 parties

### Groupe A — Fondation et continuité

Parties 01 à 18 : vision, historique, architecture, méthodologie, tests, roadmap, état réel, décisions, reprise, maintenance et validation.

### Groupe B — Managers du socle

Parties 19 à 28 : ContextManager, IdentityManager, AuthorizationManager, OrganizationManager, WorkspaceManager V2, MembershipManager, AuthenticationManager, SessionManager, DeviceManager et NodeNetworkManager.

### Groupe C — Réseau et distribution

Parties 29 à 37 : topologie, découverte, heartbeat, transport sécurisé, routage, tests réseau, clôture de phase 07, réplication, conflits et synchronisation.

### Groupe D — Référence globale

Parties 38 à 40 : architecture cible complète, conventions et guide de reprise final.

---

## 15. 🚦 Tâche active autorisée

### Priorité immédiate

Terminer la documentation et la synchronisation, puis valider l’ensemble documentaire.

### Phase technique suspendue

`07A — NodeNetworkManager`

### Sous-tâche technique suspendue

`7A.3b`

À la reprise, poursuivre uniquement le bloc de topologie statique prévu, après inspection précise du fichier réel et des tests associés.

### Condition de reprise

La sous-tâche `7A.3b` ne doit reprendre qu’après validation complète de la documentation et de la synchronisation.

### Interdictions immédiates

- ne pas reprendre le développement technique avant validation documentaire ;
- ne pas démarrer 7B ;
- ne pas refondre l’architecture ;
- ne pas créer un second manager concurrent ;
- ne pas effectuer de remplacement global ;
- ne pas modifier simultanément plusieurs domaines ;
- ne pas committer la documentation avant revue du diff.

---

## 16. ▶️ Procédure de reprise

Avant toute nouvelle intervention :

```bash
git branch --show-current
git status --short
git log -5 --oneline --decorate
git diff --check
```

Ensuite :

1. identifier la tâche active ;
2. ouvrir son document propriétaire ;
3. inspecter le code réel ;
4. comparer avec les tests présents ;
5. appliquer un seul changement ;
6. exécuter tout le pipeline de validation ;
7. actualiser la note opérationnelle ;
8. actualiser cette note uniquement si la structure globale change.

---

## 17. ⚠️ Dette documentaire restante

- l’API partielle doit être distinguée de la cible complète ;
- les placeholders ne sont pas des intégrations opérationnelles ;
- la note `.mdc` doit rester qualifiée comme historique non canonique tant que sa conservation définitive n’est pas décidée ;
- les rapports des phases 01 à 03 et 07 doivent être fondés sur des preuves réelles.

---

## 18. ✅ Définition documentaire de « solide »

La documentation est cohérente lorsque :

- chaque information possède un propriétaire ;
- l’état réel et la cible future sont séparés ;
- aucun placeholder n’est présenté comme fonctionnel ;
- les ADR sont reliés aux sections qu’ils gouvernent ;
- chaque phase terminée possède un rapport ;
- chaque phase active possède une note opérationnelle ;
- la roadmap est alignée sur les phases réelles ;
- le README reste une présentation ;
- la CLI et l’API disposent de documents distincts ;
- les références permettent une reprise sans supposition ;
- les répétitions sont remplacées par des renvois.

---

## 19. 📎 Références locales

- `docs/dossier_maitre_continuite/REGISTRE_TRACABILITE_40_PARTIES.md`
- `docs/dossier_maitre_continuite/sources/GUIDE_TECHNIQUE_MAITRE.docx`
- `docs/dossier_maitre_continuite/sources/SIGMA_FORCE_MASTER_BACKLOG_v1.0.txt`
- `docs/dossier_maitre_continuite/sources/NOTE_CONTINUITE_PHASE_07.md`
- `docs/architecture/decisions/ADR-001-DATA-OWNERSHIP.md`
- `docs/architecture/decisions/ADR-002-SOURCE-OF-TRUTH.md`
- `docs/development/phase_04/PLAN.md`
- `docs/development/phase_04/RESULT.md`
- `docs/development/phase_05/RESULT.md`
- `docs/development/phase_06/RESULT.md`
- `docs/dossier_maitre_continuite/NOTE_SYNTHESE_TRAVAIL_DOCUMENTAIRE.md` — synthèse canonique active
- `docs/dossier_maitre_continuite/NOTE_SYNTHESE_TRAVAIL_DOCUMENTAIRE.mdc` — version historique non canonique, conservée sans modification

---

## 20. 🧭 Principe final

> La documentation guide le travail.
> Les ADR fixent les décisions.
> Les rapports prouvent les validations.
> Le dépôt Git reste la vérité finale sur ce qui existe réellement.
