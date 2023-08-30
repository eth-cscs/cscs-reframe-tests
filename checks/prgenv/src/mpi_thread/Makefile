all: mpi_init_thread_single.exe mpi_init_thread_funneled.exe mpi_init_thread_serialized.exe mpi_init_thread_multiple.exe
RM := rm -f

# CC -D_MPI_THREAD_SINGLE mpi_init_thread.cpp -o ./MpiInitTest_0
mpi_init_thread_single.exe: mpi_init_thread.cpp
	$(PREP) $(CXX) -D_MPI_THREAD_SINGLE $(CXXFLAGS) $< -o $(@) $(LDFLAGS)

mpi_init_thread_funneled.exe: mpi_init_thread.cpp
	$(PREP) $(CXX) -D_MPI_THREAD_FUNNELED $(CXXFLAGS) $< -o $(@) $(LDFLAGS)

mpi_init_thread_serialized.exe: mpi_init_thread.cpp
	$(PREP) $(CXX) -D_MPI_THREAD_SERIALIZED $(CXXFLAGS) $< -o $(@) $(LDFLAGS)

mpi_init_thread_multiple.exe: mpi_init_thread.cpp
	$(PREP) $(CXX) -D_MPI_THREAD_MULTIPLE $(CXXFLAGS) $< -o $(@) $(LDFLAGS)

clean:
	-$(RM) *.o *.exe
