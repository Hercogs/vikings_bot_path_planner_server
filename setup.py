from setuptools import find_packages, setup
import os
from glob import glob
import yaml

package_name = 'path_planner_server'

# set correct behavior.xml path in *bt_navigator.yaml files
# because $(find-pkg-share) doesn't work in yaml file for some reason..
def find_key_set_val(data, search_key=None, set_value=None):
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = find_set_key_dict(value, search_key, set_value)
        else:
            if key == search_key:
                data[search_key] = set_value
                return data
    return data

behavior_file_path = os.path.join(os.getcwd(), "config", "behavior.xml")
config_file_list = os.listdir(os.path.join(os.getcwd(), "config"))

for config_file in config_file_list:
    if config_file.endswith("bt_navigator.yaml"):
        # change default_nav_to_pose_bt_xml property
        config_file_abs_path = os.path.join(os.getcwd(), "config", config_file)

        # read contents into variable
        yaml_file = open(config_file_abs_path, "r")
        content = yaml.safe_load(yaml_file)
        yaml_file.close()

        # find default_nav_to_pose_bt_xml property and change
        content = find_key_set_val(
            data=content,
            search_key="default_nav_to_pose_bt_xml",
            set_value=behavior_file_path)
        
        # write to file
        yaml_file = open(config_file_abs_path, "w")
        yaml.dump(content, yaml_file, sort_keys=False)
        yaml_file.close()


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join("share", package_name, "config"), glob("config/*")),
        (os.path.join("share", package_name, "rviz"), glob("rviz/*")),
        (os.path.join("share", package_name, "launch"), glob("launch/*")),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hercogs',
    maintainer_email='jecuks96@gmail.coms',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
