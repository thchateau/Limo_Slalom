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

## Tutoriel ROS2 : perception et commande

Cette section montre comment construire une chaîne ROS2 minimale sans résoudre la détection des
portes. Le principe est de découper le programme en deux nœuds :

```text
/scan ──> perception ──> /perception/heading_error ──> controller ──> /cmd_vel
```

Le nœud de perception transforme les mesures brutes du lidar en une information simple, ici une
erreur de direction en radians. Le nœud de commande transforme cette erreur en vitesse. Le choix
de l'algorithme qui détecte une porte est volontairement laissé à l'équipe.

### 1. Créer un paquet Python

Depuis `ros2_ws/src` :

```bash
ros2 pkg create mon_equipe_limo \
  --build-type ament_python \
  --dependencies rclpy sensor_msgs geometry_msgs std_msgs
```

Le paquet créé contient notamment `package.xml`, `setup.py` et le répertoire Python
`mon_equipe_limo/`. Ajoutez les deux exécutables dans `setup.py` :

```python
entry_points={
    'console_scripts': [
        'perception = mon_equipe_limo.perception_node:main',
        'controller = mon_equipe_limo.controller_node:main',
    ],
},
```

Le nom avant `=` est la commande utilisée avec `ros2 run`. Le nom après `=` indique le module
Python et la fonction `main`.

### 2. Observer le message lidar

Avant de programmer, observez ce que publie le simulateur :

```bash
ros2 topic list
ros2 topic echo /scan --once
ros2 topic hz /scan
ros2 interface show sensor_msgs/msg/LaserScan
```

`ranges[i]` est une distance en mètres. L'angle de cette mesure se calcule avec :

```python
angle = scan.angle_min + i * scan.angle_increment
```

Les valeurs `NaN`, `Inf`, ou hors de l'intervalle `[scan.range_min, scan.range_max]` ne doivent
pas être utilisées. Dans le repère du robot, on peut convertir une mesure polaire valide en point
cartésien :

```python
x = distance * math.cos(angle)  # avant du robot
y = distance * math.sin(angle)  # gauche du robot
```

### 3. Écrire un nœud de perception

Créez `mon_equipe_limo/perception_node.py`. Le squelette suivant reçoit chaque scan et publie
l'interface que le contrôleur utilisera. La partie qui produit réellement `heading_error` est à
concevoir par l'équipe.

```python
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32


class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception')
        self.error_publisher = self.create_publisher(
            Float32, '/perception/heading_error', 10)
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

    def scan_callback(self, scan):
        valid_points = []
        for i, distance in enumerate(scan.ranges):
            if not math.isfinite(distance):
                continue
            if not scan.range_min <= distance <= scan.range_max:
                continue

            angle = scan.angle_min + i * scan.angle_increment
            valid_points.append((
                distance * math.cos(angle),
                distance * math.sin(angle),
            ))

        # TODO: filtrer les points, reconnaître une porte et calculer heading_error.
        # Quand une cible fiable est trouvée :
        # self.error_publisher.publish(Float32(data=heading_error))
        self.get_logger().debug(f'{len(valid_points)} points lidar valides')


def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

Compilez après avoir ajouté le fichier :

```bash
cd ~/Limo_Slalom/ros2_ws
colcon build --packages-select mon_equipe_limo
source install/setup.bash
ros2 run mon_equipe_limo perception
```

Le `TODO` ne doit pas être remplacé par une loi de commande. Son unique rôle est de publier une
observation : par exemple une direction vers le milieu d'une porte et, si nécessaire, une mesure
de confiance dans un second topic.

### 4. Écrire un nœud de commande

Créez `mon_equipe_limo/controller_node.py`. Ce nœud est indépendant du lidar : il ne connaît que
l'erreur de direction fournie par la perception. Cette séparation permet de tester perception et
commande séparément.

```python
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller')
        self.declare_parameter('linear_speed', 0.15)
        self.declare_parameter('angular_gain', 1.0)
        self.declare_parameter('max_angular_speed', 0.8)
        self.command_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(
            Float32, '/perception/heading_error', self.error_callback, 10)

    def error_callback(self, message):
        gain = self.get_parameter('angular_gain').value
        maximum = self.get_parameter('max_angular_speed').value

        command = Twist()
        command.linear.x = self.get_parameter('linear_speed').value
        command.angular.z = max(-maximum, min(maximum, gain * message.data))
        self.command_publisher.publish(command)


def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.command_publisher.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()
```

La loi ci-dessus est une première loi proportionnelle bornée :

```text
v = vitesse_linéaire
ω = saturation(gain × erreur_de_direction)
```

Elle n'est pas suffisante pour le défi : l'équipe doit décider quand avancer, ralentir, tourner,
s'arrêter et rechercher une porte. Ajoutez notamment une vitesse nulle lorsqu'aucune donnée de
perception récente n'est disponible.

### 5. Tester chaque brique avant de les relier

Dans trois terminaux sourcés, démarrez l'arène, puis le contrôleur :

```bash
ros2 launch limo_slalom slalom_simulation.launch.py
ros2 run mon_equipe_limo controller
```

Avant que la perception ne soit écrite, simulez une erreur de direction pendant un temps court :

```bash
ros2 topic pub --rate 5 /perception/heading_error std_msgs/msg/Float32 "{data: 0.2}"
```

Le Limo doit avancer lentement et tourner dans une direction. Interrompez la commande avec
`Ctrl+C`. Essayez ensuite une valeur négative et vérifiez que le sens de rotation s'inverse.

Pour contrôler les connexions ROS2 :

```bash
ros2 node list
ros2 topic info /scan -v
ros2 topic info /perception/heading_error -v
ros2 topic info /cmd_vel -v
ros2 topic echo /cmd_vel
```

N'utilisez pas `teleop_twist_keyboard` en même temps que votre contrôleur : les deux programmes
publieraient sur `/cmd_vel`. Pendant les essais sur le robot réel, ajoutez un nœud de sécurité ou
un état d'arrêt qui a priorité sur la commande nominale.

### 6. Regrouper les nœuds dans un launch

Lorsque les deux nœuds fonctionnent séparément, créez un fichier
`mon_equipe_limo/launch/slalom.launch.py` pour les démarrer ensemble. Un launch minimal contient
deux actions `Node` :

```python
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(package='mon_equipe_limo', executable='perception', output='screen'),
        Node(package='mon_equipe_limo', executable='controller', output='screen'),
    ])
```

Installez les fichiers de lancement dans `setup.py`, puis reconstruisez. La dernière étape est de
remplacer les tests manuels par la perception de porte, une machine à états et les protections de
sécurité définies dans l'énoncé.

Pour cela, ajoutez ces imports et cette entrée dans `data_files` :

```python
from glob import glob
import os

# Dans la liste data_files :
(os.path.join('share', package_name, 'launch'),
 glob(os.path.join('launch', '*.launch.py'))),
```
