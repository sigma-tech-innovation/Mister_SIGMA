# 📚 Mister_SIGMA — Index documentaire canonique

> Point d’entrée officiel vers la documentation du dépôt.
> Le code, les tests et les résultats réellement exécutés restent la vérité finale.

---

## 🧭 Continuité et gouvernance

| Document | Responsabilité |
|---|---|
| [`governance/REGLES_CANONIQUES.md`](governance/REGLES_CANONIQUES.md) | Règles normatives communes du projet |
| [`dossier_maitre_continuite/NOTE_MAITRE_ECOSYSTEME_SIGMA.md`](dossier_maitre_continuite/NOTE_MAITRE_ECOSYSTEME_SIGMA.md) | Vue consolidée de l’écosystème |
| [`dossier_maitre_continuite/REGISTRE_TRACABILITE_40_PARTIES.md`](dossier_maitre_continuite/REGISTRE_TRACABILITE_40_PARTIES.md) | Traçabilité des 40 DOCX officiels et attribution de leurs propriétaires documentaires |
| [`dossier_maitre_continuite/sources/NOTE_CONTINUITE_PHASE_07.md`](dossier_maitre_continuite/sources/NOTE_CONTINUITE_PHASE_07.md) | État opérationnel de la phase active |
| [`dossier_maitre_continuite/sources/SIGMA_FORCE_MASTER_BACKLOG_v1.0.txt`](dossier_maitre_continuite/sources/SIGMA_FORCE_MASTER_BACKLOG_v1.0.txt) | Gouvernance SIGMA FORCE et epics |
| `dossier_maitre_continuite/sources/GUIDE_TECHNIQUE_MAITRE.docx` | Spécification détaillée des phases 1 à 10 |

---

## 🏗️ Architecture

| Document | Responsabilité |
|---|---|
| [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) | Architecture synthétique du dépôt |
| [`architecture/decisions/ADR-001-DATA-OWNERSHIP.md`](architecture/decisions/ADR-001-DATA-OWNERSHIP.md) | Propriété et séparation des données |
| [`architecture/decisions/ADR-002-SOURCE-OF-TRUTH.md`](architecture/decisions/ADR-002-SOURCE-OF-TRUTH.md) | Sources de vérité et réconciliation |

---

## ✅ Développement et preuves

| Phase | Manager | Document |
|---:|---|---|
| 04 | AuthenticationManager | [`development/phase_04/PLAN.md`](development/phase_04/PLAN.md) |
| 04 | AuthenticationManager | [`development/phase_04/RESULT.md`](development/phase_04/RESULT.md) |
| 05 | SessionManager | [`development/phase_05/RESULT.md`](development/phase_05/RESULT.md) |
| 06 | DeviceManager | [`development/phase_06/RESULT.md`](development/phase_06/RESULT.md) |
| 07 | NodeNetworkManager | Note opérationnelle et documentation en cours |

Les rapports absents ne doivent être créés qu’à partir de preuves Git et de validations réellement exécutées.

---

## 🗺️ Planification

| Document | Statut |
|---|---|
| [`ROADMAP.md`](ROADMAP.md) | Roadmap canonique active : phase 7A et cibles futures |
| [`../ROADMAP.md`](../ROADMAP.md) | Point d’entrée historique vers la roadmap canonique |

Une roadmap décrit des travaux prévus. Elle ne prouve jamais qu’une fonctionnalité est implémentée.

---

## ⌨️ Interfaces

| Document | Statut |
|---|---|
| [`CLI.md`](CLI.md) | Référence canonique active des 46 routes publiques |
| API | Documentation dédiée à créer après inventaire des routes réelles |
| [`cli/SIGMA_CLI_MVP.md`](cli/SIGMA_CLI_MVP.md) | Point d’entrée de compatibilité vers la référence canonique |

La CLI est actuellement plus développée que l’API. L’API reste partielle.

---

## 🗄️ Registres et configuration

| Document | Statut |
|---|---|
| [`REGISTRY.md`](REGISTRY.md) | Référence canonique des propriétaires, copies transitoires et règles de consolidation |
| [`WORKSPACE.md`](WORKSPACE.md) | Référence canonique du workspace local, de la CLI historique et de WorkspaceManager V2 |
| [`../MASTER_REGISTRY.md`](../MASTER_REGISTRY.md) | Registre historique racine |

---

## 📝 Versions et historique

| Document | Statut |
|---|---|
| [`CHANGELOG.md`](CHANGELOG.md) | Journal canonique des releases et évolutions non publiées |
| [`../CHANGELOG.md`](../CHANGELOG.md) | Point d’entrée historique vers le journal canonique |

---

## 🔌 Écosystème et intégrations

| Domaine | État observé |
|---|---|
| Plugins | Socle minimal |
| Notion | Provider présent |
| PostgreSQL | Backend présent |
| API | Partielle |
| CLI | Développée |
| Home Assistant | Placeholder |
| ESPHome | Placeholder |
| Firmware | Placeholder |
| Hardware | Placeholder |
| Raspberry Pi | Placeholder |
| Intégrations génériques | Répertoire absent |

Un placeholder ne doit jamais être présenté comme une intégration opérationnelle.

---

## 🔄 Règle de synchronisation documentaire

Chaque sujet possède un document propriétaire :

1. la note maître contient la synthèse ;
2. les ADR contiennent les décisions ;
3. les rapports contiennent les preuves ;
4. le Guide technique contient les procédures détaillées ;
5. les roadmaps contiennent uniquement la cible future ;
6. les documents d’interface décrivent uniquement les commandes ou routes réellement présentes ;
7. les répétitions doivent être remplacées par des liens.

---

## 🚦 État actif

- Branche : `feature/SIG-07B-node-network-endpoints`
- Commit de référence : `203d932`
- Phase technique active : `07A`
- Manager : `NodeNetworkManager`
- Priorité immédiate : terminer la documentation et la synchronisation
- Validation requise : valider l’ensemble documentaire avant la reprise technique
- Sous-tâche technique suspendue : `7A.3b`
- Portée technique à reprendre ensuite : topologie statique de la phase 7A
- Phase 7B interdite avant validation complète de 7A
- Règle d’interface : [`UX-002`](governance/REGLES_CANONIQUES.md#%EF%B8%8F-ux-002--ind%C3%A9pendance-du-mat%C3%A9riel-et-des-interfaces)
