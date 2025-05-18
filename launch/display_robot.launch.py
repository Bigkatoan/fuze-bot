# my_robot_description/launch/display_robot.launch.py

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    # Tìm thư mục chia sẻ của package này
    pkg_share = get_package_share_directory('fuze-bot')

    # Đường dẫn đến tệp URDF (hoặc Xacro)
    # Thay 'my_robot.urdf' bằng tên tệp của bạn
    urdf_file_path = os.path.join(pkg_share, 'urdf', 'robot.urdf')
    # Nếu bạn dùng Xacro:
    # urdf_file_path = os.path.join(pkg_share, 'urdf', 'my_robot.urdf.xacro')

    # Khai báo launch argument cho việc sử dụng tệp URDF
    # urdf_model_arg = DeclareLaunchArgument(
    #     'urdf_model',
    #     default_value=urdf_file_path,
    #     description='Path to robot URDF file'
    # )

    # Lấy nội dung URDF từ tệp
    # Nếu dùng URDF thuần:
    with open(urdf_file_path, 'r') as infp:
        robot_desc_content = infp.read()
    # Nếu dùng Xacro, bạn cần xử lý nó trước:
    # robot_desc_content = Command(['xacro ', LaunchConfiguration('urdf_model')])

    # Khai báo launch argument cho việc sử dụng sim_time (nếu dùng Gazebo)
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true'
    )

    # --- Robot State Publisher Node ---
    # Node này publish các transform (TF) của robot dựa trên URDF và joint states
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_desc_content,
            'use_sim_time': use_sim_time
        }]
        # Nếu dùng Xacro, thay 'robot_description': robot_desc_content bằng:
        # 'robot_description': Command(['xacro ', urdf_file_path])
    )

    # --- Joint State Publisher Node (Tùy chọn, cho robot không có controller thật) ---
    # Node này cho phép bạn điều khiển các khớp bằng thanh trượt GUI hoặc publish giá trị khớp giả
    # Cần thiết nếu robot của bạn không có node nào khác publish /joint_states
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        # condition=UnlessCondition(LaunchConfiguration('gui')) # Có thể thêm điều kiện nếu muốn
    )

    # --- Joint State Publisher GUI Node (Tùy chọn) ---
    # Cung cấp giao diện đồ họa để điều khiển các khớp
    # use_gui = LaunchConfiguration('gui', default='true')
    # joint_state_publisher_gui_node = Node(
    #     package='joint_state_publisher_gui',
    #     executable='joint_state_publisher_gui',
    #     name='joint_state_publisher_gui',
    #     condition=IfCondition(use_gui)
    # )

    # --- RViz2 Node ---
    # Khởi chạy RViz2 để hiển thị mô hình robot
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'display_robot.rviz') # Tạo file này ở bước sau
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file], # Tải file cấu hình RViz2
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        # urdf_model_arg, # Nếu bạn khai báo argument này
        use_sim_time_arg,
        robot_state_publisher_node,
        joint_state_publisher_node, # Bỏ đi nếu robot của bạn tự publish /joint_states
        # joint_state_publisher_gui_node, # Bỏ đi nếu không cần GUI điều khiển khớp
        rviz_node
    ])
