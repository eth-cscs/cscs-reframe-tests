program hello_world_mpi_openmp
#ifdef _OPENMP
    use omp_lib
#endif
#ifdef USE_MPI   
    use mpi
   !include 'mpif.h'
#endif
   implicit none

   integer :: rank=0, size=1, tid=0, nthreads=1
   integer :: ierr, i, j, k
   integer :: mpiversion=0, mpisubversion=0
   integer :: resultlen = -1

#ifdef USE_MPI   
   character(len=MPI_MAX_PROCESSOR_NAME) :: processor_name
   character(len=MPI_MAX_LIBRARY_VERSION_STRING) :: mpilibversion
   !integer, dimension(MPI_STATUS_SIZE) :: status
   call MPI_INIT(ierr)
   call MPI_COMM_RANK(MPI_COMM_WORLD, rank, ierr)
   call MPI_COMM_SIZE(MPI_COMM_WORLD, size, ierr)
   call MPI_Get_processor_name(processor_name, resultlen, ierr)
   if (rank .eq. 0) then
        call MPI_Get_version(mpiversion, mpisubversion, iErr)
        call MPI_Get_library_version(mpilibversion, resultlen, ierr)
        write (*, '(A6,I1,A1,I1)') '# MPI-', mpiversion, '.', mpisubversion
        print *,trim(mpilibversion)
   endif
#else
   character(len=3) :: processor_name = 'nid'
#endif

!$OMP PARALLEL PRIVATE(tid, nthreads)
#ifdef _OPENMP
   if (rank .eq. 0) then
       print *, '# OMP-', _OPENMP
   endif
   tid = omp_get_thread_num()
   nthreads = omp_get_num_threads()
#else   
   tid = 0
   nthreads = 1
#endif   
   write(*, '(A24,1X,I3,A7,I3,1X,A12,1X,I3,1X,A6,I3,1X,A10)') &
       "Hello, World from thread ", &
       tid, "out of", nthreads, &
       "from rank", rank, "out of", size, trim(processor_name)
   ! flush(6)
!$OMP END PARALLEL

#ifdef USE_MPI   
   call MPI_FINALIZE(ierr)
#endif

end program hello_world_mpi_openmp
