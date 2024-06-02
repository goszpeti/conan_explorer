project("ConanExplorer")
cmake_minimum_required(VERSION 3.22)
set(CONAN_DISABLE_CHECK_COMPILER ON)

# if ( EXISTS ${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo_multi.cmake)
#     include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo_multi.cmake)
# elseif ( EXISTS ${CMAKE_CURRENT_BINARY_DIR}/../conanbuildinfo_multi.cmake)
#     include(${CMAKE_CURRENT_BINARY_DIR}/../conanbuildinfo_multi.cmake)
# endif()

# if ( EXISTS ${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
#     include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
# elseif ( EXISTS ${CMAKE_CURRENT_BINARY_DIR}/../conanbuildinfo.cmake)
#     include(${CMAKE_CURRENT_BINARY_DIR}/../conanbuildinfo.cmake)
# endif()
# conan_basic_setup(TARGETS NO_OUTPUT_DIRS)

# C++ standard settings:
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)#
list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
list(APPEND CMAKE_PREFIX_PATH ${CMAKE_BINARY_DIR})

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt6 REQUIRED COMPONENTS Widgets Core)

# set(PYTHON_EXECUTABLE "path to python executable")
set(PYTHON_LIBRARY_DIR ${CMAKE_ROOT_DIR}/.venv/Lib/site-packages)
find_package(pybind11 REQUIRED)
# find_package(cpython REQUIRED)

set(AUTOGEN_BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR}/autogen)

set(SOURCES
    src/fluent_window/fluent_window.cpp
    src/fluent_window/fluent_window.h
    src/fluent_window/fluent.qrc
)
set(EXE_NAME ConanExplorer)
add_executable(${EXE_NAME}
    ${SOURCES}
)

# set_target_properties(${EXE_NAME} PROPERTIES VERSION 1.0.0)

# for export symbols
target_compile_definitions(${EXE_NAME}
    PRIVATE FLW_LIBRARY
)

# Make all non-exported symbols hidden by default
set_target_properties(${EXE_NAME}
    PROPERTIES
        CXX_VISIBILITY_PRESET hidden
        AUTOGEN_BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR}
)

# Export the library's public header path to dependent targets
target_include_directories(${EXE_NAME}
    INTERFACE
        ${CMAKE_CURRENT_SOURCE_DIR}/fluent_window/src
)

target_link_libraries(${EXE_NAME}
    PUBLIC

    # Qt5::Core
    # Qt5::Widgets
    # Qt5::Gui
    qt::qt
    pybind11::embed
)

install(TARGETS ${EXE_NAME}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION bin
        PUBLIC_HEADER DESTINATION include)

# add_executable(${EXE_NAME}_EXAMPLE
#     src/fluent_window/main.cpp
# )

# target_include_directories(${EXE_NAME}_EXAMPLE PRIVATE
#     $<$<CONFIG:RELWITHDEBINFO>:${CMAKE_CURRENT_BINARY_DIR}/include_RelWithDebInfo>
#     $<$<CONFIG:RELEASE>:${CMAKE_CURRENT_BINARY_DIR}/include_Release>
#     $<$<CONFIG:DEBUG>:${CMAKE_CURRENT_BINARY_DIR}/include_Debug>
# )

# target_link_libraries(${EXE_NAME}_EXAMPLE
#     ${EXE_NAME}
#     qt::qt
# )

# add_custom_command( TARGET ${EXE_NAME} POST_BUILD
#         COMMAND ${CMAKE_COMMAND} -E copy
#             ${CONAN_QT_ROOT}/bin/Qt5Core${CMAKE_SHARED_LIBRARY_SUFFIX}
#             ${CONAN_QT_ROOT}/bin/Qt5Gui${CMAKE_SHARED_LIBRARY_SUFFIX}
#             ${CONAN_QT_ROOT}/bin/Qt5Widgets${CMAKE_SHARED_LIBRARY_SUFFIX}
#             $<TARGET_FILE_DIR:${EXE_NAME}>
#         )

# if (MSVC)
# add_custom_command(TARGET ${EXE_NAME} POST_BUILD
#     COMMAND ${CMAKE_COMMAND} -E make_directory() 
#     "$<TARGET_FILE_DIR:${EXE_NAME}>/platforms"
# )
# add_custom_command( TARGET ${EXE_NAME} POST_BUILD
#         COMMAND ${CMAKE_COMMAND} -E copy
#             ${CONAN_QT_ROOT}/bin/archdatadir/plugins/platforms/qwindows.dll
#             $<TARGET_FILE_DIR:${EXE_NAME}>/platforms/
#         )
# endif()