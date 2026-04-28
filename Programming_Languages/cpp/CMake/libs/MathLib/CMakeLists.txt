cmake_minimum_required(VERSION 3.13)

project(MathLib)

add_library(MathLib MathLib.cpp)

target_include_directories(MathLib
  PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

set_target_properties(MathLib PROPERTIES PUBLIC_HEADER MathLib.h)

install(TARGETS MathLib
    LIBRARY DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)

