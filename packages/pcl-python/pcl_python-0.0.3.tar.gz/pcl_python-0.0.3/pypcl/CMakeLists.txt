cmake_minimum_required(VERSION 3.10)

include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})

add_cython_target(_pypcl CXX)
add_library(_pypcl MODULE _pypcl pcd_reader.cpp)

target_link_libraries(_pypcl ${PCL_LIBRARIES}  ${PYTHON_LIBRARIES} )
target_include_directories(_pypcl PUBLIC ${PYTHON_INCLUDE_DIRS} ./)
target_compile_definitions(_pypcl PUBLIC ${PCL_DEFINITIONS})

python_extension_module(_pypcl)

install(TARGETS _pypcl LIBRARY DESTINATION pypcl)
