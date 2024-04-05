import Oasys.gRPC


# Metaclass for static properties and constants
class UnitsType(type):
    _consts = {'ACCELERATION', 'AREA', 'CONDUCTIVITY', 'CURRENT', 'DENSITY', 'DISPLACEMENT', 'ELECTRIC_FIELD_VECTOR', 'ENERGY', 'ENERGY_DENSITY', 'FLUX', 'FORCE', 'FORCE_WIDTH', 'FREQUENCY', 'LENGTH', 'MAGNETIC_FLUX_VECTOR', 'MASS', 'MASS_FLOW', 'MOMENT', 'MOMENTUM', 'MOMENT_WIDTH', 'NONE', 'POWER', 'PRESSURE', 'Q_CRITERION', 'ROTATION', 'ROTATIONAL_ACCELERATION', 'ROTATIONAL_VELOCITY', 'STRAIN', 'STRESS', 'TEMPERATURE', 'THERMAL_DIFFUSIVITY', 'TIME', 'UNKNOWN', 'VECTOR_POTENTIAL', 'VELOCITY', 'VISCOSITY', 'VOLUME', 'VORTICITY', 'WORK'}

    def __getattr__(cls, name):
        if name in UnitsType._consts:
            return Oasys.THIS._connection.classGetter(cls.__name__, name)

        raise AttributeError("Units class attribute '{}' does not exist".format(name))


    def __setattr__(cls, name, value):
# If one of the constants we define then error
        if name in UnitsType._consts:
            raise AttributeError("Cannot set Units class constant '{}'".format(name))

# Set the property locally
        cls.__dict__[name] = value


class Units(Oasys.gRPC.OasysItem, metaclass=UnitsType):


    def __del__(self):
        if not Oasys.THIS._connection:
            return

        if self._handle is None:
            return

        Oasys.THIS._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
# If constructor for an item fails in program, then _handle will not be set and when
# __del__ is called to return the object we will call this to get the (undefined) value
        if name == "_handle":
            return None

        raise AttributeError("Units instance attribute '{}' does not exist".format(name))


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value


# Static methods
    def USER(mass, time, length, angle, temperature, current=Oasys.gRPC.defaultArg):
        """
        Setup a user defined UNIT

        Parameters
        ----------
        mass : float
            Power for mass dimensions
        time : float
            Power for time dimensions
        length : float
            Power for length dimensions
        angle : float
            Power for angle dimensions
        temperature : float
            Power for temperature dimensions
        current : float
            Optional. Power for current dimensions

        Returns
        -------
        int
            integer
        """
        return Oasys.THIS._connection.classMethod(__class__.__name__, "USER", mass, time, length, angle, temperature, current)

