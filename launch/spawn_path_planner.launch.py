import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node, SetParameter
from launch.conditions import IfCondition, UnlessCondition
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
    PythonExpression,
    PathJoinSubstitution
)


def generate_launch_description():

    ### DATA INPUT ###
    vikings_bot_name_arg = DeclareLaunchArgument("vikings_bot_name",
        default_value="vikings_bot_1",
        description="Namespace of robot - [vikings_bot_1 or vikings_bot_2]"
    )

    use_sim_arg = DeclareLaunchArgument("use_sim",
        default_value="True",
        description='Use simulation or real time'
    )

    use_lidar_arg = DeclareLaunchArgument(
        'use_lidar',
        default_value='True',
        description="Use lidar for navigation"
    )
    
    use_depth_cam_arg = DeclareLaunchArgument(
        'use_depth_cam',
        default_value='False',
        description="Use depth camera for navigation"
    )


    vikings_bot_name = LaunchConfiguration("vikings_bot_name")
    use_sim = LaunchConfiguration("use_sim")
    use_lidar = LaunchConfiguration('use_lidar')
    use_depth_cam = LaunchConfiguration('use_depth_cam')

    package_name = 'vikings_bot_path_planner_server'


    ### CONFIG FILES ###
    controller_yaml = PathJoinSubstitution([get_package_share_directory(package_name), 'config', PythonExpression(["'", vikings_bot_name, "_controller.yaml'"]) ])
    bt_navigator_yaml = PathJoinSubstitution([get_package_share_directory(package_name), 'config', PythonExpression(["'", vikings_bot_name, "_bt_navigator.yaml'"]) ])
    planner_yaml = PathJoinSubstitution([get_package_share_directory(package_name), 'config', PythonExpression(["'", vikings_bot_name, "_planner_server.yaml'"]) ])
    recovery_yaml = PathJoinSubstitution([get_package_share_directory(package_name), 'config', PythonExpression(["'", vikings_bot_name, "_recovery.yaml'"]) ])

    behavior = PathJoinSubstitution([get_package_share_directory(package_name), 'config', 'behavior.xml'])

    # topic and observation source change conditions for local_costmap controller
    do_use_lidar = PythonExpression(["'", use_lidar, "'.lower() == 'true'"])
    do_use_depth_cam = PythonExpression(["'", use_depth_cam, "'.lower() == 'true'"])
    do_use_lidar_and_depth_cam = PythonExpression(["('", use_depth_cam, "'.lower() == 'true') and ('", use_lidar, "'.lower() == 'true')"])
   
    ### NODES ###
    controller_node_n_params = GroupAction( # group to only set these params for this node
        actions=[
            SetParameter( # set obesrvation sources to only lidar
                name="voxel_layer.observation_sources",
                value='scan',
                condition=IfCondition(do_use_lidar)
            ),
            SetParameter( # set observation sources to only depth cam
                name="voxel_layer.observation_sources",
                value='point_cloud',
                condition=IfCondition(do_use_depth_cam)
            ),
            SetParameter( # set obesrvation sources to both lidar and depth cam
                name="voxel_layer.observation_sources",
                value='scan point_cloud',
                condition=IfCondition(do_use_lidar_and_depth_cam)
            ),
            Node(
                namespace=vikings_bot_name,
                package='nav2_controller',
                executable='controller_server',
                name='controller_server',
                output='screen',
                respawn=True,
                parameters=[
                    controller_yaml,
                    {'use_sim_time': use_sim}
                ]
            )
        ]
    )   

    planner_node_n_params = GroupAction( # group to only set these params for this node
        actions=[
            SetParameter( # set obesrvation sources to only lidar
                name="obstacle_layer.observation_sources",
                value='scan',
                condition=IfCondition(do_use_lidar)
            ),
            SetParameter( # set observation sources to only depth cam
                name="obstacle_layer.observation_sources",
                value='point_cloud',
                condition=IfCondition(do_use_depth_cam)
            ),
            SetParameter( # set obesrvation sources to both lidar and depth cam
                name="obstacle_layer.observation_sources",
                value='scan point_cloud',
                condition=IfCondition(do_use_lidar_and_depth_cam)
            ),
            Node(
                namespace=vikings_bot_name,
                package='nav2_planner',
                executable='planner_server',
                name='planner_server',
                output='screen',
                respawn=True,
                parameters=[
                    planner_yaml,
                    {'use_sim_time': use_sim}
                ]
            )
        ]
    )

    behaviour = Node(
        namespace=vikings_bot_name,
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        respawn=True,
        parameters=[
            recovery_yaml,
            {'use_sim_time': use_sim}
        ],
        output='screen',
    )

    navigator = Node(
        namespace=vikings_bot_name,
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        respawn=True,
        parameters=[
            bt_navigator_yaml,
            {"default_nav_to_pose_bt_xml": behavior},
            {'use_sim_time': use_sim}
        ]
    )

    lifecycle = Node(
        namespace=vikings_bot_name,
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_pathplanner',
        output='screen',
        respawn=True,
        parameters=[
            {'autostart': True},
            {'use_sim_time': use_sim},
            {'node_names': [
                'planner_server',
                'controller_server',
                'behavior_server',
                'bt_navigator'
            ]}
        ]
    )

    return LaunchDescription([
        vikings_bot_name_arg,
        use_sim_arg,
        use_lidar_arg,
        use_depth_cam_arg,

        SetParameter('use_sim_time',  use_sim),

        controller_node_n_params,
        planner_node_n_params,
        behaviour,
        navigator,
        lifecycle

    ])

