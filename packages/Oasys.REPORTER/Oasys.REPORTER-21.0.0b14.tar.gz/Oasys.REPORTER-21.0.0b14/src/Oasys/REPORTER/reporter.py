import Oasys.gRPC


# Metaclass for static properties and constants
class ReporterType(type):
    _consts = {'AUTO_TABLE_DIRECTORY', 'AUTO_TABLE_FILE', 'AUTO_TABLE_HEADER', 'AUTO_TABLE_ROWS', 'CAP_FLAT', 'CAP_ROUND', 'CAP_SQUARE', 'CONDITION_BETWEEN', 'CONDITION_CONTAINS_STRING', 'CONDITION_DOESNT_CONTAIN_STRING', 'CONDITION_DOESNT_MATCH_REGEX', 'CONDITION_EQUAL_TO', 'CONDITION_GREATER_THAN', 'CONDITION_LESS_THAN', 'CONDITION_MATCHES_REGEX', 'CONDITION_NOT_BETWEEN', 'CONDITION_NOT_EQUAL_TO', 'JOIN_BEVEL', 'JOIN_MITRE', 'JOIN_ROUND', 'JUSTIFY_BOTTOM', 'JUSTIFY_CENTRE', 'JUSTIFY_LEFT', 'JUSTIFY_MIDDLE', 'JUSTIFY_RIGHT', 'JUSTIFY_TOP', 'LINE_DASH', 'LINE_DASH_DOT', 'LINE_DASH_DOT_DOT', 'LINE_DOT', 'LINE_NONE', 'LINE_SOLID', 'TEXT_BOLD', 'TEXT_ITALIC', 'TEXT_NORMAL', 'TEXT_UNDERLINE', 'VIEW_DESIGN', 'VIEW_PRESENTATION'}

    def __getattr__(cls, name):
        if name in ReporterType._consts:
            return Oasys.REPORTER._connection.classGetter(cls.__name__, name)

        raise AttributeError("Reporter class attribute '{}' does not exist".format(name))


    def __setattr__(cls, name, value):
# If one of the constants we define then error
        if name in ReporterType._consts:
            raise AttributeError("Cannot set Reporter class constant '{}'".format(name))

# Set the property locally
        cls.__dict__[name] = value


class Reporter(Oasys.gRPC.OasysItem, metaclass=ReporterType):


    def __del__(self):
        if not Oasys.REPORTER._connection:
            return

        if self._handle is None:
            return

        Oasys.REPORTER._connection.destructor(self.__class__.__name__, self._handle)


    def __getattr__(self, name):
# If constructor for an item fails in program, then _handle will not be set and when
# __del__ is called to return the object we will call this to get the (undefined) value
        if name == "_handle":
            return None

        raise AttributeError("Reporter instance attribute '{}' does not exist".format(name))


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value
