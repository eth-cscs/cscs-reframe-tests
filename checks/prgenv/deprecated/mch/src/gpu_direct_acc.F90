program GpuDirectAcc
    ! This code tests MPI communication on GPU with OpenACC using the
    ! host_data directive - the test will fail of not compiled with OpenACC

    use mpi

    implicit none

    integer :: ierr, status(MPI_STATUS_SIZE), i
    integer :: mpi_size, mpi_rank
    integer(8) :: mydata(1), data_sum(1), ref_val

    call MPI_Init(ierr)

    call MPI_Comm_size(MPI_COMM_WORLD, mpi_size, ierr)
    call MPI_Comm_rank(MPI_COMM_WORLD, mpi_rank, ierr)

    mydata(1) = mpi_rank
    data_sum(1)=0

#ifdef _OPENACC
    if (mpi_rank==0) write(*,*) "MPI test on GPU with OpenACC using ",mpi_size,"tasks"
#else
    if (mpi_rank==0) write (*,*) "Error : test not compiled with OpenACC"
    call mpi_abort(MPI_COMM_WORLD, -1, ierr) 
#endif

    !$acc data create(mydata,data_sum)
    !$acc update device(mydata,data_sum)
    ! Errase mydata on CPU to make sure only GPU values are used
    mydata(1)=-9999

    !$acc host_data use_device(mydata,data_sum)
    call MPI_Reduce(mydata, data_sum, 1, MPI_INTEGER8, MPI_SUM, 0, MPI_COMM_WORLD, ierr)
    !$acc end host_data

    !$acc update host(data_sum)


    !Check results
    if (mpi_rank.eq.0) then
      ref_val=0
      !$acc parallel loop reduction(+:ref_val)
      do i=0,mpi_size-1
        ref_val=ref_val+i
      end do
      if (data_sum(1)/=ref_val) then
        write (*,*) "Result : FAIL"
        write (*,*) "Expected value : ", ref_val, "actual value:",data_sum(1)
      else
        write (*,*) "Result : OK"
      end if
    end if
    !$acc end data

    call MPI_Finalize(ierr);

end program GpuDirectAcc
