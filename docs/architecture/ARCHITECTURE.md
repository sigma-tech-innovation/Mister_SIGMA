# 🏗️ Mister_SIGMA — Architecture du dépôt

> **Statut :** document propriétaire de l’architecture synthétique.
>
> Le code, les tests exécutés et les rapports de validation constituent la preuve de l’état réel.
> Les ADR gouvernent les décisions structurelles.
> Les composants futurs sont séparés explicitement des composants présents.

## 1. Périmètre

Mister_SIGMA est organisé autour d’un moteur Python, `SigmaEngine`, de managers spécialisés, de fournisseurs de données et de stockages locaux.

Le noyau métier doit rester indépendant du matériel, de l’écran, de la résolution, de l’interface utilisateur et de la plateforme d’exécution.

Les interfaces CLI, API, web, mobile ou embarquées sont des adaptateurs remplaçables. Un ESP32 ou un ESP32 CYD peut servir de prototype ou de cible expérimentale, mais ne constitue pas une dépendance architecturale obligatoire.

Règle propriétaire : [`UX-002`](../governance/REGLES_CANONIQUES.md#%EF%B8%8F-ux-002--ind%C3%A9pendance-du-mat%C3%A9riel-et-des-interfaces).

## 2. Moteur actuel

Le fichier `sigma-core/engine.py` définit `SigmaEngine`.

Le moteur fixe la racine du dépôt, expose les chemins de données et de projets, instancie les composants intégrés, les publie dans `self.managers` et fournit des utilitaires JSON.

```python
engine = SigmaEngine()
```

## 3. Composants actuellement composés par `SigmaEngine`

### Données et configuration

- `DatabaseManager`
- `DatabaseConfigManager`
- `DataProviderManager`
- `NotionProvider`
- `ConfigManager`
- `LocalConfigManager`
- `LocalConfigMigrationManager`

### Projets et actifs techniques

- `ProjectManager`
- `NodeManager`
- `PackageManager`
- `RegistryManager`
- `TemplateManager`
- `ReleaseManager`
- `PluginManager`

### Identité, organisation et accès

- `IdentityManager`
- `ContextManager`
- `AuthorizationManager`
- `OrganizationManager`
- `UserManager`
- `MembershipManager`
- `AuthenticationManager`
- `SessionManager`

### Exploitation et orchestration

- `DeviceManager`
- `WorkspaceManager`
- `ServiceManager`
- `LoggerManager`
- `EventManager`
- `TaskManager`
- `SyncManager`
- `ApiManager`

## 4. Composant présent hors de la composition actuelle

`NodeNetworkManager` existe dans :

```text
sigma-core/managers/node_network_manager.py
```

Des tests dédiés existent dans :

```text
sigma-core/tests/test_node_network_manager.py
```

Cependant, `NodeNetworkManager` n’est pas actuellement chargé, instancié ou enregistré par `SigmaEngine`.

État de continuité :

- phase technique active : `07A` ;
- sous-tâche suspendue : `7A.3b` ;
- priorité immédiate : documentation et synchronisation ;
- reprise technique après validation documentaire ;
- phase `7B` interdite avant validation complète de `7A`.

## 5. Sources de vérité architecturales

| Sujet | Propriétaire |
|---|---|
| Architecture synthétique | ce document |
| Propriété et séparation des données | [`ADR-001`](decisions/ADR-001-DATA-OWNERSHIP.md) |
| Sources de vérité et réconciliation | [`ADR-002`](decisions/ADR-002-SOURCE-OF-TRUTH.md) |
| Règles communes | [`REGLES_CANONIQUES.md`](../governance/REGLES_CANONIQUES.md) |
| État opérationnel de la phase 07 | [`NOTE_CONTINUITE_PHASE_07.md`](../dossier_maitre_continuite/sources/NOTE_CONTINUITE_PHASE_07.md) |
| Traçabilité des 40 parties | [`REGISTRE_TRACABILITE_40_PARTIES.md`](../dossier_maitre_continuite/REGISTRE_TRACABILITE_40_PARTIES.md) |
| Preuve d’implémentation | code, tests et rapports exécutés |

## 6. Cibles futures non implémentées

Les composants suivants n’ont pas été trouvés dans le code Python actuel :

- `EventBus`
- `Scheduler`
- `ReplicationManager`
- `ConflictManager`
- `SynchronizationEngine`

Ils ne doivent pas être présentés comme opérationnels.

Les phases futures restent des objectifs : `7B`, `7C`, `7D`, `7E`, `7F`, phase 8, phase 9 et phase 10.

## 7. Plateformes et intégrations

Plateformes possibles : Android, Linux, Windows, macOS, WSL, VPS, Raspberry Pi et systèmes embarqués expérimentaux.

Intégrations envisagées : GitHub, VPS, Notion, n8n, Google Drive, Gmail, Docker Desktop, Home Assistant, ESPHome et Mosquitto.

Leur présence dans la vision globale ne constitue pas une preuve d’intégration au dépôt.

## 8. Règles d’évolution

Toute évolution architecturale doit :

1. inspecter le code et les tests réels ;
2. distinguer l’implémenté, le partiel et le futur ;
3. utiliser un ADR pour une décision structurelle durable ;
4. conserver un seul document propriétaire par sujet ;
5. éviter toute dépendance du noyau envers une interface ou un matériel précis ;
6. mettre à jour ce document lorsque la composition réelle de `SigmaEngine` change.
