# RTIS Dev Remote Python Wrapper

This is a wrapper of the RTIS Dev Remote library to use RTIS Dev remotely over IP from your Python interpreter. 
Quickly develop with connected RTIS devices. Almost all RTIS Dev functions are available as well as automatic conversion
of RTIS Dev custom class objects.

This work is published under the [CC BY-NC-SA 4.0 DEED](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.

## Installation

### Dependencies
* Python 3.6 or higher with modules:
  * Numpy
  * Scipy
* Supported RTIS Dev version is v2.12.3.

### From PyPi
You can install this module from the [PyPi repository](https://pypi.org/project/rtisdevremotepy/) like any other:
```bash
pip install rtisdevremotepy
```

### Install from source
Install all dependencies listed above. 
We suggest to always use pip:
```bash
pip install MODULE_NAME
```

When you clone this repository you will need to manually update the gitmodules to get the right version of [RTIS Dev Remote](https://cosysgit.uantwerpen.be/rtis-software/rtisdevremote).
For example:
```bash
cd rtisdevremotepy
git submodule init
git submodule update
```

To install the Python Module so that you can use it in any Python script: 
```bash
pip install .
```

## Usage

### Unavailable RTIS Dev methods 
Here is a short list of the current RTIS Dev methods that aren't available through this wrapper:
* [create_measure_external_trigger_queue](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_measure_external_trigger_queue)
* [create_measure_external_trigger_callback](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_measure_external_trigger_callback)
* [create_processing_workers](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#create_processing_workers)
* [set_log_mode](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#set_log_mode)
* [set_custom_logger](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#set_custom_logger)


### Initial setup
When starting with this wrapper, first try to make a connection the remote RTIS Device.
This both tests the connection as makes sure that the RTIS Dev version used on the remote device is supported by the version of this wrapper.
The only required argument is the IP of the remote RTIS Device. To learn more about how to find out the IP, please see this [guide](https://cosysgit.uantwerpen.be/rtis-software/ertissoftwareusageguide/-/wikis/Initial-Connection-&-Network-Setup).
```python
import rtisdevremotepy

rtisdev = rtisdevremotepy.RTISDev("192.168.1.150")
```
Now the `rtisdev` object can be used to run RTIS Dev methods from.

### Executing remote methods
After the connection is made and no errors were shown, you can now use [all available RTIS Dev commands](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home). Some don't work and are listed in the [list](#unavailable-rtis-dev-methods) above.
Please use the [RTIS Dev wiki](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home) to know which arguments to use. 
The commands should be called from the `rtisdev` objects. For example:
```python
rtisdev.open_connection()
```

### Arguments
Please see the [RTIS Dev wiki](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home) to know which arguments are optional and which are required.
They use the exact same naming formats.
```python
rtisdev.set_recording_settings(callDuration=4.4, callMinimumFrequency=30000, callMaximumFrequency=60000)
```

When you provide wrong arguments or run into other exceptions to RTIS Dev, the Python wrapper will raise an exception listing and describing the problem.

### Custom data types
Some methods return or require one of the [RTIS Dev custom class object](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home#classes). 
The RTIS Dev Python wrapper will automatically convert these to Python dictionary objects.
When these dictionary objects are provided as arguments, the wrapper will automatically convert them again, so it should all work straight out of the box!
```python
settings = rtisdev.get_current_settings(configName=config_uuid)
rtisdev.set_settings_from_class(settings)

measurement_raw = rtisdev.get_raw_measurement(behaviour=true, configName=config_uuid)
measurement_processed_from_raw = rtisdev.process_measurement(measurement_raw, configName=config_uuid)
```

If one has RTIS Dev fully installed and imported, one can also use the function `convert_to_rtis_class(rtis_dict)` to convert the dictionary objects back to the full RTIS Dev custom class objects. For example:
```python
import rtisdev as fullrtisdev
measurement_processed_from_raw = rtisdev.process_measurement(measurement_raw, configName=config_uuid)
measurement_processed_from_raw_converted = rtisdev.convert_to_rtis_class(measurement_processed_from_raw)
```

## Full example
A bigger example showing how to connect, record and process a measurement and plot the RTIS Energyscape.
```python
import matplotlib.pyplot as plt
import numpy as np
import rtisdevremotepy

# Connect and verify matching versions of RTIS Dev
rtisdev = rtisdevremotepy.RTISDev("192.168.1.150")

# Connect to RTIS Device
rtisdev.open_connection()

# Configure the recording and processing settings
config_uuid = rtisdev.set_recording_settings(microphoneSamples=163840, callMinimumFrequency=25000, callMaximumFrequency=50000)
rtisdev.set_processing_settings(directions=91, maxRange=5, configName=config_uuid)
settings = rtisdev.get_current_settings(configName=config_uuid)

# Get an ACTIVE measurement (protect your ears!) and process it
measurement_processed = rtisdev.get_processed_measurement(behaviour=True, configName=config_uuid)

# Plot the 2D energyscape of this processed measurement.
plt.imshow(np.transpose(measurement_processed['processedData']), cmap="hot", interpolation='nearest')
plt.xlabel("Directions (degrees)")
plt.ylabel("Range (meters)")
indexes_x = np.arange(0, measurement_processed['processedData'].shape[0], 20)
labels_x = np.round(np.rad2deg(settings['directions'][indexes_x, 0])).astype(int)
indexes_y = np.arange(0, measurement_processed['processedData'].shape[1], 100)
labels_y = settings['ranges'][indexes_y]
fmt_x = lambda x: "{:.0f}°".format(x)
fmt_y = lambda x: "{:.2f}m".format(x)
plt.xticks(indexes_x, [fmt_x(i) for i in labels_x])
plt.yticks(indexes_y, [fmt_y(i) for i in labels_y])
plt.title("RTIS Dev - 2D Energyscape Example")
ax = plt.gca()
ax.invert_yaxis()
ax.set_aspect("auto")
plt.show()
```