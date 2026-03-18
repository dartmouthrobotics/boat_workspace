cmake_minimum_required(VERSION 3.8)
project(catabot_bringup)

find_package(ament_cmake REQUIRED)

# Install launch files
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

# Install param files
install(DIRECTORY param/
  DESTINATION share/${PROJECT_NAME}/param
)

# Install scripts
install(DIRECTORY script/
  DESTINATION lib/${PROJECT_NAME}
  USE_SOURCE_PERMISSIONS   
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
