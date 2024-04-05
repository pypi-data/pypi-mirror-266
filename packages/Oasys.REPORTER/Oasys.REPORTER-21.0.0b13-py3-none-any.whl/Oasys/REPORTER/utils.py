import Oasys.gRPC


# Metaclass for static properties and constants
class UtilsType(type):

    def __getattr__(cls, name):

        raise AttributeError("Utils class attribute '{}' does not exist".format(name))


class Utils(Oasys.gRPC.OasysItem, metaclass=UtilsType):


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

        raise AttributeError("Utils instance attribute '{}' does not exist".format(name))


    def __setattr__(self, name, value):
# Set the property locally
        self.__dict__[name] = value


# Static methods
    def Build():
        """
        Returns the build number

        Returns
        -------
        int
            integer
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "Build")

    def CallPromiseHandlers():
        """
        Manually call any promise handlers/callbacks in the job queue

        Returns
        -------
        None
            no return value
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "CallPromiseHandlers")

    def GarbageCollect():
        """
        Forces garbage collection to be done. This should not normally need to be called
        but in exceptional circumstances it can be called to ensure that garbage collection is done to
        return memory

        Returns
        -------
        None
            no return value
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "GarbageCollect")

    def HiResTimer():
        """
        A high resolution timer that can be used to time how long things take.
        The first time this is called the timer will start and return 0. Subsequent calls will return
        the time in nanoseconds since the first call. Note that the timer will almost certainly not have
        1 nanosecond precision but, depending on the platform, should should have a resolution of at least 1 microsecond.
        The resolution can be found by using Utils.TimerResolution()

        Returns
        -------
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "HiResTimer")

    def TimerResolution():
        """
        Returns the resolution (precision) of the Utils.HiResTimer() timer in nanoseconds

        Returns
        -------
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "TimerResolution")

    def Version():
        """
        Returns the version number

        Returns
        -------
        float
            real
        """
        return Oasys.REPORTER._connection.classMethod(__class__.__name__, "Version")

