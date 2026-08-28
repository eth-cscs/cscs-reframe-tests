program offload_f
    use, intrinsic :: iso_fortran_env
    use omp_lib, only : omp_is_initial_device, omp_get_num_devices
    implicit none

    integer, parameter :: n = 1048576
    real(real64), allocatable :: a(:)
    integer :: i
    logical :: gpu = .false.

    allocate(a(n), stat=)

    !$omp target teams distribute parallel do map(from:a) map(tofrom:gpu)
    do i = 1, n
        a(i) = 2.0_real64 * i
        if (i == 1) gpu = .not. omp_is_initial_device()
    enddo
    print '(A,I0,A,L1)', "ndev=", omp_get_num_devices(), " gpu=", gpu
    deallocate(a)

end program offload_f
