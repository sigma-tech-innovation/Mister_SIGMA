# 🧭 Mister_SIGMA — Règles canoniques

> **Statut :** canonique
> **Portée :** développement, documentation, validation et travail assisté
> **Propriétaire :** gouvernance Mister_SIGMA
> **Dernière mise à jour :** 15 juillet 2026

Ce registre contient les règles normatives communes du projet.

Les documents spécialisés conservent leur propre responsabilité :

- `SECURITY.md` détaille les règles de sécurité ;
- `CONTRIBUTING.md` résume les attentes pour les contributeurs ;
- les ADR fixent les décisions d’architecture ;
- les rapports de phase contiennent les preuves ;
- les roadmaps décrivent uniquement les travaux futurs ;
- la note maître fournit la synthèse de l’écosystème ;
- la note de phase décrit l’état opérationnel immédiat ;
- `docs/REGISTRY.md` définit la propriété des registres, leurs copies transitoires et leurs règles de consolidation ; `MASTER_REGISTRY.md` reste un inventaire historique.

---

## 🥇 GOV-001 — Une seule tâche active

Une seule tâche cohérente doit être active à la fois.

La tâche suivante ne commence qu’après :

1. contrôle syntaxique ou compilation ;
2. tests ciblés ;
3. tests globaux ;
4. diagnostics applicables ;
5. revue du diff ;
6. validation explicite ;
7. commit atomique lorsque le commit est autorisé.

Une tâche n’est clôturée que lorsque son résultat est explicitement validé.

---

## 🥇 GOV-002 — Pilotage opérationnel assisté

Pendant une session de développement assisté :

- l’assistant pilote le diagnostic et prépare les modifications ;
- l’utilisateur exécute les commandes proposées ;
- une seule commande ou un seul bloc cohérent est fourni à la fois ;
- l’assistant attend la sortie complète avant de poursuivre ;
- les explications restent brèves lorsqu’aucune décision détaillée n’est requise ;
- l’assistant privilégie les scripts et patchs contrôlés plutôt que les modifications manuelles longues ou fragiles.

Cette règle ne dispense jamais de la revue humaine des modifications.

---

## 🥇 GOV-003 — Informations manquantes

Une information absente ne doit jamais être inventée.

Lorsqu’une information nécessaire manque, il faut :

1. signaler explicitement l’information manquante ;
2. expliquer brièvement pourquoi elle est nécessaire ;
3. demander la source, le fichier, l’export, la preuve ou la sortie correspondante ;
4. suspendre toute modification dépendant de cette information.

Avant de déclarer une partie terminée, vérifier si des informations, preuves,
documents, dépendances ou décisions restent manquants.

---

## 🔎 DEV-001 — Diagnostic avant modification

Avant toute modification :

1. confirmer la racine du dépôt ;
2. confirmer la branche active ;
3. inspecter le working tree ;
4. identifier le chemin exact ;
5. vérifier l’existence du fichier ;
6. localiser la classe, fonction, section ou ancre concernée ;
7. inspecter la zone réelle ;
8. vérifier les tests, références et dépendances ;
9. arrêter l’opération si une hypothèse est fausse.

Aucune modification ne doit être réalisée à partir d’un chemin, d’une structure
ou d’un emplacement supposé.

---

## 🩹 DEV-002 — Modification ciblée et contrôlée

Toute modification doit être :

- localisée ;
- minimale ;
- reproductible ;
- sauvegardée lorsque le risque l’exige ;
- limitée à une ancre vérifiée ;
- contrôlée par un diff ;
- suivie d’une validation.

Les remplacements globaux sur une ancre ambiguë sont interdits.

Une modification irréversible doit être isolée, documentée et validée
séparément.

---

## 🧪 DEV-003 — Pipeline de validation

Après toute modification fonctionnelle, exécuter les contrôles applicables
dans cet ordre :

1. inspection ciblée ;
2. contrôle syntaxique ou compilation ;
3. tests ciblés ;
4. tests globaux ;
5. Sigma Doctor ;
6. Sigma Health ;
7. Sigma Sync Validate ;
8. `git diff --check` ;
9. revue du diff ;
10. contrôle du working tree.

Un commit ne doit pas être proposé lorsqu’un contrôle obligatoire échoue.

Les contrôles indisponibles doivent être signalés explicitement et ne doivent
pas être présentés comme réussis.

---

## ♻️ DOC-001 — Anti-duplication sémantique

Avant d’ajouter une règle, une section ou une information :

1. rechercher une formulation identique ;
2. rechercher une formulation différente ayant le même sens ;
3. identifier le document propriétaire du sujet ;
4. fusionner les formulations compatibles ;
5. conserver la formulation la plus précise ;
6. remplacer les répétitions par des références ;
7. documenter les contradictions au lieu de les masquer.

Une différence de titre ne signifie pas qu’une règle est nouvelle.

Une copie divergente ne doit jamais devenir une seconde source de vérité.

---

## 🧠 DOC-002 — Propriété documentaire unique

Chaque sujet doit posséder un document propriétaire identifiable.

Les synthèses peuvent référencer une information, mais ne doivent pas recopier
inutilement son contenu détaillé.

Répartition générale :

- décisions durables : ADR ;
- preuves : rapports ;
- travaux futurs : roadmaps ;
- état immédiat : note de phase ;
- synthèse globale : note maître ;
- procédures détaillées : guides ;
- contrats observés : documentation d’interface ;
- actifs, identifiants et sources de registre : `docs/REGISTRY.md` ;
- règles normatives communes : présent registre.

