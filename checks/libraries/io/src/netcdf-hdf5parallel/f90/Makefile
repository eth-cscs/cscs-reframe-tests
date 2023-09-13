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
	INCP += ${shell pkg-config --cflags netcdf-fortran}
	LDFLAGS += ${shell pkg-config --libs netcdf-fortran} -Wl,-rpath,${shell pkg-config --variable=prefix netcdf-fortran}/lib -Wl,-rpath,${shell pkg-config --variable=prefix netcdf}/lib
else	
	INCP += -I $(NETCDF_DIR_PE)/include
	LDFLAGS += -L $(NETCDF_DIR_PE)/lib -Wl,-rpath,$(NETCDF_DIR_PE)/lib -lnetcdff
endif


.SUFFIXES: .o .F90

all: wr.exe rd.exe

wr.exe: simple_xy_par_wr2.F90
	$(PREP) $(FC) $(INCP) $< -o $(@) $(LDFLAGS)

rd.exe: simple_xy_par_rd.F90 wr.exe
	$(PREP) $(FC) $(INCP) $< -o $(@) $(LDFLAGS)

clean:
	-$(RM) *.o *.exe *.nc
