cmake_minimum_required(VERSION 3.14)
project(panthera_ht_description)

find_package(ament_cmake REQUIRED)

install(
		DIRECTORY meshes xacro config urdf
		DESTINATION share/${PROJECT_NAME}/
)

ament_package()
