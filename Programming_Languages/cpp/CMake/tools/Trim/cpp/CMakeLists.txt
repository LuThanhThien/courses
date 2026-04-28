cmake_minimum_required(VERSION 4.3.2)

project(Trim)

add_executable(trim main.cpp)

install(TARGETS trim DESTINATION bin)
