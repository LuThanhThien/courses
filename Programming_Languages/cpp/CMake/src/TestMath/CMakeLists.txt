cmake_minimum_required(VERSION 3.13)

project(TestMath VERSION 1.0)


# Options
option(USE_MATHLIB "Use provided math library" ON)

if (USE_MATHLIB)
    # add_subdirectory(MathLib)
    list(APPEND EXTRA_LIBS_DIRS "MathLib")
    list(APPEND EXTRA_INCLUDES_DIRS "${PROJECT_SOURCE_DIR}/MathLib") 
    list(APPEND EXTRA_LINKS "MathLib")
endif()


# Configure
configure_file(${PROJECT_SOURCE_DIR}/TestMathConfig.h.in ${PROJECT_BINARY_DIR}/TestMathConfig.h)
add_executable(${PROJECT_NAME} main.cpp)
target_include_directories(${PROJECT_NAME} PUBLIC ${PROJECT_BINARY_DIR})

# DOWNLOAD THE SUBMODULES
find_package(Git QUIET)
if (GIT_FOUND AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
    # Update submodules as needed
    option(GIT_MODULE "Check submodules during build" ON)
    if (GIT_SUBMODULE)
        message(STATUS "Submodule update")
        execute_process(COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
                        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                        RESULT_VARIABLE GIT_SUBMOD_RESULT)
        if (NOT GIT_SUBMOD_RESULT EQUAL "0")
            message(FATAL_ERROR "git submodule update --init failed with ${GIT_SUBMOD_RESULT}, please checkout submodules")
        endif()
    endif()
endif()

# CHECK ALL SUBMODULES
if (NOT EXISTS "${PROJECT_SOURCE_DIR}/third_party/glfw/CMakeLists.txt")
    message(FATAL_ERROR "The GLFW submodule was not downloaded! GIT_SUBMODULE was turned off or failed. Please update submodules and try again.")
endif()

add_subdirectory(third_party/glfw)

target_include_directories(${PROJECT_NAME} 
    PUBLIC third_party/glfw/include
    ${EXTRA_INCLUDES_DIRS}
)

target_link_directories(${PROJECT_NAME} 
    PRIVATE third_party/glfw/src
    ${EXTRA_LIBS_DIRS}
)

target_link_libraries(${PROJECT_NAME} ${EXTRA_LINKS} glfw)

