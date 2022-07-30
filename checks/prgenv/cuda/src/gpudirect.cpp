// Copyright (c) 2022 CSCS, ETH Zurich
#include <cassert>
#include <cuda_runtime.h>
#include <iostream>
#include <mpi.h>
#include <numeric>
#include <vector>

inline void checkErr(cudaError_t err, const char *filename, int lineno,
                     const char *funcName) {
  if (err != cudaSuccess) {
    const char *errName = cudaGetErrorName(err);
    const char *errStr = cudaGetErrorString(err);
    fprintf(stderr,
            "CUDA Error at %s:%d. Function %s returned err %d: %s - %s\n",
            filename, lineno, funcName, err, errName, errStr);
    exit(EXIT_FAILURE);
  }
}

#define checkGpuErrors(errcode)                                                \
  checkErr((errcode), __FILE__, __LINE__, #errcode);

void gpuDirect(int rank, int numElements, bool leak) {
  int *src;
  int *dest;
  checkGpuErrors(cudaMalloc((void **)&src, numElements * sizeof(int)));
  checkGpuErrors(cudaMalloc((void **)&dest, numElements * sizeof(int)));

  std::vector<int> init(numElements, -1);
  checkGpuErrors(cudaMemcpy(src, init.data(), numElements * sizeof(int),
                            cudaMemcpyHostToDevice));
  checkGpuErrors(cudaMemcpy(dest, init.data(), numElements * sizeof(int),
                            cudaMemcpyHostToDevice));

  std::vector<int> ref(numElements);
  std::iota(ref.begin(), ref.end(), 0);
  std::vector<int> probe(numElements);
  std::vector<MPI_Request> sendRequests;
  int tag = 0;

  if (rank == 0) {
    // std::cout << "rk=" << rank << std::endl;
    checkGpuErrors(cudaMemcpy(src, ref.data(), numElements * sizeof(int),
                              cudaMemcpyHostToDevice));

    int err = MPI_Send(src, numElements, MPI_INT, 1, tag, MPI_COMM_WORLD);
    assert(err == MPI_SUCCESS);
  } else {
    int err = MPI_Recv(dest, numElements, MPI_INT, 0, tag, MPI_COMM_WORLD,
                       MPI_STATUS_IGNORE);
    assert(err == MPI_SUCCESS);

    checkGpuErrors(cudaMemcpy(probe.data(), dest, numElements * sizeof(int),
                              cudaMemcpyDeviceToHost));
    if (probe == ref) {
      std::cout << "PASS:rk=" << rank << std::endl;
    } else {
      std::cout << "FAIL:rk=" << rank << ":";
      std::cout << probe[1] << std::endl;
      // for (auto i : probe)
      //   std::cout << i << " ";
      // std::cout << std::endl;
    }
  }

  if (!leak) {
    checkGpuErrors(cudaFree(src));
    checkGpuErrors(cudaFree(dest));
  }
  MPI_Barrier(MPI_COMM_WORLD);
}

int main(int argc, char **argv) {
  MPI_Init(&argc, &argv);

  int direct = getenv("MPICH_RDMA_ENABLED_CUDA") == NULL
                   ? 0
                   : atoi(getenv("MPICH_RDMA_ENABLED_CUDA"));
  if (direct != 1) {
    printf("MPICH_RDMA_ENABLED_CUDA not enabled!\n");
    exit (EXIT_FAILURE);
  }

  int rank = 0, nRanks = 0;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &nRanks);

  int thisExampleRanks = 2;

  if (nRanks != thisExampleRanks)
    throw std::runtime_error("this test needs 2 ranks\n");

  gpuDirect(rank, 16384, false); // 1st call
  gpuDirect(rank, 16384, false); //  2d call

  MPI_Finalize();
}
