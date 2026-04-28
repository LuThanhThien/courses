cmake_minimum_required(VERSION 3.13)

project(TestTimer)

set(TESTS_DIRS
  TestMath
  TestTimer
)

foreach(TEST_DIR ${TESTS_DIRS})
  add_subdirectory(${TEST_DIR})
endforeach()