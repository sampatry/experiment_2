import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    map_file = os.path.join(
        get_package_share_directory('navigation_pkg'), 'config', 'my_map.yaml'
    )

    param_file = os.path.join(
        get_package_share_directory('navigation_pkg'), 'config', 'turtlebot3.yaml'
    )

    nav2_launch = os.path.join(
        get_package_share_directory('turtlebot3_manipulation_navigation2'),
        'launch', 'navigation2.launch.py'
    )

    moveit_launch_path = os.path.join(
        get_package_share_directory('turtlebot3_manipulation_moveit_config'),
        'launch', 'move_group.launch.py'
    )

     # Path to your mask yaml (the black and white image description)
    mask_yaml_file = os.path.join(
        get_package_share_directory('navigation_pkg'), 'config', 'keepout_mask.yaml'
    )

    filter_mask_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='filter_mask_server',
        output='screen',
        parameters=[param_file, {'yaml_filename': mask_yaml_file}]
    )

    costmap_filter_info_server = Node(
        package='nav2_map_server',
        executable='costmap_filter_info_server',
        name='costmap_filter_info_server',
        output='screen',
        parameters=[param_file]
    )

    # 1. Define the Lifecycle Manager to "turn on" the filter nodes
    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_filter',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['filter_mask_server', 'costmap_filter_info_server']
        }]
    )

    return LaunchDescription([
        # 2. Add the actual server nodes to the launch list
        filter_mask_server,
        costmap_filter_info_server,
        lifecycle_manager_node,

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(nav2_launch),
            launch_arguments={
                'map_yaml_file': map_file,
                'params_file': param_file,
                'use_sim': 'true',
                'start_rviz': 'true',
            }.items()
        ),
        # This starts the /move_action server your Python script is looking for
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(moveit_launch_path),
            launch_arguments={
                'use_sim_time': 'true',
            }.items()
        ),
    ])