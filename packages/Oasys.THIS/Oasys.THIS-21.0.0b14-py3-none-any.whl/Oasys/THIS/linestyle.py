import Oasys.gRPC


# Metaclass for static properties and constants
class LineStyleType(type):
    _consts = {'DASH', 'DASH2', 'DASH3', 'DASH4', 'DASH5', 'DASH6', 'NONE', 'SOLID'}

    def __getattr__(cls, name):
        if name in LineStyleType._consts:
            return Oasys.THIS._connection.classGetter(cls.__name__, name)

        raise AttributeError("LineStyle class attribute '{}' does not exist".format(name))


    def __setattr__(cls, name, value):
# If one of the constants we define then error
        if name in LineStyleType._consts:
            raise AttributeError("Cannot set LineStyle class constant '{}'".format(name))

# Set the property locally
        cls.__dict__[name] = value


class LineStyle(Oasys.gRPC.OasysItem, metaclass=LineStyleType):


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

        raise AttributeError("LineStyle instance attribute '{}' does not exist".format(name))


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value
