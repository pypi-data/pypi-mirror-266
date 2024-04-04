import cffi
import os
import numpy as np
import sys
from typing import Sequence, Union

__all__ = ['PointMassTrajectorySolver', 'PointMassTrajectoryHSolver']

def load_lib():
    HERE = os.path.dirname(__file__)
    if sys.platform.startswith('linux'):
        LIB_FILE_NAME = os.path.abspath(os.path.join(HERE, ".", "compiled", "build", "bin", "lib", "libsextbal.so"))
    elif sys.platform.startswith('win32'):
        LIB_FILE_NAME = os.path.abspath(os.path.join(HERE, ".", "compiled", "build", "bin", "libsextbal.dll"))
    else:
        raise Exception('Неподдерживаемая платформа')
    ffi = cffi.FFI()

    ffi.cdef(
        '''
        void count_eb(double *y0, double d, double q, double *cx_list, double *mach_list, int n_mach,\n
        double max_distance, double tstep, double tmax);
        '''
    )
    ffi.cdef(
        '''
        void dense_count_eb(double *y_array, double d, double q, double *cx_list, double *mach_list, int n_mach,\n
        double max_distance, double tstep, double tmax, int *n_tsteps);
        '''
    )

    ffi.cdef(
        '''
        typedef struct shell{
        double d;
        double L;
        double q;
        double A;
        double B;
        double mu;
        double c_q;
        double h;
        } shell;
        '''
    )

    ffi.cdef(
        '''
        void dense_count_eb_h(
        double *y_array,
        double *cx_list, double *mach_list, int n_mach,
        shell *ashell,
        double *diag_vals,
        double eta,
        double sigma_dop,
        double delta_dop,
        double *sigma_array,
        double *delta_array,
        double max_distance,
        double tstep,
        double tmax,
        int *n_tsteps
        );
        '''
    )
    bal_lib = ffi.dlopen(LIB_FILE_NAME)
    return ffi, bal_lib

FFI, EBAL_LIB = load_lib()

class PointMassTrajectorySolver:

    mah_list = np.array([0.4, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6,
                         1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7,
                         2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6])

    cx_list = np.array([0.157, 0.158, 0.158, 0.160, 0.190, 0.325, 0.378, 0.385, 0.381, 0.371,
                        0.361, 0.351, 0.342, 0.332, 0.324, 0.316, 0.309, 0.303, 0.297,
                        0.292, 0.287, 0.283, 0.279, 0.277, 0.273, 0.270, 0.267, 0.265,
                        0.263, 0.263, 0.261, 0.260])

    name = 'point_mass_eb_solver'

    preprocess_data = dict(
        d=None,
        q=None,
        theta_angle=None,
        v0=None,
        cx_list=None,
        mach_list=None
    )

    def preprocessor(self, data: dict, global_state: dict):

        self.preprocess_data['d'] = data['gun_char']['d']
        self.preprocess_data['q'] = global_state['mcc_solver']['shell']['q']
        self.preprocess_data['theta_angle'] = data['initial_cond']['theta0']
        self.preprocess_data['v0'] = data['initial_cond']['V']
        self.preprocess_data['cx_list'] = global_state['mcdrag_solver']['cx_list']
        self.preprocess_data['mach_list'] = global_state['mcdrag_solver']['mach_list']


    def run(self, data: dict, global_state: dict):

        eb_data = self.preprocess_data
        eb_settings = data['point_mass_eb_settings']

        v0 = eb_data['v0']
        theta_angle = eb_data['theta_angle']
        q = eb_data['q']
        d = eb_data['d']

        cx_list = eb_data['cx_list']
        mach_list = eb_data['mach_list']

        max_distance = eb_settings['max_distance']
        tstep = eb_settings['tstep']
        tmax = eb_settings['tmax']

        y0 = np.array([0., 0., v0, np.deg2rad(theta_angle)], dtype=np.float64, order='F')
        cx_list = np.asfortranarray(cx_list, dtype=np.float64)
        mach_list = np.asfortranarray(mach_list, dtype=np.float64)
        y0_ptr = FFI.cast("double*", y0.__array_interface__['data'][0])
        cx_list_ptr = FFI.cast("double*", cx_list.__array_interface__['data'][0])
        mach_list_ptr = FFI.cast("double*", mach_list.__array_interface__['data'][0])

        EBAL_LIB.count_eb(
            y0_ptr, d, q, cx_list_ptr, mach_list_ptr, len(cx_list),
            max_distance, tstep, tmax
        )

        global_state[PointMassTrajectorySolver.name] = dict(L_max=y0[0],
                                                            vc=y0[2])

