"""
RTIS Dev Remote Python Wrapper
==============================

This is a library used to be able to use RTIS Dev remotely over IP with Python.
Quickly develop with connected RTIS devices.

By Cosys-Lab, University of Antwerp

Contributors: Wouter Jansen

Unavailable RTIS Dev methods
----------------------------
Here is a short list of the current RTIS Dev methods that aren't available through this wrapper:
 - `create_measure_external_trigger_queue <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_measure_external_trigger_queue>`_
 - `create_measure_external_trigger_callback <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_measure_external_trigger_callback>`_
 - `create_processing_workers <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_processing_workers>`_
 - `set_log_mode <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#set_log_mode>`_
 - `set_custom_logger <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#set_custom_logger>`_

Initial setup
-------------
When starting with this wrapper, first try to make a connection the remote RTIS Device.
This both tests the connection as makes sure that the RTIS Dev version used on the remote device is supported
by the version of this wrapper.
The only required argument is the IP of the remote RTIS Device. To learn more about how to find out the IP,
please see this `guide <https://cosysgit.uantwerpen.be/rtis-software/ertissoftwareusageguide/-/wikis/Initial-Connection-&-Network-Setup>`_.

To correctly connect::

    >>> import rtisdevremotepy
    >>> rtisdev = rtisdevremotepy.RTISDev("192.168.1.150")

Now the `rtisdev` object can be used to run RTIS Dev methods from.

Executing remote methods
------------------------
After the connection is made and no errors were shown, you can now use
`all available RTIS Dev commands <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home>`_.
Some don't work and are listed in the list above.
Please use that wiki to know which arguments to use.
The commands should be called from the `rtisdev` objects. For example::

    >>> rtisdev.open_connection()


Providing arguments
-------------------
Please see the `RTIS Dev wiki <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home>`_
to know which arguments are optional and which are required.
They use the exact same naming formats. For example::

    >>> config_uuid = rtisdev.set_recording_settings(callDuration=4.4, callMinimumFrequency=30000, callMaximumFrequency=60000)

When you provide wrong arguments or run into other exceptions to RTIS Dev,
 the Python wrapper will raise an exception listing and describing the problem.

Custom data types
-----------------
Some methods return or require one of the `RTIS Dev custom class object <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#classes>`_.
The RTIS Dev Python wrapper will automatically convert these to Python dictionary objects.
When these dictionary objects are provided as arguments,
the wrapper will automatically convert them again, so it should all work straight out of the box!
For example::

    >>> settings = rtisdev.get_current_settings(configName=config_uuid)
    >>> rtisdev.set_settings_from_class(settings)

    >>> measurement_raw = rtisdev.get_raw_measurement(behaviour=true, configName=config_uuid)
    >>> measurement_processed_from_raw = rtisdev.process_measurement(measurement_raw, configName=config_uuid)

If one has RTIS Dev fully installed and imported, one can also use the function `convert_to_rtis_class(rtis_dict)` to convert the dictionary objects back to the full RTIS Dev custom class objects. For example::

>>> import rtisdev as fullrtisdev
>>> measurement_processed_from_raw = rtisdev.process_measurement(measurement_raw, configName=config_uuid)
>>> measurement_processed_from_raw_converted = rtisdev.convert_to_rtis_class(measurement_processed_from_raw)

Example
-------
A bigger example showing how to connect, record and process a measurement and plot the RTIS Energyscape.
Import necessary modules::
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np
    >>> import rtisdevremotepy

Connect and verify matching versions of RTIS Dev::

    >>> rtisdev = rtisdevremotepy.RTISDev("192.168.1.150")

Connect to RTIS Device::

    >>> rtisdev.open_connection()

Configure the recording and processing settings::

    >>> config_uuid = rtisdev.set_recording_settings(microphoneSamples=163840, callMinimumFrequency=25000, callMaximumFrequency=50000)
    >>> rtisdev.set_processing_settings(directions=91, maxRange=5, configName=config_uuid)
    >>> settings = rtisdev.get_current_settings(configName=config_uuid)

Get an ACTIVE measurement (protect your ears!) and process it::

    >>> measurement_processed = rtisdev.get_processed_measurement(behaviour=True, configName=config_uuid)

Plot the 2D energyscape of this processed measurement::

    >>> plt.imshow(np.transpose(measurement_processed['processedData']), cmap="hot", interpolation='nearest')
    >>> plt.xlabel("Directions (degrees)")
    >>> plt.ylabel("Range (meters)")
    >>> indexes_x = np.arange(0, measurement_processed['processedData'].shape[0], 20)
    >>> labels_x = np.round(np.rad2deg(settings['directions'][indexes_x, 0])).astype(int)
    >>> indexes_y = np.arange(0, measurement_processed['processedData'].shape[1], 100)
    >>> labels_y = settings['ranges'][indexes_y]
    >>> fmt_x = lambda x: "{:.0f}°".format(x)
    >>> fmt_y = lambda x: "{:.2f}m".format(x)
    >>> plt.xticks(indexes_x, [fmt_x(i) for i in labels_x])
    >>> plt.yticks(indexes_y, [fmt_y(i) for i in labels_y])
    >>> plt.title("RTIS Dev - 2D Energyscape Example")
    >>> ax = plt.gca()
    >>> ax.invert_yaxis()
    >>> ax.set_aspect("auto")
    >>> plt.show()
"""

