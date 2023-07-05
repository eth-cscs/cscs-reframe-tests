#include <stdio.h>
#ifdef _OPENMP
#include <omp.h>
#endif
#ifdef USE_MPI
#include "mpi.h"
#endif

int main(int argc, char *argv[]) {
  int rank = 0, size = 1;
  int mpiversion, mpisubversion;
  int resultlen = -1;
#ifdef USE_MPI
  char mpilibversion[MPI_MAX_LIBRARY_VERSION_STRING];
  int namelen;
  char processor_name[MPI_MAX_PROCESSOR_NAME];
#else
  char processor_name = '\0';
#endif
  int tid = 0, nthreads = 1;

#ifdef USE_MPI
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);
  MPI_Get_processor_name(processor_name, &namelen);
  if (rank == 0) {
    MPI_Get_version(&mpiversion, &mpisubversion);
    MPI_Get_library_version(mpilibversion, &resultlen);
    printf("# MPI-%d.%d = %s\n", mpiversion, mpisubversion, mpilibversion);
  }
#endif

#pragma omp parallel default(shared) private(tid)
  {
#ifdef _OPENMP
    nthreads = omp_get_num_threads();
    tid = omp_get_thread_num();
#endif
    printf(
        "Hello, World from thread %d out of %d from rank %d out of %d %s\n",
        tid, nthreads, rank, size, processor_name);
  }

#ifdef USE_MPI
  MPI_Finalize();
#endif

  return 0;
}
