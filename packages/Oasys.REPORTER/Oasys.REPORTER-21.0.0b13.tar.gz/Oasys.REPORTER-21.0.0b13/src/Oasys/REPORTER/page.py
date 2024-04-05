import Oasys.gRPC


# Metaclass for static properties and constants
class PageType(type):

    def __getattr__(cls, name):

        raise AttributeError("Page class attribute '{}' does not exist".format(name))


class Page(Oasys.gRPC.OasysItem, metaclass=PageType):
    _props = {'name'}
    _rprops = {'items', 'master'}


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

# If one of the properties we define then get it
        if name in Page._props:
            return Oasys.REPORTER._connection.instanceGetter(self.__class__.__name__, self._handle, name)

# If one of the read only properties we define then get it
        if name in Page._rprops:
            return Oasys.REPORTER._connection.instanceGetter(self.__class__.__name__, self._handle, name)

        raise AttributeError("Page instance attribute '{}' does not exist".format(name))


    def __setattr__(self, name, value):
# If one of the properties we define then set it
        if name in Page._props:
            Oasys.REPORTER._connection.instanceSetter(self.__class__.__name__, self._handle, name, value)
            return

# If one of the read only properties we define then error
        if name in Page._rprops:
            raise AttributeError("Cannot set read-only Page instance attribute '{}'".format(name))

# Set the property locally
        self.__dict__[name] = value


# Constructor
    def __init__(self, template, options=Oasys.gRPC.defaultArg):
        handle = Oasys.REPORTER._connection.constructor(self.__class__.__name__, template, options)
        Oasys.gRPC.OasysItem.__init__(self, self.__class__.__name__, handle)
        """
        Create a new Page.

        Parameters
        ----------
        template : Template
            Template to create page in
        options : dict
            Optional. Options specifying various page properties, including where the page should be created. If omitted, the default values below will be used

        Returns
        -------
        dict
            Page object
        """


# Instance methods
    def DeleteItem(self, index):
        """
        Deletes an item from a page

        Parameters
        ----------
        index : integer
            The index of the item that you want to delete. Note that indices start at 0

        Returns
        -------
        None
            No return value
        """
        return Oasys.REPORTER._connection.instanceMethod(self.__class__.__name__, self._handle, "DeleteItem", index)

    def Duplicate(self, index=Oasys.gRPC.defaultArg):
        """
        Duplicate a page

        Parameters
        ----------
        index : integer
            Optional. The page index that you want to insert the duplicate page at in the template. Note that indices start at 0.
            If omitted the duplicate page will be put after the one that you are duplicating

        Returns
        -------
        dict
            Page object
        """
        return Oasys.REPORTER._connection.instanceMethod(self.__class__.__name__, self._handle, "Duplicate", index)

    def Generate(self):
        """
        Generate a page

        Returns
        -------
        None
            no return value
        """
        return Oasys.REPORTER._connection.instanceMethod(self.__class__.__name__, self._handle, "Generate")

    def GetAllItems(self):
        """
        Gets all of the items from a page

        Returns
        -------
        list
            List of Item objects
        """
        return Oasys.REPORTER._connection.instanceMethod(self.__class__.__name__, self._handle, "GetAllItems")

    def GetItem(self, index):
        """
        Get an item from a page

        Parameters
        ----------
        index : integer
            The index of the item on the page that you want to get. Note that indices start at 0

        Returns
        -------
        """
        return Oasys.REPORTER._connection.instanceMethod(self.__class__.__name__, self._handle, "GetItem", index)

    def ImportItem(self, filename):
        """
        Import an item from a file onto the page

        Parameters
        ----------
        filename : string
            File containing the object to import

        Returns
        -------
        """
        return Oasys.REPORTER._connection.instanceMethod(self.__class__.__name__, self._handle, "ImportItem", filename)