from typing import List
from rtisdevremotepy.rtisdevremote import RTISDevRemote

# Global settings
RTISDEV_VERSION = "2.12.3"


class RTISDev:
    """This is class describing a wrapper of the RTIS Dev Remote library to
    %   use RTIS Dev remotely over self.ip from Python. Quickly develop with connected RTIS devices.
    %   Almost all RTIS Dev functions are available as well as automatic conversion of RTIS Dev custom class objects.

       Attributes
       ----------
       ip : string
           The self.ip of the remote RTIS device

       rtisdev_version : string
           The supported RTIS Dev version by wrapper
    """

    def __init__(self, ip: str = "192.168.1.150"):
        """Parameters
           ----------
           ip : string
               The self.ip of the remote RTIS device
        """

        self.ip = ip
        self.rtisdev_version = RTISDEV_VERSION


    def convert_to_rtis_class(self, rtis_dict: dict) -> any:
        """Convert a dictionary that represents a converted RTIS Dev object class.
           This method should only be used if the full RTIS Dev module is installed and imported.

           Parameters
           ----------
           rtis_dict : Dict
               The dictionary of the RTIS Dev object class.

           Returns
           -------
           rtis_object : any
               The object in the data format of the RTIS Dev object class.
        """

        return RTISDevRemote.convert_to_rtis_class(rtis_dict)

    def open_connection(self, port: str = '/dev/ttyACM0', allowDebugMode: bool = False) -> bool:
        """Connect to the port of the RTIS Hardware.

           Parameters
           ----------
           port : string (default = '/dev/ttyACM0')
               Name of the port.

           allowDebugMode : bool (default = False)
               When enabled, if a connection can not be made to a real RTIS Device to the chosen port,
               it will instead automatically go into a debug mode where a virtual RTIS device is
               used instead of throwing an exception. This is mostly for debugging and testing of the library.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "open_connection"
        arguments = ["port", "allowDebugMode"]
        values = (port, allowDebugMode)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def close_connection(self) -> bool:
        """Manually close the connection to the RTIS device.
           Normally, when your script ends without exceptions the connection will automatically
           be closed gracefully. This will also unload all RTIS CUDA workers.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "close_connection"
        arguments = []
        values = ()

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def set_recording_settings(self, premade: str = None, jsonPath: str = None, callCustom: str = None,
                               microphoneSamples: int = 163840, microphoneSampleFrequency: int = 4500000,
                               callSampleFrequency: int = 450000, callDuration: float = 2.5,
                               callMinimumFrequency: int = 25000,
                               callMaximumFrequency: int = 50000, callEmissions: int = 1, configName: str = "",
                               applyToDevice: bool = True) -> bool:
        """Set the recording settings. All parameters are optional and most have default values.
           Please read their decription carefully.

           Parameters
           ----------
           premade : String (default = Not used)
               When using get_premade_recording_settings_list() you can get a set of premade configurations with a unique
               identifier as name. To use one of those use that identifier name with this argument.

           jsonPath : String (default = Not used)
               One can also store the recording settings in a json file. To load the recording settings from a json file,
               please use the absolute path to this json file with this argument. See the examples for more information.

           callCustom : String (default = Not used)
               One can use a custom call pulse to emmit from the RTIS Device in active mode. To load the custom pulse,
               use the absolute path to the csv file with this argument. See the examples for more information.

           microphoneSamples : int (default = 163840)
               The amount of microphone samples. Must be dividable by 32768.

           microphoneSampleFrequency : int (default = 4500000)
               The microphone sample frequency (without subsampling of PDM).
               The frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible) depending on the wanted mode.

           callSampleFrequency : int (default = 450000)
               The chosen sample frequency of the call. Must be larger than 160 KHz and smaller than 2 MHz.

           callDuration : float (default = 2.5)
               The duration in miliseconds of the call.

           callMinimumFrequency: int (default = 25000)
               The minimum frequency in Hz of the call sweep used for generating the pulse.

           callMaximumFrequency: int (default = 50000)
               The maximum frequency in Hz of the call sweep used for generating the pulse.

           callEmissions : int (default = 1)
               The amount of times the pulse should be emitted during one measurement.

           configName : String (default = "")
               String to identify these settings with.
               If set to empty it will default to a unique UUID.

           applyToDevice : bool (default = True)
               A configuration toggle to optionally disable applying the recording settings to the RTIS Device.

           Returns
           -------
           configName : string
               returns the given configuration name or generated UUID on successful completion
               or will raise an exception on failure.

           Examples
           --------
           You can get the available premade settings with `get_premade_recording_settings_list()`.
           Create settings from a premade setup::
               >>> config_uuid = rtisdev.set_recording_settings(premade="short_20_80")

           Create settings from a json file.
           This expects a json to be available with a format such as seen below.
           Here we use auto-generated pulse call to emit.
           More examples can be found in rtisdev/config/premadeSettings/recording/.
           An example json::

                {
                    "microphoneSamples" : 294912,
                    "microphoneSampleFrequency" : 4500000,
                    "callSampleFrequency" : 450000,
                    "callDuration" : 2.5,
                    "callMinimumFrequency" : 25000,
                    "callMaximumFrequency" : 50000,
                    "callEmissions": 1
                }

               >>> config_uuid = rtisdev.set_recording_settings(jsonPath="./myrecordingsettings.json")

           Create settings from a json file.
           This expects a json to be available with a format such as seen below.
           Here we use manually generated call.
           It has to be available on the given path and have the right format.
           An example of such a custom call can be found in rtisdev/config/premadeSettings/recording/flutter.csv::

                {
                    "microphoneSamples" : 16777216,
                    "microphoneSampleFrequency" : 4500000,
                    "callSampleFrequency" : 450000,
                    "callCustom": "mycall.csv",
                    "callEmissions": 1
                }

               >>> config_uuid = rtisdev.set_recording_settings(jsonPath="./myrecordingsettings.json")

           Create full custom settings with the arguments. All arguments that aren't filled in will use default values::

               >>> config_uuid = rtisdev.set_recording_settings(microphoneSamples=294912, callDuration=3,
                                                                callMinimumFrequency=25000, callMaximumFrequency=80000)

           Load in manually generated call. This requires the file to exist on the path and have the right format.
           An example of such a custom call can be found in rtisdev/config/premadeSettings/recording/flutter.csv::

               >>> config_uuid = rtisdev.set_recording_settings(callCustom="mycall.csv")

           Note that when multiple recording configurations are loaded, the module will automatically
           load the settings as asked for by the configName argument to the RTIS device before performing a new measurement.
           """

        method_name = "set_recording_settings"
        arguments = ["premade", "jsonPath", "callCustom", "microphoneSamples", "microphoneSampleFrequency",
                     "callSampleFrequency", "callDuration", "callMinimumFrequency", "callMaximumFrequency",
                     "callEmissions", "configName", "applyToDevice"]
        values = (premade, jsonPath, callCustom, microphoneSamples, microphoneSampleFrequency,
                  callSampleFrequency, callDuration, callMinimumFrequency, callMaximumFrequency,
                  callEmissions, configName, applyToDevice)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def set_processing_settings(self, configName: str, premade: str = None,
                                jsonPath: str = None, customPath: str = None,
                                microphoneLayout: str = "eRTIS_v3D1", mode: int = 1, directions: int = 181,
                                azimuthLowLimit : float = -90, azimuthHighLimit: float = 90,
                                elevationLowLimit : float = -90, elevationHighLimit : float = 90,
                                minRange: float = 0.5, maxRange: float = 5, pdmEnable: bool = True,
                                matchedFilterEnable: bool = True, preFilterEnable: bool = False,
                                beamformingEnable: bool = True, postFilterEnable : bool = False,
                                enveloppeEnable: bool = True, cleanEnable: bool = True, preloadToggle: bool = True,
                                preFilter=None, postFilter=None, meanEnergyRangeMultiplier: float = 2,
                                maxEnergyRangeThresholdMultiplier: float = 0.5) -> bool:
        """Set the processing settings. All parameters are optional and most have default values.
           Please read their decription carefully.

           Parameters
           ----------
           configName : String
               String to identify these settings with.

           premade : String (default = Not used)
               When using get_premade_processing_settings_list() you can get a set of premade configurations with a unique
               identifier as name. To use one of those use that identifier name with this argument.

           jsonPath : String (default = Not used)
               One can also store the processing settings in a json file. To load the processing settings from a json file,
               please use the absolute path to this json file with this argument. See the examples for more information.

           customPath : String (default = Not used)
               One can use a custom set of processing files (delaymatrix.csv, directions.csv and ranges.csv).
               To load the custom files use the absolute path to the folder where these csvs are located.
               See the examples for more information.

           microphoneLayout : String (default = eRTIS_v3D1)
               Identifier of the microphone layout used for this configuration.

           mode : int (default = 1)
               Defines if using 3D or 2D processing. If set to 1 a 2D horizontal plane layout will be generated.
               When set to 0 a 3D equal distance layout will be generated
               for the frontal hemisphere of the sensor.

           directions : int (default = 181)
               Defines how many directions the layout should generate.

           azimuthLowLimit : float (default = -90)
               The lower limit of the azimuth in degrees of the directions to generate. Has to be between -90 and 90.

           azimuthHighLimit : float (default = 90)
               The higher limit of the azimuth in degrees of the directions to generate. Has to be between -90 and 90.

           elevationLowLimit : float (default = -90)
               The lower limit of the elevation in degrees of the directions to generate. Has to be between -90 and 90.

           elevationHighLimit : float (default = 90)
               The higher limit of the elevation in degrees of the directions to generate. Has to be between -90 and 90.

           minRange : float (default = 0.5)
               The minimum distance in meters of the energyscape to generate.

           maxRange : float (default = 5)
               The maximum distance in meters of the energyscape to generate.

           pdmEnable : bool (default = True)
               Toggle for PDM filtering part of the RTIS processing pipeline using RTIS CUDA.

           preFilterEnable : bool (default = False)
               Toggle for the optional pre-filter part of the RTIS processing pipeline using RTIS CUDA.

           matchedFilterEnable : bool (default = True)
               Toggle for optional matched filter part of the RTIS processing pipeline using RTIS CUDA.

           beamformingEnable : bool (default = True)
               Toggle for beamforming part of the RTIS processing pipeline using RTIS CUDA.

           postFilterEnable : bool (default = False)
               Toggle for the optional post-beamforming filter part of the RTIS processing pipeline using RTIS CUDA.

           enveloppeEnable : bool (default = True)
               Toggle for enveloppe part of the RTIS processing pipeline using RTIS CUDA.

           cleanEnable : bool (default = True)
               Toggle for cleaning part of the RTIS processing pipeline using RTIS CUDA.

           preloadToggle : bool (default = True)
               Toggle for using RTIS CUDA preloading

           preFilter : Numpy ndarray (default = Not used)
               The array holding the optional pre-filter created with scipy firwin. (shape: nprefilter x 1)

           postFilter : Numpy ndarray (default = Not used)
               The array holding the optional post-beamforming filter created with scipy firwin. (shape: npostfilter x 1)

           meanEnergyRangeMultiplier : float (default = 2)
               The multiplier weight used to calculate the mean energy for each range during the cleaning step.

           maxEnergyRangeThresholdMultiplier : float (default = 0.5)
               The multiplier weight used to threshold the energy based on the maximum
               for each range during the cleaning step.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.

           Examples
           --------
           You can get the available premade settings with `get_premade_recording_settings_list()`.
           Create settings from a premade setup with all processing steps on::

               >>> rtisdev.set_processing_settings(premade="3D_5m_3000", pdmEnable=True, matchedFilterEnable=True,
                                                   preFilterEnable=False, beamformingEnable=True,
                                                   enveloppeEnable=True, postFilterEnable=False, cleanEnable=True,
                                                   preloadToggle=True, configName=config_uuid)

           You don't have to define all the processing steps, as they are all on by default::

               >>> rtisdev.set_processing_settings(directions=91, configName=config_uuid)

           Create settings from a premade setup with only part of the processing steps enabled and no preloading.
           You can get the available premade settings with `get_premade_recording_settings_list()`::

               >>> rtisdev.set_processing_settings(pdmEnable=True, preFilterEnable=False,
                                                   matchedFilterEnable=True, beamformingEnable=False,
                                                   enveloppeEnable=False, cleanEnable=False, configName=config_uuid)

           Create settings from a json file with full processing settings on.
           This expects a json to be available with a premade a format such as seen below.
           Note that the json does not include support for pre- and post-filters. Any other setting not defined in the
           json example below should also still be set manually as argument if the default value is not desired.
           An example of such json files can be found in rtisdev/config/premadeSettings/processing/.
           Here we use auto-generated processing files::

                {
                    "microphoneLayout" : "eRTIS_v3D1",
                    "minRange" : 0.5,
                    "maxRange" : 5,
                    "directions": 181,
                    "azimuthLowLimit": -30,
                    "azimuthHighLimit": 30,
                    "2D": 1
                }

               >>> rtisdev.set_processing_settings(jsonPath="./myprocessingsettings.json", configName=config_uuid)

           Create settings from a json file with full processing settings on.
           This expects a json to be available with a format such as seen below.
           Here we use manually generated processing files.
           They have to be available on these paths and have the right format.
           Note that the json does not include support for pre- and post-filters. Any other setting not defined in the
           json example below should also still be set manually as argument if the default value is not desired.
           An example of such custom processing files can be found in rtisdev/config/premadeSettings/processing/ as well::

                {
                    "microphoneLayout" : "eRTIS_v3D1",
                    "directionsCustom": "./directions.csv",
                    "delayMatrixCustom": ".premade/delaymatrix.csv",
                    "rangesCustom": ".premade/ranges.csv"
                }

               >>> rtisdev.set_processing_settings(jsonPath="./myprocessingsettings.json", configName=config_uuid)

           Create full custom settings with the arguments. All arguments that aren't filled in will use default values::

               >>> rtisdev.set_processing_settings(mode = 0, directions = 1337, minRange = 0.5, configName=config_uuid)

           Load in manually generated processing files. This requires 3 files to exist in the given path:
           delaymatrix.csv, directions.csv and ranges.csv. Don't forget to also perhaps set the microphoneLayout and
           microphoneSampleFrequency values correctly as these are absent in these csv files!
           Note that the custom paths does not include support for pre- and post-filters.
           Any other setting not should also still be set manually as argument if the default value is not desired.
           An example of such custom processing files can be found in rtisdev/config/premadeSettings/processing/::

               >>> rtisdev.set_processing_settings(customPath="mysettingsfolder", configName=config_uuid)

           The pre-filter is an optional filter to be performed after PDM filtering and before matched filter.
           It should be created using a scipy firwin filter function as in the example below::

               >>> pref = scipy.signal.firwin(513, 20000 / (450000 / 2), pass_zero=False).astype(np.float32)
               >>> rtisdev.set_processing_settings(postFilter=pref, preFilterEnable=True, configName=config_uuid)

           Similarly, The post-beamforming filter is an optional filter to be performed after beamforming.
           It should be created using a scipy firwin filter function as in the example below::

               >>> postf = scipy.signal.firwin(512, [40000 / (450000 / 2), 50000 / (450000 / 2)],
                                               pass_zero=False).astype(np.float32)
               >>> rtisdev.set_processing_settings(postFilter=postf, postFilterEnable=True, configName=config_uuid)
        """

        method_name = "set_processing_settings"
        arguments = ["configName", "premade", "jsonPath", "customPath", "microphoneLayout", "mode",
                     "directions", "azimuthLowLimit", "azimuthHighLimit", "elevationLowLimit", "elevationHighLimit",
                     "minRange", "maxRange",
                     "pdmEnable", "preFilterEnable", "matchedFilterEnable", "beamformingEnable", "postFilterEnable",
                     "enveloppeEnable", "cleanEnable", "preloadToggle", "preFilter", "postFilter",
                     "meanEnergyRangeMultiplier", "maxEnergyRangeThresholdMultiplier"]
        values = (configName, premade, jsonPath, customPath, microphoneLayout, mode,
                  directions, azimuthLowLimit, azimuthHighLimit, elevationLowLimit , elevationHighLimit, minRange,
                  maxRange, pdmEnable, preFilterEnable, matchedFilterEnable, beamformingEnable, postFilterEnable,
                  enveloppeEnable, cleanEnable, preloadToggle, preFilter, postFilter,
                  meanEnergyRangeMultiplier, maxEnergyRangeThresholdMultiplier)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_premade_processing_settings_list(self) -> List[str]:
        """Get a list of names of all the available premade settings for processing.

           Returns
           -------
           recordingSettings : list[str]
               A list holding all the names of available settings that can be loaded.
        """

        method_name = "get_current_settings_config_name_list"
        arguments = []
        values = ()

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_current_settings(self, configName: str = "") -> dict:
        """Returns all(dict) or a single `RTISSettings` object of the current settings for processing and recording.

           Parameters
           ----------
           configName : String
               String to identify these settings with. If given will only return this settings configuration if found.
               If not provided will return a dict of all RTISSettings objects identified by their own config name.

           Returns
           -------
           settings : RTISSettings object as dict or dict
               If the configName parameter is given, it will only return the complete class containing
               all RTIS settings for recording and processing. If this argument is not given it will return
               a dict of all RTISSettings objects identified by their own config name. If there is only one settings object
               defined it will return this one instead of a dict. Returns 'None' or
               will raise an exception on failure.
           """

        method_name = "get_current_settings"
        arguments = ["configName"]
        values = (configName,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def clear_current_settings(self, configName: str = ""):
        """Clear all or the current applied `RTISSettings` configuration depending on setting the configName parameter.

           Parameters
           ----------
           configName: string
               The identity of the settings configuration to be cleared. If not given it will clear all settings.
        """

        method_name = "clear_current_settings"
        arguments = ["configName"]
        values = (configName,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_settings(self, recordingPremade: str = None, recordingJsonPath: str = None, recordingCallCustom: str = None,
                     processingPremade: str = None, processingJsonPath: str = None, processingCustomPath: str = None,
                     microphoneSamples: int = 163840, microphoneSampleFrequency: int = 4500000,
                     callSampleFrequency: int = 450000, callDuration: float = 2.5, callMinimumFrequency: int = 25000,
                     callMaximumFrequency: int = 50000, callEmissions: int = 1,
                     microphoneLayout: str = "eRTIS_v3D1", mode: int = 1, directions: int = 181,
                     azimuthLowLimit: float = -90, azimuthHighLimit: float = 90,
                     elevationLowLimit: float = -90, elevationHighLimit: float = 90,
                     minRange: float = 0.5, maxRange: float = 5, pdmEnable: bool = True, preFilterEnable: bool = True,
                     matchedFilterEnable: bool = True,
                     beamformingEnable: bool = True, enveloppeEnable: bool = True, postFilterEnable: bool = False,
                     cleanEnable: bool = True, preloadToggle: bool = True, preFilter=None,
                     postFilter=None, meanEnergyRangeMultiplier: float = 2,
                     maxEnergyRangeThresholdMultiplier: float = 0.5, configName: str = "") -> dict:
        """Returns an `RTISSettings` object with all chosen recording and processing settings based on the
           given arguments. It will not set these settings to the RTIS Device or activate processing. It only creates
           the settings object. For examples of what some of these settings do and how to use them, please see
           the `set_recording_settings()` and `set_processing_settings()` examples.

           Parameters
           ----------
           recordingPremade : String (default = Not used)
               When using get_premade_recording_settings_list() you can get a set of premade configurations with a unique
               identifier as name. To use one of those use that identifier name with this argument.

           recordingJsonPath : String (default = Not used)
               One can also store the recording settings in a json file. To load the recording settings from a json file,
               please use the absolute path to this json file with this argument.

           recordingCallCustom : String (default = Not used)
               One can use a custom call pulse to emmit from the RTIS Device in active mode. To load the custom pulse,
               use the absolute path to the csv file with this argument.

           processingPremade : String (default = Not used)
               When using get_premade_processing_settings_list() you can get a set of premade configurations with a unique
               identifier as name. To use one of those use that identifier name with this argument.

           processingJsonPath : String (default = Not used)
               One can also store the processing settings in a json file. To load the processing settings from a json file,
               please use the absolute path to this json file with this argument.

           processingCustomPath : String (default = Not used)
               One can use a custom set of processing files (delaymatrix.csv, directions.csv and ranges.csv).
               To load the custom files use the absolute path to the folder where these csvs are located.

           microphoneSamples : int (default = 163840)
               The amount of microphone samples. Must be dividable by 32768.

           microphoneSampleFrequency : int (default = 4500000)
               The microphone sample frequency (without subsampling of PDM).
               The frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible) depending on the wanted mode.

           callSampleFrequency : int (default = 450000)
               The chosen sample frequency of the call. Must be larger than 160 KHz and smaller than 2 MHz.

           callDuration : float (default = 2.5)
               The duration in milliseconds of the call.

           callMinimumFrequency: int (default = 25000)
               The minimum frequency in Hz of the call sweep used for generating the pulse.

           callMaximumFrequency: int (default = 50000)
               The maximum frequency in Hz of the call sweep used for generating the pulse.

           callEmissions : int (default = 1)
               The amount of times the pulse should be emitted during one measurement.

           microphoneLayout : String (default = eRTIS_v3D1)
               Identifier of the microphone layout used for this configuration.

           mode : int (default = 1)
               Defines if using 3D or 2D processing. If set to 1 a 2D horizontal plane layout will be generated.
               When set to 0 a 3D equal distance layout will be generated
               for the frontal hemisphere of the sensor.

           directions : int (default = 181)
               Defines how many directions the layout should generate.

           azimuthLowLimit : float (default = -90)
               The lower limit of the azimuth in degrees of the directions to generate. Has to be between -90 and 90.

           azimuthHighLimit : float (default = 90)
               The higher limit of the azimuth in degrees of the directions to generate. Has to be between -90 and 90.

           elevationLowLimit : float (default = -90)
               The lower limit of the elevation in degrees of the directions to generate. Has to be between -90 and 90.

           elevationHighLimit : float (default = 90)
               The higher limit of the elevation in degrees of the directions to generate. Has to be between -90 and 90.

           minRange : float (default = 0.5)
               The minimum distance in meters of the energyscape to generate.

           maxRange : float (default = 5)
               The maximum distance in meters of the energyscape to generate.

           pdmEnable : bool (default = True)
               Toggle for PDM filtering part of the RTIS processing pipeline using RTIS CUDA.

           preFilter : Numpy ndarray (default = Not used)
               The array holding the optional pre-filter created with scipy firwin. (shape: nprefilter x 1)

           matchedFilterEnable : bool (default = True)
               Toggle for the optional matched filter part of the RTIS processing pipeline using RTIS CUDA.

           beamformingEnable : bool (default = True)
               Toggle for beamforming part of the RTIS processing pipeline using RTIS CUDA.

           postFilterEnable : bool (default = False)
               Toggle for the optional post-beamforming filter part of the RTIS processing pipeline using RTIS CUDA.

           enveloppeEnable : bool (default = True)
               Toggle for enveloppe part of the RTIS processing pipeline using RTIS CUDA.

           cleanEnable : bool (default = True)
               Toggle for cleaning part of the RTIS processing pipeline using RTIS CUDA.

           preloadToggle : bool (default = True)
               Toggle for using RTIS CUDA preloading

           preFilter : Numpy ndarray (default = Not used)
               The array holding the optional pre-filter created with scipy firwin. (shape: nprefilter x 1)

           postFilter : Numpy ndarray (default = Not used)
               The array holding the optional post-beamforming filter created with scipy firwin. (shape: npostfilter x 1)

           meanEnergyRangeMultiplier : float (default = 2)
               The multiplier weight used to calculate the mean energy for each range during the cleaning step.

           maxEnergyRangeThresholdMultiplier : float (default = 0.5)
               The multiplier weight used to threshold the energy based on the maximum
               for each range during the cleaning step.

           configName : String (default = "")
               String to identify these settings with.
               If set to empty (as it is by default) it will default to a unique UUID.

           Returns
           -------
           settings : RTISSettings object as dict
               The complete class containing all RTIS settings for recording and processing. Returns 'None' or
               will raise an exception on failure.
           """

        method_name = "get_settings"
        arguments = ["recordingPremade", "recordingJsonPath", "recordingCallCustom",
                     "processingPremade", "processingJsonPath", "processingCustomPath",
                     "microphoneSamples", "microphoneSampleFrequency",
                     "callSampleFrequency", "callDuration", "callMinimumFrequency", "callMaximumFrequency",
                     "callEmissions", "microphoneLayout", "mode",
                     "directions", "azimuthLowLimit", "azimuthHighLimit", "elevationLowLimit" , "elevationHighLimit",
                     "minRange", "maxRange", "pdmEnable", "preFilterEnable", "matchedFilterEnable",
                     "beamformingEnable", "postFilterEnable", "enveloppeEnable", "cleanEnable",
                     "preloadToggle", "preFilter", "postFilter", "meanEnergyRangeMultiplier",
                     "maxEnergyRangeThresholdMultiplier", "configName"]
        values = (recordingPremade, recordingJsonPath, recordingCallCustom,
                  processingPremade, processingJsonPath, processingCustomPath,
                  microphoneSamples, microphoneSampleFrequency,
                  callSampleFrequency, callDuration, callMinimumFrequency, callMaximumFrequency,
                  callEmissions, microphoneLayout, mode,
                  directions, azimuthLowLimit, azimuthHighLimit, elevationLowLimit , elevationHighLimit, minRange,
                  maxRange, pdmEnable, preFilterEnable, matchedFilterEnable, beamformingEnable, postFilterEnable,
                  enveloppeEnable, cleanEnable, preloadToggle, preFilter, postFilter,
                  meanEnergyRangeMultiplier, maxEnergyRangeThresholdMultiplier, configName)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def set_settings_from_class(self, settings: dict, applyToDevice: bool = True) -> bool:
        """Set the wanted settings from an `RTISSettings` object. These can be created
           with the `get_settings()` or `get_current_settings()` methods.

           Parameters
           ----------
           settings : RTISSettings object as dict
               The complete class containing all RTIS settings for recording and processing that needs to be set.

           applyToDevice : bool (default = True)
               A configuration toggle to optionally disable applying the recording settings to the RTIS Device.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "set_settings_from_class"
        arguments = ["settings", "applyToDevice"]
        values = (settings, applyToDevice)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_premade_recording_settings_list(self) -> List[str]:
        """Get a list of names of all the available premade settings for recording.

           Returns
           -------
           recordingSettings : list[str]
               A list holding all the names of available settings that can be loaded.
        """

        method_name = "get_premade_recording_settings_list"
        arguments = []
        values = ()

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_microphone_layout_list(self) -> List[str]:
        """Get a list of names of all the available microphone layouts that are available for recording.

           Returns
           -------
           microphoneLayouts : list[str]
               A list holding all the names of available microphone layouts that can be loaded.
        """

        method_name = "get_microphone_layout_list"
        arguments = []
        values = ()

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def prepare_processing(self, configName: str = "") -> bool:
        """Start the CUDA workers for looped measurements with processing enabled.
           It is not required to run this method for doing processing, but it will speed up the workflow
           significantly if doing many processed measurements at a high frequency.
           Furthermore, if using the default settings for processing this is enabled already.
           If no config name parameter is provided it will assume only one settings configuration is available and
           will prepare that one.

           Parameters
           ----------
           configName: string
               The identity of the settings configuration to be used. If not given it will assume only one
               settings configuration is defined within RTIS Dev.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "prepare_processing"
        arguments = ["configName"]
        values = (configName,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def unload_processing(self, configName: str = "") -> bool:
        """Stop all CUDA workers of all workers or of one specified if the configuration name is provided.
           Only required if actually using preloading of CUDA workers. CUDA workers are also automatically
           stopped when your script ends.

           Parameters
           ----------
           configName: string
               The identity of the settings configuration to be used. If not given it will stop the workers
               of all configurations.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "unload_processing"
        arguments = ["configName"]
        values = (configName,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_raw_measurement(self, behaviour: bool = False, configName: str = "") -> dict:
        """Start an RTIS sonar measurement and return the raw data in an `RTISMeasurement` object.
           This means that it will only record and not perform any processing.

           Parameters
           ----------
           behaviour : bool (default = False)
               A configuration toggle to set the required sonar behaviour (active or passive).

           configName: string
               The identity of the settings configuration to be used. If not given it will assume only one
               settings configuration is defined within RTIS Dev.

           Returns
           -------
           measurement : RTISMeasurement object as dict
               The data class holding the raw measurement of the RTIS device with the raw binary data under
               `measurement.rawData`.

           Examples
           --------
           Create a connection, set recording settings and make a raw measurement with passive behaviour::

               >>> import rtisdevremotepy
               >>> rtisdev.open_connection()
               >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
               >>> measurement = rtisdev.get_raw_measurement(True, configName=config_uuid)

           Note that when multiple recording configurations are loaded, the module will automatically
           load the settings as asked for by the configName argument to the RTIS device before performing a new measurement.
        """

        method_name = "get_raw_measurement"
        arguments = ["behaviour", "configName"]
        values = (behaviour, configName)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_signal_measurement(self, behaviour: bool = False, configName: str = "") -> dict:
        """Start an RTIS sonar measurement and process it with only PDM filtering
           and subsampling enabled to get the microphone signals returned in an `RTISMeasurement` object.
           This means it will overwrite the enabled and disabled processing steps that the user might
           have set. But will still use the other chosen recording and processing settings.

           Parameters
           ----------
           behaviour : bool (default = False)
               A configuration toggle to set the required sonar behaviour (active or passive).

           configName: string
               The identity of the settings configuration to be used. If not given it will assume only one
               settings configuration is defined within RTIS Dev.

           Returns
           -------
           measurement : RTISMeasurement object as dict
               The data class holding the signal measurement of the RTIS device under `measurement.processedData`
               and the raw binary data under `measurement.rawData`.

           Examples
           --------
           Create a connection, set recording and processing settings and make a signal measurement with active behaviour::

               >>> import rtisdevremotepy
               >>> rtisdev.open_connection()
               >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
               >>> signal_measurement = rtisdev.get_signal_measurement(True, configName=config_uuid)

           Note that when multiple recording configurations are loaded, the module will automatically
           load the settings as asked for by the configName argument to the RTIS device before performing a new measurement.
        """

        method_name = "get_signal_measurement"
        arguments = ["behaviour", "configName"]
        values = (behaviour, configName)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_processed_measurement(self, behaviour: bool = False, configName: str = "") -> dict:
        """Start an RTIS sonar measurement and process it and return the raw and processed data
           in an `RTISMeasurement` object. This will use the chosen recording and processing settings.

           Parameters
           ----------
           behaviour : bool (default = False)
               A configuration toggle to set the required sonar behaviour (active or passive).

           configName: string
               The identity of the settings configuration to be used. If not given it will assume only one
               settings configuration is defined within RTIS Dev.

           Returns
           -------
           measurement : RTISMeasurement object as dict
               The data class holding the processed measurement (the microphone signals)
               of the RTIS device under `measurement.processedData`
               and the raw binary data under `measurement.rawData`.

           Examples
           --------
           Create a connection, set recording and processing settings and make
           a processed measurement with active behaviour::

               >>> import rtisdevremotepy
               >>> rtisdev.open_connection()
               >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
               >>> rtisdev.set_processing_settings(directions=91, configName=config_uuid)
               >>> processed_measurement = rtisdev.get_processed_measurement(True, configName=config_uuid)

           Note that when multiple recording configurations are loaded, the module will automatically
           load the settings as asked for by the configName argument to the RTIS device before performing a new measurement.
        """

        method_name = "get_processed_measurement"
        arguments = ["behaviour", "configName"]
        values = (behaviour, configName)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def process_measurement(self, measurement: dict, configName: str = "") -> dict:
        """Process a previously recorded raw RTIS sonar measurement from a `RTISMeasurement` object
           and return same measurement with processed data in a new `RTISMeasurement` object.

           Parameters
           ----------
           measurement : RTISMeasurement object as dict
               The data class holding the raw measurement of the RTIS device.

           configName: string
               The identity of the settings configuration to be used. If not given it will assume only one
               settings configuration is defined within RTIS Dev.

           Returns
           -------
           measurement :RTISMeasurement object
               The data class holding the processed measurement of the RTIS device under `measurement.processedData`
               and the raw binary data under `measurement.rawData`.

           Examples
           --------
           Create a connection, set recording and processing settings and make a raw measurement with active behaviour.
           Then afterward process it::

               >>> import rtisdevremotepy
               >>> rtisdev.open_connection()
               >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
               >>> rtisdev.set_processing_settings(directions=91, configName=config_uuid)
               >>> measurement = rtisdev.get_raw_measurement(True, configName=config_uuid)
               >>> processed_measurement = rtisdev.process_measurement(measurement, configName=config_uuid)
        """

        method_name = "process_measurement"
        arguments = ["measurement", "configName"]
        values = (measurement, configName)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def set_counter(self, newCount: int = 0) -> bool:
        """Set the internal measurement counter of the sonar hardware.

           Parameters
           ----------
           newCount : int (default = 0)
               The new count index to set.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "set_counter"
        arguments = ["newCount"]
        values = (newCount,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def set_behaviour(self, mode: bool) -> bool:
        """Set the behaviour of the sonar hardware to passive or active. This is only necessary if using external
           measurement triggers. As using the normal RTIS Dev functions of `get_raw_measurement(behaviour)`,
           `get_signal_measurement(behaviour)` and `get_processed_measurement(behaviour)` will use the given function
           argument to define the sonar behaviour.

           Parameters
           ----------
           mode : bool
               the behaviour mode chosen.
               False = passive
               True = active

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "set_behaviour"
        arguments = ["mode"]
        values = (mode,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def get_firmware_version(self) -> str:
        """Get the firmware version of the internal RTIS firmware used on the device.

           Returns
           -------
           firmwareVersion : string
               returns the firmware version as a string in 'vMajor.Minor.Bugfix' format. Returns 'undefined' or will
               raise an exception on failure.
        """

        method_name = "get_firmware_version"
        arguments = []
        values = ()

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def toggle_amplifier(self, mode: bool) -> bool:
        """Enable/disable the high voltage amplifier's step up controller.
           It is enabled by default so has to be manually disabled if wanted.
           This will save on power usage and heat production.

           Parameters
           ----------
           mode : bool
               The amplifier mode chosen. `False` = disable, `True` = enable

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "toggle_amplifier"
        arguments = ["mode"]
        values = (mode,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def toggle_external_triggers(self, mode: bool, pin: int = 1) -> bool:
        """Enable/disable external triggers being able to start a measurement on the RTIS device.
           They are disabled by default so have to be manually enabled. You can also set the input pin (1 or 2).

           Parameters
           ----------
           mode : bool
               the external trigger mode chosen.`False` = disable, `True` = enable
           pin : Integer (default = 1)
               change the trigger pin to use. This has to be 1 or 2.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "toggle_external_triggers"
        arguments = ["mode", "pin"]
        values = (mode, pin)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def custom_command(self, command: str) -> bool:
        """Send a custom command to the RTIS device to execute over serial.
           This is usually in the format of !c,i,j,k. With c being the command ID character and i,j and k being the three
           comma-seperated command values.

           Parameters
           ----------
           command : str
               the command string to send to the RTIS device.

           Returns
           -------
           returnValue : int
               returns the returned value of the RTIS device as an integer.
        """

        method_name = "custom_command"
        arguments = ["command"]
        values = (command,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result

    def reset_device(self, stm32pin: int = 7) -> bool:
        """The function to reset the RTIS device hardware.

           Parameters
           ----------
           stm32pin : Integer (default = 7)
               Change the GPIO pin used for the STM32 connection.
               Please ask a Cosys-Lab member for the correct pin number if not working as intended with the default value.

           Returns
           -------
           success : bool
               returns `True` on successful completion, returns `False` or will raise an exception on failure.
        """

        method_name = "reset_device"
        arguments = ["stm32pin"]
        values = (stm32pin,)

        result, issues = RTISDevRemote.send_command(self.ip, RTISDEV_VERSION, method_name, arguments, values)

        if len(issues) == 1:
            raise Exception(issues[0])
        elif len(issues) > 1:
            raise Exception(issues)
        return result
