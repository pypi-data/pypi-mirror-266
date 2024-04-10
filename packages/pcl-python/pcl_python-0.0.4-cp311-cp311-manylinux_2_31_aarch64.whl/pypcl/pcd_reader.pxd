import cython
cimport cython
from libcpp.vector cimport vector
from libcpp.string cimport string
from libc.stdint cimport uint16_t

cdef extern from "pcd_reader.h" namespace "my_library":
    cdef cppclass PCDReader:
        PCDReader()
        int read(string)
        
        int get_height()
        int get_width()
        
        vector[float] get_data()
        vector[float] get_x()
        vector[float] get_y()
        vector[float] get_z()
        vector[float] get_intensity()
        vector[double] get_timestamp()
        vector[uint16_t] get_ring()
        

        