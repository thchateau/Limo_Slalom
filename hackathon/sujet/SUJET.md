# Hackathon ROS2 — Slalom autonome du Limo

## Contexte

Vous êtes une équipe de robotique chargée de développer le logiciel de pilotage d'un robot
mobile Limo. Votre mission est de lui faire franchir, de manière autonome et en sécurité, un
parcours de slalom constitué de portes. Une porte est formée de deux plots. Le robot doit passer
entre les deux plots et enchaîner les portes dans l'ordre du parcours.

Le projet se réalise d'abord en simulation Gazebo, puis sur le robot réel. Le parcours, le nombre
de portes et les dimensions sont communiqués au lancement du hackathon. Certaines manches
comporteront des variations mineures (écartement des portes, position de départ ou ordre des
portes) : votre logiciel ne doit donc pas dépendre de coordonnées écrites en dur.

## Objectifs

À l'issue du hackathon, vous devrez être capables de :

- organiser une application ROS2 en plusieurs nœuds communicant par topics ;
- exploiter les mesures du lidar (`sensor_msgs/LaserScan`) ;
- appliquer un traitement de signal simple et robuste ;
- concevoir une commande de vitesse et de direction ;
- mettre en oeuvre une machine à états ;
- travailler en équipe avec Git et une méthode Agile légère ;
- présenter et justifier des choix techniques.

Vous n'avez pas à utiliser de navigation, de SLAM, de caméra ni d'intelligence artificielle.
Une solution simple, comprise et fiable sera mieux évaluée qu'une solution complexe non
maîtrisée.

## Mission fonctionnelle

Votre programme doit :

1. démarrer le Limo immobilisé ;
2. analyser le lidar pour identifier la prochaine porte ;
3. conduire le robot vers le milieu de cette porte ;
4. franchir la porte sans toucher les plots ;
5. rechercher la porte suivante ;
6. s'arrêter proprement à la fin du parcours ou lorsqu'une situation sûre ne peut plus être
   garantie.

Le Limo est commandé par un message `geometry_msgs/Twist` sur `/cmd_vel`. Les mesures du
lidar sont disponibles sur `/scan`. Les repères angulaires, limites de vitesse et dimensions
précises du parcours seront donnés pendant le hackathon.

## Exigences de sécurité

La sécurité est prioritaire sur la performance.

- Le robot doit s'arrêter si un obstacle est détecté trop près dans la zone frontale.
- Le robot doit s'arrêter si les données lidar ne sont plus reçues ou sont trop anciennes.
- Un membre de l'équipe doit pouvoir demander l'arrêt à tout instant.
- Une seule partie de votre système publie la consigne finale sur `/cmd_vel`.
- Toute modification de gains ou de code est d'abord validée en simulation.
- Pendant les essais réels, une seule équipe utilise le robot à la fois et les personnes restent
  hors de la zone de déplacement.

Une collision, une perte de contrôle ou une intervention de sécurité arrête immédiatement la
manche.

## Attendus techniques

Votre système doit être découpé en composants dont la responsabilité est claire. Vous choisissez
les noms, les messages intermédiaires et la structure exacte, mais votre documentation doit
indiquer le rôle de chaque nœud et de chaque topic.

Les éléments suivants sont attendus :

- un prétraitement des données lidar : élimination des mesures invalides, sélection de secteurs
  angulaires et au moins un mécanisme de filtrage justifié ;
- une détection de porte fondée sur la géométrie des mesures lidar ;
- une estimation de la direction à suivre, par exemple à partir du milieu de la porte ;
- une commande qui transforme l'erreur de direction en vitesse linéaire et angulaire ;
- une machine à états explicite, par exemple attente, recherche, approche, franchissement,
  récupération et arrêt ;
- un superviseur de sécurité qui a priorité sur la commande nominale ;
- un fichier launch qui démarre l'ensemble de votre application.

Vous pouvez utiliser une loi proportionnelle ou un PID simple. Les paramètres doivent être
centralisés et documentés. Pour chaque filtre ou régulateur, précisez le problème traité, les
paramètres retenus et un exemple d'observation ayant conduit à ce réglage.

## Déroulement indicatif — 32 heures

