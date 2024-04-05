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

__version__ = "1.0.8"