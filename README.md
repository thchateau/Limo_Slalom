# Limo Slalom

Environnement ROS2 du hackathon « Slalom autonome du Limo ».

Le dépôt contient :

- `ros2_ws/src/limo_ros2` : simulation Gazebo du Limo et ses mondes de TP ;
- `ros2_ws/src/limo_slalom` : monde de slalom, lancement de la simulation et exemple minimal
  de lecture du lidar ;
- `hackathon/sujet/SUJET.md` : énoncé destiné aux étudiants.

## Pré-requis

Le projet cible Ubuntu 22.04 avec ROS2 Humble et Gazebo Classic. Les dépendances ROS2
nécessaires sont notamment `gazebo_ros`, `xacro`, `joy` et les messages standards.

La machine virtuelle fournie pour le TP contient normalement ces dépendances. Sur une installation
Ubuntu 22.04 avec ROS2 Humble déjà configurée, elles peuvent être installées avec :

```bash
sudo apt update
sudo apt install \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-joy \
  ros-humble-xacro \
  python3-colcon-common-extensions
```

## Installation, compilation et lancement

```bash
git clone https://github.com/thchateau/Limo_Slalom.git
cd Limo_Slalom/ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

Les dossiers `build`, `install` et `log` sont produits localement par `colcon` et ne doivent pas
être ajoutés dans Git.

### Cas d'un disque partagé ou monté

L'option `--symlink-install` est pratique lors du développement, mais elle nécessite que le
système de fichiers accepte les liens symboliques. Elle ne doit pas être utilisée si le dépôt est
placé sur un dossier partagé de machine virtuelle, un disque réseau ou un volume monté tel que
`/home/student/Disque_M`.

Dans ce cas, compilez sans cette option :

```bash
cd /home/student/Disque_M/HackathonM1/Limo_Slalom/ros2_ws
source /opt/ros/humble/setup.bash
rm -rf build install log
colcon build --cmake-args -DAMENT_CMAKE_SYMLINK_INSTALL=OFF
source install/setup.bash
```

La suppression concerne uniquement les dossiers générés par `colcon`. Elle est nécessaire si une
compilation précédente a enregistré l'option d'installation par liens symboliques dans le cache
CMake.

Si l'erreur `Errno 95: Operation not supported` persiste, clonez le dépôt dans le répertoire
personnel, généralement situé sur le système de fichiers Linux local :

```bash
cd ~
git clone https://github.com/thchateau/Limo_Slalom.git
cd ~/Limo_Slalom/ros2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

À chaque nouveau terminal, il faut sourcer à nouveau ROS2 et le workspace :

```bash
cd ~/Limo_Slalom/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

### Démarrer l'arène de slalom

Dans un terminal où le workspace a été sourcé :

```bash
ros2 launch limo_slalom slalom_simulation.launch.py
```

Le lancement démarre Gazebo, le robot à gauche du parcours et le nœud
`scan_observer`. Ce dernier publie la distance minimale dans un secteur frontal sur
`/slalom/front_distance` afin d'aider à prendre en main le lidar :

```bash
ros2 topic echo /slalom/front_distance
```

Il ne commande pas le robot. Les équipes doivent créer leur propre architecture et leur propre
launch à partir de cette base.

Pour piloter temporairement le robot durant les essais de simulation :

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Si cette commande n'est pas disponible, installez le paquet `ros-humble-teleop-twist-keyboard`.

## Proposer une stratégie

L'objectif n'est pas de trouver immédiatement une solution complète, mais de proposer une
stratégie qui peut être développée, testée et améliorée par petites étapes. Avant de coder,
chaque équipe rédige une page dans son dépôt qui répond aux questions suivantes.

### 1. Que peut mesurer le robot ?

Le lidar fournit une liste de distances et l'angle associé à chaque mesure. Identifiez :

- quelles mesures correspondent à l'avant du robot ;
- les valeurs à écarter (`NaN`, `Inf`, valeurs hors des bornes du capteur) ;
- les informations utiles pour reconnaître deux plots et estimer le milieu d'une porte ;
- les situations ambiguës : porte partiellement visible, plot isolé, données bruitées ou absence
  de porte.

Commencez par afficher ou publier une grandeur simple et vérifiable. Le nœud `scan_observer`
montre un exemple de distance minimale frontale ; il ne constitue pas un détecteur de porte.

### 2. Découper le comportement

Définissez une machine à états avant de choisir les gains de commande. Une première version peut
contenir les états suivants :

| État | Rôle | Condition de sortie |
|---|---|---|
| `WAIT` | Robot immobile, capteurs vérifiés | Ordre de démarrage et lidar valide |
| `SEARCH_GATE` | Recherche d'une porte plausible | Porte détectée avec une confiance suffisante |
| `APPROACH_GATE` | Alignement et progression vers son milieu | Porte franchie ou perdue |
| `RECOVERY` | Arrêt ou recherche lente après une perte | Porte retrouvée ou délai dépassé |
| `STOP` | Commande nulle | Fin de parcours ou défaut de sécurité |

Vous pouvez modifier ces états, mais documentez les transitions et la commande produite dans
chacun d'eux.

### 3. Séparer perception, décision et commande

Une architecture facile à tester sépare trois responsabilités :

1. **Perception** : filtre `/scan` et publie les caractéristiques de la porte détectée.
2. **Décision** : choisit l'état courant et la cible à poursuivre.
3. **Commande** : transforme l'erreur de direction et la distance en un `Twist` borné.

Ajoutez un superviseur de sécurité qui peut annuler la vitesse en cas d'obstacle frontal, de
message lidar périmé ou de mesure incohérente. Il doit avoir priorité sur la commande nominale.
Une seule sortie publie sur `/cmd_vel`.

### 4. Choisir une première loi de commande

Pour une première itération, utilisez une loi simple et bornée : une erreur de direction vers le
milieu de la porte augmente la vitesse angulaire, tandis que la vitesse linéaire diminue lorsque
l'erreur est grande ou lorsqu'un obstacle est proche. Notez les limites de vitesse, les gains et
les raisons de leur choix. Un PID n'est pertinent qu'après avoir observé les limites d'une loi
proportionnelle.

Ne réglez jamais la commande directement sur le robot réel. Commencez lentement en simulation,
testez une seule porte, puis augmentez progressivement le nombre de portes et la vitesse.

### 5. Définir les tests avant l'intégration

Ajoutez au backlog des tests observables, par exemple :

- le filtre écarte les données invalides ;
- le robot s'arrête si aucune mesure lidar valide n'est reçue ;
- une porte centrée produit une vitesse angulaire proche de zéro ;
- une porte décalée produit une rotation dans le bon sens ;
- une porte perdue conduit à `RECOVERY` puis à `STOP` après le délai prévu ;
- le robot ne publie jamais une vitesse au-delà des limites définies.

À chaque modification, conservez une branche Git courte, testez-la dans Gazebo, puis faites-la
relire par un autre membre avant fusion dans `main`.
