cmake_minimum_required(VERSION 3.13)

project(TestTimer)

add_executable(TestTimer main.cpp)

target_link_libraries(TestTimer
  PRIVATE
    Timer
)