---

## 🌱 DOC-003 — Système de notes vivant

Les notes doivent former un système évolutif, traçable et enrichissable.

Un modèle de note doit pouvoir contenir, selon son usage :

- identifiant stable ;
- titre ;
- catégorie ;
- statut ;
- date d’observation ;
- source ;
- propriétaire documentaire ;
- faits observés ;
- preuves ;
- décisions ;
- hypothèses ;
- cible future ;
- tâches ouvertes ;
- dépendances ;
- contradictions ;
- informations manquantes ;
- historique de mise à jour ;
- liens vers les autres notes.

L’enrichissement doit être progressif.

Une information déjà possédée par un document ne doit pas être recopiée dans
plusieurs notes : elle doit être référencée.

---

## 🔄 DOC-004 — Synchronisation documentaire globale

La synchronisation documentaire doit couvrir progressivement :

- le dépôt Git ;
- les tests et rapports ;
- les ADR ;
- les roadmaps ;
- le Guide technique maître ;
- le Master Backlog ;
- le Dossier Maître de Continuité ;
- les notes existantes ;
- les documents collectés ;
- les pages et bases Notion ;
- les futurs modèles de notes.

Synchroniser ne signifie pas fusionner tout le contenu dans un seul fichier.

La synchronisation consiste à :

1. inventorier ;
2. classer ;
3. dédupliquer ;
4. attribuer un propriétaire ;
5. créer les références ;
6. séparer état réel et cible future ;
7. identifier les contradictions ;
8. signaler les informations manquantes ;
9. maintenir la traçabilité.

Une synchronisation ne doit pas être déclarée complète tant qu’une source
nécessaire n’a pas été inspectée.

---

## 🧾 DOC-005 — Classification des informations

Toute information importante doit être classée comme l’un des éléments
suivants :

- **fait observé** ;
- **preuve validée** ;
- **décision acceptée** ;
- **hypothèse à vérifier** ;
- **cible future** ;
- **information manquante** ;
- **déclaration du propriétaire non encore vérifiée techniquement**.

Une cible future ne doit jamais être présentée comme une implémentation réelle.

Une déclaration humaine peut être enregistrée comme telle, mais elle ne doit
pas être confondue avec une preuve technique.

---

## 🎨 UX-001 — Icônes et stabilité du nommage

Les icônes peuvent être utilisées lorsqu’elles améliorent la lisibilité des
sorties destinées aux humains :

- messages interactifs ;
- sorties `print()` ;
- diagnostics ;
- titres documentaires ;
- rapports ;
- menus ;
- interfaces visuelles.

Les icônes sont interdites dans les éléments techniques stables :

- variables ;
- fonctions ;
- classes ;
- fichiers et répertoires techniques ;
- identifiants ;
- clés de registre ;
- clés JSON ;
- colonnes de base de données ;
- routes API ;
- commandes et options CLI ;
- schémas ;
- migrations ;
- protocoles ;
- valeurs analysées par des machines ;
- valeurs dont dépendent les tests ou automatisations.

> Icônes pour les humains, identifiants ASCII stables pour les machines.

Toute sortie machine doit conserver un mode stable, prévisible et sans
décoration.

---

## 🖥️ UX-002 — Indépendance du matériel et des interfaces

Le cœur métier de Mister_SIGMA ne doit dépendre d’aucun écran, contrôleur,
format d’affichage, résolution ou dispositif embarqué particulier.

Les éléments suivants sont des adaptateurs ou des options d’interface :

- CLI ;
- API ;
- interface web ;
- interface mobile ;
- écran embarqué ;
- splashscreen ;
- menus ;
- ESP32 et ESP32 CYD ;
- toute autre interface future.

ESP32 CYD peut être utilisé comme prototype ou cible expérimentale. Il ne
constitue pas une plateforme obligatoire et ne doit pas contraindre
l’architecture générale.

Les règles métier, la validation, la persistance et les managers doivent rester
réutilisables lorsque l’interface, l’écran, la résolution ou la plateforme
matérielle changent.

Une interface peut imposer ses contraintes locales dans son propre adaptateur,
mais elle ne doit pas les propager au moteur métier.

---

## 📐 SCI-001 — Relations scientifiques explicites

Le symbole graphique de proportionnalité ne doit pas être utilisé dans les
formules présentées à l’utilisateur.

La relation doit être écrite explicitement, par exemple :

```text
y = k × x
```

ou expliquée ainsi :

```text
y varie proportionnellement à x, avec k comme constante de proportionnalité.
```

La constante, les unités, le domaine de validité et les hypothèses doivent être
précisés lorsqu’ils sont nécessaires à l’interprétation scientifique.

---

## 🔐 Références de sécurité

Les règles détaillées concernant les secrets, mots de passe, clés, jetons,
fichiers d’environnement et données sensibles restent la responsabilité de
`SECURITY.md`.

Aucun diagnostic, rapport ou sortie utilisateur ne doit révéler de secret.

---

## ✅ Condition d’évolution du registre

Avant d’ajouter ou de modifier une règle canonique :

1. inspecter le registre actuel ;
2. rechercher les règles sémantiquement équivalentes ;
3. identifier les documents spécialisés concernés ;
4. vérifier les contradictions ;
5. modifier uniquement la règle propriétaire ;
6. contrôler le diff ;
7. mettre à jour les références nécessaires.

Une nouvelle règle ne doit être créée que lorsqu’aucune règle existante ne
couvre déjà son intention.
