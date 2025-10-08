cmake_minimum_required(VERSION 3.13)

project(MathLib)

add_library(MathLib MathLib.cpp)									# lib/impl

set_target_properties(MathLib PROPERTIES PUBLIC_HEADER MathLib.h) 	# header

install(TARGETS MathLib 
	LIBRARY DESTINATION lib
	PUBLIC_HEADER DESTINATION include
)

