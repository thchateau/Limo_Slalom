"""Launch the Gazebo slalom arena, a Limo and a lidar observation example."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    simulation_share = get_package_share_directory('limo_simulation')
    simulation_launch = os.path.join(
        simulation_share, 'launch', 'gazebo_simulation_common.launch.py')
    spawn_launch = os.path.join(
        simulation_share, 'launch', 'gazebo_spawn_common.launch.py')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(simulation_launch),
            launch_arguments={
                'environnement_path': 'worlds/slalom.world',
                'env_pkg': 'limo_slalom',
            }.items(),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(spawn_launch),
            launch_arguments={
                'spawn_x_val': '-4.5',
                'spawn_y_val': '0.0',
                'spawn_z_val': '0.0',
                'spawn_yaw_val': '0.0',
                'entity_name': 'limo',
            }.items(),
        ),
        Node(
            package='limo_slalom',
            executable='scan_observer',
            name='scan_observer',
            output='screen',
        ),
    ])
