.SUFFIXES : .F .f .c .o .a .f90 .f95 .F90
########################################################################
#              Adapt these variables to your environment
########################################################################
F90      = gfortran
#F90FLAGS = -C -check -fpp
#F90FLAGS = -check bounds
#F90FLAGS = -pg
F90FLAGS = -O2 -fPIC -ffree-line-length-512 -I/usr/include -I/usr/local/include -I/opt/local/include -I/usr/lib64/gfortran/modules -L/usr/lib -L/usr/include/lib -L/opt/local/lib
NCDF_INC = /usr/include
NCDF_LIB = /usr/lib

INC = /usr/include
LIB = /usr/lib

# Non-optional simulators. You should not need to change this
RS_PATH = quickbeam
CS_PATH = actsim
LLNL_PATH = llnl
ISCCP_PATH = icarus-scops-4.1-bsd
MISR_PATH = MISR_simulator
MODIS_PATH = MODIS_simulator
########################################################################
#              End of modifications
########################################################################

OBJS =  cosp_radar.o cosp_types.o cosp_constants.o cosp_simulator.o \
        cosp_utils.o scops.o prec_scops.o cosp.o cosp_stats.o \
        pf_to_mr.o \
        cosp_lidar.o radar_simulator_types.o zeff.o \
        array_lib.o atmos_lib.o dsd.o calc_Re.o format_input.o \
        gases.o scale_LUTs_io.o radar_simulator_init.o \
        math_lib.o mrgrnk.o optics_lib.o radar_simulator.o \
        lidar_simulator.o cosp_io.o llnl_stats.o lmd_ipsl_stats.o \
        cosp_isccp_simulator.o icarus.o \
        cosp_misr_simulator.o MISR_simulator.o \
        cosp_modis_simulator.o modis_simulator.o \
        cosp_rttov_simulator.o

.PHONY: all

all: $(OBJS)

%.o: %.f90
	@echo $(F90) $(F90FLAGS) -c -I$(NCDF_INC) $<
	$(F90) $(F90FLAGS) -c -I$(NCDF_INC) $<
	@echo "-----------------------------"

%.o: %.F90
	@echo $(F90) $(F90FLAGS) -c -I$(NCDF_INC) $<
	$(F90) $(F90FLAGS) -c -I$(NCDF_INC) $<
	@echo "-----------------------------"

cosp_io.o       : cosp_constants.o cosp_types.o cosp_modis_simulator.o
cosp.o          : cosp_simulator.o cosp_types.o cosp_modis_simulator.o
cosp_lidar.o    : cosp_constants.o cosp_types.o
cosp_radar.o    : cosp_constants.o cosp_types.o radar_simulator_types.o \
	              array_lib.o atmos_lib.o format_input.o math_lib.o optics_lib.o
cosp_simulator.o: cosp_types.o cosp_radar.o cosp_lidar.o \
                  cosp_isccp_simulator.o cosp_misr_simulator.o \
                  cosp_modis_simulator.o cosp_rttov_simulator.o cosp_stats.o
cosp_stats.o    : cosp_constants.o cosp_types.o llnl_stats.o lmd_ipsl_stats.o
cosp_types.o    : cosp_constants.o cosp_utils.o radar_simulator_types.o \
                  scale_LUTs_io.o radar_simulator_init.o
cosp_utils.o    : cosp_constants.o
lmd_ipsl_stats.o : llnl_stats.o
array_lib.o    : mrgrnk.o
dsd.o          : array_lib.o math_lib.o calc_Re.o
format_input.o : array_lib.o
math_lib.o                : array_lib.o mrgrnk.o
radar_simulator.o         : array_lib.o math_lib.o mrgrnk.o optics_lib.o \
	                        radar_simulator_types.o
zeff.o                    : math_lib.o optics_lib.o
cosp_isccp_simulator.o    : cosp_constants.o cosp_types.o
cosp_misr_simulator.o     : cosp_constants.o cosp_types.o
cosp_modis_simulator.o    : cosp_constants.o cosp_types.o modis_simulator.o
cosp_rttov_simulator.o    : cosp_constants.o cosp_types.o

clean_objs:
	rm -f $(OBJS) *.mod *.o

clean:
	rm -f $(OBJS) *.mod *.o fort.*

scops.o : $(ISCCP_PATH)/scops.f
	$(F90) $(F90FLAGS) -c -I$(ISCCP_PATH) $<

icarus.o : $(ISCCP_PATH)/icarus.f
	$(F90) $(F90FLAGS) -c $<

prec_scops.o : $(LLNL_PATH)/prec_scops.f
	$(F90) $(F90FLAGS) -c $<

pf_to_mr.o : $(LLNL_PATH)/pf_to_mr.f
	$(F90) $(F90FLAGS) -c $<

radar_simulator_types.o : $(RS_PATH)/radar_simulator_types.f90
	$(F90) $(F90FLAGS) -c $<

radar_simulator_init.o : $(RS_PATH)/radar_simulator_init.f90
	$(F90) $(F90FLAGS) -c $<

scale_LUTs_io.o : $(RS_PATH)/scale_LUTs_io.f90
	$(F90) $(F90FLAGS) -c $<

atmos_lib.o : $(RS_PATH)/atmos_lib.f90
	$(F90) $(F90FLAGS) -c $<

zeff.o : $(RS_PATH)/zeff.f90
	$(F90) $(F90FLAGS) -c $<

array_lib.o : $(RS_PATH)/array_lib.f90
	$(F90) $(F90FLAGS) -c $<

dsd.o : $(RS_PATH)/dsd.f90
	$(F90) $(F90FLAGS) -c $<

calc_Re.o : $(RS_PATH)/calc_Re.f90
	$(F90) $(F90FLAGS) -c $<

format_input.o : $(RS_PATH)/format_input.f90
	$(F90) $(F90FLAGS) -c $<

gases.o : $(RS_PATH)/gases.f90
	$(F90) $(F90FLAGS) -c $<

math_lib.o : $(RS_PATH)/math_lib.f90
	$(F90) $(F90FLAGS) -c $<

mrgrnk.o : $(RS_PATH)/mrgrnk.f90
	$(F90) $(F90FLAGS) -c $<

optics_lib.o : $(RS_PATH)/optics_lib.f90
	$(F90) $(F90FLAGS) -c $<

radar_simulator.o : $(RS_PATH)/radar_simulator.f90
	$(F90) $(F90FLAGS) -c $<

lidar_simulator.o : $(CS_PATH)/lidar_simulator.F90
	$(F90) $(F90FLAGS) -c $<

lmd_ipsl_stats.o : $(CS_PATH)/lmd_ipsl_stats.F90
	$(F90) $(F90FLAGS) -c $<

llnl_stats.o : $(LLNL_PATH)/llnl_stats.F90
	$(F90) $(F90FLAGS) -c $<

cosp_radar.o : $(LLNL_PATH)/cosp_radar.F90
	$(F90) $(F90FLAGS) -c $<

MISR_simulator.o : $(MISR_PATH)/MISR_simulator.f
	$(F90) $(F90FLAGS) -c $<

modis_simulator.o : $(MODIS_PATH)/modis_simulator.F90
	$(F90) $(F90FLAGS) -c $<

cosp_rttov.o : cosp_rttov.F90
	$(F90) $(F90FLAGS) -c -I $(RTTOV_INC_PATH) -I $(RTTOV_MOD_PATH) $<
