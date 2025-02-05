! https://github.com/olcf/vector_addition_tutorials/blob/master/OpenACC/vecAdd.f90
program main
   use openacc
   implicit none
#ifdef _MPI
   include 'mpif.h'
#endif

   ! Size of vectors
   integer :: n = 100000
   ! Input vectors
   real(8), dimension(:), allocatable :: a
   real(8), dimension(:), allocatable :: b
   ! Output vector
   real(8), dimension(:), allocatable :: c
   !
   integer :: i, ierr=-1, isize=1, irank=0, num_devices=0
   real(8) :: sum
   integer(acc_device_kind) :: devtype
!!!   character*256 :: devvendor, devname
!!!   real :: devmem

#ifdef _MPI
   call MPI_Init(ierr)
   call MPI_Comm_size(MPI_COMM_WORLD, isize, ierr)
   call MPI_Comm_rank(MPI_COMM_WORLD, irank, ierr)
#endif

   devtype = acc_get_device_type()
   num_devices = acc_get_num_devices(devtype)
#ifdef _MPI
   if (irank .eq. 0) then
#endif   
       print '("Found "I0" device(s)"):', num_devices
       print *, '_OPENACC:', _OPENACC
#ifdef _MPI
   end if
#endif   
   !!! nvidia compiler only:
!!!   do i = 1, num_devices
!!!       devmem = real(acc_get_property(i, devtype, acc_property_memory)) / 1073741824
!!!       call acc_get_property_string(i, devtype, acc_property_vendor, devvendor)
!!!       call acc_get_property_string(i, devtype, acc_property_name, devname)
!!!       print '(" - "I3" : "A" | "F0.2" GB | "A"")', i, devvendor, devmem, devname
!!!   end do

   ! Allocate memory for each vector
   allocate (a(n))
   allocate (b(n))
   allocate (c(n))

   ! Initialize content of input vectors, vector a[i] = sin(i)^2 vector b[i] = cos(i)^2
   do i = 1, n
      a(i) = sin(i*1D0)*sin(i*1D0)
      b(i) = cos(i*1D0)*cos(i*1D0)
   end do

   ! Sum component wise and save result into vector c
   !$acc kernels copyin(a(1:n),b(1:n)), copyout(c(1:n))
   do i = 1, n
      c(i) = a(i) + b(i)
   end do
   !$acc end kernels

   sum = 0d0
   ! Sum up vector c and print result divided by n, this should equal 1 within error
   do i = 1, n
      sum = sum + c(i)
   end do
   sum = sum/n/isize

#ifdef _MPI
   if (irank .eq. 0) then
      call MPI_Reduce(MPI_IN_PLACE, sum, 1, MPI_REAL8, MPI_SUM, 0, MPI_COMM_WORLD, ierr)
      print *, 'final result: ', sum
   else
      call MPI_Reduce(sum, sum, 1, MPI_REAL8, MPI_SUM, 0, MPI_COMM_WORLD, ierr)
   end if
#else
   print *, 'final result: ', sum
#endif

   ! Release memory
   deallocate (a)
   deallocate (b)
   deallocate (c)

#ifdef _MPI
   call MPI_Finalize(ierr)
#endif

end program
