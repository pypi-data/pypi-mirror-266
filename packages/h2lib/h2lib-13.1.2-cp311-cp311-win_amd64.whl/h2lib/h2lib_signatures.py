# noqa

from h2lib.dll_wrapper import DLLWrapper


class H2LibSignatures():
    def add_sensor(self, sensor_line, index_start, index_stop):
        '''subroutine add_sensor(sensor_line, index_start, index_stop) bind(C, name="add_sensor")
      integer*8 :: index_start, index_stop
      character(kind=c_char, len=1), intent(in)       :: sensor_line(1024)
    end subroutine'''
        return self.get_lib_function('add_sensor')(sensor_line, index_start, index_stop)

    def echo_version(self, ):
        '''subroutine echo_version() BIND(C, NAME='echo_version')
    !DEC$ ATTRIBUTES DLLEXPORT :: echo_version
    !GCC$ ATTRIBUTES DLLEXPORT :: echo_version
    type (tbuildinfo)   :: b
end subroutine'''
        return self.get_lib_function('echo_version')()

    def extern_write_log(self, c_msg, n, dll_name, error, warning):
        '''subroutine extern_write_log(c_msg, n, dll_name, error, warning) bind(C, name="extern_write_log")
            integer, intent(in) :: n
            character(kind=c_char, len=1), intent(in) :: c_msg(n)
            character(kind=c_char), intent(in) :: dll_name(50)
            logical(kind=c_bool), intent(in), optional :: error, warning
    character(kind=c_char, len=1), intent(in) :: c_msg(n_msg)
    integer, intent(in) :: n_msg
    character(kind=c_char), intent(in) :: dll_name(50)
    character(len=50) :: n
    logical(kind=c_bool), intent(in), optional :: error, warning
end subroutine'''
        return self.get_lib_function('extern_write_log')(c_msg, n, dll_name, error, warning)

    def fail(self, str_arr):  # pragma: no cover
        '''subroutine fail(str_arr) bind(C, name='fail')
    character(kind=c_char, len=1), intent(inout)       :: str_arr(255)
  end subroutine'''
        return self.get_lib_function('fail')(str_arr)

    def finalize(self, ):
        '''SUBROUTINE finalize() bind(C, name="finalize")
!DEC$ ATTRIBUTES DLLEXPORT :: finalize
  integer:: i
  real*4:: T2
END SUBROUTINE'''
        return self.get_lib_function('finalize')()

    def getSquare(self, val, restype):
        '''function getSquare(val) result(valSquared) BIND(C, NAME='getSquare')
  !DEC$ ATTRIBUTES DLLEXPORT :: getSquare
        real(RK), intent(in) :: val
        real(RK)             :: valSquared
    end function'''
        return self.get_lib_function('getSquare')(val, restype=restype)

    def getState(self, restype):
        '''function getState() result(val) BIND(C, NAME='getState')
  !DEC$ ATTRIBUTES DLLEXPORT :: getState
        integer             :: val
    end function'''
        return self.get_lib_function('getState')(restype=restype)

    def get_aerosections_forces(self, rotor, Fxyz):
        '''subroutine get_aerosections_forces(rotor, Fxyz) bind(C, name='get_aerosections_forces')
    integer*8, intent(in) :: rotor
    real(c_double),intent(out)::Fxyz(rotors_gl%rotor(rotor)%nbld, rotors_gl%rotor(rotor)%blade(1)%nsec, 3)
  end subroutine'''
        return self.get_lib_function('get_aerosections_forces')(rotor, Fxyz)

    def get_aerosections_moments(self, rotor, Mxyz):
        '''subroutine get_aerosections_moments(rotor, Mxyz) bind(C, name='get_aerosections_moments')
    integer*8, intent(in) :: rotor
    real(c_double),intent(out):: Mxyz(rotors_gl%rotor(rotor)%nbld, rotors_gl%rotor(rotor)%blade(1)%nsec, 3)
  end subroutine'''
        return self.get_lib_function('get_aerosections_moments')(rotor, Mxyz)

    def get_aerosections_position(self, rotor, position):
        '''subroutine get_aerosections_position(rotor, position) bind(C, name="get_aerosections_position")
    integer*8, intent(in) :: rotor
    real(c_double),intent(out)   :: position(rotors_gl%rotor(rotor)%nbld, rotors_gl%rotor(rotor)%blade(1)%nsec, 3)
  end subroutine'''
        return self.get_lib_function('get_aerosections_position')(rotor, position)

    def get_bem_grid(self, rotor, azi, rad):
        '''subroutine get_bem_grid(rotor, azi, rad) bind(C, name="get_bem_grid")
    integer*8, intent(in)               :: rotor
    real(c_double), intent(out)       :: azi(rotors_gl%rotor(rotor)%dyn_induc%bem%nazi)
    real(c_double), intent(out)       :: rad(rotors_gl%rotor(rotor)%dyn_induc%bem%nrad)
  end subroutine'''
        return self.get_lib_function('get_bem_grid')(rotor, azi, rad)

    def get_bem_grid_dim(self, rotor, nazi, nrad):
        '''subroutine get_bem_grid_dim(rotor, nazi, nrad) bind(C, name="get_bem_grid_dim")
    integer*8, intent(in)               :: rotor
    integer*8, intent(out)              :: nazi, nrad
  end subroutine'''
        return self.get_lib_function('get_bem_grid_dim')(rotor, nazi, nrad)

    def get_diameter(self, rotor, restype):
        '''function get_diameter(rotor) bind(C, name="get_diameter")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_diameter
    integer*8, intent(in) :: rotor
    Type (Taerorotor),pointer :: rotor_p
    real(c_double)  :: get_diameter
 end function'''
        return self.get_lib_function('get_diameter')(rotor, restype=restype)

    def get_induction_axisymmetric(self, rotor, induction):
        '''subroutine get_induction_axisymmetric(rotor, induction) bind(C, name="get_induction_axisymmetric")
    integer*8, intent(in)        :: rotor
    real(c_double),intent(out)   :: induction(rotors_gl%rotor(rotor)%dyn_induc%bem%nrad)
  end subroutine'''
        return self.get_lib_function('get_induction_axisymmetric')(rotor, induction)

    def get_induction_polargrid(self, rotor, induction):
        '''subroutine get_induction_polargrid(rotor, induction) bind(C, name="get_induction_polargrid")
      integer*8, intent(in)        :: rotor
      real(c_double),intent(out)   :: induction(rotors_gl%rotor(rotor)%dyn_induc%bem%nazi, rotors_gl%rotor(rotor)%dyn_induc%bem%nrad)
  end subroutine'''
        return self.get_lib_function('get_induction_polargrid')(rotor, induction)

    def get_induction_rotoravg(self, rotor, induction):
        '''subroutine get_induction_rotoravg(rotor, induction) bind(C, name="get_induction_rotoravg")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_induction_rotoravg
    integer*8, intent(in)        :: rotor
    real(c_double), intent(out) :: induction
  end subroutine'''
        return self.get_lib_function('get_induction_rotoravg')(rotor, induction)

    def get_nSections(self, rotor, blade, restype):
        '''function get_nSections(rotor, blade) bind(C, name="get_nSections")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_nSections
    integer*8, intent(in) :: rotor, blade
    integer*8             :: get_nSections
  end function'''
        return self.get_lib_function('get_nSections')(rotor, blade, restype=restype)

    def get_nblades(self, rotor, restype):
        '''function get_nblades(rotor) bind(C, name="get_nblades")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_nblades
    integer*8, intent(in) ::  rotor
    integer*8             :: get_nblades
  end function'''
        return self.get_lib_function('get_nblades')(rotor, restype=restype)

    def get_nrotors(self, restype):
        '''function get_nrotors() bind(C, name="get_nrotors")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_nrotors
    integer*8 :: get_nrotors
  end function'''
        return self.get_lib_function('get_nrotors')(restype=restype)

    def get_rotor_avg_wsp(self, coo, rotor, wsp):
        '''subroutine get_rotor_avg_wsp(coo, rotor, wsp) bind(C, name="get_rotor_avg_wsp")
    integer*8, intent(in) :: rotor
    integer*8, intent(in) :: coo ! 1: global, 2: rotor
    real(c_double), dimension(3):: wsp
  end subroutine'''
        return self.get_lib_function('get_rotor_avg_wsp')(coo, rotor, wsp)

    def get_rotor_orientation(self, rotor, yaw, tilt, azi):
        '''subroutine get_rotor_orientation(rotor, yaw, tilt, azi) bind(C, name="get_rotor_orientation")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_rotor_orientation
    integer*8, intent(in) :: rotor
    real(c_double), intent(out) :: yaw, tilt, azi
  end subroutine'''
        return self.get_lib_function('get_rotor_orientation')(rotor, yaw, tilt, azi)

    def get_rotor_position(self, rotor, position):
        '''subroutine get_rotor_position(rotor, position) bind(C, name="get_rotor_position")
    !DEC$ ATTRIBUTES DLLEXPORT :: get_rotor_position
    integer*8, intent(in) :: rotor
    real(c_double), dimension(3), intent(out) ::  position
  !DEC$ ATTRIBUTES DLLEXPORT :: get_rotor_avg_wsp
    integer*8, intent(in) :: rotor
    integer*8, intent(in) :: coo ! 1: global, 2: rotor
  end subroutine'''
        return self.get_lib_function('get_rotor_position')(rotor, position)

    def get_sensor_info(self, id, name, unit, desc):
        '''subroutine get_sensor_info(id, name, unit, desc) bind(C, name="get_sensor_info")
      integer*8, intent(in) :: id
      character(kind=c_char, len=1), intent(out)       :: name(30), unit(10), desc(512)
    end subroutine'''
        return self.get_lib_function('get_sensor_info')(id, name, unit, desc)

    def get_sensor_values(self, ids, values, n):
        '''subroutine get_sensor_values(ids, values, n) bind(C, name="get_sensor_values")
      integer*8, intent(in) :: n
      integer*8, intent(in) :: ids(n)
      real(c_double), intent(out)        :: values(n)
    end subroutine'''
        return self.get_lib_function('get_sensor_values')(ids, values, n)

    def get_time(self, time):
        '''subroutine
subroutine'''
        return self.get_lib_function('get_time')(time)

    def get_version(self, s):
        '''subroutine get_version(s) BIND(C, NAME='get_version')
                character(kind=c_char, len=1), intent(inout)  :: s(255)
            end subroutine'''
        return self.get_lib_function('get_version')(s)

    def init(self, ):
        '''subroutine init() bind(C, name="init")
     !DEC$ ATTRIBUTES DLLEXPORT :: init
    end subroutine'''
        return self.get_lib_function('init')()

    def init_windfield(self, Nxyz, dxyz, box_offset_yz, transport_speed):
        '''subroutine init_windfield(Nxyz, dxyz, box_offset_yz, transport_speed) bind(C, name="init_windfield")
      integer*8, dimension(3), intent(in) :: Nxyz
      real*8              :: transport_speed
    end subroutine'''
        return self.get_lib_function('init_windfield')(Nxyz, dxyz, box_offset_yz, transport_speed)

    def loop(self, N, restype):
        '''function loop(N) bind(C, Name='loop')
    !DEC$ ATTRIBUTES DLLEXPORT :: loop
    integer*8, intent(in) :: N
    real(c_double) :: loop,a
    integer*8 :: i, j
  end function'''
        return self.get_lib_function('loop')(N, restype=restype)

    def myfunction(self, int, dbl, restype):
        '''function myfunction(int, dbl) bind(C, name='myfunction')
      !DEC$ ATTRIBUTES DLLEXPORT :: myfunction
      integer*8, intent(in) :: int
      real(c_double), intent(in) :: dbl
      real(c_double) :: myfunction
    end function'''
        return self.get_lib_function('myfunction')(int, dbl, restype=restype)

    def mysubroutine(self, str_arr, dbl_arr):
        '''subroutine mysubroutine(str_arr, dbl_arr) bind(C, name='mysubroutine')
      character(kind=c_char, len=1), intent(inout)       :: str_arr(20)
      real(c_double), intent(inout), dimension(2) :: dbl_arr
    end subroutine'''
        return self.get_lib_function('mysubroutine')(str_arr, dbl_arr)

    def read_input(self, htc_path):
        '''subroutine read_input(htc_path) bind(C, name="read_input")
      character(kind=c_char, len=1), intent(in)       :: htc_path(1024)
    end subroutine'''
        return self.get_lib_function('read_input')(htc_path)

    def run(self, time, restype):
        '''function run(time) bind(C, name='run')
      !DEC$ ATTRIBUTES DLLEXPORT :: run
      real(c_double), intent(in) :: time
      real(c_double) :: run, eps
    end function'''
        return self.get_lib_function('run')(time, restype=restype)

    def setState(self, val):
        '''subroutine setState(val) BIND(C, NAME='setState')
  integer, intent(in) :: val
 end subroutine'''
        return self.get_lib_function('setState')(val)

    def set_aerosections_windspeed(self, rotor, uvw):
        '''subroutine set_aerosections_windspeed(rotor, uvw) bind(C, name="set_aerosections_windspeed")
    integer*8, intent(in) :: rotor
    real(c_double),intent(in)   :: uvw(rotors_gl%rotor(rotor)%nbld, rotors_gl%rotor(rotor)%blade(1)%nsec, 3)
  end subroutine'''
        return self.get_lib_function('set_aerosections_windspeed')(rotor, uvw)

    def set_variable_sensor_value(self, id, value):
        '''subroutine set_variable_sensor_value(id, value) bind(C, name="set_variable_sensor_value")
      integer*8, intent(in) :: id
      real(c_double)        :: value
    end subroutine'''
        return self.get_lib_function('set_variable_sensor_value')(id, value)

    def set_windfield(self, uvw, box_offset_x, time):
        '''subroutine set_windfield(uvw, box_offset_x, time) bind(C, name="set_windfield")
      real*4, intent(in) :: uvw(3, gwsd%TMOD%buffer_points_x,gwsd%TMOD%buffer_points_y,gwsd%TMOD%buffer_points_z)
      real*8, intent(in):: box_offset_x, time
    end subroutine'''
        return self.get_lib_function('set_windfield')(uvw, box_offset_x, time)

    def sqr2(self, val):
        '''subroutine sqr2(val) BIND(C, NAME='sqr2')
  integer, intent(inout) :: val
 end subroutine'''
        return self.get_lib_function('sqr2')(val)

    def step(self, restype):
        '''function step() bind(C, name='step')
      !DEC$ ATTRIBUTES DLLEXPORT :: step
      real(c_double) :: step
    end function'''
        return self.get_lib_function('step')(restype=restype)

    def test_hdf5(self, ):
        '''subroutine test_hdf5() BIND(C, NAME='test_hdf5')
  !DEC$ ATTRIBUTES DLLEXPORT :: test_hdf5
  INTEGER     ::   hdferr ! Error flag
  CHARACTER(9) :: filename = 'test.hdf5'
  INTEGER(HID_T) :: file_id       ! File identifier
  INTEGER(HID_T) :: H5_Create_file,H5_Open_file      ! File identifier
  type(c_ptr) :: x
 end subroutine'''
        return self.get_lib_function('test_hdf5')()

    def work(self, time, restype):
        '''function work(time) bind(C, Name='work')
    !DEC$ ATTRIBUTES DLLEXPORT :: work
    real(c_double), intent(in) :: time
    real*4 :: start_time, t
    integer*8 :: N, work
  end function'''
        return self.get_lib_function('work')(time, restype=restype)
