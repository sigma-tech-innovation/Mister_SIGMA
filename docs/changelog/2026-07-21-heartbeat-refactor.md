# Heartbeat Refactor

Date: 2026-07-21

Commit:
76b346e

## Objectif

Séparer la factory de la logique métier.

## Changements

### new_heartbeat()

Responsabilité :
- validation du node_id
- création d'un objet Heartbeat

Ne fait plus :
- enregistrement
- mise à jour du repository
- publication d'événements

### heartbeat()

Responsabilité :
- création via new_heartbeat()
- enregistrement dans _heartbeats
- mise à jour du repository
- publication de node.recovered
- retour du Heartbeat

## Tests

477 tests

Résultat :
OK

## Statut

✅ Étape terminée

Architecture obtenue :

new_heartbeat() -> Factory

heartbeat() -> Service métier
