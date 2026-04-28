cmake_minimum_required(VERSION 3.13)

project(cmake_libs)

set(LIBS_DIRS
  Timer
  MathLib
)

foreach(LIB_DIR ${LIBS_DIRS})
  add_subdirectory(${LIB_DIR})
endforeach()
