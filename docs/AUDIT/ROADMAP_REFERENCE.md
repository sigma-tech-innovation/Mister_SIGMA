# 🗺️ Mister_SIGMA — Roadmap canonique

> **Statut :** document propriétaire de la planification technique.
>
> Cette roadmap décrit l’état de la phase active et les travaux futurs.
> Elle ne constitue jamais une preuve d’implémentation.
> Le code, les tests exécutés et les rapports validés restent la vérité opérationnelle.

---

## 1. État actif

| Élément | État |
|---|---|
| Branche | `feature/SIG-07B-node-network-endpoints` |
| Commit de référence documentaire | `203d932` |
| Phase technique active | `07A — NodeNetworkManager` |
| Sous-tâche technique active | `7A.3b` |
| État de la sous-tâche | temporairement suspendue |
| Priorité immédiate | documentation, synchronisation et validation documentaire |
| Reprise autorisée | après validation complète de l’ensemble documentaire |
| Phase suivante interdite | `7B` avant validation complète de `7A` |

La suspension de `7A.3b` ne signifie pas que la phase 7A est abandonnée. Elle conserve son statut de tâche technique active et devra reprendre depuis le code et les tests réellement présents.

---

## 2. Phase 7A — Modèle et topologie statique

### Éléments actuellement établis

La note opérationnelle de phase confirme comme implémentés :

- le repository ;
- le modèle `Node` ;
- la politique réseau ;
- le cycle de vie de base.

Le module et ses tests dédiés existent :

```text
sigma-core/managers/node_network_manager.py
sigma-core/tests/test_node_network_manager.py
```

`NodeNetworkManager` n’est toutefois pas encore chargé, instancié ou enregistré par `SigmaEngine`.

### Portée restante déclarée

Les éléments restant à compléter dans la phase 7A sont :

- les endpoints ;
- les capacités ;
- les zones et régions ;
- la topologie statique ;
- les liens entre nœuds ;
- les snapshots de topologie ;
- la recherche par zone ou capacité.

### Prochaine reprise technique

Après validation documentaire :

1. inspecter le code réel de `NodeNetworkManager` ;
2. inspecter ses tests ;
3. confirmer la portée exacte de `7A.3b` ;
4. appliquer un seul changement cohérent ;
5. exécuter les validations techniques ;
6. actualiser la note opérationnelle ;
7. committer uniquement après validation complète.

---

## 3. Phase 7B — Découverte et heartbeat

> **Statut :** cible future non implémentée.

Objectifs prévus :

- découverte des nœuds ;
- heartbeat ;
- TTL ;
- expiration ;
- transitions d’état ;
- états `UNKNOWN`, `HEALTHY`, `DEGRADED`, `UNREACHABLE`, `DISABLED` et `REVOKED`.

### Prérequis

- phase 7A terminée ;
- topologie statique validée ;
- tests 7A au vert ;
- documentation 7A à jour.

---

## 4. Phase 7C — Sécurité du transport

> **Statut :** cible future non implémentée.

Objectifs prévus :

- TLS ;
- mTLS ;
- certificats ;
- identité cryptographique des nœuds ;
- rotation des clés ;
- révocation ;
- politique de confiance explicite.

### Prérequis

- phase 7B terminée ;
- découverte et heartbeat validés ;
- modèle d’identité réseau stabilisé.

---

## 5. Phase 7D — Routage réseau

> **Statut :** cible future non implémentée.

Objectifs prévus :

- sélection déterministe des chemins ;
- coûts ;
- latence ;
- priorité ;
- mécanismes de repli ;
- routage multi-saut ;
- détection des cycles ;
- cache avec invalidation.

### Prérequis

- phase 7C terminée ;
- transport sécurisé ;
- topologie dynamique fiable.

---

## 6. Phase 7E — Tests réseau et résilience

> **Statut :** cible future non implémentée.

Objectifs prévus :

- tests de topologie ;
- tests de heartbeat ;
- tests TLS et mTLS ;
- tests de routage ;
- tests de partitions réseau ;
- tests de reprise ;
- tests de résilience ;
- vérification des comportements dégradés.

### Prérequis

- phases 7A à 7D terminées ;
- interfaces de test stabilisées ;
- scénarios réseau reproductibles.

---

## 7. Phase 7F — Validation finale de la phase 07

> **Statut :** cible future non commencée.

La phase 07 ne pourra être considérée comme terminée qu’après :

- compilation réussie ;
- tests ciblés au vert ;
- suite complète au vert ;
- Doctor : OK ;
- Health : OK ;
- Sync Validate : prêt ;
- `git diff --check` sans erreur ;
- revue du diff ;
- documentation actualisée ;
- commit atomique ;
- fusion validée.

---

