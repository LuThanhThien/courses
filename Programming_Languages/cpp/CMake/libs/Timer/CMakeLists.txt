cmake_minimum_required(VERSION 3.13)

project(Timer)

add_library(Timer Timer.cpp)

target_include_directories(Timer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})