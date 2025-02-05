# fix for https://jira.cscs.ch/browse/VCMSA-344
NETCDF_BASEDIR = /opt/cray/pe/netcdf-hdf5parallel/default
RM := rm -f

ifeq ($(PE_ENV),)
    $(error PE_ENV is not set)
endif

ifeq ($(PE_ENV),CRAY)
	NETCDF_DIR_PE = ${shell ls -d $(NETCDF_BASEDIR)/CRAYCLANG/*}
endif

ifeq ($(PE_ENV),GNU)
	NETCDF_DIR_PE = ${shell ls -d $(NETCDF_BASEDIR)/GNU/*}
endif

ifeq ($(PE_ENV),NVIDIA)
	NETCDF_DIR_PE = ${shell ls -d $(NETCDF_BASEDIR)/NVIDIA/*}
endif

ifeq ($(PE_ENV),AOCC)
	NETCDF_DIR_PE = ${shell ls -d $(NETCDF_BASEDIR)/AOCC/*}
endif

ifeq ($(PE_ENV),UENV)
	INCP += ${shell pkg-config --cflags netcdf-cxx4}
	LDFLAGS += ${shell pkg-config --libs netcdf-cxx4} -Wl,-rpath,${shell pkg-config --variable=prefix netcdf-cxx4}/lib -Wl,-rpath,${shell pkg-config --variable=prefix netcdf}/lib
else	
	INCP += -I $(NETCDF_DIR_PE)/include
	LDFLAGS += -L $(NETCDF_DIR_PE)/lib -Wl,-rpath,$(NETCDF_DIR_PE)/lib -lnetcdf_c++4
endif

.SUFFIXES: .o .cpp

all: wr.exe rd.exe

wr.exe: simple_xy_wr.cpp
	-echo "# building serial C++ code"
	$(PREP) $(CXX) $(INCP) $< -o $(@) $(LDFLAGS)

rd.exe: simple_xy_rd.cpp wr.exe
	$(PREP) $(CXX) $(INCP) $< -o $(@) $(LDFLAGS)

clean:
	-$(RM) *.o *.exe *.nc