| Séquence | Durée | Résultat attendu |
|---|---:|---|
| Cadrage, prise en main et backlog | 3 h | Équipe organisée, dépôt Git et backlog initial |
| Exploration ROS2 et lidar | 5 h | Nœud d'observation et premières mesures exploitables |
| Traitement du signal et détection | 7 h | Détection validée sur plusieurs configurations simulées |
| Commande, états et sécurité | 7 h | Slalom partiel sûr en simulation |
| Intégration et robustesse | 5 h | Parcours complet simulé via un launch unique |
| Transfert sur robot réel | 3 h | Essais progressifs et réglages justifiés |
| Finale et présentation | 2 h | Démonstration et restitution |

Ce planning est une proposition : votre équipe peut le modifier dans son backlog si elle en
explique la raison.

## Travail en équipe avec une méthode Agile légère

Vous utiliserez un tableau de tâches simple, dans GitHub Projects, GitLab, un tableau physique
ou un fichier partagé. Chaque tâche doit être courte, formulée avec un verbe et posséder un
critère de fin vérifiable.

Exemples :

- « Publier la distance minimale dans le secteur frontal » ;
- « Afficher les données lidar filtrées » ;
- « Arrêter le robot quand le lidar ne répond plus » ;
- « Tester le franchissement d'une porte en simulation ».

Au début de chaque demi-journée, réalisez un point de 10 minutes :

1. qu'ai-je terminé depuis le dernier point ?
2. que vais-je faire maintenant ?
3. qu'est-ce qui me bloque ?

À la fin de chaque demi-journée, montrez une fonctionnalité qui fonctionne, même incomplète.
Mettez à jour le tableau : `à faire`, `en cours`, `à vérifier`, `terminé`. Une tâche n'est
terminée que si elle est testée et si son code est intégré à la branche principale.

Conservez dans votre dépôt un court fichier `RETROSPECTIVE.md` répondant à ces questions :

- qu'est-ce qui a bien fonctionné dans l'organisation ?
- quel problème avez-vous rencontré ?
- quelle action concrète avez-vous choisie pour la suite ?

## Utilisation de Git

Un membre crée un dépôt privé pour l'équipe et ajoute les autres membres. Ne travaillez pas
directement tous sur les mêmes fichiers sans vous coordonner.

Pour commencer :

```bash
git clone <url-du-depot>
cd <nom-du-depot>
git switch -c feature/nom-court
```

Une branche correspond à une tâche ou à une petite fonctionnalité. Avant de modifier des fichiers,
mettez votre branche à jour :

```bash
git switch main
git pull
git switch feature/nom-court
git merge main
```

Quand votre tâche fonctionne :

```bash
git status
git add <fichiers-modifies>
git commit -m "Ajouter la détection de porte"
git push -u origin feature/nom-court
```

Créez ensuite une *pull request* vers `main`. Un autre membre de l'équipe relit la modification,
vérifie que la fonctionnalité démarre et écrit au moins un commentaire avant la fusion. Ne
versionnez pas les dossiers ROS2 `build/`, `install/` et `log/`.

Les messages de commit doivent être brefs et décrire une action : `Ajouter ...`, `Corriger ...`,
`Tester ...`, `Documenter ...`. Faites de petits commits fréquents ; ils sont plus simples à
relire, tester et annuler.

## Livrables

Avant la finale, votre dépôt doit contenir :

- le ou les paquets ROS2 développés par l'équipe ;
- un `README.md` expliquant l'installation, la compilation et la commande de lancement ;
- un schéma de l'architecture ROS2 (nœuds, topics et flux principaux) ;
- les paramètres de réglage et leur signification ;
- un launch permettant de lancer la démonstration ;
- le backlog final et `RETROSPECTIVE.md` ;
- une courte vidéo de la simulation ou des essais si le temps le permet.

La démonstration finale dure cinq minutes : lancement du système, parcours autonome et réponse
aux questions techniques.

## Évaluation

| Critère | Points |
|---|---:|
| Sécurité et comportement d'arrêt | 4 |
| Traitement lidar et robustesse de la détection | 4 |
| Commande, machine à états et franchissement autonome | 4 |
| Intégration ROS2, launch et qualité du dépôt Git | 3 |
| Organisation Agile, collaboration et traçabilité | 2 |
| Démonstration, explication et recul technique | 3 |
| **Total** | **20** |

La vitesse n'est qu'un critère secondaire. Une solution qui franchit moins de portes mais reste
prédictible, sûre et expliquée obtiendra une meilleure évaluation qu'une solution rapide et
fragile.
