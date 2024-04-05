import Oasys.gRPC


# Metaclass for static properties and constants
class UnitSystemType(type):
    _consts = {'U1', 'U2', 'U3', 'U4', 'U5', 'U6'}

    def __getattr__(cls, name):
        if name in UnitSystemType._consts:
            return Oasys.THIS._connection.classGetter(cls.__name__, name)

        raise AttributeError("UnitSystem class attribute '{}' does not exist".format(name))


    def __setattr__(cls, name, value):
# If one of the constants we define then error
        if name in UnitSystemType._consts:
            raise AttributeError("Cannot set UnitSystem class constant '{}'".format(name))

# Set the property locally
        cls.__dict__[name] = value


class UnitSystem(Oasys.gRPC.OasysItem, metaclass=UnitSystemType):


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

        raise AttributeError("UnitSystem instance attribute '{}' does not exist".format(name))


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value
