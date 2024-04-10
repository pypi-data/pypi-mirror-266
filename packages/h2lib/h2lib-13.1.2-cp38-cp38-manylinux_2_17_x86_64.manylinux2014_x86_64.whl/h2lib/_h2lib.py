from contextlib import contextmanager
from h2lib.dll_wrapper import DLLWrapper
from h2lib.h2lib_signatures import H2LibSignatures
import os
import sys

from multiclass_interface.multiprocess_interface import MultiProcessClassInterface, ProcessClass
import numpy as np


def H2Lib(suppress_output=False, subprocess=True):
    H2 = [H2LibThread, H2LibProcess][subprocess]
    return H2(suppress_output=suppress_output)


class H2LibThread(H2LibSignatures, DLLWrapper):
    _model_path = '.'
    _aero_sections_data_shape = {}

    def __init__(self, suppress_output=True, filename=None, cwd='.'):
        if filename is None:
            if os.name == 'nt':
                filename = os.path.dirname(__file__) + '/HAWC2Lib.dll'
            else:
                filename = os.path.dirname(__file__) + '/HAWC2Lib.so'  # pragma: no cover
        # doubles the speed of single instances and 2N of N instances on linux
        os.environ['MKL_THREADING_LAYER'] = 'sequential'
        filename = os.path.abspath(filename)
        library_bin = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '../Library/bin'))
        if os.path.isdir(library_bin):  # pragma: no cover
            os.add_dll_directory(library_bin)
        DLLWrapper.__init__(self, filename, cwd=cwd, cdecl=True)
        self.suppress_output = suppress_output
        self._initialized = False
        self.time = 0

    @property
    def model_path(self):
        return self._model_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self._initialized:
            self.finalize()
        DLLWrapper.close(self)
        return "closed h2lib"

    def getState(self):
        return H2LibSignatures.getState(self, restype=np.int32)[1]

    def work(self, time):
        """Return number of loops"""
        return H2LibSignatures.work(self, np.float64(time), restype=np.int64)[1]

    def loop(self, N):
        """Return time to compute N loops"""
        return H2LibSignatures.loop(self, int(N), restype=np.float64)[1]

    def get_version(self):
        s = " " * 255
        return H2LibSignatures.get_version(self, s)[0][0].strip()

    def get_wind_speed(self, pos_g):
        return self.get_lib_function('get_wind_speed')(np.asarray(pos_g, dtype=np.float64),
                                                       np.asarray([0, 0, 0], dtype=np.float64))[0][1]

    def get_uvw(self, pos_g):
        vx, vy, vz = self.get_wind_speed(pos_g)
        return [vy, vx, -vz]

    def get_time(self):
        return np.round(H2LibSignatures.get_time(self, time=0.)[0][0], 6)

    def read_input(self, htc_path='htc/input_hawc.htc', model_path='.'):
        self._model_path = model_path
        self.cwd = self.model_path
        return H2LibSignatures.read_input(self, htc_path)

    def init(self, htc_path=None, model_path='.'):
        assert not hasattr(self, '_init_result'), "init called twice"
        if htc_path is not None:
            self.read_input(htc_path, model_path)
        r = H2LibSignatures.init(self)
        self._initialized = True
        return r

    def step(self):
        self.time = np.round(H2LibSignatures.step(self, restype=np.float64)[1], 6)
        return self.time

    def run(self, time):
        self.time = np.round(H2LibSignatures.run(self, np.float64(time), restype=np.float64)[1], 6)
        return self.time

    def add_sensor(self, sensor_line):
        """Add sensor to hawc2. The sensor will be accessible from h2lib but will not show up in the output file of HAWC2
        Note, that some sensors consist of multiple HAWC2 sensors, e.g. "wind free_wind" which has a Vx, Vy and Vz sensors

        Parameters
        ----------
        Sensor_line : str
            Sensor line as used in the output sections in HAWC2. See How2Hawc2

        Returns
        -------
        index_lst : list
            List of sensor index(es). These index(es) can be used to call get_sensor_info or get_sensor_values
        """
        if ";" not in sensor_line:
            sensor_line += ";"
        index_start, index_stop = 0, 0
        index_start, index_stop = H2LibSignatures.add_sensor(self, sensor_line.lower(), index_start, index_stop)[0][1:]
        return tuple(range(index_start, index_stop + 1))

    def get_sensor_info(self, id):
        "return name, unit, description"
        if isinstance(id, tuple):
            return [self.get_sensor_info(i) for i in id]
        return [s[:-1].strip()  # remove null termination
                for s in H2LibSignatures.get_sensor_info(self, id, name=" " * 30, unit=" " * 10, desc=" " * 512)[0][1:]]

    def get_sensor_values(self, id_lst):
        """Get sensor values from HAWC2

        Parameters
        ----------
        id_lst : array_like or int
            list of sensor ids

        Returns
        -------
        values : array_like or float
        """
        if isinstance(id_lst, int):
            return self.get_sensor_values([id_lst])[0]
        values = np.zeros(len(id_lst), dtype=np.float64)
        id_lst = np.array(id_lst, dtype=np.int64)
        return H2LibSignatures.get_sensor_values(self, id_lst, values, len(id_lst))[0][1]

    def set_variable_sensor_value(self, id, value):
        return H2LibSignatures.set_variable_sensor_value(self, id, np.float64(value))

    def init_windfield(self, Nxyz, dxyz, box_offset_yz, transport_speed):
        """Initialize wind field which afterwards can be set using set_windfield


        x: direction of wind
        y: horizontal to the left when looking along x
        z: vertical up

        Parameters
        ----------
        Nxyz : (int, int, int)
            Number of points in wind field
        dxyz : (float, float, float)
            Distance between wind field points
        box_offset_yz : (float, float)
            Box offset in y and z, relative to hawc2 origo. Note this is in met coordinates as described above
            To set a wind field of size 200x80x80, such that the center is located at hawc2 coordinate (0,0,-70),
            box_offset_yz must be (-40,30)
            Note that the wind field size is (Nxyz)-1*dxyz
        transport_speed : float
            Box transport speed

        Notes
        -----
        The wind field will be transported in the hawc2 global y-direction with the transport speed,
        In HAWC2:
        - shear format is set to 0 (which also means that the mean wind (transport speed) is not added)
        - turbformat is set to 1 (mann), but the buffer should be filled manually via set_windfield
        - center_pos0 is set such that the lower right corner (when looking along global y) is located at box_offset_yz
        - windfield_rotations is set to (0,0,0), i.e. the wind is aligned with y, and w points up (opposite global z)
        - scaling is disabled
        - the buffer is interpolated in the standard way, i.e. it is mirrored in the lateral and vertical direction and
          repeated in the longitudinal direction

        """
        return H2LibSignatures.init_windfield(self, np.array(Nxyz, dtype=np.int64), np.array(dxyz, dtype=np.float64),
                                              np.array(box_offset_yz, dtype=np.float64), np.float64(transport_speed))

    def set_windfield(self, uvw, box_offset_x, time=None):
        """Set wind field, must be called after init_windfield and init

        Parameters
        ----------
        uvw : array_like, dims=(3,Nx,Ny,Nz)
            wind field components including mean wind speed, shear etc.
        box_offset_x : float
            Offset in x direction at the <time>
            To set a wind field of size 200x80x80, such that the front plane (largest x) is located
            at hawc2 coordinate (0,20,-70), i.e. 20m downstream of origo, set box_offset_x=-180
            Note that the wind field size is (Nxyz)-1*dxyz
            Note also that the end plane (x=0) will be located in -180 and repeated in 20+dx
        time : float, optional
            Time at which the the last plane (x=0) is at x=box_offset_x
            If None, default, time is set to the current time in HAWC2

        Notes
        -----
        uvw must be scaled in advance to the right turbulence level
        and should contain mean wind, shear, gusts, direction change etc.
        and uvw(:,1) is the back plane of the turbulence box, while uvw(:,Nx) is the front plane
        """
        if time is None:
            time = self.get_time()
        return H2LibSignatures.set_windfield(self, np.asarray(uvw, dtype=np.float32),
                                             np.float64(box_offset_x), np.float64(time))

    # ===================================================================================================================
    # H2rotor
    # ===================================================================================================================

    def get_rotor_dims(self):
        return [[self.get_nSections(r, b) for b in range(self.get_nblades(r))]
                for r in range(self.get_nrotors())]

    def get_nrotors(self):
        return H2LibSignatures.get_nrotors(self, restype=np.int64)[1]

    def get_nblades(self, rotor=0):
        return H2LibSignatures.get_nblades(self, rotor + 1, restype=np.int64)[1]

    def get_nSections(self, rotor=0, blade=0):
        return H2LibSignatures.get_nSections(self, rotor + 1, blade + 1, restype=np.int64)[1]

    def get_diameter(self, rotor=0):
        return H2LibSignatures.get_diameter(self, rotor + 1, restype=np.float64)[1]

    def aero_sections_data_shape(self, rotor):
        if rotor not in self._aero_sections_data_shape:
            self._aero_sections_data_shape[rotor] = (self.get_nblades(rotor), self.get_nSections(rotor), 3)
        return self._aero_sections_data_shape[rotor]

    def get_aerosections_position(self, rotor=0):
        position = np.zeros(self.aero_sections_data_shape(rotor), dtype=np.float64, order='F')
        return H2LibSignatures.get_aerosections_position(self, rotor + 1, position)[0][1]

    def set_aerosections_windspeed(self, uvw, rotor=0):
        return H2LibSignatures.set_aerosections_windspeed(self, rotor + 1, uvw)

    def get_aerosections_forces(self, rotor=0):
        shape = self.aero_sections_data_shape(rotor)
        Fxyz = np.zeros(shape, dtype=np.float64, order='F')
        return H2LibSignatures.get_aerosections_forces(self, rotor + 1, Fxyz)[0][1]

    def get_aerosections_moments(self, rotor=0):
        shape = self.aero_sections_data_shape(rotor)
        Mxyz = np.zeros(shape, dtype=np.float64, order='F')
        return H2LibSignatures.get_aerosections_moments(self, rotor + 1, Mxyz)[0][1]

    def get_bem_grid_dim(self, rotor=0):
        """returns (nazi, nrad)"""
        return H2LibSignatures.get_bem_grid_dim(self, rotor + 1, 0, 0)[0][1:]

    def get_bem_grid(self, rotor=0):
        """returns azi, rad"""
        nazi, nrad = self.get_bem_grid_dim(rotor)
        return H2LibSignatures.get_bem_grid(self, rotor + 1,
                                            np.zeros(nazi, dtype=np.float64, order='F'),
                                            np.zeros(nrad, dtype=np.float64, order='F'))[0][1:]

    def get_induction_polargrid(self, rotor=0):
        nazi, nrad = self.get_bem_grid_dim(rotor)
        induction = np.zeros((nazi, nrad), dtype=np.float64, order='F')
        return H2LibSignatures.get_induction_polargrid(self, rotor + 1, induction)[0][1]

    def get_induction_axisymmetric(self, rotor=0):
        nrad = self.get_bem_grid_dim(rotor)[1]
        induction = np.zeros(nrad, dtype=np.float64)
        return H2LibSignatures.get_induction_axisymmetric(self, rotor + 1, induction)[0][1]

    def get_induction_rotoravg(self, rotor=0):
        induction = np.float64(0)
        return H2LibSignatures.get_induction_rotoravg(self, rotor + 1, induction)[0][1]

    def get_rotor_orientation(self, rotor=0, deg=False):
        """return yaw, tilt, azi(of first blade) in rad(default) or deg"""
        r = H2LibSignatures.get_rotor_orientation(self, rotor=rotor + 1, yaw=0., tilt=0., azi=0.)[0][1:]
        if deg:
            return np.rad2deg(r)
        else:
            return r

    def get_rotor_position(self, rotor=0):
        return H2LibSignatures.get_rotor_position(self, rotor=rotor + 1, position=np.zeros(3, dtype=np.float64))[0][1]

    def get_rotor_avg_wsp(self, coo=1, rotor=0):
        """Returns the rotor averaged wind speed in global(coo=1, default) or rotor(coo=2) coordinates."""
        assert self.time > 0
        wsp = np.zeros(3, dtype=np.float64)
        return H2LibSignatures.get_rotor_avg_wsp(self, coo=coo, rotor=rotor + 1, wsp=wsp)[0][2]

    def get_rotor_avg_uvw(self, rotor=0):
        vx, vy, vz = self.get_rotor_avg_wsp(1, rotor)
        return [vy, vx, -vz]


