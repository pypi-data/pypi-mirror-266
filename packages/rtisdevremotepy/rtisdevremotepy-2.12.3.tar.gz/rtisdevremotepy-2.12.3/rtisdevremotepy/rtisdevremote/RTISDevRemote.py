"""RTIS Dev Remote
==================

This is a library used to be able to use RTIS Dev remotely over IP. Quickly develop with connected RTIS devices.
Intended to be used by RTIS Dev wrappers.

By Cosys-Lab, University of Antwerp
Contributors: Wouter Jansen

Here is a small example that goes over most basic steps.

Initialize the module of how a wrapper could be made::

    >>> rtisdev_version = "2.6.2"
    >>> ip = "localhost"
    >>> success, issues = send_connect(ip, rtisdev_version)

Define the method name, the arguments as a list of strings and the values as a tuple::

    >>> method_name = "open_connection"
    >>> arguments = ["port", "allowDebugMode"]
    >>> values = ("/dev/ttyACM0", True)

Send and execute the command on the connected RTIS device where a listener is waiting.
The result will either be a simple datatype or in case of a custom RTIS Dev object class be converted to a dictionary.
In case of problems, the issues variable will be a list of strings containing the name(s) and description(s) of
the problem(s) encountered::

    >>> result, issues = send_command(ip, rtisdev_version, method_name, arguments, values)

For more information check the wiki, source code documentation or one of the already available wrappers.
"""

import socket
import pickle
from typing import Callable, List, Tuple
from inspect import getfullargspec
try:
    import rtisdev
except:
    pass
import pkg_resources
from struct import pack
from struct import unpack

# Global settings
HEADER = "RTISDEVREMOTE"
VERSION = "v1.0.8"


###########################
# RTIS Dev Remote Classes #
###########################


class ArgumentDescriptor:
    """Class describing of an RTIS Dev method.

       Attributes
       ----------
       name : string
           The unique identifier to identify this argument.

       class_type : string
           The data type of the argument.

       required: bool (default = False)
           Define if the argument is required by the method or optional.
    """

    def __init__(self, name: str, class_type: type, required: bool = False):
        self.name = name
        self.class_type = class_type.__name__
        self.required = required

    def __eq__(self, other: any):
        if isinstance(other, ArgumentDescriptor):
            return self.name == other.name and self.compare_custom_types(other.class_type)
        return False

    def compare_custom_types(self, other: any) -> bool:
        """Compare this argument descriptor object with another to see if the name and data type matches.

           Parameters
           ----------
           other: `ArgumentDescriptor`
               The other descriptor to compare against.
        """

        if not self.class_type == other:
            if (self.class_type == "str" and other == "string") \
                    or (self.class_type == "string" and other == "str"):
                return True
            elif self.class_type == "NoneType" or other == "NoneType":
                return True
            elif (self.class_type == "int" and other == "float") \
                    or (self.class_type == "float" and other == "int"):
                return True
            else:
                return False
        else:
            return True

    def __ne__(self, other):
        return not self.__eq__(other)


#####################################
# RTIS Dev Remote Private Functions #
#####################################


def __get_available_arguments(method: Callable[[any], any]) -> Tuple[List[ArgumentDescriptor], List[str], str]:
    """Get the arguments of the method given and get their descriptors, a list of which ones are required by the method
       and the data type of the optionally returned object.

       Parameters
       ----------
       method : Callable
           The method to receive the arguments for.

       Returns
       -------
       argument_descriptors, required_arguments, return_type : Tuple
           A tuple of a list of ArgumentDescriptor objects, a list of the names of the required arguments and a string
           with the data type of the optional returned object.
    """

    arguments = getfullargspec(method)
    argument_names = arguments.args
    return_type = ''
    if "return" in arguments.annotations:
        if type(arguments.annotations["return"]) == type:
            return_type = arguments.annotations["return"].__name__
        else:
            if "typing.List" in str(arguments.annotations["return"]):
                return_type = "List"
            elif "typing.Tuple" in str(arguments.annotations["return"]):
                return_type = "Tuple"
            elif "typing.Callable" in str(arguments.annotations["return"]):
                return_type = "Callable"
            elif "typing.Dict" in str(arguments.annotations["return"]):
                return_type = "Dict"
            else:
                return_type = "UNKNOWN"
    if len(argument_names) > 0:
        optional_arguments_size = 0
        if arguments.defaults is not None:
            optional_arguments_size = len(arguments.defaults)
        required_arguments_size = len(argument_names) - optional_arguments_size
        required_arguments = []
        argument_descriptors = []
        for index, argument_name in enumerate(argument_names):
            argument_descriptors.append(ArgumentDescriptor(argument_name, arguments.annotations[argument_name],
                                                           not index >= required_arguments_size))
            if index < required_arguments_size:
                required_arguments.append(argument_name)
        return argument_descriptors, required_arguments, return_type
    else:
        return [], [], return_type


