project(test_alm)
cmake_minimum_required(VERSION 2.6)

# check libs and packages (headers + lib)

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

############ lbfgs library ################################################
file(GLOB LBFGS_FILES "${CMAKE_CURRENT_SOURCE_DIR}/../liblbfgs/lib/*.c")
file(GLOB LBFGS_INCS "${CMAKE_CURRENT_SOURCE_DIR}/../liblbfgs/include/*.h")
add_library(LBFGS STATIC ${LBFGS_FILES} ${LBFGS_INCS})
target_link_libraries(LBFGS m)
###########################################################################

############ alm library ##################################################
file(GLOB ALM_INCS "${CMAKE_CURRENT_SOURCE_DIR}/../include/*.h")
set(ALM_INCS ${ALM_INCS} ${LBFGS_INCS})
file(GLOB ALM_FILES "${CMAKE_CURRENT_SOURCE_DIR}/../lib/*.c")
add_library(ALM STATIC ${ALM_FILES} ${ALM_INCS})
target_link_libraries(ALM m LBFGS)
###########################################################################

set(CMAKE_BUILD_TYPE "Release")

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/../liblbfgs/include/ ${CMAKE_CURRENT_SOURCE_DIR}/../liblbfgs/lib/ ${CMAKE_CURRENT_SOURCE_DIR}/../include/)
link_directories(${CMAKE_CURRENT_SOURCE_DIR}/lib/)
set(LIBS ${CMAKE_REQUIRED_LIBRARIES} m LBFGS ALM)
link_libraries(${LIBS})

add_executable(thomson thomson.c)
