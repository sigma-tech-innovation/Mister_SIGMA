# AGENTS.md — Mister_SIGMA

## Mission

Mister_SIGMA est la plateforme centrale de l'écosystème Sigma.

L'objectif est de construire une architecture modulaire, robuste, testable et maintenable, sans casser la compatibilité existante.

---

# Source de vérité

La référence officielle est GitHub.

Les développements sont réalisés dans des branches Git dédiées.

Aucun développement direct sur `main`.

---

# Avant toute modification

Toujours :

1. Lire ce fichier AGENTS.md.
2. Vérifier `git status`.
3. Identifier la branche courante.
4. Comprendre complètement le fichier concerné avant toute modification.

---

# Règles de développement

Privilégier :

- petites fonctions ;
- responsabilité unique ;
- architecture modulaire ;
- code facilement testable ;
- noms explicites ;
- suppression des duplications.

Éviter :

- casser les API publiques ;
- modifier un comportement sans justification ;
- mélanger plusieurs refactorings dans un même changement.

---

# Refactoring

Avant de modifier un fichier :

- comprendre son fonctionnement ;
- conserver son comportement ;
- améliorer uniquement sa structure.

Le refactoring ne doit jamais modifier les fonctionnalités sans demande explicite.

---

# Tests

Après chaque modification :

- exécuter les tests concernés ;
- vérifier les imports ;
- vérifier la compatibilité des appels.

---

# Git

Ne jamais :

- travailler directement sur `main` ;
- faire un force push ;
- réécrire l'historique partagé ;
- créer des commits inutiles.

Toujours travailler dans une branche dédiée.

---

# Sécurité

Ne jamais exposer :

- secrets ;
- tokens ;
- clés privées ;
- cookies de session.

---

# Méthode Sigma

Pour chaque fichier important :

1. analyser complètement le fichier ;
2. proposer un plan ;
3. réaliser le refactoring complet ;
4. vérifier les impacts ;
5. exécuter les tests ;
6. résumer les changements.

---

# Rapport attendu

Toujours indiquer :

- fichiers analysés ;
- fichiers modifiés ;
- commandes exécutées ;
- tests exécutés ;
- risques éventuels ;
- prochaine étape recommandée.