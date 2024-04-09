import ctypes as ct
import os
import numpy as np
from numpy.ctypeslib import ndpointer

class STEAM_materials:

    def __init__(self, func_name, n_arg, n_points, C_FUN_folder=None):
        """

        :param func_name: string with function name corresponding to dll file name (without the .dll in the string)
        :param n_arg:	number of arguments of the func_name function. This corresponds to number of columns in 2D numpy array, numpy2d, to be used in the method. Use numpy2d.shape[1] to get the number.
        :param n_points: number of points to evaluate. This corresponds to number of rows in 2D numpy array, numpy2d, to be used in the eval method. Use numpy2d.shape[0] to get the number.
        :param C_FUN_folder: If not specified, the code assumes the .dll files are in a folder called CFUN in the same directory as this script. Otherwise a full path to a folder needs to be given.
        """
        if C_FUN_folder:
            self.C_FUN_folder = C_FUN_folder  # allows user to specify full path to folder with .dlls
        else:
            self.C_FUN_folder = os.path.join(os.getcwd(), "CFUN")  # Assumes .dlls are in a folder called CFUN in the same directory as this script
        _dll = ct.CDLL(os.path.join(self.C_FUN_folder + os.sep + 'CFUN', f'{func_name}.dll'))
        self.func_name = func_name.encode('ascii')
        self.n_points = n_points
        self.n_arg = n_arg
        array_type = ct.c_double * self.n_points
        self.RealPtr = array_type()
        self.Int_Ptr = array_type()
        _doublepp = ndpointer(dtype=np.uintp, ndim=1, flags='C')
        f_name = ct.c_char_p
        n_arg = ct.c_int
        b_size = ct.c_int
        ifail = ct.c_long
        _dll.init.argtypes = []
        _dll.init.restype = ct.c_long
        self.eval = _dll.eval
        self.eval.argtypes = [f_name, n_arg, _doublepp, _doublepp, b_size, array_type, array_type]
        self.eval.restype = ifail

    def evaluate(self, numpy2d):
        """
        DLL funcion call. It can take a tuple with arguments or numpy array where each row is a set of arguments
        :param numpy2d: Numpy array with number of columns corresponding to number of function arguments and points to evaluate in rows
        :return: Numpy array with values calculated by .dll function
        """
        inReal = (numpy2d.__array_interface__['data'][0] + np.arange(numpy2d.shape[0]) * numpy2d.strides[0]).astype(np.uintp)
        error_out = self.eval(self.func_name, self.n_arg, inReal, inReal, self.n_points, self.RealPtr, self.Int_Ptr)
        if error_out == 1:
            pass
        else:
            raise ValueError(f"There was a problem with calling {self.func_name}.dll with arguments {numpy2d}. Check if dll file exists or if number of arguments is correct.")
        return np.array(self.RealPtr)

