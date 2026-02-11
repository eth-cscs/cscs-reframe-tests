cmake_minimum_required(VERSION 3.18)
project(IntraNodePinnedHostComm LANGUAGES CXX CUDA)

# Optimization flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
set(CMAKE_CUDA_FLAGS "${CMAKE_CUDA_FLAGS} -O3")

# Find CUDA toolkit
find_package(CUDAToolkit REQUIRED)

# Find MPI with C++ support
find_package(MPI REQUIRED)

# Your source file
set(SOURCES intranode_pinned_host_comm.cpp)

add_executable(intranode_pinned_host_comm ${SOURCES})

# Include directories
target_include_directories(intranode_pinned_host_comm PRIVATE
    /user-environment/env/default/include
    ${MPI_INCLUDE_PATH}
    ${CUDAToolkit_INCLUDE_DIRS}
)

link_directories(/user-environment/env/default/lib/)

# Link libraries
target_link_libraries(intranode_pinned_host_comm PRIVATE
    MPI::MPI_CXX
    CUDA::cudart
)
