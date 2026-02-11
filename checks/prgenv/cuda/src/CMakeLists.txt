cmake_minimum_required(VERSION 3.18)
project(IntraNodePinnedHostComm LANGUAGES CXX)

# Find CUDA toolkit
find_package(CUDAToolkit REQUIRED)

# Find MPI with C++ support
find_package(MPI REQUIRED)

# Your source file
set(SOURCES intranode_pinned_host_comm.cpp)

add_executable(intranode_pinned_host_comm ${SOURCES})

# Link libraries
target_link_libraries(intranode_pinned_host_comm PRIVATE
    MPI::MPI_CXX
    CUDA::cudart
)