program offload_f
    use, intrinsic :: iso_fortran_env
    use omp_lib
    implicit none

    integer, parameter :: n = 1048576
    real(real64), allocatable :: a(:)
    integer :: i
    logical :: gpu = .false.

    allocate(a(n))

    !$omp target teams distribute parallel do map(from:a) map(tofrom:gpu)
    do i = 1, n
        a(i) = 2.0d0 * i
        if (i == 1) gpu = .not. omp_is_initial_device()
    enddo
    deallocate(a)
    print '(A,I0,A,L1)', "ndev=", omp_get_num_devices(), " gpu=", gpu

end program offload_f
