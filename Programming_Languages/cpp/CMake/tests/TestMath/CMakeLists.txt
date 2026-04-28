cmake_minimum_required(VERSION 3.13)

project(TestMath VERSION 1.0)

# Options
option(USE_MATHLIB "Use provided math library" ON)

# Configure
add_executable(${PROJECT_NAME} main.cpp)

if (USE_MATHLIB)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_MATHLIB)
    target_link_libraries(${PROJECT_NAME} PRIVATE MathLib)
endif()