@contextmanager
def set_LD_LIBRARY_PATH():
    _file__ = np.__file__
    old = os.environ.get('LD_LIBRARY_PATH', "")

    if '/lib/' in _file__:  # pragma: no cover  (only on linux)
        lib_path = _file__[:_file__.index("/lib/") + 5]
        os.environ['LD_LIBRARY_PATH'] = f'{lib_path}:{old}'

    try:
        yield
    finally:
        os.environ['LD_LIBRARY_PATH'] = old


class H2LibProcess(ProcessClass, H2LibThread):
    def __init__(self, suppress_output, filename=None, cwd='.'):
        with set_LD_LIBRARY_PATH():
            ProcessClass.__init__(self, cls=H2LibThread, cls_attrs=set(dir(H2LibThread)) - set(dir(ProcessClass)))
            self(suppress_output=suppress_output, filename=filename, cwd=cwd)


def MultiH2Lib(N, filename=None, cwd='.', suppress_output=False):

    if not hasattr(suppress_output, '__len__'):
        suppress_output = [suppress_output] * N
    args = [(suppress_output[i], filename, cwd) for i in range(N)]

    with set_LD_LIBRARY_PATH():
        from multiclass_interface import mpi_interface
        if mpi_interface.size > 1:  # pragma: no cover
            # try:
            #     with H2LibThread(filename):
            #         pass
            #     # LD_LIBRARY_PATH is set. Run H2LibThread directly in mpi processes
            #     cls = H2LibThread
            # except OSError:
            #     # Set LD_LIBRARY_PATH in mpi workers and run H2LibThread from the workers via ProcessClass
            #     cls = H2LibProcess
            from multiclass_interface.mpi_interface import MPIClassInterface
            cls = H2LibProcess
            return MPIClassInterface(cls, args)
        else:
            return MultiProcessClassInterface(H2LibThread, args)