class PointMassTrajectoryHSolver:

    name = 'point_mass_ebh_solver'

    preprocess_data = dict(
        d=None,
        L=None,
        q=None,
        A=None,
        B=None,
        h=None,
        mu=None,
        c_q=None,
        sigma_dop=0.6,
        delta_dop=2.,
        theta_angle=None,
        v0=None,
        cx_list=None,
        mach_list=None
    )

    def preprocessor(self, data: dict, global_state: dict):

        self.preprocess_data['d'] = data['gun_char']['d']
        self.preprocess_data['eta_k'] = data['gun_char']['eta_k']
        self.preprocess_data['q'] = global_state['mcc_solver']['shell']['q']
        self.preprocess_data['L'] = global_state['geometry_solver']['L_all']
        self.preprocess_data['A'] = global_state['mcc_solver']['shell']['A']
        self.preprocess_data['B'] = global_state['mcc_solver']['shell']['B']
        self.preprocess_data['h'] = global_state['mcc_solver']['shell']['h']
        self.preprocess_data['mu'] = global_state['mcc_solver']['shell']['mu']
        self.preprocess_data['c_q'] = global_state['mcc_solver']['shell']['c_q']
        self.preprocess_data['theta_angle'] = data['initial_cond']['theta0']
        self.preprocess_data['v0'] = data['initial_cond']['V']
        self.preprocess_data['cx_list'] = global_state['kontur_solver']['cx_list']
        self.preprocess_data['mach_list'] = global_state['kontur_solver']['mach_list']
        print(self.preprocess_data['A'])
        print(self.preprocess_data['B'])
        print(self.preprocess_data['L'])
        print(self.preprocess_data['h'])

    def _get_fortran_shell(self):

        ashell = FFI.new('shell *ashell')
        ashell[0].d = self.preprocess_data['d']
        ashell[0].q = self.preprocess_data['q']
        ashell[0].A = self.preprocess_data['A']
        ashell[0].B = self.preprocess_data['B']
        ashell[0].mu = self.preprocess_data['mu']
        ashell[0].c_q = self.preprocess_data['c_q']
        ashell[0].L = self.preprocess_data['L']
        ashell[0].h = self.preprocess_data['h']

        return ashell

    # Определение по диаграмме устойчивости правильность полёта
    def stability_define(self, m, n, eta_k, h, d, hd_kr, eta_kr):
        # Гироскопическая устойчивость
        h_d = h / d

        eta_list = [i / 1000 for i in range(100)]
        h_d_sigma_list = [(eta ** 2) * m for eta in eta_list]

        # Направленность полёта
        h_d_stab_list = [eta * n for eta in eta_list]

        # Определяем устойчив ли снаряд


        # ДОДЕЛАТЬ

    def run(self, data: dict, global_state: dict):

        ebh_settings = data['settings']['point_mass_eb']

        tstep = ebh_settings['tstep']
        tmax = ebh_settings['tmax']

        eta_k = self.preprocess_data['eta_k']

        ashell = self._get_fortran_shell()

        n_tsteps = FFI.new('int *')
        n_tsteps[0] = int(tmax / tstep)

        cx_list = self.preprocess_data['cx_list']
        mach_list = self.preprocess_data['mach_list']

        cx_list = np.asfortranarray(cx_list, dtype=np.float64)
        mach_list = np.asfortranarray(mach_list, dtype=np.float64)

        y_array = np.zeros((5, n_tsteps[0]), dtype=np.float64, order='F')
        y_array[:, 0] = [0., 0., self.preprocess_data['v0'], np.deg2rad(self.preprocess_data['theta_angle']), 0.0]

        sigma_array = np.zeros(n_tsteps[0], dtype=np.float64, order='F')
        delta_array = np.zeros(n_tsteps[0], dtype=np.float64, order='F')

        diag_vals_array = np.empty(4, dtype=np.float64, order='F')

        y_array_ptr = FFI.cast("double*", y_array.__array_interface__['data'][0])
        cx_list_ptr = FFI.cast("double*", cx_list.__array_interface__['data'][0])
        mach_list_ptr = FFI.cast("double*", mach_list.__array_interface__['data'][0])
        sigma_array_ptr = FFI.cast("double*", sigma_array.__array_interface__['data'][0])
        delta_array_ptr = FFI.cast("double*", delta_array.__array_interface__['data'][0])
        diag_vals_array_ptr = FFI.cast("double*", diag_vals_array.__array_interface__['data'][0])


        EBAL_LIB.dense_count_eb_h(
            y_array_ptr,
            cx_list_ptr, mach_list_ptr, len(cx_list),
            ashell,
            diag_vals_array_ptr,
            eta_k,
            self.preprocess_data['sigma_dop'],
            np.deg2rad(self.preprocess_data['delta_dop']),
            sigma_array_ptr,
            delta_array_ptr,
            ebh_settings['max_distance'],
            tstep,
            tmax,
            n_tsteps
        )

        # Диаграмма устойчивости
        self.stability_define(m=diag_vals_array[0], n=diag_vals_array[1], eta_k=eta_k,
                              h=global_state['mcc_solver']['shell']['h'], d=data['shell_size']['d'],
                              hd_kr=diag_vals_array[2], eta_kr=diag_vals_array[3])


        t_s = np.linspace(0., tstep * n_tsteps[0], n_tsteps[0])
        y_array = y_array[:, :n_tsteps[0]]
        sigma_array = sigma_array[:n_tsteps[0]]
        delta_array = delta_array[:n_tsteps[0]]
        y_array[3] = np.rad2deg(y_array[3])

        global_state[PointMassTrajectoryHSolver.name] = dict(
            m=diag_vals_array[0],
            n=diag_vals_array[1],
            hd_kr=diag_vals_array[2],
            eta_kr=diag_vals_array[3],
            L_max=y_array[0, -1],
            vc=y_array[2, -1],
            t_array=t_s,
            x_array=y_array[0],
            y_array=y_array[1],
            v_array=y_array[2],
            theta_array=y_array[3],
            omega_array=y_array[4],
            sigma_array=sigma_array,
            delta_array=delta_array
        )