def __convert_to_rtis_class(rtis_dict: dict) -> any:
    """Convert a dictionary that represents a converted RTIS Dev object class.

       Parameters
       ----------
       rtis_dict : Dict
           The dictionary of the RTIS Dev object class.

       Returns
       -------
       rtis_object : any
           The object in the data format of the RTIS Dev object class.
    """

    rtis_object = None
    try:
        method = getattr(rtisdev, rtis_dict["RTISDevClass"])

        arguments = getfullargspec(method.__init__)
        argument_names = arguments.args
        required_arguments = []
        if len(argument_names) > 0:
            optional_arguments_size = 0
            if arguments.defaults is not None:
                optional_arguments_size = len(arguments.defaults)
            required_arguments_size = len(argument_names) - optional_arguments_size
            for index, argument_name in enumerate(argument_names):
                if index < required_arguments_size and argument_name != "self":
                    required_arguments.append(argument_name)
        required_arguments_dict = {}
        for required_argument in required_arguments:
            required_arguments_dict[required_argument] = None
        rtis_object = method(**required_arguments_dict)
        for attribute_key in rtis_dict:
            if attribute_key != 'RTISDevClass':
                if type(rtis_dict[attribute_key]).__name__ == 'ndarray':
                    setattr(rtis_object, attribute_key, rtis_dict[attribute_key].copy())
                else:
                    setattr(rtis_object, attribute_key, rtis_dict[attribute_key])
    except AttributeError:
        pass
    return rtis_object


def __parse_arguments_and_execute(method: Callable[[any], any], method_name: str,
                                  arguments: List[str], values: Tuple[any]) -> Tuple[Tuple[any], List[str]]:
    """Get and parse all the argument of a given RTIS Dev method to make sure all required ones are available and all
       have the right data type. If all checks out, execute the method and return the response. If not, returns a list
       of the issues encountered and their description.

       Parameters
       ----------
       method : Callable
           The method to receive the arguments for.

       method_name : string
           The name of the method.

       arguments : List[string]
           The names of the provided arguments

       values : Tuple
           The values of the provided arguments in the same order.

       Returns
       -------
       result, issues : Tuple
           The optional response results and a list of strings containing potential problems.
    """

    method_argument_descriptors, required_arguments, return_type = __get_available_arguments(method)
    available_argument_descriptors = []
    available_argument_dict = {}
    issues = []
    result = None
    for index, argument in enumerate(arguments):
        available_argument_descriptors.append(ArgumentDescriptor(argument, type(values[index])))
        available_argument_dict[argument] = values[index]
    for required_argument in required_arguments:
        found = False
        for available_argument in available_argument_descriptors:
            if required_argument == available_argument.name:
                found = True
                break
        if not found:
            issues.append("RequiredArgumentMissing, The required argument '" + required_argument + "' was not given.")
    for available_argument in available_argument_descriptors:
        if available_argument not in method_argument_descriptors:
            found = False
            for method_argument in method_argument_descriptors:
                if available_argument.name == method_argument.name:
                    if (available_argument.class_type == "dict"
                            and "RTISDevClass" in available_argument_dict[available_argument.name]):
                        rtis_object = __convert_to_rtis_class(available_argument_dict[available_argument.name])
                        if rtis_object is not None:
                            available_argument_dict[available_argument.name] = rtis_object
                        else:
                            issues.append("WrongCustomClassType, The argument '"
                                          + available_argument.name + "' for method '" + method_name + "' is an"
                                          + " unknown custom RTIS Dev class type.")
                    else:
                        issues.append("WrongArgumentType, The argument '"
                                      + available_argument.name + "' for method '" + method_name + "' has data type"
                                      + " '" + available_argument.class_type + "' but it should be '" +
                                      method_argument.class_type + "'.")
                    found = True
                    break
            if not found:
                issues.append("UnknownArgument, The argument '" + available_argument.name
                              + "' for method '" + method_name + "' does not exist.")
    if len(issues) == 0:
        try:
            result = method(**available_argument_dict)
        except Exception as ex:
            issues.append(type(ex).__name__ + ", " + ex.args[0])
            result = None
        if "RTIS" in return_type:
            if result is not None:
                if type(result) is not dict:
                    result = vars(result)
                    result["RTISDevClass"] = return_type
                else:
                    for key in result:
                        result[key] = vars(result[key])
                        result[key]["RTISDevClass"] = return_type
    return result, issues


def __parse_command_and_execute(method_name: str, arguments: List[str],
                                values: Tuple[any]) -> Tuple[Tuple[any], List[str]]:
    """Get and parse the request for a RTIS Dev method to make sure it actually exists before proceeding.
       If all checks out, execute the method and return the response. If not, returns a list
       of the issues encountered and their description.

       Parameters
       ----------
       method_name : string
           The name of the method.

       arguments : List[string]
           The names of the provided arguments

       values : Tuple
           The values of the provided arguments in the same order.

       Returns
       -------
       result, issues : Tuple
           The optional response results and a list of strings containing potential problems.
    """

    try:
        method = getattr(rtisdev, method_name)
        result, issues = __parse_arguments_and_execute(method, method_name, arguments, values)
    except AttributeError:
        result = None
        issues = ["UnknownMethod, The method '" + method_name + "' does not exist in RTIS Dev."]
    return result, issues