## 8. Phase 8 — ReplicationManager

> **Statut :** cible future non implémentée.

Objectif général : propager des unités versionnées de manière fiable, idempotente et traçable.

Fonctions envisagées :

- réplication idempotente ;
- traitement par lots ;
- curseurs ;
- accusés de réception ;
- push, pull ou mode hybride ;
- reprise après interruption ;
- détection des doublons.

### Prérequis

- phase 07 entièrement validée ;
- modèle réseau stable ;
- stratégie de versionnement définie.

---

## 9. Phase 9 — ConflictManager

> **Statut :** cible future non implémentée.

Objectif général : détecter les écritures concurrentes et appliquer une politique explicite et déterministe.

Fonctions envisagées :

- détection des versions concurrentes ;
- classification des conflits ;
- conservation des versions candidates ;
- résolution déterministe ;
- résolution automatique ou manuelle ;
- audit complet.

### Prérequis

- phase 8 terminée ;
- réplication versionnée validée ;
- règles de résolution formalisées.

---

## 10. Phase 10 — SynchronizationEngine

> **Statut :** cible future non implémentée.

Objectif général : orchestrer la réplication, les conflits, le fonctionnement hors ligne, la reprise et la convergence globale.

Fonctions envisagées :

- orchestration de la réplication ;
- synchronisation bidirectionnelle ;
- fonctionnement hors ligne ;
- checkpoints ;
- résolution des conflits ;
- reprise après interruption ;
- convergence ;
- rapports de synchronisation.

### Prérequis

- phases 8 et 9 terminées ;
- réplication et gestion des conflits validées ;
- observabilité et reprise définies.

---

## 11. Dépendances entre les phases

```text
Documentation et synchronisation
            |
            v
Reprise de 7A.3b
            |
            v
Validation complète de 7A
            |
            v
7B -> 7C -> 7D -> 7E -> 7F
                         |
                         v
                    Phase 8
                         |
                         v
                    Phase 9
                         |
                         v
                    Phase 10
```

Aucune phase future ne doit commencer avant validation complète de ses prérequis.

---

## 12. Interfaces et plateformes

Les interfaces ne définissent pas l’architecture métier.

Les options possibles comprennent :

- CLI ;
- API ;
- interface web ;
- application mobile ;
- interface embarquée ;
- autres adaptateurs futurs.

Un écran, une résolution, un contrôleur, un ESP32 ou un ESP32 CYD ne constitue pas une exigence obligatoire du noyau.

Les contraintes correspondantes sont gouvernées par [`UX-002`](governance/REGLES_CANONIQUES.md#%EF%B8%8F-ux-002--ind%C3%A9pendance-du-mat%C3%A9riel-et-des-interfaces).

---

## 13. Intégrations externes

Les services suivants appartiennent à la vision d’écosystème, mais leur mention ne prouve pas leur intégration au dépôt :

- GitHub ;
- VPS ;
- Notion ;
- n8n ;
- Google Drive ;
- Gmail ;
- Docker Desktop ;
- Home Assistant ;
- ESPHome ;
- Mosquitto.

Leur statut doit être démontré par du code, une configuration, un test ou un rapport d’exécution.

---

## 14. Sources documentaires

| Sujet | Document propriétaire |
|---|---|
| État opérationnel immédiat | [`NOTE_CONTINUITE_PHASE_07.md`](dossier_maitre_continuite/sources/NOTE_CONTINUITE_PHASE_07.md) |
| Architecture synthétique | [`ARCHITECTURE.md`](architecture/ARCHITECTURE.md) |
| Règles canoniques | [`REGLES_CANONIQUES.md`](governance/REGLES_CANONIQUES.md) |
| Traçabilité des 40 sources | [`REGISTRE_TRACABILITE_40_PARTIES.md`](dossier_maitre_continuite/REGISTRE_TRACABILITE_40_PARTIES.md) |
| Synthèse documentaire | [`NOTE_SYNTHESE_TRAVAIL_DOCUMENTAIRE.md`](dossier_maitre_continuite/NOTE_SYNTHESE_TRAVAIL_DOCUMENTAIRE.md) |
| Procédures détaillées | `dossier_maitre_continuite/sources/GUIDE_TECHNIQUE_MAITRE.docx` |
| Preuves d’implémentation | code, tests et rapports validés |

---

## 15. Règles de mise à jour

Cette roadmap doit être mise à jour uniquement lorsqu’un des événements suivants survient :

- changement de phase active ;
- validation ou clôture d’une phase ;
- modification des dépendances ;
- ajout ou retrait d’une cible future ;
- décision architecturale acceptée ;
- preuve nouvelle modifiant le statut réel.

Une fonctionnalité planifiée ne doit jamais être marquée comme terminée sans preuve vérifiable.
