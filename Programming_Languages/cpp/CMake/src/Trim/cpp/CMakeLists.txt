cmake_minimum_required(VERSION 3.0)

project(Trim)

add_executable(trim main.cpp)

install(TARGETS trim DESTINATION bin)
