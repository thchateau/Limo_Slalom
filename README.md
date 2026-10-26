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

## Installation et compilation

```bash
git clone https://github.com/thchateau/Limo_Slalom.git
cd Limo_Slalom/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

Les dossiers `build`, `install` et `log` sont produits localement par `colcon` et ne doivent pas
être ajoutés dans Git.

## Démarrer l'arène de slalom

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
