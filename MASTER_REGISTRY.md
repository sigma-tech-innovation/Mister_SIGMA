# 🗂️ Sigma Master Registry

Version : v1.0.0  
Projet : Sigma Engineering Platform  
Dépôt : Mister_SIGMA

---

# Objectif

Ce document est le registre maître de l'écosystème Sigma.

Il référence tous les actifs importants : machines, dépôts Git, logiciels, services, bases de données, scripts, équipements, firmwares, documents et procédures.

---

# Règle officielle

Aucun composant Sigma important ne doit exister sans :

- identifiant unique ;
- nom officiel ;
- catégorie ;
- statut ;
- emplacement ;
- documentation ;
- lien avec un projet.

---

# Catégories d'identifiants

| Préfixe | Catégorie |
|---|---|
| SIG-PC | Ordinateurs |
| SIG-PHONE | Téléphones |
| SIG-WSL | Environnements WSL |
| SIG-VPS | Serveurs VPS |
| SIG-RPI | Raspberry Pi |
| SIG-GIT | Dépôts Git |
| SIG-DOC | Documents |
| SIG-SCRIPT | Scripts |
| SIG-DB | Bases de données |
| SIG-SERVICE | Services |
| SIG-ESP | ESP32 / microcontrôleurs |
| SIG-IOT | IoT |
| SIG-LAB | Matériel laboratoire |
| SIG-AI | Agents IA |

---

# Registre initial

| ID | Nom | Catégorie | Statut | Emplacement | Projet lié |
|---|---|---|---|---|---|
| SIG-GIT-001 | Mister_SIGMA | Dépôt Git | Actif | GitHub / Termux | Mister SIGMA |
| SIG-PHONE-001 | Admin-Sigma-Phone | Téléphone Android Termux | Actif | Termux | Sigma Platform |
| SIG-PC-001 | PC Windows Ayoub | PC Windows | Actif | Windows | Sigma Platform |
| SIG-WSL-001 | Ubuntu WSL2 | WSL | Actif | PC Windows | Sigma Platform |
| SIG-SERVICE-001 | Docker Desktop | Service | Actif | Windows | Sigma Infrastructure |
| SIG-SERVICE-002 | Home Assistant | Service Docker | Actif | Docker | Sigma IoT |
| SIG-SERVICE-003 | ESPHome | Service Docker | Actif | Docker | Sigma IoT |
| SIG-SERVICE-004 | Mosquitto MQTT | Service Docker | Actif | Docker | Sigma Communication |
| SIG-DOC-001 | ROADMAP.md | Document | Actif | Git | Sigma Management |
| SIG-DOC-002 | MASTER_REGISTRY.md | Document | Actif | Git | Sigma Management |

---

# Statuts officiels

| Statut | Signification |
|---|---|
| Draft | En préparation |
| Actif | Utilisé actuellement |
| À vérifier | Nécessite audit |
| Obsolète | À remplacer |
| Archivé | Conservé pour historique |

---

# Notes

Ce registre sera progressivement synchronisé avec Notion, PostgreSQL et les futurs outils Sigma.

