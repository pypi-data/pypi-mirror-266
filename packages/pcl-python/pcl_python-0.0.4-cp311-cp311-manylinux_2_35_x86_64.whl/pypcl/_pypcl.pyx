# cython: language_level=3
# cython: profile=True
# distutils: language = c++

from libcpp.vector cimport vector
from libcpp.string cimport string
from .pcd_reader cimport PCDReader as PCDReaderCpp
from cython.operator cimport dereference as deref
from libcpp.memory cimport shared_ptr, make_shared
import sys

cdef class PCDReader:
    cdef shared_ptr[PCDReaderCpp] ptr

    def __cinit__(self):
        self.ptr = make_shared[PCDReaderCpp]()

    def __len__(self):
        return self.get_width()

    def __repr__(self):
        return "<PointCloud of %d points>" % self.get_width()

    def _encode(self, path):
        if isinstance(path, bytes):
            return path
        else:
            return path.encode(sys.getfilesystemencoding())

    def _read(self, const char *filename):
        ret = deref(self.ptr).read(string(filename))
        assert(ret!=-1)
        return ret

    def read(self, filename):
        return self._read(self._encode(filename))

    def get_height(self):
        return deref(self.ptr).get_height()

    def get_width(self):
        return deref(self.ptr).get_width()
    
    def get_x(self):
        return deref(self.ptr).get_x()
    
    def get_y(self):
        return deref(self.ptr).get_y()

    def get_z(self):
        return deref(self.ptr).get_z()

    def get_intensity(self):
        return deref(self.ptr).get_intensity()

    def get_timestamp(self):
        return deref(self.ptr).get_timestamp()

    def get_ring(self):
        return deref(self.ptr).get_ring()
