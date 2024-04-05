"""
RTIS Dev
========

This is a library used to quickly develop in Python with RTIS devices.

By Cosys-Lab, University of Antwerp

Contributors: Wouter Jansen, Arne Aerts, Dennis Laurijssen & Jan Steckel

Documentation
-------------
For  examples and documentation on available methods of RTIS Dev,
check the small method examples in the documentation on the `wiki <https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home>`_.

Small example
-------------

Here is a small example that goes over most basic steps::

    >>> import rtisdev
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np

Open a connection to the RTIS Device over the default serial port::

    >>> success_connect = rtisdev.open_connection()

Set the default recording settings with 163840 samples and a call sweep between 25 and 50 KHz::

    >>> config_uuid = rtisdev.set_recording_settings(premade="default_25_50")

Enable all processing steps and preload them with RTIS CUDA. This will produce a 2D energyscape with 181 directions
with a maximum distance of 5m::

    >>> success_settings_processing = rtisdev.set_processing_settings(premade="2D_5m_181", configName=config_uuid)

Get the used settings as a RTISSettings object::

    >>> settings = rtisdev.get_current_settings()

Get an ACTIVE measurement (protect your ears!) in raw data::

    >>> measurement = rtisdev.get_raw_measurement(True)

Store the raw data of that measurement as a binary file. This can be opened in another application for further work::

    >>> raw_data_sonar = measurement.rawData.tobytes()
    >>> file_handle_data = open("test_measurement_" + str(measurement.index) + ".bin", "wb")
    >>> file_handle_data.write(raw_data_sonar)
    >>> file_handle_data.close()

Process that raw measurement to an energyscape using the configuration chosen earlier::

    >>> processed_measurement = rtisdev.process_measurement(measurement)

Get a new ACTIVE measurement (protect your ears!) in both raw and processed data formats directly::

    >>> new_processed_measurement = rtisdev.get_processed_measurement(True)

Plot the 2D energyscape of this processed measurement using matplotlib::

    >>> plt.imshow(np.transpose(new_processed_measurement.processedData), cmap="hot", interpolation='nearest')
    >>> plt.xlabel("Directions (degrees)")
    >>> plt.ylabel("Range (meters)")
    >>> indexes_x = np.arange(0, new_processed_measurement.processedData.shape[0], 20)
    >>> labels_x = np.round(np.rad2deg(settings.directions[indexes_x, 0])).astype(int)
    >>> indexes_y = np.arange(0, new_processed_measurement.processedData.shape[1], 100)
    >>> labels_y = settings.ranges[indexes_y]
    >>> fmt_x = lambda x: "{:.0f}°".format(x)
    >>> fmt_y = lambda x: "{:.2f}m".format(x)
    >>> plt.xticks(indexes_x, [fmt_x(i) for i in labels_x])
    >>> plt.yticks(indexes_y, [fmt_y(i) for i in labels_y])
    >>> plt.title("RTIS Dev - 2D Energyscape Example")
    >>> ax = plt.gca()
    >>> ax.invert_yaxis()
    >>> ax.set_aspect("auto")
    >>> plt.show()

Get a new ACTIVE measurement (protect your ears!) in both raw and microphone signal format directly::

    >>> signal_measurement = rtisdev.get_signal_measurement(True)

Plot the microphone signals of this measurement::

    >>> fig, axs = plt.subplots(8, 4, figsize=(10,16), constrained_layout = True)
    >>> for microphone_index_i in range(0, 8):
    ...     for microphone_index_j in range(0, 4):
    ...         axs[microphone_index_i, microphone_index_j].set_title(str(microphone_index_j+(microphone_index_i*4)+1))
    ...         axs[microphone_index_i, microphone_index_j].plot(signal_measurement.processedData[microphone_index_j+(microphone_index_i*4),:])
    ...         if microphone_index_j != 0:
    ...             plt.setp(axs[microphone_index_i, microphone_index_j], yticklabels=[])
    ...         if microphone_index_i != 7:
    ...             plt.setp(axs[microphone_index_i, microphone_index_j], xticklabels=[])
    ...         if microphone_index_i == 7:
    ...             axs[microphone_index_i, microphone_index_j].set_xlabel("Time (Samples)")
    ...         if microphone_index_j == 0:
    ...             axs[microphone_index_i, microphone_index_j].set_ylabel("Amplitude")
    >>> plt.show()
    >>> fig.suptitle("RTIS Dev - Microphone Signals")
"""
from .RTISDev import *
__version__ = "2.11.0"
