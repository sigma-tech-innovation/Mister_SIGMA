# Phase 04 — AuthenticationManager

## Objectif

Construire une authentification locale sécurisée et extensible, indépendante
des interfaces CLI, API et des plateformes d’exécution.

PostgreSQL deviendra la source de vérité serveur. Les tests unitaires utilisent
des dépendances injectées et ne nécessitent aucun service externe.

## Limites de la phase

Cette phase couvre :

- identité authentifiable ;
- identifiants et credentials ;
- hash et vérification des mots de passe ;
- verrouillage et désactivation ;
- événements d’authentification ;
- audit minimal ;
- contrats stables pour SessionManager.

Cette phase ne couvre pas encore :

- sessions persistantes ;
- refresh tokens ;
- appareils de confiance ;
- OAuth/OIDC ;
- MFA matériel ;
- réseau de nœuds ;
- réplication ;
- synchronisation distribuée.

## Découpage

### 4A — Contrats et modèle

- AuthenticationManager ;
- CredentialRecord ;
- statuts et invariants ;
- erreurs stables ;
- tests unitaires.

### 4B — Stockage des credentials

- repository local transitoire ;
- unicité par utilisateur ;
- séparation données utilisateur / secrets ;
- compatibilité PostgreSQL future ;
- tests de persistance.

### 4C — Hash, vérification et politiques

- PBKDF2 standard Python par défaut ;
- sel aléatoire ;
- comparaison constante ;
- politique minimale ;
- verrouillage après échecs ;
- tests sécurité.

### 4D — Service applicatif et événements

- authenticate ;
- set/change/revoke password ;
- événements ;
- audit ;
- erreurs normalisées.

### 4E — API et CLI

- commandes non interactives ;
- aucune fuite de secret ;
- codes de sortie stables ;
- sortie JSON ;
- tests de contrat.

### 4F — Intégration

- compilation ;
- tests ;
- doctor ;
- health ;
- sync validate ;
- rapport ;
- commit, push et merge contrôlé.

## Principes de sécurité

- Aucun mot de passe en clair n’est persisté.
- Aucun secret n’apparaît dans les logs ou snapshots.
- Les identifiants publics restent opaques.
- Les opérations mutantes sont auditables.
- L’authentification ne crée pas encore de session.
- Les dépendances cryptographiques optionnelles ne sont pas obligatoires.
- Les tests sont déterministes lorsque cela est nécessaire.

## Critères de sortie de 4A

- manager chargeable indépendamment ;
- validation structurée ;
- contrats documentés ;
- tests unitaires verts ;
- aucune modification de SessionManager ou DeviceManager ;
- working tree cohérent et diff vérifié.