def __get_data(connection: socket) -> Tuple[any]:
    """Get all data available on a socket and unpickle (deserialize) it.

       Parameters
       ----------
       connection : socket
           The connected TCP socket.

       Returns
       -------
       package : Tuple
           The data package containing all the values.
    """

    length_data = connection.recv(8)
    (length,) = unpack('>Q', length_data)
    data = b''
    while len(data) < length:
        to_read = length - len(data)
        data += connection.recv(4096 if to_read > 4096 else to_read)
    package = pickle.loads(data)
    return package


####################################
# RTIS Dev Remote Public Functions #
####################################


def convert_to_rtis_class(rtis_dict: dict) -> any:
    """Convert a dictionary that represents a converted RTIS Dev object class.

       Parameters
       ----------
       rtis_dict : Dict
           The dictionary of the RTIS Dev object class.

       Returns
       -------
       rtis_object : any
           The object in the data format of the RTIS Dev object class.
    """

    return __convert_to_rtis_class(rtis_dict)


def send_connect(ip: str, rtisdev_version: str) -> Tuple[bool, List[str]]:
    """Connect to a remote RTIS device that has a RTIS Dev Remote listener enabled.
       After successfully connecting it will also make sure that the client has the same RTIS Dev version as the
       remote device to ensure compatibility. As well as that the Remote listener and the client also match versions.


       Parameters
       ----------
       ip : string
           The IP of the remote RTIS device to connect to.

       rtisdev_version : string
           The version of the client supported RTIS Dev.

       Returns
       -------
       result, issues : Tuple
           The boolean indicating a good or bad connection and a list of strings containing potential problems.
    """

    result, issues = send_command(ip, rtisdev_version, "rtisdev_remote_connect", [], ())
    if result is True:
        return True, []
    else:
        return False, issues


def send_command(ip: str, rtisdev_version: str, method_name: str,
                 arguments: List[str], values: Tuple) -> Tuple[any, List[str]]:
    """Connect to a remote RTIS device that has a RTIS Dev Remote listener enabled and execute a command.


       Parameters
       ----------
       ip : string
           The IP of the remote RTIS device to connect to.

       rtisdev_version : string
           The version of the client supported RTIS Dev.

       method_name : string
           The name of the method.

       arguments : List[string]
           The names of the provided arguments

       values : Tuple
           The values of the provided arguments in the same order.

       Returns
       -------
       result, issues : Tuple
           The optional response results and a list of strings containing potential problems.
    """

    package = (HEADER, rtisdev_version, VERSION, method_name, arguments, values)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = None
    issues = []
    try:
        client_socket.connect((ip, 65447))
        data = pickle.dumps(package, protocol=2)
        length = pack('>Q', len(data))
        client_socket.sendall(length)
        client_socket.sendall(data)
        package = __get_data(client_socket)
        result = package[0]
        issues = package[1]
        client_socket.close()
    except ConnectionRefusedError:
        issues.append("ConnectionRefused, Connection to RTIS Device with IP '" + ip + "' could not be made.")
    except ConnectionResetError:
        issues.append("ConnectionReset, Connection to RTIS Device with IP '" + ip + "' was ended.")
    except TimeoutError:
        issues.append("ConnectionTimeout, Connection to RTIS Device with IP '" + ip + "' could not be made."
                      + " Is it the right IP?")
    except socket.gaierror:
        issues.append("ConnectionAddressFailure, Connection to RTIS Device with IP '" + ip + "' could not be made."
                      + " The address chosen could not be found. Please provide an IP address.")
    return result, issues


#################################
# RTIS Dev Remote Main Listener #
#################################


if __name__ == '__main__':

    local_rtisdev_version = pkg_resources.get_distribution("rtisdev").version
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 65447))
    server_socket.listen(1)
    while True:
        connection, client = server_socket.accept()
        package = __get_data(connection)
        header = package[0]
        supported_rtisdev_version = package[1]
        supported_remote_version = package[2]
        method_name = package[3]
        arguments = package[4]
        values = package[5]
        result = None
        issues = []
        if header == HEADER:
            if supported_remote_version == VERSION:
                if supported_rtisdev_version == local_rtisdev_version:
                    if method_name == "rtisdev_remote_connect":
                        result = True
                    else:
                        result, issues = __parse_command_and_execute(method_name, arguments, values)
                else:
                    issues.append("VersionMismatch, The supported RTIS Dev version is v"
                                  + local_rtisdev_version + " but version v" + supported_rtisdev_version + " was used.")
            else:
                issues.append("VersionMismatch, The RTIS Dev Remote version is required to be "
                              + VERSION + " but version " + supported_remote_version + " was used.")
        else:
            issues.append("HeaderMismatch, The RTIS Dev Remote header was not provided. Dropping message")
        data = pickle.dumps((result, issues), protocol=2)
        length = pack('>Q', len(data))
        connection.sendall(length)
        connection.sendall(data)
