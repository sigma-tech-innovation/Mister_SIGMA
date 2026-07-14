# ADR-001 — Propriété et séparation des données Sigma

- Statut : Accepté
- Date : 2026-07-14
- Projet : Mister SIGMA
- Version de départ : v1.1.0

## Contexte

Mister SIGMA doit devenir une plateforme unique, multi-utilisateurs,
multi-machines, synchronisée et duplicable.

L’audit de la version 1.1.0 montre que certaines données propres à une
machine sont actuellement suivies par Git et donc copiées sur toutes les
installations.

Exemples :

- machine_id ;
- node_id ;
- user_id généré localement ;
- hostname ;
- type de périphérique ;
- chemin absolu du workspace ;
- environnement local ;
- last_sync.

Le projet possède également plusieurs représentations concurrentes des
nœuds et du registre :

- sigma-config.json ;
- sigma-core/registry/registry.json ;
- sigma-db/nodes.json ;
- sigma-db/registry.json ;
- .sigma-workspace/configs/config.json.

## Problèmes identifiés

1. sigma-config.json mélange configuration globale et configuration locale.
2. Les identités machine, utilisateur et nœud sont générées ensemble.
3. Un même utilisateur ne peut pas conserver une identité stable sur
   plusieurs machines.
4. Le hostname Android « localhost » n’est pas une identité fiable.
5. Deux nœuds différents décrivent actuellement le même téléphone.
6. sigma-core/registry/registry.json et sigma-db/nodes.json se recouvrent.
7. La commande sync ne synchronise actuellement que Git.
8. Aucun modèle formel d’organisation, équipe, rôle ou permission n’existe.
9. Les chemins absolus locaux sont présents dans des fichiers partagés.
10. PostgreSQL, API, Notion et VPS ne sont pas encore des sources de vérité.

## Décision

Les données Sigma seront séparées en trois catégories officielles.

### 1. Données globales partagées

Ces données peuvent être versionnées ou synchronisées avec le serveur :

- organisations ;
- équipes ;
- rôles ;
- permissions ;
- utilisateurs publics ;
- projets ;
- modèles ;
- politiques ;
- schémas de données ;
- documentation ;
- versions et releases.

### 2. Données locales propres à une installation

Ces données ne doivent pas être partagées directement par Git :

- machine_id ;
- node_id ;
- hostname ;
- système d’exploitation ;
- chemin du workspace ;
- profil local ;
- environnement local ;
- état et date de dernière synchronisation ;
- caches, journaux et sauvegardes locales.

Elles seront stockées dans :

.sigma-workspace/configs/local.json

Ce fichier devra être ignoré par Git.

### 3. Données secrètes

Ces données ne doivent jamais être versionnées :

- mots de passe ;
- tokens ;
- clés API ;
- clés privées ;
- certificats privés ;
- secrets MQTT ;
- identifiants PostgreSQL ;
- secrets Notion et VPS.

Elles seront stockées dans un mécanisme local sécurisé, hors Git.

## Modèle d’identité cible

- organization_id : organisation propriétaire ;
- user_id : identité globale et stable d’un utilisateur ;
- machine_id : identité locale persistante d’une machine ;
- node_id : instance Sigma installée sur une machine ;
- workspace_id : espace de travail partagé ;
- installation_id : installation locale précise de Mister SIGMA.

Relations :

Organization
  └── Users
      └── Memberships / Roles
          └── Workspaces
              └── Projects

Machine
  └── Sigma Node
      └── Local Installation
          └── Workspace connection

## Source de vérité cible

Phase transitoire :

- Git : code, documentation, schémas et configuration modèle ;
- fichiers locaux ignorés : identité locale et secrets ;
- JSON Sigma : données de développement uniquement.

Architecture cible :

- PostgreSQL : données partagées transactionnelles ;
- API Sigma : accès contrôlé aux données ;
- GitHub : code et documentation ;
- Notion : documentation et vues de gestion ;
- MQTT : événements et télémétrie ;
- VPS : hébergement de l’API et de PostgreSQL.

## Migration prévue

1. Créer un modèle de configuration globale sans identité locale.
2. Créer .sigma-workspace/configs/local.json.
3. Retirer les identités locales de sigma-config.json.
4. Définir les schémas Organization, User, Membership, Machine, Node et
   Workspace.
5. Désigner une seule représentation officielle de chaque entité.
6. Ajouter validation, migration et tests.
7. Préparer l’API et PostgreSQL.
8. Connecter ensuite Notion, MQTT, VPS et les autres machines.

## Contraintes

- aucune suppression de données sans sauvegarde ;
- migration rétrocompatible ;
- une seule étape à la fois ;
- tests obligatoires ;
- aucun secret dans Git ;
- documentation avant chaque modification importante.
