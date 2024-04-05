"""RTIS Dev

This is a library used to quickly develop in Python with RTIS devices.

By Cosys-Lab, University of Antwerp

Contributors: Wouter Jansen, Arne Aerts, Dennis Laurijssen & Jan Steckel

Here is a small example that goes over most basic steps::

    >>> import rtisdev
    >>> import matplotlib.pyplot as plt
    >>> import numpy as np

Open a connection to the RTIS Device over the default serial port::

    >>> success_connect = rtisdev.open_connection()

Set the recording settings with 163840 samples and a call sweep between 25 and 50 KHz::

    >>> config_uuid = rtisdev.set_recording_settings(microphoneSamples=163840, callMinimumFrequency=25000, callMaximumFrequency=50000)

Enable all processing steps and preload them with RTIS CUDA. This will produce a 2D energyscape with 91 directions
with a maximum distance of 6m::

    >>> success_settings_processing = rtisdev.set_processing_settings(directions=91, maxRange=5, configName=config_uuid)

Get the used settings as a RTISSettings object::

    >>> settings = rtisdev.get_current_settings(configName=config_uuid)

Get an ACTIVE measurement (protect your ears!) in raw data::

    >>> measurement = rtisdev.get_raw_measurement(True, configName=config_uuid)

Store the raw data of that measurement as a binary file. This can be opened in another application for further work::

    >>> raw_data_sonar = measurement.rawData.tobytes()
    >>> file_handle_data = open("test_measurement_" + str(measurement.index) + ".bin", "wb")
    >>> file_handle_data.write(raw_data_sonar)
    >>> file_handle_data.close()

Process that raw measurement to an energyscape using the configuration chosen earlier::

    >>> processed_measurement = rtisdev.process_measurement(measurement, configName=config_uuid)

Get a new ACTIVE measurement (protect your ears!) in both raw and processed data formats directly::

    >>> new_processed_measurement = rtisdev.get_processed_measurement(True, configName=config_uuid)

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

    >>> signal_measurement = rtisdev.get_signal_measurement(True, configName=config_uuid)

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

For more examples, check the small method examples in the documentation.
"""

import time
import numpy as np
import re
import scipy.io
import scipy.signal
try:
    import rtiscuda
except:
    pass
import os
if os.name == 'nt':
    try:
        import serial.tools.list_ports
    except:
        pass
else:
    try:
        import rtisserial
    except:
        pass
import socket
import logging
import multiprocessing_logging
import os
import json
from numpy import genfromtxt
import warnings
import string
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
from copy import deepcopy
import sys
import signal
import atexit
import uuid
from typing import Callable, List, Dict, Tuple, Optional
from rtisdev.RTISGenerateSettings import *
from multiprocessing import Queue, Pool, Process, Event, active_children, Value

#########################
# Initial Configuration #
#########################

# Global settings
PORT = '/dev/ttyACM0'
LOG = 3
DEBUG = 1
ID = socket.gethostname()
SETTINGS = {}
WORKERS = []
CUDA_USED = False
PACKAGE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
BEHAVIOUR = False
AMPLIFIER_ACTIVE = False
DEBUG_COUNTER = 0
VERSION = "v2.11.0"
CURRENT_RECORDING_CONFIG = ""


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    purple = "\x1b[35m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] - %(name)s - %(levelname)s - %(message)s"
    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: bold_red + format + reset,
        logging.CRITICAL: purple + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Configure logging
logger = logging.getLogger("RTISDev " + ID)
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)
logger.debug("Loaded RTIS Dev " + VERSION + ".")
multiprocessing_logging.install_mp_handler()


#######################
# RTIS Dev Exceptions #
#######################


class RTISError(Exception):
    """Base class for custom exceptions in RTIS Dev.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class RTISSettingsError(RTISError):
    """Exception raised for when no configured settings can be found.
    """

    def __init__(self):
        global logger
        logger.error('Could not find any configuration settings. Did you use set_recording_settings() yet?')
        self.message = "Could not find any configuration settings. Did you use set_recording_settings() yet?"
        super().__init__(self.message)


class RTISSettingsByIDNotFoundError(RTISError):
    """Exception raised for when no configured settings can be found for the given config name ID.
    """

    def __init__(self):
        global logger
        logger.error('Could not find any configuration settings with the given config name ID.')
        self.message = "Could not find any configuration settings with the given config name ID."
        super().__init__(self.message)


class RTISProcessingSettingsError(RTISError):
    """Exception raised for when settings are found but have no processing configuration.
    """

    def __init__(self):
        global logger
        logger.error("Could not find any processing configuration in the settings. " +
                     "Did you use set_processing_settings() yet?")
        self.message = "Could not find any processing configuration in the settings. " + \
                       "Did you use set_processing_settings() yet?"
        super().__init__(self.message)


class RTISCUDAError(RTISError):
    """Exception raised for when the RTIS CUDA python module cannot be found.
    """

    def __init__(self):
        global logger
        logger.error("The RTIS CUDA Python module was not found to be installed. Make sure to install it or disable"
                     "all processing steps to avoid using RTIS CUDA.")
        self.message = "The RTIS CUDA Python module was not found to be installed. Make sure to install it or" \
                       " disable all processing steps to avoid using RTIS CUDA."
        super().__init__(self.message)


class RTISWorkerError(RTISError):
    """Exception raised for when a processing working was already loaded into RTIS CUDA when trying to start a
       processing working pool.
    """

    def __init__(self):
        global logger
        logger.error("You have loaded processing settings into RTIS CUDA. This will cause a crash if continuing." +
                     " Please disable 'preloadToggle' or make sure to " +
                     "not use 'prepare_processing()' before this point.")
        self.message = ("You have loaded processing settings into RTIS CUDA. This will cause a crash if continuing." +
                        " Please disable 'preloadToggle' or make sure to " +
                        "not use 'prepare_processing()' before this point.")
        super().__init__(self.message)


class RTISSerialError(RTISError):
    """Exception raised for when the RTIS Serial python module cannot be found.
    """

    def __init__(self):
        global logger
        logger.error("The RTIS Serial Python module was not found to be installed. Make sure to install it.")
        self.message = "The RTIS Serial Python module was not found to be installed. Make sure to install it."
        super().__init__(self.message)


class RTISPySerialError(RTISError):
    """Exception raised for when the PySerial module cannot be found.
    """

    def __init__(self):
        global logger
        logger.error("The PySerial Python module was not found to be installed and Windows OS was detected."
                     " Make sure to install it.")
        self.message = "The PySerial Python module was not found to be installed and Windows OS was detected." \
                       " Make sure to install it."
        super().__init__(self.message)


class RTISDuplicateCallError(RTISError):
    """Exception raised for when the recording settings are trying to both use custom call path and a JSON.
    """

    def __init__(self):
        global logger
        logger.error("The JSON has both a custom call loaded as well as call settings defined. Please choose one.")
        self.message = "The JSON has both a custom call loaded as well as call settings defined. Please choose one."
        super().__init__(self.message)


class RTISPremadeRecordingSettingsError(RTISError):
    """Exception raised for when the settings for recording are using a non-existing premade name.
    """

    def __init__(self, value):
        global logger
        logger.error("Could not load premade recording configuration '" + str(value) + "'. " +
                     "Please make sure to use the correct name. You can find all available" +
                     " with get_premade_recording_settings_list().")
        self.message = ("Could not load premade recording configuration '" + str(value) + "'. " +
                        "Please make sure to use the correct name. You can find all available" +
                        " with get_premade_recording_settings_list().")
        super().__init__(self.message)


class RTISPremadeProcessingSettingsError(RTISError):
    """Exception raised for when the settings for processing are using a non-existing premade name.
    """

    def __init__(self, value):
        global logger
        logger.error("Could not load premade processing configuration '" + str(value) + "'. " +
                     "Please make sure to use the correct name. You can find all available" +
                     " with get_premade_processing_settings_list().")
        self.message = ("Could not load premade processing configuration '" + str(value) + "'. " +
                        "Please make sure to use the correct name. You can find all available" +
                        " with get_premade_processing_settings_list().")
        super().__init__(self.message)


class RTISPremadeAndJsonSettingsError(RTISError):
    """Exception raised for when trying to set settings using both a premade configuration and
       a custom JSON at the same time.
    """

    def __init__(self):
        global logger
        logger.error("You defined both a premade settings name and a custom json file to load. Please only use one.")
        self.message = "You defined both a premade settings name and a custom json file to load. Please only use one."
        super().__init__(self.message)


class RTISMultipleSettingsFoundError(RTISError):
    """Exception raised when there are multiple settings configurations are defined within RTIS Dev and no specific
       config was chosen by the config ID.
    """

    def __init__(self):
        global logger
        logger.error("Multiple settings configurations defined within RTIS Dev, please provide a config name ID.")
        self.message = "Multiple settings configurations defined within RTIS Dev, please provide a config name ID."
        super().__init__(self.message)


####################
# RTIS Dev Classes #
####################


class RTISMeasurement:
    """Class storing all data and information on an RTIS device measurement.

       Attributes
       ----------
       id : string
           The unique identifier to identify this RTIS Client by.

       timestamp : float
           The epoch timestamp of the measurement.

       behaviour: bool
           The sonar behaviour (active or passive).

       index: int
           The internal measurement index.

       rawData: Numpy ndarray
           This stores the raw data returned by the RTIS Device. This is stored as a list of uint32 values.

       processedData: Numpy ndarray
           This stores the (partially) processed data that has gone
           through the processing pipeline as configured by the user.

       configName: string
           The identity of the settings configuration used for this measurement (and its processing).
    """

    def __init__(self, id: str = "", timestamp: float = 0, behaviour: bool = False, index: int = 0,
                 rawData: np.ndarray = None, processedData: np.ndarray = None, configName: str = ""):
        """Parameters
           ----------
           id : string
               The unique identifier to identify this RTIS Client by.

           timestamp : float
               The epoch timestamp of the measurement.

           behaviour: bool
               The sonar behaviour (active or passive).

           index: int
               The internal measurement index.

           rawData: Numpy ndarray
               This stores the raw data returned by the RTIS Device. This is stored as a list of uint32 values.

           processedData: Numpy ndarray (default = None)
               This stores the (partially) processed data that has gone through
               the processing pipeline as configured by the user.

           configName: string
           The identity of the settings configuration used for this measurement (and its processing).
        """

        self.id = id
        self.timestamp = timestamp
        self.behaviour = behaviour
        self.index = index
        self.rawData = rawData
        self.processedData = processedData
        self.configName = configName

    def update_processed_data(self, processedData: np.ndarray):
        """If only the attribute `processedData` needs to be updated, use this function.

           Parameters
           ----------
           processedData: Numpy ndarray (None by default)
               This stores the (partially) processed data that has gone through
               the processing pipeline as configured by the user.
        """

        self.processedData = processedData


class RTISSettings(object):
    """Class describing all the processing and recording settings related to RTIS devices.
       Too many variables to describe here. Check the source-code for more information on which variables are available.
       Can be converted to a dictionary.
    """

    def __init__(self, firmwareVersion: str, configName: str):
        self.version = VERSION
        self.firmwareVersion = firmwareVersion
        self.pdmSampleFrequency = 4500000
        self.meanEnergyRangeMultiplier = np.float32(2)
        self.maxEnergyRangeThresholdMultiplier = np.float32(0.5)
        self.pdmSubsampleFactor = 10
        self.nMicrophones = 32
        self.beamformingDrop = 512
        self.energyscapeSubsampleFactor = 10
        self.recordingSettings = False
        self.processingSettings = False
        self.configName = configName

    def set_recording_settings(self, adcSignal, dacSignal, microphoneSampleFrequency, dacSampleFrequency,
                               microphoneSamples, callDuration, callMinimumFrequency, callMaximumFrequency,
                               callEmissions):
        self.adcSignal = adcSignal
        self.dacSignal = dacSignal
        self.dacSamples = self.dacSignal.shape[0]
        self.microphoneSampleFrequency = microphoneSampleFrequency
        self.dacSampleFrequency = dacSampleFrequency
        self.microphoneSamples = microphoneSamples
        self.callDuration = callDuration
        self.callMinimumFrequency = callMinimumFrequency
        self.callMaximumFrequency = callMaximumFrequency
        self.callEmissions = callEmissions
        self.measurementDuration = (1 / (self.microphoneSampleFrequency / 10) *
                                    self.microphoneSamples / self.pdmSubsampleFactor)
        self.rawDataDimension = self.microphoneSamples
        self.recordingSettings = True
        self.nspsls = int(self.microphoneSamples / self.pdmSubsampleFactor)

    def set_processing_settings(self, pdmEnable, preFilterEnable, matchedFilterEnable, beamformingEnable,
                                postFilterEnable, enveloppeEnable, cleanEnable, preloadToggle, delayMatrix, directions,
                                ranges, microphoneLayout, disableList, postFilter, preFilter,
                                meanEnergyRangeMultiplier, maxEnergyRangeThresholdMultiplier):

        self.pdmEnable = bool(pdmEnable)
        self.preFilterEnable = bool(preFilterEnable)
        self.matchedFilterEnable = bool(matchedFilterEnable)
        self.beamformingEnable = bool(beamformingEnable)
        self.postFilterEnable = bool(postFilterEnable)
        self.enveloppeEnable = bool(enveloppeEnable)
        self.cleanEnable = bool(cleanEnable)
        self.processingEnable = True
        self.disableList = disableList
        if (self.pdmEnable is False and self.preFilterEnable is False and self.matchedFilterEnable is False
                and self.beamformingEnable is False and self.postFilterEnable is False and self.enveloppeEnable is False
                and self.cleanEnable is False):
            self.processingEnable = False
        self.preloadToggle = preloadToggle
        self.delayMatrix = delayMatrix
        self.directions = directions
        self.ranges = ranges
        self.microphoneLayout = microphoneLayout
        self.minRange = min(self.ranges)
        self.maxRange = max(self.ranges)
        self.meanEnergyRangeMultiplier = meanEnergyRangeMultiplier
        self.maxEnergyRangeThresholdMultiplier = maxEnergyRangeThresholdMultiplier
        self.nDirections = self.delayMatrix.shape[1]
        self.energyscapeSplStart = (int(round(self.minRange * 2 / 343 *
                                              (self.microphoneSampleFrequency / 10) / self.energyscapeSubsampleFactor)))
        self.energyscapeSplStop = (int(round(self.maxRange * 2 / 343 *
                                             (self.microphoneSampleFrequency / 10) / self.energyscapeSubsampleFactor)))
        self.nspses = self.energyscapeSplStop - self.energyscapeSplStart
        self.pdmFc = 100000 / (self.pdmSampleFrequency / 2)
        self.pdmb, self.pdma = scipy.signal.butter(4, self.pdmFc)
        self.lpfesb, self.lpfesb = scipy.signal.butter(2, 1000 / ((self.microphoneSampleFrequency / 10) / 2), 'low')
        self.pdmFilter = scipy.signal.firwin(512, self.pdmFc).astype(np.float32)
        self.lpEsFilter = scipy.signal.firwin(512, 1000 / ((self.microphoneSampleFrequency / 10) / 2)).astype(
            np.float32)
        if self.preFilterEnable:
            self.preFilter = preFilter.astype(np.float32)
        else:
            self.preFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        if self.matchedFilterEnable:
            adcSignalConcat = np.concatenate((self.adcSignal, np.zeros(self.nspsls - self.adcSignal.size)))
            adcSignalFft = np.transpose(np.conj(np.fft.rfft(adcSignalConcat)))
            self.sigBaseMatchedFilter = np.resize(adcSignalFft, (self.nMicrophones, int(self.nspsls / 2 + 1)))
            self.sigBaseMatchedFilterReal = np.real(self.sigBaseMatchedFilter).astype(np.float32)
            self.sigBaseMatchedFilterImag = np.imag(self.sigBaseMatchedFilter).astype(np.float32)
        else:
            self.sigBaseMatchedFilterReal = np.zeros(shape=(1, 1)).astype(np.float32)
            self.sigBaseMatchedFilterImag = np.zeros(shape=(1, 1)).astype(np.float32)
        if self.postFilterEnable:
            self.postFilter = postFilter.astype(np.float32)
        else:
            self.postFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        self.processingDataDimensionOne = 0
        self.processingDataDimensionTwo = 0
        if self.processingEnable is True:
            self.processingDataDimensionOne = self.nMicrophones
            self.processingDataDimensionTwo = self.nspsls
            if self.cleanEnable or self.enveloppeEnable:
                self.processingDataDimensionOne = self.nDirections
                self.processingDataDimensionTwo = self.nspses
            elif self.beamformingEnable or self.postFilterEnable:
                self.processingDataDimensionOne = self.nDirections
                self.processingDataDimensionTwo = self.nspsls - self.beamformingDrop

        self.processingSettings = True

    def set_signal_processing_only(self):
        self.processingEnable = True
        self.pdmEnable = True
        self.preFilterEnable = False
        self.matchedFilterEnable = False
        self.beamformingEnable = False
        self.postFilterEnable = False
        self.enveloppeEnable = False
        self.cleanEnable = False
        self.processingEnable = True
        self.processingSettings = True
        self.processingDataDimensionOne = self.nMicrophones
        self.processingDataDimensionTwo = self.nspsls
        self.pdmFc = 100000 / (self.pdmSampleFrequency / 2)
        self.pdmb, self.pdma = scipy.signal.butter(4, self.pdmFc)
        self.lpfesb, self.lpfesb = scipy.signal.butter(2, 1000 / ((self.microphoneSampleFrequency / 10) / 2), 'low')
        self.pdmFilter = scipy.signal.firwin(512, self.pdmFc).astype(np.float32)
        self.lpEsFilter = scipy.signal.firwin(512, 1000 / ((self.microphoneSampleFrequency / 10) / 2)).astype(
            np.float32)
        self.preFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        self.sigBaseMatchedFilterReal = np.zeros(shape=(1, 1)).astype(np.float32)
        self.sigBaseMatchedFilterImag = np.zeros(shape=(1, 1)).astype(np.float32)
        self.postFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        self.disableList = []
        self.nDirections = 0
        self.energyscapeSplStart = 0
        self.energyscapeSplStop = 0
        self.delayMatrix = np.zeros(shape=(1, 1)).astype(np.int32)

    def __iter__(self):
        yield 'version', self.version
        yield 'firmwareVersion', self.firmwareVersion
        yield 'pdmSampleFrequency', self.pdmSampleFrequency
        yield 'meanEnergyRangeMultiplier', float(self.meanEnergyRangeMultiplier)
        yield 'maxEnergyRangeThresholdMultiplier', float(self.maxEnergyRangeThresholdMultiplier)
        yield 'pdmSubsampleFactor', self.pdmSubsampleFactor
        yield 'nMicrophones', self.nMicrophones
        yield 'beamformingDrop', self.beamformingDrop
        yield 'energyscapeSubsampleFactor', self.energyscapeSubsampleFactor
        yield 'configName', self.configName

        if self.recordingSettings:
            yield 'dacSamples', self.dacSamples
            yield 'microphoneSamples', self.microphoneSamples
            yield 'microphoneSampleFrequency', self.microphoneSampleFrequency
            yield 'dacSampleFrequency', self.dacSampleFrequency
            yield 'callDuration', self.callDuration
            yield 'callMinimumFrequency', self.callMinimumFrequency
            yield 'callMaximumFrequency', self.callMaximumFrequency
            yield 'measurementDuration', self.measurementDuration
            yield 'callEmissions', self.callEmissions
            yield 'rawDataDimension', self.rawDataDimension
            yield 'nspsls', self.nspsls
            yield "adcSignal", self.adcSignal.tolist()

        if self.processingSettings:
            yield 'pdmEnable', self.pdmEnable
            yield 'preFilterEnable', self.preFilterEnable
            yield 'matchedFilterEnable', self.matchedFilterEnable
            yield 'beamformingEnable', self.beamformingEnable
            yield 'postFilterEnable', self.postFilterEnable
            yield 'enveloppeEnable', self.enveloppeEnable
            yield 'cleanEnable', self.cleanEnable
            yield 'processingEnable', self.processingEnable
            yield 'minRange', self.minRange
            yield 'maxRange', self.maxRange
            yield "ranges" , self.ranges.tolist()
            yield 'nDirections', self.nDirections
            yield "directions_azimuth" , self.directions[:, 0].tolist()
            yield "directions_elevation" , self.directions[:, 1].tolist()
            yield 'energyscapeSplStart', self.energyscapeSplStart
            yield 'energyscapeSplStop', self.energyscapeSplStop
            yield 'pdmFc', self.pdmFc
            yield 'pdmb', self.pdmb.tolist()
            yield 'pdma', self.pdma.tolist()
            yield 'lpfesb', self.lpfesb.tolist()
            yield 'lpfesb', self.lpfesb.tolist()
            yield 'preFilter', self.preFilter.tolist()
            yield 'postFilter', self.postFilter.tolist()
            yield 'processingDataDimensionOne', self.processingDataDimensionOne
            yield 'processingDataDimensionTwo', self.processingDataDimensionTwo
            yield 'microphoneLayout', self.microphoneLayout
            yield 'disableList', self.disableList


class TimeStampRecorderProcess(Process):
    """The class based on a Multiprocessing Process to start a process to store the latest timestamp of a recorded
       measurement using RTIS Sync pulses. It will use the Jetson GPIO library to wait for the RTIS Sync pulse
       and store the system time. This is to circumvent having to take the timestamp after a measurement instead of
       before.
    """

    _latestTimestamp = None
    _debug = None
    _localLogger = None

    def __init__(self, *args, **kwargs):
        super(TimeStampRecorderProcess, self).__init__()
        self._stop_set = Event()

    def set_configuration(self, latestTimestamp, localLogger, debug):
        """Set the configuration parameters for this process after creating it.

           Parameters
           ----------
           latestTimestamp : multiprocessing.Manager.Value
               Memory storage shared between processes to store the latest timestamp value on.

           localLogger : logging.Logger
               The custom logger to be used by RTIS Dev.

           debug : int
               The toggle of the debug mode where a RTIS device is simulated using pre-recorded data.
        """

        self._latestTimestamp = latestTimestamp
        self._debug = debug
        self._localLogger = localLogger

    def stop_thread(self):
        """Stop the process gracefully.
        """

        self._stop_set.set()

    def stopped(self):
        """Get status of the process if it should be stopped or not.
        """

        return self._stop_set.is_set()

    def run(self):
        """Main process function to run continuously. Should not be used directly. Use `start()` instead.
        """
        if self._debug == 0:
            try:
                with open(os.devnull, "w") as devNull:
                    original = sys.stderr
                    sys.stderr = devNull
                    import Jetson.GPIO as GPIO
                    sys.stderr = original
                    GPIO.cleanup()
                    GPIO.setmode(GPIO.BOARD)
                    GPIO.setup(15, GPIO.IN)
            except Exception as ex:
                self._localLogger.error("Could not start timestamp recording process due to unknown error: " + str(ex))
                raise

            try:
                while not self.stopped():
                    GPIO.wait_for_edge(15, GPIO.RISING)
                    self._latestTimestamp.value = time.time()
            except KeyboardInterrupt:
                self.stop_thread()


class MeasureExternalTriggerQueueThread(Process):
    """The class based on a Multiprocessing Process to start RTIS sonar measurements triggered by an external trigger.
       To set the data queue correctly use `set_queue(dataQueue)` function.
       the `RTISMeasurement` objects will then be put on this queue.
       To start the process use the `start()` function. To stop use the `stop_thread()` function.
       By default, using a `signal.SIGINT` exit (ex. using CTRL+C) will gracefully end the script.

       Use `create_measure_external_trigger_queue(dataQueue)` to make an easy to use the class.
    """

    _dataQueue = None
    _settings = None
    _debugCounter = None
    _behaviour = None
    _id = None
    _debug = None
    _localLogger = None
    _latestTimestamp = None
    _useTimestampRecorder = None

    def __init__(self, *args, **kwargs):
        super(MeasureExternalTriggerQueueThread, self).__init__()
        self._stop_set = Event()

    def set_configuration(self, dataQueue, settings, debugCounter, behaviour,
                          device_id, localLogger, debug, latestTimestamp, useTimestampRecorder):
        """Set the configuration parameters for this process after creating it.

           Parameters
           ----------
           dataQueue : multiprocessing.Manager.Queue
               This is the data queue that will be used to store the RTISMeasurement objects on.

           settings : RTISSettings
               The complete class containing all RTIS settings for recording and processing that needs to be set.

           debugCounter : int
               The internal counter to use for indexing measurements in debug mode.

           behaviour : int
               The behaviour mode chosen.
               0 = passive
               1 = active

           device_id : String
               The identifier to use for the measurements.

           localLogger : logging.Logger
               The custom logger to be used by RTIS Dev.

           debug : int
               The toggle of the debug mode where a RTIS device is simulated using pre-recorded data.

           latestTimestamp : multiprocessing.Manager.Value
               Memory storage shared between processes to store the latest timestamp value on.

           useTimestampRecorder : bool
               Indicate to use the separate timestamp recorder or take timestamp afterward.
        """

        self._dataQueue = dataQueue
        self._settings = settings
        self._debugCounter = debugCounter
        self._behaviour = behaviour
        self._id = device_id
        self._debug = debug
        self._localLogger = localLogger
        self._latestTimestamp = latestTimestamp
        self._useTimestampRecorder = useTimestampRecorder

    def stop_thread(self):
        """Stop the measurement process gracefully.
        """

        self._stop_set.set()
        self._localLogger.info("Stopping the measurement process for external triggers and storage on queue.")

    def stopped(self):
        """Get status of the process if it should be stopped or not.
        """

        return self._stop_set.is_set()

    def run(self):
        """Main process function to run continuously. Should not be used directly. Use `start()` instead.
        """

        requestedBytesSize = int((self._settings.microphoneSamples * self._settings.nMicrophones) // 8)
        header = 1364413970
        footer = 792823410
        self._localLogger.info("Starting the measurement process for external triggers and storage on queue.")

        # Debugging mode (no real RTIS hardware connected).
        # Uses sample ACTIVE sonar measurement of a 32 microphone array with the 32_v1 layout.
        # Should be used with the default_25_50 recording settings and the 2D_5m_181 processing settings
        # for proper operation.
        if self._debug == 1:
            self._localLogger.warning("Recording using debug mode. Make sure to use open_connection().")
            try:
                while not self.stopped():
                    rawDataClean = np.fromfile(PACKAGE_DIRECTORY + "/simulate.bin", dtype=np.uint32)
                    index = self._debugCounter
                    self._debugCounter = self._debugCounter + 1
                    timestamp = time.time()
                    package = RTISMeasurement(self._id, timestamp, self._behaviour, index, rawDataClean,
                                              configName=self._settings.configName)
                    self._dataQueue.put(package)
                    self._localLogger.info("Completed externally triggered measurement #" + str(package.index)
                                           + " and added to queue.")
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop_thread()
        else:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=None)
                serPort.reset_input_buffer()
                serPort.reset_output_buffer()
            else:
                rtisserial.flush()
            try:
                while not self.stopped():
                    try:
                        if os.name == 'nt':
                            dataBytes = serPort.read(requestedBytesSize + 12)
                            dataUint32 = np.frombuffer(dataBytes, dtype='uint32')
                            if dataUint32[0] == header and dataUint32[-1] == footer:
                                timestamp = time.time()
                                index = dataUint32[1]
                                dataUint32Measurement = dataUint32[2:-1]
                                package = RTISMeasurement(ID, timestamp, BEHAVIOUR, index, dataUint32Measurement,
                                                          configName=self._settings.configName)
                                self._dataQueue.put(package)
                                self._localLogger.info("Completed externally triggered measurement #"
                                                       + str(package.index) + " and added to queue.")
                            else:
                                self._localLogger.warning("Disregarding measurement of RTIS Device as header and/or"
                                                          " footer were incorrect.")
                        else:
                            data = rtisserial.getdata(requestedBytesSize + 12)
                            if data[0:4].ravel().view("uint32") == header \
                                    and data[requestedBytesSize + 8:requestedBytesSize + 12].ravel().view(
                                    "uint32") == footer:
                                if self._useTimestampRecorder:
                                    timestamp = self._latestTimestamp.value
                                else:
                                    timestamp = time.time()
                                index = data[4:8].ravel().view("uint32")[0]
                                dataUint32Measurement = data[8:requestedBytesSize + 8].ravel().view("uint32")
                                package = RTISMeasurement(self._id, timestamp, self._behaviour, index,
                                                          dataUint32Measurement, configName=self._settings.configName)
                                self._dataQueue.put(package)
                                self._localLogger.info("Completed externally triggered measurement #"
                                                       + str(package.index) + " and added to queue.")
                            else:
                                self._localLogger.warning("Disregarding measurement of RTIS Device as header and/or"
                                                          " footer were incorrect.")
                    except Exception as ex:
                        self._localLogger.error("Could not measure on RTIS device. Unexpected error: " + str(ex))
                        raise
            except KeyboardInterrupt:
                self.stop_thread()


class MeasureExternalTriggerCallbackThread(Process):
    """The class based on a Multiprocessing Process to start RTIS sonar measurements triggered by an external trigger.
       To set the callback function correctly use `set_callback(callback)` function.
       Your callback function should only have one argument, the `RTISMeasurement` data package.
       To start the process use the `start()` function. To stop use the `stop_thread()` function.
       By default, using a `signal.SIGINT` exit (ex. using CTRL+C) will gracefully end the script.

       Use `create_measure_external_trigger_callback(callback)` to make an easy to use the class.
    """

    _callback = None
    _settings = None
    _debugCounter = None
    _behaviour = None
    _id = None
    _debug = None
    _localLogger = None
    _latestTimestamp = None
    _useTimestampRecorder = None

    def __init__(self, *args, **kwargs):
        super(MeasureExternalTriggerCallbackThread, self).__init__()
        self._stop_set = Event()

    def set_configuration(self, callback, settings, debugCounter, behaviour, device_id,
                          localLogger, debug, latestTimestamp, useTimestampRecorder):
        """Set the configuration parameters for this process after creating it.

        Parameters
           ----------
           callback : method with one argument (RTISMeasurement)
               This is the method that will be used as a callback when a new measurement is triggered by the
               external trigger. This function should only require one argument,
               the `RTISMeasurement` object containing the measurement data.

           settings : RTISSettings
               The complete class containing all RTIS settings for recording and processing that needs to be set.

           debugCounter : int
               The internal counter to use for indexing measurements in debug mode.

           behaviour : int
               The behaviour mode chosen.
               0 = passive
               1 = active

           device_id : String
               The identifier to use for the measurements.

           localLogger : logging.Logger
               The custom logger to be used by RTIS Dev.

           debug : int
               The toggle of the debug mode where a RTIS device is simulated using pre-recorded data.

           latestTimestamp : multiprocessing.Manager.Value
               Memory storage shared between processes to store the latest timestamp value on.

           useTimestampRecorder : bool
               Indicate to use the separate timestamp recorder or take timestamp afterward.
        """

        self._callback = callback
        self._settings = settings
        self._debugCounter = debugCounter
        self._behaviour = behaviour
        self._id = device_id
        self._debug = debug
        self._localLogger = localLogger
        self._latestTimestamp = latestTimestamp
        self._useTimestampRecorder = useTimestampRecorder

    def stop_thread(self):
        """Stop the measurement process gracefully.
        """

        self._stop_set.set()
        self._localLogger.info("Stopping the measurement process for external triggers and storage on queue.")

    def stopped(self):
        """Get status of the process if it should be stopped or not.
        """

        return self._stop_set.is_set()

    def run(self):
        """Main process function to run continuously. Should not be used directly. Use `start()` instead.
        """

        requestedBytesSize = int((self._settings.microphoneSamples * self._settings.nMicrophones) // 8)
        header = 1364413970
        footer = 792823410
        self._localLogger.info("Starting the measurement process for external triggers and callback passthrough.")

        # Debugging mode (no real RTIS hardware connected).
        # Uses sample ACTIVE sonar measurement of a 32 microphone array with the 32_v1 layout.
        # Should be used with the default_25_50 recording settings and the 2D_5m_181 processing settings
        # for proper operation.
        if self._debug == 1:
            self._localLogger.warning("Recording using debug mode. Make sure to use open_connection().")
            try:
                while not self.stopped():
                    rawDataClean = np.fromfile(PACKAGE_DIRECTORY + "/simulate.bin", dtype=np.uint32)
                    index = self._debugCounter
                    self._debugCounter = self._debugCounter + 1
                    timestamp = time.time()
                    package = RTISMeasurement(self._id, timestamp, self._behaviour, index, rawDataClean,
                                              configName=self._settings.configName)
                    self._callback(package)
                    self._localLogger.info("Completed externally triggered measurement #" + str(package.index)
                                           + " and triggered callback.")
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop_thread()
        else:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=None)
                serPort.reset_input_buffer()
                serPort.reset_output_buffer()
            else:
                rtisserial.flush()
            try:
                while not self.stopped():
                    try:
                        if os.name == 'nt':
                            dataBytes = serPort.read(requestedBytesSize + 12)
                            dataUint32 = np.frombuffer(dataBytes, dtype='uint32')
                            if dataUint32[0] == header and dataUint32[-1] == footer:
                                timestamp = time.time()
                                index = dataUint32[1]
                                dataUint32Measurement = dataUint32[2:-1]
                                package = RTISMeasurement(ID, timestamp, BEHAVIOUR, index, dataUint32Measurement,
                                                          configName=self._settings.configName)
                                self._callback(package)
                                self._localLogger.info("Completed externally triggered measurement #"
                                                       + str(package.index) + " and triggered callback.")
                            else:
                                self._localLogger.warning("Disregarding measurement of RTIS Device as header and/or"
                                                          " footer were incorrect.")
                        else:
                            data = rtisserial.getdata(requestedBytesSize + 12)
                            if data[0:4].ravel().view("uint32") == header \
                                    and data[requestedBytesSize + 8:requestedBytesSize + 12].ravel().view(
                                    "uint32") == footer:
                                if self._useTimestampRecorder:
                                    timestamp = self._latestTimestamp.value
                                else:
                                    timestamp = time.time()
                                index = data[4:8].ravel().view("uint32")[0]
                                dataUint32Measurement = data[8:requestedBytesSize + 8].ravel().view("uint32")
                                package = RTISMeasurement(self._id, timestamp, self._behaviour, index,
                                                          dataUint32Measurement, configName=self._settings.configName)
                                self._callback(package)
                                self._localLogger.info("Completed externally triggered measurement #"
                                                       + str(package.index) + " and triggered callback.")
                            else:
                                self._localLogger.warning("Disregarding measurement of RTIS Device as header and/or"
                                                          " footer were incorrect.")
                    except Exception as ex:
                        self._localLogger.error("Could not measure on RTIS device. Unexpected error: " + str(ex))
                        raise
            except KeyboardInterrupt:
                self.stop_thread()


##############################
# RTIS Dev Private Functions #
##############################


def __get_firmware_version():
    """Get the firmware version of the sonar.

       Returns
       -------
       firmwareVersion : string
           returns the firmware version as a string in 'vMajor.Minor.Bugfix' format. Returns 'undefined' or
           will raise an exception on failure.
    """

    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!Y,0,0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!Y,0,0,0\n', True)
            returnValueInt8 = [(returnValue >> k) & (1 << 8) - 1 for k in range(0, 32, 8)]
            logger.debug("RTIS Device reports back after getting firmware version: v"
                         + str(int.from_bytes(returnValueInt8[2:3], "little")) + '.' + str(returnValueInt8[1])
                         + '.' + str(returnValueInt8[0]) + ".")
            return 'v' + str(int.from_bytes(returnValueInt8[2:3], "little")) \
                   + '.' + str(returnValueInt8[1]) + '.' + str(returnValueInt8[0])
        except Exception as ex:
            logger.error("Could not get the firmware version of the sonar. Unknown error: " + str(ex))
            raise
    else:
        return 'v0.0.0'


def __check_and_activate_amplifier():
    """The function to check if the high voltage amplifier's step up controller is active and activate it if not.

       Returns
       -------
       toggledAmplifier : bool
           Returns True if the amplifier had to be enabled, False if it was already active.
    """

    global AMPLIFIER_ACTIVE

    if AMPLIFIER_ACTIVE:
        return False
    else:
        logger.info("The high voltage amplifier's step up controller "
                    "was enabled to allow active behaviour of the sonar.")
        __toggle_amplifier(1)
        AMPLIFIER_ACTIVE = True


def __set_sonar_behaviour(mode):
    """Set the behaviour of the sonar hardware to passive or active.

       Parameters
       ----------
       mode : int
           the behaviour mode chosen.
           0 = passive
           1 = active

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    mode = int(mode)
    global BEHAVIOUR
    global AMPLIFIER_ACTIVE
    if mode != 1 and mode != 0:
        logger.error("Could not toggle behaviour of the sonar: it has to be a int of 0(passive) or 1(active).")
        raise TypeError("Could not toggle behaviour of the sonar: it has to be a int of 0(passive) or 1(active).")
    if mode:
        BEHAVIOUR = 1
        logger.debug("Setting sonar behaviour to active.")
    else:
        BEHAVIOUR = 0
        logger.debug("Setting sonar behaviour to passive.")

    if BEHAVIOUR == 1:
        __check_and_activate_amplifier()
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!H,' + str(mode) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!H,' + str(mode) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after setting sonar behaviour: " +
                         str(returnValue) + ".")
            return True
        except Exception as ex:
            logger.error("Could not toggle behaviour of the sonar. Unknown error: " + str(ex))
            raise
    else:
        return True


def __set_microphones_samples(microphoneSamples):
    """Set the amount of microphone samples of the sonar hardware.

       Parameters
       ----------
       microphoneSamples : int
           The amount of microphone samples. Must be dividable by 32768.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    if np.mod(microphoneSamples, 32768) != 0:
        logger.error("Could not set microphone samples on RTIS device to " + str(microphoneSamples) +
                     ": The amount of microphone samples must be dividable by 32768.")
        raise ValueError("Could not set microphone samples on RTIS device to " + str(microphoneSamples) +
                         ": The amount of microphone samples must be dividable by 32768.")
    logger.debug("Setting microphone samples on RTIS device to " + str(microphoneSamples) + ".")
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!G,' + str((microphoneSamples * 4)) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!G,' + str((microphoneSamples * 4)) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after setting microphone samples amount: " +
                         str(returnValue) + ".")
            return True
        except Exception as ex:
            logger.error(
                "Could not set microphone samples on RTIS device to " + str(microphoneSamples) +
                ". Unknown error: " + str(ex))
            raise
    else:
        return True


def __set_measurement_counter(newCount):
    """Set the internal measurement counter of the sonar hardware.

       Parameters
       ----------
       newCount : int
           the new count index to set.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    logger.debug("Setting internal measurement counter on RTIS device to " + str(newCount) + ".")
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!B,' + str(newCount) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!B,' + str(newCount) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after setting internal measurement counter: " +
                         str(returnValue) + ".")
            return True
        except Exception as ex:
            logger.error(
                "Could not set internal measurement counter on RTIS device to " + str(newCount)
                + ". Unknown error: " + str(ex))
            raise
    else:
        return True


def __set_microphones_samplefrequency(microphoneSampleFrequency):
    """Set the microphone sample frequency of the sonar hardware.
       The chosen sample frequency. Must be either:
            - 4500000 (4.5 MHz) for ultrasonic measurements
            - 1125000 (1.125 MHz) for audible measurements

       Parameters
       ----------
       microphoneSampleFrequency : int
           The actual microphone sample frequency (without subsampling of PDM).
           The frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible) depending on the wanted mode.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    if (microphoneSampleFrequency != 4500000
            and microphoneSampleFrequency != 1125000):
        logger.error("Could not set microphone sample frequency on RTIS device to " + str(microphoneSampleFrequency) +
                     ": The microphone sample frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible).")
        raise ValueError("Could not set microphone sample frequency on RTIS device to "
                         + str(microphoneSampleFrequency) + ": The microphone sample frequency must be"
                                                            " 4.5M Hz(ultrasound) or 1.125 MHz(audible).")
    logger.debug(
        "Setting microphone sample frequency on RTIS device to " + str(microphoneSampleFrequency) + ".")
    if not DEBUG:
        try:
            mode = 0
            if microphoneSampleFrequency == 1125000:
                mode = 1
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!F,' + str(mode) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!F,' + str(mode) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after setting microphone sample frequency: " +
                         str(returnValue) + ".")
            return True
        except Exception as ex:
            logger.error("Could not set microphone sample frequency on RTIS device to "
                         + str(microphoneSampleFrequency) + ". Unknown error: " + str(ex))
            raise
    else:
        return True


def __set_dac_samplefrequency(dacSampleFrequency):
    """Set the DAC sample frequency of the sonar hardware.

       Parameters
       ----------
       dacSampleFrequency : int
           The chosen sample frequency. Must be larger than 160 KHz and smaller than 2 MHz.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    if dacSampleFrequency < 160000 or dacSampleFrequency > 2000000:
        logger.error("Could not set DAC sample frequency on RTIS device to " + str(dacSampleFrequency) +
                     ": The DAC sample frequency must be larger than 160 KHz and smaller than 2 MHz.")
        raise ValueError("Could not set DAC sample frequency on RTIS device to " + str(dacSampleFrequency) +
                         ": The DAC sample frequency must be larger than 160 KHz and smaller than 2 MHz.")
    logger.debug("Setting DAC sample frequency on RTIS device to " + str(dacSampleFrequency) + ".")
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!D,' + str(dacSampleFrequency) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!D,' + str(dacSampleFrequency) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after setting DAC sample frequency: " +
                         str(returnValue) + ".")
            return True
        except Exception as ex:
            logger.error("Could not set DAC sample frequency on RTIS device to "
                         + str(dacSampleFrequency) + ". Unknown error: " + str(ex))
            raise
    else:
        return True


def __set_dac_pulse(dacSignal):
    """Set the DAC signal of the sonar hardware.
       You need to use set_dac_samples(dacSamples) first to set the right buffer size.

       Parameters
       ----------
       dacSignal : numpy ndarray (float64)
           Shape (dacSamples, ) with dacSamples the amount of samples.
           Each sample is the actual amplitude values chosen.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    logger.debug("Setting DAC pulse on RTIS device.")
    pulse = np.floor((dacSignal * 2047) + 2048)
    pulse = pulse.astype(int)
    hashCurrent = __get_device_pulse_hash()
    hashThis = __get_this_pulse_hash(dacSignal)
    if hashCurrent == hashThis:
        logger.debug("RTIS Device already has the same DAC signal active. Not updating.")
        return True
    else:
        if not DEBUG:
            try:
                for index, sample in np.ndenumerate(pulse):
                    if os.name == 'nt':
                        serPort = serial.Serial(PORT, 115200, timeout=5)
                        serPort.write(bytes('!C,' + str(int(index[0])) + ',' + str(sample) + ',0\n', encoding='utf-8'))
                        serPort.read(4)
                        serPort.close()
                    else:
                        rtisserial.command('!C,' + str(int(index[0])) + ',' + str(sample) + ',0\n', True)
                    time.sleep(0.001)
                hashResponse = __get_device_pulse_hash()
                if hashResponse != hashThis:
                    logger.error("The returned DAC pulse hash does not match the one calculated. Expected: "
                                 + str(hashThis) + ", but received: " + str(hashResponse))
                    return False
                else:
                    return True
            except Exception as ex:
                logger.error("Could not set DAC pulse on RTIS device. Unknown error: " + str(ex))
                raise
        else:
            return True


def __get_device_pulse_hash():
    """Request the XOR hash of the DAC signal that is currently active on the RTIS device.

       Returns
       -------
       hashValue : int
           Returns the integer value of the XOR hash on success. Returns 0 or
           will raise an exception on failure.
    """

    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!L,0,0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int(int.from_bytes(returnValue, "little"))
                serPort.close()
            else:
                returnValue = int(rtisserial.command('!L,0,0,0\n', True))
            logger.debug("RTIS Device reports back after getting XOR hash of DAC signal: "
                         + str(returnValue) + ".")
            return returnValue
        except Exception as ex:
            logger.error("Could not get the XOR hash of the DAC signal. Unknown error: " + str(ex))
            raise
    else:
        return 0


def __get_this_pulse_hash(dacSignal):
    """Calculate the XOR hash value of the DAC signal.

       Parameters
       ----------
       dacSignal : numpy ndarray (float64)
           Shape (dacSamples, ) with dacSamples the amount of samples.
           Each sample is the actual amplitude values chosen.

       Returns
       -------
       hashValue : int
           Returns the integer value of the XOR hash.
    """
    pulse = np.floor((dacSignal * 2047) + 2048)
    pulse = pulse.astype(int)
    hashValue = 0
    for index, sample in np.ndenumerate(pulse):
        hashValue = hashValue ^ sample
    return hashValue


def __set_dac_samples(dacSamples):
    """Set the DAC sample amount of the sonar hardware to prepare the buffer on the hardware side.
       This should always be used before set_dac_pulse(dacSignal).

       Parameters
       ----------
       dacSamples : int
           The amount of samples chosen. The amount of DAC samples must be larger than 64 and smaller than 65535.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    if dacSamples < 64 or dacSamples > 65535:
        logger.error("Could not set DAC samples on RTIS device to " + str(dacSamples) +
                     ":The amount of DAC samples must be larger than 64 and smaller than 65535.")
        raise ValueError("Could not set DAC samples on RTIS device to " + str(dacSamples) +
                         ":The amount of DAC samples must be larger than 64 and smaller than 65535.")
    logger.debug("Setting DAC samples on RTIS device to " + str(dacSamples) + ".")
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!E,' + str(dacSamples) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!E,' + str(dacSamples) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after setting DAC samples amount: " +
                         str(returnValue) + ".")
            return True
        except Exception as ex:
            logger.error("Could not set DAC samples on RTIS device to " + str(dacSamples)
                         + ". Unknown error: " + str(ex))
            raise
    else:
        return True


def __set_dac_emissions(emissions):
    """Set the amount of times the DAC pulse should be emitted during one measurement by the RTIS Client device.

       Parameters
       ----------
       emissions : int
           The amount of emissions chosen.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    logger.debug("Setting DAC emission amount on RTIS device to " + str(emissions) + ".")
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!I,' + str(emissions) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!I,' + str(emissions) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after setting DAC emission amount: " +
                         str(returnValue) + ".")
            return True
        except Exception as ex:
            logger.error("Could not set DAC emission amount on RTIS device to "
                         + str(emissions) + ". Unknown error: " + str(ex))
            raise
    else:
        return True


def __toggle_external_trigger(mode, pin):
    """Enable/disable external triggers being able to start a measurement on the RTIS device.
       They are disabled by default so have to be manually enabled. You can also set the input pin (1 or 2).

       Parameters
       ----------
       mode : int
           0 = disable
           1 = enable
       pin : int
           Change the trigger pin to use.


       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    if mode != 1 and mode != 0:
        logger.error("Could not toggle the external triggers of the sonar: it has to be 0(disable) or 1(enable)")
        raise TypeError("Could not toggle the external triggers of the sonar: it has to be 0(disable) or 1(enable)")
    if pin != 1 and pin != 2:
        logger.error("Could not toggle the external triggers of the sonar: the pin has to be 1 or 2")
        raise TypeError("Could not toggle the external triggers of the sonar: the pin has to be 1 or 2")
    if mode:
        logger.debug("Enabling external triggers on pin " + str(pin) + ".")
    else:
        logger.debug("Disabling external triggers on pin " + str(pin) + ".")
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!J,' + str(mode) + ',' + str(pin) + ',0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!J,' + str(mode) + ',' + str(pin) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after toggling the external triggers: " +
                         str(returnValue) + ".")
            if mode == 1 and returnValue == 0:
                logger.warning("RTIS Device could not enable the external triggers of the sonar."
                               " Are you sure the RTIS device supports this feature?")
            return True
        except Exception as ex:
            logger.error("Could not toggle the external triggers on RTIS device. Unknown error: " + str(ex))
            raise
    else:
        return True


def __custom_command(command):
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

    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes(command + '\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command(command + '\n', True)
            logger.debug("RTIS Device reports back after sending custom command: " +
                         str(returnValue) + ".")
            return returnValue
        except Exception as ex:
            logger.error("Could not send custom command to RTIS device. Unknown error: " + str(ex))
            raise
    else:
        return 1


def __toggle_amplifier(mode):
    """Enable/disable the high voltage amplifier's step up controller.
       It is enabled by default so has to be manually disabled. This will save on power usage and heat production.

       Parameters
       ----------
       mode : int
           0 = disable
           1 = enable

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    if mode != 1 and mode != 0:
        logger.error("Could not toggle the HV amplifier of the sonar: it has to be 0(disable) or 1(enable)")
        raise TypeError("Could not toggle the HV amplifier of the sonar: it has to be 0(disable) or 1(enable)")
    if mode:
        logger.debug("Enabling HV amplifier.")
    else:
        logger.debug("Disabling HV amplifier.")
    if not DEBUG:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=5)
                serPort.write(bytes('!K,' + str(mode) + ',0,0\n', encoding='utf-8'))
                returnValue = serPort.read(4)
                returnValue = int.from_bytes(returnValue, "little")
                serPort.close()
            else:
                returnValue = rtisserial.command('!K,' + str(mode) + ',0,0\n', True)
            logger.debug("RTIS Device reports back after toggling the HV amplifier: " +
                         str(returnValue) + ".")
            if mode == 1 and returnValue == 0:
                logger.warning("RTIS Device could not enable the HV amplifier of the sonar."
                               " Are you sure the RTIS device supports this feature?")
            return True
        except Exception as ex:
            logger.error("Could not toggle the HV amplifier on RTIS device. Unknown error: " + str(ex))
            raise
    else:
        return True


def __gracefully_close_measure_processes(signum, frame):
    """Internal function to close all running measurement processes gracefully.
       """

    measure_processes = [process for process in active_children()
                         if (isinstance(process, MeasureExternalTriggerQueueThread)
                             or isinstance(process, MeasureExternalTriggerCallbackThread)
                             or isinstance(process, TimeStampRecorderProcess))]
    for measure_process in measure_processes:
        measure_process.stop_thread()


def __measure(behaviour, settings):
    """The function to start an RTIS sonar measurement.

       Parameters
       ----------
       behaviour : bool
           A configuration toggle to read the required sonar behaviour (active or passive).

       settings : RTISSettings
           The complete class containing all RTIS settings for recording and processing.

       Returns
       -------
       package : RTISMeasurement
           The data class holding the measurement of the RTIS device.
    """

    global DEBUG_COUNTER
    global CURRENT_RECORDING_CONFIG
    requestedBytesSize = int((settings.microphoneSamples * settings.nMicrophones) // 8)
    header = 1364413970
    footer = 792823410
    logger.debug("Starting a measurement.")

    # Check if the right microphone configuration is currently is set and if not configure it again
    if settings.configName != CURRENT_RECORDING_CONFIG:
        __configure_rtis_device(settings)

    # Update the global behaviour tracker
    global BEHAVIOUR
    BEHAVIOUR = behaviour
    if BEHAVIOUR:
        __check_and_activate_amplifier()

    # Debugging mode (no real RTIS hardware connected).
    # Uses sample ACTIVE sonar measurement of a 32 microphone array with the 32_v1 layout.
    # Should be used with the default_25_50 recording settings and the 2D_5m_181 processing settings
    # for proper operation.
    if DEBUG == 1:
        logger.warning("Recording using debug mode. Make sure to use open_connection().")
        rawDataClean = np.fromfile(PACKAGE_DIRECTORY + "/simulate.bin", dtype=np.uint32)
        index = DEBUG_COUNTER
        DEBUG_COUNTER = DEBUG_COUNTER + 1
        timestamp = time.time()
        package = RTISMeasurement(ID, timestamp, BEHAVIOUR, index, rawDataClean, configName=settings.configName)
        logger.info("Completed measurement #" + str(package.index) + ".")
    else:
        try:
            if os.name == 'nt':
                serPort = serial.Serial(PORT, 115200, timeout=0.5)
                serPort.reset_input_buffer()
                serPort.reset_output_buffer()
                serPort.write(bytes('!A,' + str(int(BEHAVIOUR is False)) + ',0,0', encoding='utf-8'))
                timestamp = time.time()
                headerReturnValue = serPort.read(4)
                indexReturnValue = serPort.read(4)
                dataBytes = serPort.read(requestedBytesSize)
                footerReturnValue = serPort.read(4)
                if (int.from_bytes(headerReturnValue, "little") == header
                        and int.from_bytes(footerReturnValue, "little") == footer):
                    logger.debug("RTIS Device reports back after starting measurement: " +
                                 str(int.from_bytes(indexReturnValue, "little")) + ".")
                    index = int.from_bytes(indexReturnValue, "little")
                    dataUint32Measurement = np.frombuffer(dataBytes, dtype='uint32')
                    serPort.close()
                    package = RTISMeasurement(ID, timestamp, BEHAVIOUR, index, dataUint32Measurement,
                                              configName=settings.configName)
                    logger.info("Completed measurement #" + str(package.index) + ".")
                else:
                    logger.warning("Disregarding measurement of RTIS Device as header and/or"
                                   " footer were incorrect.")
                    package = RTISMeasurement(ID, timestamp, BEHAVIOUR, None, None, configName=settings.configName)
            else:
                rtisserial.command('!A,' + str(int(BEHAVIOUR is True)) + ',0,0\n', False)
                timestamp = time.time()
                data = rtisserial.getdata(requestedBytesSize + 12)
                if data[0:4].ravel().view("uint32") == header \
                        and data[requestedBytesSize + 8:requestedBytesSize + 12].ravel().view("uint32") == footer:
                    index = data[4:8].ravel().view("uint32")[0]
                    dataUint32Measurement = data[8:requestedBytesSize + 8].ravel().view("uint32")
                    package = RTISMeasurement(ID, timestamp, BEHAVIOUR, index, dataUint32Measurement,
                                              configName=settings.configName)
                    logger.info("Completed measurement #" + str(package.index) + ".")
                else:
                    logger.warning("Disregarding measurement of RTIS Device as header and/or"
                                   " footer were incorrect.")
                    package = RTISMeasurement(ID, timestamp, BEHAVIOUR, None, None, configName=settings.configName)
        except Exception as ex:
            logger.error("Could not measure on RTIS device. Unknown error: " + str(ex))
            raise
    return package


def __configure_rtis_device(settings):
    """The function to configure the connected RTIS Hardware.

       Parameters
       ----------
       settings : RTISSettings
           The complete class containing all RTIS settings for recording and processing.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    global CURRENT_RECORDING_CONFIG

    if not DEBUG:
        if os.name == 'nt':
            pass
        else:
            rtisserial.flush()
    else:
        logger.warning("Configuring a virtual device in debug mode. Make sure to use open_connection().")
    if CURRENT_RECORDING_CONFIG != "":
        logger.info("Switching recording settings from '" + CURRENT_RECORDING_CONFIG
                    + "' to '" + settings.configName + "'.")
    CURRENT_RECORDING_CONFIG = settings.configName
    __set_microphones_samples(settings.microphoneSamples)
    __set_microphones_samplefrequency(settings.microphoneSampleFrequency)
    __set_dac_samplefrequency(settings.dacSampleFrequency)
    __set_dac_samples(settings.dacSamples)
    __set_dac_pulse(settings.dacSignal)
    __set_dac_emissions(settings.callEmissions)
    logger.info("Successfully configured RTIS device for recording.")
    return True


def __unload_all():
    """The function to unload all CUDA workers after all work is completed and unload the used GPU memory.
    """

    global WORKERS
    global CUDA_USED

    logger.debug("Unloading RTISCUDA.")
    try:
        rtiscuda.unloadall()
    except NameError:
        raise RTISCUDAError
    WORKERS.clear()
    CUDA_USED = False


def __unload_one(configName: str):
    """The function to unload one CUDA worker and unload the used GPU memory.

       Parameters
       ----------
       configName: string
           The identity of the settings configuration to be unloaded.
    """

    global WORKERS
    global CUDA_USED

    if configName in WORKERS:
        logger.debug("Unloading RTIS CUDA configuration with ID '" + configName + "'.")
        try:
            rtiscuda.unloadone(configName)
        except NameError:
            raise RTISCUDAError
        WORKERS.remove(configName)
        if len(WORKERS) == 0:
            CUDA_USED = False
    else:
        logger.warning("Could not unload  RTIS CUDA configuration with ID '" + configName + "' as it doesn't exist.")


def __preload(settings):
    """The function to prepare a CUDA worker to process RTIS measurements to process.

       Parameters
       ----------
       settings : RTISSettings
           The complete class containing all RTIS settings for recording and processing.
    """

    global WORKERS
    global CUDA_USED
    if settings.configName not in WORKERS:
        logger.info("Preloading RTIS CUDA for processing with configuration '" + settings.configName + "'.")
        try:
            disableList = np.multiply(np.ones((64,)), 64).astype(dtype=np.uint32)
            disableList[0:len(settings.disableList)] = np.array(settings.disableList)
            if isinstance(settings.pdmFilter, np.floating):
                settings.pdmFilter = np.zeros(shape=(1, 1)).astype(np.float32)
            if isinstance(settings.preFilter, np.floating):
                settings.preFilter = np.zeros(shape=(1, 1)).astype(np.float32)
            if isinstance(settings.lpEsFilter, np.floating):
                settings.lpEsFilter = np.zeros(shape=(1, 1)).astype(np.float32)
            if isinstance(settings.postFilter, np.floating):
                settings.postFilter = np.zeros(shape=(1, 1)).astype(np.float32)
            if isinstance(settings.sigBaseMatchedFilterReal, np.floating):
                settings.sigBaseMatchedFilterReal = np.zeros(shape=(1, 1)).astype(np.float32)
            if isinstance(settings.sigBaseMatchedFilterImag, np.floating):
                settings.sigBaseMatchedFilterImag = np.zeros(shape=(1, 1)).astype(np.float32)
            if isinstance(settings.delayMatrix, np.floating):
                settings.delayMatrix = np.zeros(shape=(1, 1)).astype(np.int32)
            rtiscuda.preload(settings.pdmFilter, settings.preFilter, settings.lpEsFilter, settings.postFilter,
                             settings.sigBaseMatchedFilterReal,
                             settings.sigBaseMatchedFilterImag, settings.delayMatrix,
                             settings.nMicrophones,
                             settings.nDirections, settings.microphoneSamples,
                             settings.pdmSubsampleFactor,
                             settings.beamformingDrop, settings.energyscapeSubsampleFactor,
                             settings.energyscapeSplStart, settings.energyscapeSplStop,
                             settings.meanEnergyRangeMultiplier, settings.maxEnergyRangeThresholdMultiplier,
                             settings.configName,
                             int(settings.pdmEnable), int(settings.preFilterEnable), int(settings.matchedFilterEnable),
                             int(settings.beamformingEnable), int(settings.postFilterEnable),
                             int(settings.enveloppeEnable), int(settings.cleanEnable),
                             disableList.astype(dtype=np.uint32))
            WORKERS.append(settings.configName)
            CUDA_USED = True
        except NameError:
            raise RTISCUDAError
    else:
        logger.warning("Preloading RTIS CUDA for configuration '" + settings.configName
                       + "' failed as it already exists.")


def __process(packageIn, settings=None, configName: str = "", signalOnly: bool = False):
    """The function to process an RTIS measurement using RTIS CUDA.

       Parameters
       ----------
       packageIn : RTISMeasurement
           The data class holding the raw measurement of the RTIS device.

       settings : RTISSettings
           Optionally choose custom RTIS settings for recording and processing.

       configName: string
           The identity of the settings configuration to be used. If not given and no custom settings object is
           provided it will assume only one settings configuration is defined within RTIS Dev.

       signalOnly : bool
           A configuration toggle to disregard the recording settings chosen and only perform PDM filtering to get
           the (microphone) signal data.

       Returns
       -------
       packageOut : RTISMeasurement
           The data class holding the processed measurement of the RTIS device.
    """

    logger.debug("Processing measurement #" + str(packageIn.index) + ".")
    start = time.perf_counter()
    outputData = None
    if signalOnly is False:
        if configName in WORKERS and settings is None:
            if len(SETTINGS) == 0:
                raise RTISSettingsError
            if configName == "":
                if len(SETTINGS) == 1:
                    curSettings = list(SETTINGS.values())[0]
                else:
                    raise RTISMultipleSettingsFoundError
            else:
                if configName in SETTINGS:
                    curSettings = SETTINGS[configName]
                else:
                    raise RTISSettingsByIDNotFoundError

            if not curSettings.processingSettings:
                raise RTISProcessingSettingsError
            inputData = packageIn.rawData
            try:
                outputData = rtiscuda.processing(inputData, int(curSettings.pdmEnable),
                                                 curSettings.processingDataDimensionOne,
                                                 curSettings.processingDataDimensionTwo,
                                                 curSettings.configName)
            except NameError:
                raise RTISCUDAError
        elif configName not in WORKERS and settings is None:
            if len(SETTINGS) == 0:
                raise RTISSettingsError
            if configName == "":
                if len(SETTINGS) == 1:
                    curSettings = list(SETTINGS.values())[0]
                else:
                    raise RTISMultipleSettingsFoundError
            else:
                if configName in SETTINGS:
                    curSettings = SETTINGS[configName]
                else:
                    raise RTISSettingsByIDNotFoundError

            if not curSettings.processingSettings:
                raise RTISProcessingSettingsError
            inputData = packageIn.rawData
            try:
                __preload(curSettings)
                outputData = rtiscuda.processing(inputData, int(curSettings.pdmEnable),
                                                 curSettings.processingDataDimensionOne,
                                                 curSettings.processingDataDimensionTwo,
                                                 curSettings.configName)
                __unload_one(curSettings.configName)
            except NameError:
                raise RTISCUDAError
        elif settings is not None:
            if not settings.processingSettings:
                raise RTISProcessingSettingsError
            try:
                __preload(settings)
                inputData = packageIn.rawData
                outputData = rtiscuda.processing(inputData, int(settings.pdmEnable),
                                                 settings.processingDataDimensionOne,
                                                 settings.processingDataDimensionTwo,
                                                 settings.configName)
                __unload_one(settings.configName)
            except NameError:
                raise RTISCUDAError
    else:
        if settings is None:
            if len(SETTINGS) == 0:
                raise RTISSettingsError

            if len(SETTINGS) == 0:
                raise RTISSettingsError
            if configName == "":
                if len(SETTINGS) == 1:
                    curSettings = list(SETTINGS.values())[0]
                else:
                    raise RTISMultipleSettingsFoundError
            else:
                if configName in SETTINGS:
                    curSettings = SETTINGS[configName]
                else:
                    raise RTISSettingsByIDNotFoundError

            inputData = packageIn.rawData
            settingsSignal = deepcopy(curSettings)
            settingsSignal.configName = settingsSignal.configName + "_signal"
            settingsSignal.set_signal_processing_only()
            try:
                __preload(settingsSignal)
                outputData = rtiscuda.processing(inputData, int(settingsSignal.pdmEnable),
                                                 settingsSignal.processingDataDimensionOne,
                                                 settingsSignal.processingDataDimensionTwo,
                                                 settingsSignal.configName)
                __unload_one(settingsSignal.configName)
            except NameError:
                raise RTISCUDAError
        else:
            inputData = packageIn.rawData
            settingsSignal = deepcopy(settings)
            settingsSignal.configName = settingsSignal.configName + "_signal"
            settingsSignal.set_signal_processing_only()
            try:
                __preload(settingsSignal)
                outputData = rtiscuda.processing(inputData, int(settingsSignal.pdmEnable),
                                                 settingsSignal.processingDataDimensionOne,
                                                 settingsSignal.processingDataDimensionTwo,
                                                 settingsSignal.configName)
                __unload_one(settingsSignal.configName)
            except NameError:
                raise RTISCUDAError
    logger.debug("Processing with RTIS CUDA took %0.4fs", time.perf_counter() - start)
    packageIn.update_processed_data(outputData)
    packageOut = packageIn
    if signalOnly is True:
        logger.info("Processed measurement #" + str(packageOut.index) + " for signal unpacking.")
    else:
        logger.info("Processed measurement #" + str(packageOut.index) + ".")
    return packageOut


def __processing_worker(settings, inputQueue, outputQueue, localLogger):
    """Internal function that retrieves the `RTISMeasurement` on the input queue after which it will
       process these measurements using RTIS CUDA. After this the `RTISMeasurement` objects
       will be put on the output queue. Can be used to make multiple instances of this worker.

       By default, using a `signal.SIGINT` exit (ex. using CTRL+C) should gracefully end the script.

       Use `create_processing_workers(workerCount, inputQueue, outputQueue)` to make an easy to use the function.

       Parameters
       ----------
       settings : RTISSettings
           The RTIS settings for recording and processing.

       inputQueue : multiprocessing.Manager.Queue
           This is the data queue that will be used to receive the recorded RTISMeasurement objects on.

       outputQueue : multiprocessing.Manager.Queue
           This is the data queue that will be used to store the processed RTISMeasurement objects on.

       localLogger : logging.Logger
           The logger used by RTIS Dev at the moment of creating the worker process.

       Examples
       --------
       Create the data queues, set up the worker pool with 4 workers, generate some measurements and afterward parse
       all these measurements by getting them from the output queue.
       Once the work is done, terminate the workers gracefully.

       ```python
       from multiprocessing import Manager

       rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
       rtisdev.set_processing_settings(directions=91)

       manager = Manager()
       inputQueue = manager.Queue()
       outputQueue = manager.Queue()

       workersPool = rtisdev.create_processing_workers(4, inputQueue, outputQueue)

       for measurement_index in range(0, 30):
       _____measurement = rtisdev.get_raw_measurement(configName=config_uuid)
       _____inputQueue.put(measurement)

       for measurement_index in range(0, 30):
       _____measurement = outputQueue.get()

       workersPool.terminate()
       ```
    """

    try:
        disableList = np.multiply(np.ones((64,)), 64).astype(dtype=np.uint32)
        disableList[0:len(settings.disableList)] = np.array(settings.disableList)
        if isinstance(settings.pdmFilter, np.floating):
            settings.pdmFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        if isinstance(settings.preFilter, np.floating):
            settings.preFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        if isinstance(settings.lpEsFilter, np.floating):
            settings.lpEsFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        if isinstance(settings.postFilter, np.floating):
            settings.postFilter = np.zeros(shape=(1, 1)).astype(np.float32)
        if isinstance(settings.sigBaseMatchedFilterReal, np.floating):
            settings.sigBaseMatchedFilterReal = np.zeros(shape=(1, 1)).astype(np.float32)
        if isinstance(settings.sigBaseMatchedFilterImag, np.floating):
            settings.sigBaseMatchedFilterImag = np.zeros(shape=(1, 1)).astype(np.float32)
        if isinstance(settings.delayMatrix, np.floating):
            settings.delayMatrix = np.zeros(shape=(1, 1)).astype(np.int32)
        rtiscuda.preload(settings.pdmFilter, settings.preFilter, settings.lpEsFilter, settings.postFilter,
                         settings.sigBaseMatchedFilterReal,
                         settings.sigBaseMatchedFilterImag, settings.delayMatrix,
                         settings.nMicrophones,
                         settings.nDirections, settings.microphoneSamples,
                         settings.pdmSubsampleFactor,
                         settings.beamformingDrop, settings.energyscapeSubsampleFactor,
                         settings.energyscapeSplStart, settings.energyscapeSplStop,
                         settings.meanEnergyRangeMultiplier, settings.maxEnergyRangeThresholdMultiplier,
                         settings.configName,
                         int(settings.pdmEnable), int(settings.preFilterEnable), int(settings.matchedFilterEnable),
                         int(settings.beamformingEnable), int(settings.postFilterEnable),
                         int(settings.enveloppeEnable), int(settings.cleanEnable),
                         disableList.astype(dtype=np.uint32))
        localLogger.info("Started a processing worker.")

        while True:
            packageIn = inputQueue.get()
            start = time.perf_counter()
            inputData = packageIn.rawData
            outputData = rtiscuda.processing(inputData, int(settings.pdmEnable),
                                             settings.processingDataDimensionOne,
                                             settings.processingDataDimensionTwo,
                                             settings.configName)
            localLogger.debug("Processing with RTIS CUDA took %0.4fs", time.perf_counter() - start)
            packageIn.update_processed_data(outputData)
            packageOut = packageIn
            outputQueue.put(packageOut)
            localLogger.debug("Processed measurement #" + str(packageOut.index) + ".")
    except NameError:
        raise RTISCUDAError
    except KeyboardInterrupt:
        rtiscuda.unloadone(settings.configName)


@atexit.register
def __close_connection_on_exit():
    """The internal function to close the connection to the RTIS device.
       This is called automatically on detection of closing the program that uses RTIS Dev.
       This will also unload all RTIS CUDA workers.

    """

    try:
        __unload_all()
    except RTISCUDAError:
        pass
    if not DEBUG:
        try:
            if os.name == 'nt':
                pass
            else:
                rtisserial.close()
            logger.debug("RTIS hardware device connection ended.")
        except ConnectionRefusedError:
            pass
        except Exception as ex:
            logger.warning("Could not close connection to RTIS Device gracefully:" + str(ex))


def __make_valid_config_name(configName: str) -> str:
    """The internal function to parse a given configName and make sure it is valid.
       It must be character vector of alphanumerics (A–Z, a–z, 0–9) and underscores,
       such that the first character is a letter and the length of the character vector is less than or equal to 63.
       This method deletes any whitespace characters before replacing any characters
       that are not alphanumerics or underscores.

       Parameters
       ----------
       configName : String
           Those chosen string to identify these settings with.

       Returns
       -------
       configName : String
           The chosen string but possibly altered to stick to the naming conventions for valid configuration names.
    """

    containsError = False
    errorString = ""
    if configName[0].isdigit():
        containsError = True
        configName = "c" + configName
        errorString += "The given config name started with a digit which is invalid. "
    if ' ' in configName:
        containsError = True
        configName = configName.replace(" ", "")
        errorString += "The given config name contained white spaces which is invalid. "
    if ' ' in configName:
        containsError = True
        configName = configName.replace(" ", "")
        errorString += "The given config name contained white spaces which is invalid. "
    if len(configName) > 63:
        containsError = True
        configName = (configName[:63])
        errorString += "The given config name was longer than the maximum length of 63 characters. "
    if not re.match("^[A-Za-z0-9_]*$", configName):
        containsError = True
        configName = re.sub('[^0-9a-zA-Z_]+', "", configName)
        errorString += ("The given config name contained illegal characters. It can only contain "
                        "alphanumerics (A–Z, a–z, 0–9) and underscores. ")
    if containsError:
        logger.warning(errorString + "The config name has been altered to '" + configName + "'.")
    return configName


def __generate_valid_processing_settings(packageDirectory, microphoneLayout, mode, directions, minRange, maxRange,
                                         esSubFactor, microphoneSampleFrequency, azimuthLowLimit, azimuthHighLimit,
                                         elevationLowLimit, elevationHighLimit):
    """The internal function to generate valid processing settings like delay, range and direction matrices.

       Parameters
       ----------
       packageDirectory : String
           The location of the RTIS Dev package to correctly find the microphone setting files.

       microphoneLayout : String (default = eRTIS_v3D1)
           Identifier of the microphone layout used for this configuration.

       mode : int
           Defines if using 3D or 2D processing. If set to 1 a 2D horizontal plane layout will be generated.
           When set to 0 a 3D equal distance layout will be generated
           for the frontal hemisphere of the sensor.

       directions : int
           Defines how many directions the layout should generate.

       minRange : float
           The minimum distance in meters of the energyscape to generate.

       maxRange : float
           The maximum distance in meters of the energyscape to generate.

       esSubFactor : int
           The subsampling factor of the PDM demodulation.

       microphoneSampleFrequency : int
           The microphone sample frequency (without subsampling of PDM).
           The frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible) depending on the wanted mode.

       azimuthLowLimit : float
           The lower limit of the azimuth in degrees of the directions to generate. Has to be between -90 and 90.

       azimuthHighLimit : float
           The higher limit of the azimuth in degrees of the directions to generate. Has to be between -90 and 90.

       elevationLowLimit : float
           The lower limit of the elevation in degrees of the directions to generate. Has to be between -90 and 90.

       elevationHighLimit : float
           The higher limit of the elevation in degrees of the directions to generate. Has to be between -90 and 90.

       Returns
       -------
       delayMatrix : Numpy ndarray
           The array holding the delay matrix used for beamforming. (shape: nMicrophones x nDirections)

       directions : Numpy ndarray
           The array holding the directions in radians used of the energyscape.
           First column is azimuth, second elevation. (shape: nDirections x 2)

       ranges : Numpy ndarray
           The array holding the range values in meters of the energyscape. (shape: nranges x 1)
    """

    if mode != 1 and mode != 0:
        logger.error("The mode has to be 0 (3D) or 1(2D) and cannot be another value.")
        raise ValueError("The mode has to be 0 (3D) or 1(2D) and cannot be another value.")

    if directions <= 1:
        logger.error("The amount of directions has to be higher than 1.")
        raise ValueError("The amount of directions has to be higher than 1.")

    if minRange < 0:
        logger.error("The minimum range has to be higher than 0.")
        raise ValueError("The minimum range has to be higher than 0.")

    if maxRange < minRange:
        logger.error("The maximum range has to be higher than the minimum range.")
        raise ValueError("The maximum range has to be higher the minimum range.")

    if maxRange < minRange:
        logger.error("The maximum range has to be higher than the minimum range.")
        raise ValueError("The maximum range has to be higher the minimum range.")

    if microphoneSampleFrequency != 4500000 and microphoneSampleFrequency != 1125000:
        logger.error(
            "Could not set microphone sample frequency on RTIS device to " + str(microphoneSampleFrequency) +
            ": The microphone sample frequency must be 4.5 MHz (ultrasound) or 1.125 MHz (audible).")
        raise ValueError("Could not set microphone sample frequency on RTIS device to "
                         + str(microphoneSampleFrequency) + ": The microphone sample frequency must be"
                         + " 4.5 MHz (ultrasound) or 1.125 MHz (audible).")

    if azimuthLowLimit < -90 or azimuthLowLimit > 90:
        logger.error("Could not set the lower azimuth direction limit to " + str(azimuthLowLimit)
                     + " degrees : It has to be between -90 degrees and 90 degrees.")
        raise ValueError("Could not set the lower azimuth direction limit to " + str(azimuthLowLimit)
                         + " degrees : It has to be between -90 degrees and 90 degrees.")

    if azimuthHighLimit < -90 or azimuthHighLimit > 90:
        logger.error("Could not set the higher azimuth direction limit to " + str(azimuthHighLimit)
                     + " degrees : It has to be between -90 degrees and 90 degrees.")
        raise ValueError("Could not set the higher azimuth direction limit to " + str(azimuthHighLimit)
                         + " degrees : It has to be between -90 degrees and 90 degrees.")

    if elevationLowLimit < -90 or elevationLowLimit > 90:
        logger.error("Could not set the lower elevation direction limit to " + str(elevationLowLimit)
                     + " degrees : It has to be between -90 degrees and 90 degrees.")
        raise ValueError("Could not set the lower elevation direction limit to " + str(elevationLowLimit)
                         + " degrees : It has to be between -90 degrees and 90 degrees.")

    if elevationHighLimit < -90 or elevationHighLimit > 90:
        logger.error("Could not set the higher elevation direction limit to " + str(elevationHighLimit)
                     + " degrees : It has to be between -90 degrees and 90 degrees.")
        raise ValueError("Could not set the higher elevation direction limit to " + str(elevationHighLimit)
                         + " degrees : It has to be between -90 degrees and 90 degrees.")

    try:
        scipy.io.loadmat(packageDirectory + "/config/microphoneLayouts/" + microphoneLayout + "/mic_coordinates.mat")
    except FileNotFoundError:
        logger.error("Could not find the microphone layout file for " + microphoneLayout
                     + ". Use get_microphone_layout_list() to get a list of available microphone layouts.")
        raise FileNotFoundError("Could not find the microphone layout file for " + microphoneLayout
                                + ". Use get_microphone_layout_list() to get a list of available microphone layouts.")

    delaymatrix, directions, ranges = generate_processing_settings(packageDirectory, microphoneLayout,
                                                                   mode, directions, minRange, maxRange,
                                                                   esSubFactor, microphoneSampleFrequency,
                                                                   azimuthLowLimit, azimuthHighLimit,
                                                                   elevationLowLimit, elevationHighLimit)
    return delaymatrix, directions, ranges


def __return_and_verify_all_settings(sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                                     microphoneSamples, callDuration, callMinimumFrequency,
                                     callMaximumFrequency, callEmissions, delayMatrix, directions, ranges, preFilter,
                                     postFilter, meanEnergyRangeMultiplier, maxEnergyRangeThresholdMultiplier,
                                     pdmEnable, preFilterEnable, matchedFilterEnable, beamformingEnable,
                                     postFilterEnable, enveloppeEnable, cleanEnable, preloadToggle, microphoneLayout,
                                     configName):
    """The internal function to verify the chosen recording and processing settings, create the settings object and
       return it without applying it.

       Parameters
       ----------
       sigADC : Numpy ndarray
           The array holding the ADC signal call. (shape: dacSamples x 1)

       sigDAC : Numpy ndarray
           The array holding the DAC signal call, always the same as sigDAC. (shape: dacSamples x 1)

       microphoneSampleFrequency : int
           The microphone sample frequency (without subsampling of PDM).
           The frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible) depending on the wanted mode.

       callSampleFrequency : int
           The chosen sample frequency of the call. Must be larger than 160 KHz and smaller than 2 MHz.

       microphoneSamples : int
           The amount of microphone samples. Must be dividable by 32768.

       callDuration : float
           The duration in milliseconds of the call.

       callMinimumFrequency: int
           The minimum frequency in Hz of the call sweep used for generating the pulse.

       callMaximumFrequency: int
           The maximum frequency in Hz of the call sweep used for generating the pulse.

       callEmissions : int
           The amount of times the pulse should be emitted during one measurement.

       delayMatrix : Numpy ndarray
           The array holding the delay matrix used for beamforming. (shape: nMicrophones x nDirections)

       directions : Numpy ndarray
           The array holding the directions in radians used of the energyscape.
           First column is azimuth, second elevation. (shape: nDirections x 2)

       ranges : Numpy ndarray
           The array holding the range values in meters of the energyscape. (shape: nranges x 1)

       preFilter : Numpy ndarray
           The array holding the optional pre-filter created with scipy firwin. (shape: nprefilter x 1)

       postFilter : Numpy ndarray
           The array holding the optional post-beamforming filter created with scipy firwin. (shape: npostfilter x 1)

       meanEnergyRangeMultiplier : float
           The multiplier weight used to calculate the mean energy for each range during the cleaning step.

       maxEnergyRangeThresholdMultiplier : float
           The multiplier weight used to threshold the energy based on the maximum
           for each range during the cleaning step.

       pdmEnable : bool
           Toggle for PDM filtering part of the RTIS processing pipeline using RTIS CUDA.

       preFilterEnable : bool
           Toggle for the optional pre-filter part of the RTIS processing pipeline using RTIS CUDA.

       matchedFilterEnable : bool
           Toggle for the optional matched filter part of the RTIS processing pipeline using RTIS CUDA.

       beamformingEnable : bool
           Toggle for beamforming part of the RTIS processing pipeline using RTIS CUDA.

       postFilterEnable : bool
           Toggle for the optional post-beamforming filter part of the RTIS processing pipeline using RTIS CUDA.

       enveloppeEnable : bool
           Toggle for enveloppe part of the RTIS processing pipeline using RTIS CUDA.

       cleanEnable : bool
           Toggle for cleaning part of the RTIS processing pipeline using RTIS CUDA.

       preloadToggle : bool
           Toggle for using RTIS CUDA preloading.

       microphoneLayout : String
           Identifier of the microphone layout used for this configuration.

       configName : String
           String to identify these settings with. If set to empty, will default to a unique UUID.

       Returns
       -------
       settings : RTISSettings
           The complete class containing all RTIS settings for recording and processing. Returns 'None' or will
           raise an exception on failure.
    """

    firmwareVersion = __get_firmware_version()

    if np.mod(microphoneSamples, 32768) != 0:
        logger.error("Could not set microphone samples on RTIS device to " + str(microphoneSamples) +
                     ": The amount of microphone samples must be dividable by 32768.")
        raise ValueError("Could not set microphone samples on RTIS device to " + str(microphoneSamples) +
                         ": The amount of microphone samples must be dividable by 32768.")
    if microphoneSampleFrequency != 4500000 and microphoneSampleFrequency != 1125000:
        logger.error("Could not set microphone sample frequency on RTIS device to " + str(microphoneSampleFrequency) +
                     ": The microphone sample frequency must be 4.5 MHz (ultrasound) or 1.125 MHz (audible).")
        raise ValueError("Could not set microphone sample frequency on RTIS device to "
                         + str(microphoneSampleFrequency) + ": The microphone sample frequency must be"
                                                            " 4.5 MHz (ultrasound) or 1.125 MHz (audible).")
    if microphoneSamples > 16777216 and microphoneSampleFrequency == 4500000:
        logger.error("Could not set microphone samples on RTIS device to " + str(microphoneSamples)
                     + ": When in ultrasonic mode the maximum amount of microphone samples is 16777216.")
        raise ValueError("Could not set microphone samples on RTIS device to " + str(microphoneSamples)
                         + ": When in ultrasonic mode the maximum amount of microphone samples is 16777216.")
    if callSampleFrequency < 160000 or callSampleFrequency > 2000000:
        logger.error("Could not set DAC sample frequency on RTIS device to " + str(callSampleFrequency) +
                     ": The DAC sample frequency must be larger than 160 KHz and smaller than 2 MHz.")
        raise ValueError("Could not set DAC sample frequency on RTIS device to " + str(callSampleFrequency) +
                         ": The DAC sample frequency must be larger than 160 KHz and smaller than 2 MHz.")
    if sigADC.shape[0] < 64 or sigADC.shape[0] > 65535:
        logger.error("Could not set DAC samples on RTIS device to " + str(sigADC.shape[0])
                     + ":The amount of DAC samples must be larger than 64 and smaller than 65535.")
        raise ValueError("Could not set DAC samples on RTIS device to " + str(sigADC.shape[0])
                         + ":The amount of DAC samples must be larger than 64 and smaller than 65535.")
    if preFilterEnable:
        if not isinstance(preFilter, np.ndarray):
            logger.error("Could not use the given pre-filter as it is not a Numpy ndarray.")
            raise ValueError("Could not use the given pre-filter as it is not a Numpy ndarray.")
    if postFilterEnable:
        if not isinstance(postFilter, np.ndarray):
            logger.error("Could not use the given post-beamforming filter as it is not a Numpy ndarray.")
            raise ValueError("Could not use the given post-beamforming filter as it is not a Numpy ndarray.")

    if configName == "":
        configName = __make_valid_config_name("c" + uuid.uuid4().hex)
    else:
        configName = __make_valid_config_name(configName)

    meanEnergyRangeMultiplier = np.float32(meanEnergyRangeMultiplier)
    maxEnergyRangeThresholdMultiplier = np.float32(maxEnergyRangeThresholdMultiplier)

    settings = RTISSettings(firmwareVersion, configName)
    settings.set_recording_settings(sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                                    microphoneSamples, callDuration, callMinimumFrequency,
                                    callMaximumFrequency,
                                    callEmissions)

    energyscapeSplStart = (int(round(ranges[0] * 2 / 343 * (microphoneSampleFrequency / 10) /
                                     settings.energyscapeSubsampleFactor)))
    energyscapeSplStop = (int(round(ranges[-1] * 2 / 343 * (microphoneSampleFrequency / 10) /
                                    settings.energyscapeSubsampleFactor)))
    if energyscapeSplStart > (settings.nspsls - settings.beamformingDrop) / settings.energyscapeSubsampleFactor:
        logger.error("The chosen minimum range is not possible to be retrieved with the chosen amount of samples."
                     "Please change your minimum range or change the microphone samples of the recording settings.")
        raise ValueError("The chosen minimum range is not possible to be retrieved with the chosen amount of samples."
                         "Please change your minimum range or change the microphone samples of the recording settings.")
    if energyscapeSplStop > (settings.nspsls - settings.beamformingDrop) / settings.energyscapeSubsampleFactor:
        logger.error("The chosen maximum range is not possible to be retrieved with the chosen amount of samples."
                     "Please change your maximum range or change the microphone samples of the recording settings.")
        raise ValueError("The chosen maximum range is not possible to be retrieved with the chosen amount of samples."
                         "Please change your maximum range or change the microphone samples of the recording settings.")

    disableList = get_disabled_microphone_list(PACKAGE_DIRECTORY, microphoneLayout)
    settings.set_processing_settings(pdmEnable, preFilterEnable, matchedFilterEnable, beamformingEnable,
                                     postFilterEnable, enveloppeEnable, cleanEnable, preloadToggle, delayMatrix,
                                     directions, ranges, microphoneLayout, disableList, postFilter, preFilter,
                                     meanEnergyRangeMultiplier, maxEnergyRangeThresholdMultiplier)
    return settings


def __set_and_verify_recording_settings(sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                                        microphoneSamples, callDuration, callMinimumFrequency,
                                        callMaximumFrequency, callEmissions, configName, applyToDevice=True):
    """The internal function to verify the chosen recording settings, create or modify the settings object and
       apply the settings to the RTIS device.

       Parameters
       ----------
       sigADC : Numpy ndarray
           The array holding the ADC signal call. (shape: dacSamples x 1)

       sigDAC : Numpy ndarray
           The array holding the DAC signal call, always the same as sigDAC. (shape: dacSamples x 1)

       microphoneSampleFrequency : int
           The microphone sample frequency (without subsampling of PDM).
           The frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible) depending on the wanted mode.

       callSampleFrequency : int
           The chosen sample frequency of the call. Must be larger than 160 KHz and smaller than 2 MHz.

       microphoneSamples : int
           The amount of microphone samples. Must be dividable by 32768.

       callDuration : float
           The duration in milliseconds of the call.

       callMinimumFrequency: int
           The minimum frequency in Hz of the call sweep used for generating the pulse.

       callMaximumFrequency: int
           The maximum frequency in Hz of the call sweep used for generating the pulse.

       callEmissions : int
           The amount of times the pulse should be emitted during one measurement.

       configName : String
           String to identify these settings with. If set to empty, will default to a unique UUID.

       applyToDevice : bool (default = True)
           A configuration toggle to optionally disable applying the recording settings to the RTIS Device.

       Returns
       -------
       configName : string
           returns the given configuration name or generated UUID on successful completion
           or will raise an exception on failure.
    """

    global SETTINGS
    firmwareVersion = __get_firmware_version()

    if np.mod(microphoneSamples, 32768) != 0:
        logger.error("Could not set microphone samples on RTIS device to " + str(microphoneSamples) +
                     ": The amount of microphone samples must be dividable by 32768.")
        raise ValueError("Could not set microphone samples on RTIS device to " + str(microphoneSamples) +
                         ": The amount of microphone samples must be dividable by 32768.")
    if microphoneSampleFrequency != 4500000 and microphoneSampleFrequency != 1125000:
        logger.error("Could not set microphone sample frequency on RTIS device to " + str(microphoneSampleFrequency) +
                     ": The microphone sample frequency must be 4.5 MHz (ultrasound) or 1.125 MHz (audible).")
        raise ValueError("Could not set microphone sample frequency on RTIS device to "
                         + str(microphoneSampleFrequency) + ": The microphone sample frequency must be"
                         + " 4.5 MHz (ultrasound) or 1.125 MHz (audible).")
    if microphoneSamples > 16777216 and microphoneSampleFrequency == 4500000:
        logger.error("Could not set microphone samples on RTIS device to " + str(microphoneSamples)
                     + ": When in ultrasonic mode the maximum amount of microphone samples is 16777216.")
        raise ValueError("Could not set microphone samples on RTIS device to " + str(microphoneSamples)
                         + ": When in ultrasonic mode the maximum amount of microphone samples is 16777216.")
    if callSampleFrequency < 160000 or callSampleFrequency > 2000000:
        logger.error("Could not set DAC sample frequency on RTIS device to " + str(callSampleFrequency)
                     + ": The DAC sample frequency must be larger than 160 KHz and smaller than 2 MHz.")
        raise ValueError("Could not set DAC sample frequency on RTIS device to " + str(callSampleFrequency)
                         + ": The DAC sample frequency must be larger than 160 KHz and smaller than 2 MHz.")
    if sigADC.shape[0] < 64 or sigADC.shape[0] > 65535:
        logger.error("Could not set DAC samples on RTIS device to " + str(sigADC.shape[0])
                     + ":The amount of DAC samples must be larger than 64 and smaller than 65535.")
        raise ValueError("Could not set DAC samples on RTIS device to " + str(sigADC.shape[0])
                         + ":The amount of DAC samples must be larger than 64 and smaller than 65535.")

    if configName == "":
        configName = __make_valid_config_name("c" + uuid.uuid4().hex)
        logger.warning("No configuration ID given so using generated UUID '" + configName + "'.")
    else:
        configName = __make_valid_config_name(configName)

    if configName in SETTINGS:
        logger.warning("Settings with this configuration name already existed so they will be overwritten.")
        if SETTINGS[configName].processingSettings:
            logger.warning(
                "Setting a new recording configuration also means removing all processing settings. Make sure"
                " to also set a updated processing configuration.")
        clear_current_settings(configName)

    SETTINGS[configName] = RTISSettings(firmwareVersion, configName)

    SETTINGS[configName].set_recording_settings(sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                                                microphoneSamples, callDuration, callMinimumFrequency,
                                                callMaximumFrequency,
                                                callEmissions)
    if applyToDevice:
        __configure_rtis_device(SETTINGS[configName])
        return configName
    else:
        return configName


def __load_recording_settings_from_json(recordingConfig):
    """The internal function to parse and load a JSON config file for recording settings.

       Parameters
       ----------
       recordingConfig : dict
           The JSON dictionary holding the recording settings.

       Returns
       -------
       response : Tuple[Numpy ndarray, Numpy ndarray, int, int, int, float, int, int, int]
           Tuple holding sigADC (Numpy ndarray, The array holding the ADC signal call (shape: dacSamples x 1)),
           sigDAC (Numpy ndarray, The array holding the DAC signal call, always the same as sigDAC
           (shape: dacSamples x 1)), microphoneSampleFrequency (int, The microphone sample frequency
           (without subsampling of PDM). The frequency must be 4.5 MHz(ultrasound) or
           1.125 MHz(audible) depending on the wanted mode), callSampleFrequency (int, The chosen sample frequency
           of the call. Must be larger than 160 KHz and smaller than 2 MHz), microphoneSamples (int,
           The amount of microphone samples. Must be dividable by 32768), callDuration (float, The duration in
           milliseconds of the call), callMinimumFrequency (int, The minimum frequency in Hz of the call
           sweep used for generating the pulse), callMaximumFrequency (int, The maximum frequency in Hz
           of the call sweep used for generating the pulse) and callEmissions (int, The amount of times the pulse should
           be emitted during one measurement).
    """

    if 'callCustom' in recordingConfig.keys():
        if ('callDuration' in recordingConfig.keys() or 'callMinimumFrequency' in recordingConfig.keys() or
                'callMaximumFrequency' in recordingConfig.keys()):
            raise RTISDuplicateCallError
        if recordingConfig["callCustom"].startswith("premade"):
            sigADC = genfromtxt(PACKAGE_DIRECTORY + '/config/premadeSettings/recording/' +
                                recordingConfig["callCustom"].replace("premade/", ""))
            sigDAC = sigADC

            callDuration = None
            callMaximumFrequency = None
            callMinimumFrequency = None
        else:
            if os.path.isfile(recordingConfig["callCustom"]):
                sigADC = genfromtxt(recordingConfig["callCustom"], delimiter=',')
                sigDAC = sigADC

                callDuration = None
                callMaximumFrequency = None
                callMinimumFrequency = None

            else:
                logger.error("Could not load custom call file. Please make sure to use correct path and filename.")
                raise FileNotFoundError("Could not load custom call file. "
                                        + "Please make sure to use correct path and filename.")
    else:
        callDuration = 2.5
        callSampleFrequency = 450000
        callMinimumFrequency = 25000
        callMaximumFrequency = 50000
        if 'callDuration' in recordingConfig.keys():
            callDuration = recordingConfig["callDuration"]
        if 'callSampleFrequency' in recordingConfig.keys():
            callSampleFrequency = recordingConfig["callSampleFrequency"]
        if 'callMinimumFrequency' in recordingConfig.keys():
            callMinimumFrequency = recordingConfig["callMinimumFrequency"]
        if 'callMaximumFrequency' in recordingConfig.keys():
            callMaximumFrequency = recordingConfig["callMaximumFrequency"]
        sigADC, sigDAC = generate_recording_settings(callSampleFrequency,
                                                     callDuration,
                                                     callMinimumFrequency,
                                                     callMaximumFrequency)

    microphoneSamples = 163840
    microphoneSampleFrequency = 4500000
    callEmissions = 1
    callSampleFrequency = 450000
    if 'microphoneSamples' in recordingConfig.keys():
        microphoneSamples = recordingConfig["microphoneSamples"]
    if 'microphoneSampleFrequency' in recordingConfig.keys():
        microphoneSampleFrequency = recordingConfig["microphoneSampleFrequency"]
    if 'callEmissions' in recordingConfig.keys():
        callEmissions = recordingConfig["callEmissions"]
    if 'callSampleFrequency' in recordingConfig.keys():
        callSampleFrequency = recordingConfig["callSampleFrequency"]

    return (sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
            microphoneSamples, callDuration, callMinimumFrequency, callMaximumFrequency, callEmissions)


def __set_and_verify_processing_settings(delayMatrix, directions, ranges, postFilter, preFilter,
                                         meanEnergyRangeMultiplier, maxEnergyRangeThresholdMultiplier, pdmEnable,
                                         preFilterEnable, matchedFilterEnable, beamformingEnable, postFilterEnable,
                                         enveloppeEnable, cleanEnable, preloadToggle, microphoneLayout, disableList,
                                         configName):
    """The internal function to verify the chosen recording settings, create or modify the settings object and
       apply the settings to the RTIS device.

       Parameters
       ----------
       delayMatrix : Numpy ndarray
           The array holding the delay matrix used for beamforming. (shape: nMicrophones x nDirections)

       directions : Numpy ndarray
           The array holding the directions in radians used of the energyscape.
           First column is azimuth, second elevation. (shape: nDirections x 2)

       ranges : Numpy ndarray
           The array holding the range values in meters of the energyscape. (shape: nranges x 1)

       postFilter : Numpy ndarray
           The array holding the optional post-beamforming filter created with scipy firwin. (shape: npostfilter x 1)

       preFilter : Numpy ndarray
           The array holding the optional pre-filter created with scipy firwin. (shape: nprefilter x 1)

       meanEnergyRangeMultiplier : float
           The multiplier weight used to calculate the mean energy for each range during the cleaning step.

       maxEnergyRangeThresholdMultiplier : float
           The multiplier weight used to threshold the energy based on the maximum
           for each range during the cleaning step.

       pdmEnable : bool
           Toggle for PDM filtering part of the RTIS processing pipeline using RTIS CUDA.

       preFilterEnable : bool
           Toggle for the optional pre-filter part of the RTIS processing pipeline using RTIS CUDA.

       matchedFilterEnable : bool
           Toggle for the optional matched filter part of the RTIS processing pipeline using RTIS CUDA.

       beamformingEnable : bool
           Toggle for beamforming part of the RTIS processing pipeline using RTIS CUDA.

       postFilterEnable : bool
           Toggle for the optional post-beamforming filter part of the RTIS processing pipeline using RTIS CUDA.

       enveloppeEnable : bool
           Toggle for enveloppe part of the RTIS processing pipeline using RTIS CUDA.

       cleanEnable : bool
           Toggle for cleaning part of the RTIS processing pipeline using RTIS CUDA.

       preloadToggle : bool
           Toggle for using RTIS CUDA preloading.

       microphoneLayout : String
           Identifier of the microphone layout used for this configuration.

       disableList : list[int]
           List of all microphone indexes that should have their data nullified as these microphones aren't used
           in the chosen microphone layout.

       configName : String
           String to identify these settings with.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    global SETTINGS

    if not SETTINGS:
        raise RTISSettingsError
    if configName not in SETTINGS:
        raise RTISSettingsByIDNotFoundError

    microphoneSampleFrequency = SETTINGS[configName].microphoneSampleFrequency

    energyscapeSplStart = (int(round(ranges[0] * 2 / 343 * (microphoneSampleFrequency / 10)
                                     / SETTINGS[configName].energyscapeSubsampleFactor)))
    energyscapeSplStop = (int(round(ranges[-1] * 2 / 343 * (microphoneSampleFrequency / 10)
                                    / SETTINGS[configName].energyscapeSubsampleFactor)))
    if energyscapeSplStart > (SETTINGS[configName].nspsls - SETTINGS[configName].beamformingDrop) \
            / SETTINGS[configName].energyscapeSubsampleFactor:
        logger.error("The chosen minimum range is not possible to be retrieved with the chosen amount of samples."
                     "Please change your minimum range or change the microphone samples of the recording settings.")
        raise ValueError("The chosen minimum range is not possible to be retrieved with the chosen amount of samples."
                         "Please change your minimum range or change the microphone samples of the recording settings.")
    if energyscapeSplStop > (SETTINGS[configName].nspsls - SETTINGS[configName].beamformingDrop) \
            / SETTINGS[configName].energyscapeSubsampleFactor:
        logger.error("The chosen maximum range is not possible to be retrieved with the chosen amount of samples."
                     "Please change your maximum range or change the microphone samples of the recording settings.")
        raise ValueError("The chosen maximum range is not possible to be retrieved with the chosen amount of samples."
                         "Please change your maximum range or change the microphone samples of the recording settings.")
    if SETTINGS[configName].microphoneSampleFrequency != microphoneSampleFrequency:
        logger.error("the microphone sample frequency of the recording settings ("
                     + str(SETTINGS[configName].microphoneSampleFrequency)
                     + ") does not match that of the processing " +
                     "settings that are given (" + str(microphoneSampleFrequency) + ").")
        raise ValueError("the microphone sample frequency of the recording settings ("
                         + str(SETTINGS[configName].microphoneSampleFrequency)
                         + ") does not match that of the processing " +
                         "settings that are given (" + str(microphoneSampleFrequency) + ").")
    if preFilterEnable:
        if not isinstance(preFilter, np.ndarray):
            logger.error("Could not use the given pre-filter as it is not a Numpy ndarray.")
            raise ValueError("Could not use the given pre-filter as it is not a Numpy ndarray.")
    if postFilterEnable:
        if not isinstance(postFilter, np.ndarray):
            logger.error("Could not use the given post-beamforming filter as it is not a Numpy ndarray.")
            raise ValueError("Could not use the given post-beamforming filter as it is not a Numpy ndarray.")

    if SETTINGS[configName].processingSettings:
        logger.warning("Processing settings with this configuration name already existed so will be overwritten.")
        __unload_one(configName)

    meanEnergyRangeMultiplier = np.float32(meanEnergyRangeMultiplier)
    maxEnergyRangeThresholdMultiplier = np.float32(maxEnergyRangeThresholdMultiplier)

    SETTINGS[configName].set_processing_settings(pdmEnable, preFilterEnable, matchedFilterEnable, beamformingEnable,
                                                 postFilterEnable, enveloppeEnable, cleanEnable, preloadToggle,
                                                 delayMatrix, directions, ranges, microphoneLayout, disableList,
                                                 postFilter, preFilter, meanEnergyRangeMultiplier,
                                                 maxEnergyRangeThresholdMultiplier)
    if preloadToggle:
        __preload(SETTINGS[configName])
    logger.info("Successfully configured RTIS device for processing.")
    return True


def __load_processing_settings_from_json(processingConfig, microphoneSampleFrequency):
    """The internal function to parse and load a JSON config file for processing settings.

       Parameters
       ----------
       processingConfig : dict
           The JSON dictionary holding the processing settings.

       microphoneSampleFrequency : int
           The microphone sample frequency (without subsampling of PDM).
           The frequency must be 4.5 MHz(ultrasound) or 1.125 MHz(audible) depending on the wanted mode.

       Returns
       -------
       Response : Tuple[Numpy ndarray, Numpy ndarray, Numpy ndarray, String]
           Tuple holding the delayMatrix (Numpy ndarray, The array holding the delay matrix used for beamforming
           (shape: nMicrophones x nDirections)), directions (numpy ndarray, The array holding the directions
           in radians used of the energyscape. First column is azimuth, second elevation (shape: nDirections x 2)),
           ranges (Numpy ndarray, The array holding the range values in meters of the energyscape (shape: nranges x 1)),
           and microphoneLayout (String, Identifier of the microphone layout used for this configuration).
    """

    microphoneLayout = "eRTIS_v3D1"

    if 'microphoneLayout' in processingConfig.keys():
        microphoneLayout = processingConfig["microphoneLayout"]

    disableList = get_disabled_microphone_list(PACKAGE_DIRECTORY, microphoneLayout)

    if ('directionsCustom' in processingConfig.keys() or 'delayMatrixCustom' in processingConfig.keys() or
            'rangesCustom' in processingConfig.keys()):
        if ('directionsCustom' not in processingConfig.keys() or 'delayMatrixCustom' not in processingConfig.keys() or
                'rangesCustom' not in processingConfig.keys()):
            logger.error("You defined custom directions, ranges or delaymatrix but did not provide the other files.")
            raise ValueError("You defined custom directions, ranges or delaymatrix but did not "
                             + "provide the other files.")
        else:
            if processingConfig["directionsCustom"].startswith("premade"):
                delaymatrix = (
                    genfromtxt(PACKAGE_DIRECTORY + '/config/premadeSettings/processing/' +
                               processingConfig["delayMatrixCustom"].replace("premade/", ""),
                               delimiter=',', dtype=np.int32)).copy()
                directions = (genfromtxt(PACKAGE_DIRECTORY + '/config/premadeSettings/processing/' +
                                         processingConfig["directionsCustom"].replace("premade/", ""),
                                         delimiter=',')).copy()
                ranges = genfromtxt(PACKAGE_DIRECTORY + '/config/premadeSettings/processing/' +
                                    processingConfig["rangesCustom"].replace("premade/", ""), delimiter=',')
            else:
                if (os.path.isfile(processingConfig["directionsCustom"])
                        and os.path.isfile(processingConfig["delayMatrixCustom"])
                        and os.path.isfile(processingConfig["rangesCustom"])):

                    delaymatrix = (
                        genfromtxt(processingConfig["delayMatrixCustom"], delimiter=',',
                                   dtype=np.int32)).copy()
                    directions = (genfromtxt(processingConfig["directionsCustom"], delimiter=',')).copy()
                    ranges = genfromtxt(processingConfig["rangesCustom"], delimiter=',')
                else:
                    logger.error("Could not load custom processing files file. " +
                                 "Please make sure to use correct paths and filenames.")
                    raise FileNotFoundError("Could not load custom processing files file. " +
                                            "Please make sure to use correct paths and filenames.")
    else:
        minRange = 0.5
        maxRange = 5
        directions = 181
        mode = 1
        azimuthLowLimit = -90
        azimuthHighLimit = 90
        elevationLowLimit = -90
        elevationHighLimit = 90
        if 'minRange' in processingConfig.keys():
            minRange = processingConfig["minRange"]
        if 'maxRange' in processingConfig.keys():
            maxRange = processingConfig["maxRange"]
        if 'directions' in processingConfig.keys():
            directions = processingConfig["directions"]
        if '2D' in processingConfig.keys():
            mode = processingConfig["2D"]
        if 'azimuthLowLimit' in processingConfig.keys():
            azimuthLowLimit = processingConfig["azimuthLowLimit"]
        if 'azimuthHighLimit' in processingConfig.keys():
            azimuthHighLimit = processingConfig["azimuthHighLimit"]
        if 'elevationLowLimit' in processingConfig.keys():
            elevationLowLimit = processingConfig["elevationLowLimit"]
        if 'elevationHighLimit' in processingConfig.keys():
            elevationHighLimit = processingConfig["elevationHighLimit"]

        delaymatrix, directions, ranges = __generate_valid_processing_settings(PACKAGE_DIRECTORY, microphoneLayout,
                                                                               mode, directions, minRange, maxRange,
                                                                               10, microphoneSampleFrequency,
                                                                               azimuthLowLimit, azimuthHighLimit,
                                                                               elevationLowLimit, elevationHighLimit)

    return delaymatrix, directions, ranges, microphoneLayout, disableList


##############################
# RTIS Dev Public Functions #
##############################


def open_connection(port: str = '/dev/ttyACM0', allowDebugMode: bool = False) -> bool:
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

    global PORT
    global DEBUG
    PORT = port
    if os.name == 'nt':
        try:
            serPort = serial.Serial(PORT, 115200)
            serPort.timeout = 5
            serPort.reset_input_buffer()
            serPort.reset_output_buffer()
            serPort.close()
            if DEBUG == 1:
                logger.info("Connected to device on port '" + PORT + "' and disabled debug mode.")
                DEBUG = 0
            else:
                logger.info("Connected to device on port '" + PORT + "'.")
            return True
        except ConnectionRefusedError:
            logger.warning('Failed to connect to the RTIS device. This device is already connected or another'
                           ' application is using this port.')
            return False
        except ConnectionError:
            if allowDebugMode:
                logger.error('Failed to connect to the RTIS device over port \'' + str(
                    PORT) + '\'. This port could not be opened or was not found. Enabling debug mode.')
                DEBUG = 1
                return False
            else:
                logger.error("Failed to connect to the RTIS device over port '" + str(PORT) + ".'")
                raise ConnectionError("Failed to connect to the RTIS device over port '" + str(PORT) + "'.")
        except NameError:
            if allowDebugMode:
                DEBUG = 1
                logger.error("Failed to connect to the RTIS device."
                             + " The PySerial Python module was not found. Enabling debug mode.")
                return False
            else:
                raise RTISPySerialError
        except Exception as e:
            logger.error("Unexpected error while connecting to RTIS device over port '" + str(
                PORT) + "': " + str(e))
            if allowDebugMode:
                DEBUG = 1
                return False
            else:
                raise
    else:
        try:
            rtisserial.connect(PORT, 115200)
            if DEBUG == 1:
                logger.info("Connected to device on port '" + PORT + "' and disabled debug mode.")
                DEBUG = 0
            else:
                logger.info("Connected to device on port '" + PORT + "'.")
            return True
        except ConnectionRefusedError:
            logger.warning('Failed to connect to the RTIS device. This device is already connected or another'
                           ' application is using this port.')
            return False
        except ConnectionError:
            if allowDebugMode:
                logger.error('Failed to connect to the RTIS device over port \'' + str(
                    PORT) + '\'. This port could not be opened or was not found. Enabling debug mode.')
                DEBUG = 1
                return False
            else:
                logger.error("Failed to connect to the RTIS device over port '" + str(PORT) + ".'")
                raise ConnectionError("Failed to connect to the RTIS device over port '" + str(PORT) + "'.")
        except NameError:
            if allowDebugMode:
                DEBUG = 1
                logger.error("Failed to connect to the RTIS device."
                             + " The RTIS Serial Python module was not found. Enabling debug mode.")
                return False
            else:
                raise RTISSerialError
        except Exception as e:
            logger.error("Unexpected error while connecting to RTIS device over port '" + str(
                PORT) + "': " + str(e))
            if allowDebugMode:
                DEBUG = 1
                return False
            else:
                raise


def close_connection() -> bool:
    """Manually close the connection to the RTIS device.
       Normally, when your script ends without exceptions the connection will automatically
       be closed gracefully. This will also unload all RTIS CUDA workers.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    try:
        __unload_all()
    except RTISCUDAError:
        pass
    if DEBUG:
        logger.warning("Debug mode is enabled. No connection to end. Make sure to use open_connection().")
        return True
    else:
        if os.name == 'nt':
            logger.debug("RTIS hardware device connection ended.")
            return True
        else:
            try:
                rtisserial.close()
                logger.debug("RTIS hardware device connection ended.")
                return True
            except ConnectionRefusedError:
                logger.warning("Failed to close connection. RTIS hardware device was not connected.")
                return False
            except Exception as ex:
                logger.error("Could not close connection due to unknown error:" + str(ex))
                raise


def set_recording_settings(premade: str = None, jsonPath: str = None, callCustom: str = None,
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

    if configName == "":
        configName = __make_valid_config_name("c" + uuid.uuid4().hex)
    else:
        configName = __make_valid_config_name(configName)

    if not premade and not jsonPath:
        if callCustom:
            if os.path.isfile(callCustom):
                sigADC = genfromtxt(callCustom, delimiter=',')
                sigDAC = sigADC

                return __set_and_verify_recording_settings(sigADC, sigDAC, microphoneSampleFrequency,
                                                           callSampleFrequency,
                                                           microphoneSamples, callDuration, callMinimumFrequency,
                                                           callMaximumFrequency,
                                                           callEmissions, configName, applyToDevice)
            else:
                logger.error("Could not load custom call file. Please make sure to use correct path and filename.")
                raise FileNotFoundError("Could not load custom call file. " +
                                        "Please make sure to use correct path and filename.")
        else:
            sigADC, sigDAC = generate_recording_settings(callSampleFrequency,
                                                         callDuration,
                                                         callMinimumFrequency,
                                                         callMaximumFrequency)

            return __set_and_verify_recording_settings(sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                                                       microphoneSamples, callDuration, callMinimumFrequency,
                                                       callMaximumFrequency,
                                                       callEmissions, configName, applyToDevice)
    elif premade and jsonPath:
        raise RTISPremadeAndJsonSettingsError
    elif premade:
        if os.path.isfile(PACKAGE_DIRECTORY + '/config/premadeSettings/recording/'
                          + premade + '.json'):
            with open(PACKAGE_DIRECTORY + '/config/premadeSettings/recording/'
                      + premade + '.json') as json_file:
                recordingConfig = json.load(json_file)
                (sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                 microphoneSamples, callDuration, callMinimumFrequency, callMaximumFrequency, callEmissions) \
                    = __load_recording_settings_from_json(recordingConfig)

                return __set_and_verify_recording_settings(sigADC, sigDAC, microphoneSampleFrequency,
                                                           callSampleFrequency, microphoneSamples, callDuration,
                                                           callMinimumFrequency, callMaximumFrequency, callEmissions,
                                                           configName, applyToDevice)
        else:
            raise RTISPremadeRecordingSettingsError(premade)
    elif jsonPath:
        if os.path.isfile(jsonPath):
            with open(jsonPath) as json_file:
                recordingConfig = json.load(json_file)
                (sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                 microphoneSamples, callDuration, callMinimumFrequency, callMaximumFrequency, callEmissions) \
                    = __load_recording_settings_from_json(recordingConfig)

                return __set_and_verify_recording_settings(sigADC, sigDAC, microphoneSampleFrequency,
                                                           callSampleFrequency, microphoneSamples, callDuration,
                                                           callMinimumFrequency, callMaximumFrequency, callEmissions,
                                                           configName, applyToDevice)
        else:
            logger.error("Could not load recording settings json file. " +
                         "Please make sure to use correct path and filename.")
            raise FileNotFoundError("Could not load recording settings json file. " +
                                    "Please make sure to use correct path and filename.")


def set_processing_settings(configName: str, premade: str = None, jsonPath: str = None, customPath: str = None,
                            microphoneLayout: str = "eRTIS_v3D1", mode: int = 1, directions: int = 181,
                            azimuthLowLimit : float = -90, azimuthHighLimit : float = 90,
                            elevationLowLimit : float = -90, elevationHighLimit : float = 90,
                            minRange: float = 0.5, maxRange: float = 5,
                            pdmEnable: bool = True, preFilterEnable: bool = False, matchedFilterEnable: bool = True,
                            beamformingEnable: bool = True, postFilterEnable: bool = False,
                            enveloppeEnable: bool = True, cleanEnable: bool = True, preloadToggle: bool = True,
                            preFilter: np.ndarray = None, postFilter: np.ndarray = None,
                            meanEnergyRangeMultiplier: float = 2,
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

    global SETTINGS

    if not premade and not jsonPath:
        if customPath:
            if (os.path.isfile(customPath + "/delaymatrix.csv") and os.path.isfile(customPath + "/directions.csv")
                    and os.path.isfile(customPath + "/ranges.csv")):
                delaymatrix = (genfromtxt(customPath + "/delaymatrix.csv", delimiter=',', dtype=np.int32)).copy()
                directions = (genfromtxt(customPath + "/directions.csv", delimiter=',')).copy()
                ranges = genfromtxt(customPath + "/ranges.csv", delimiter=',')

                disableList = get_disabled_microphone_list(PACKAGE_DIRECTORY, microphoneLayout)

                return __set_and_verify_processing_settings(delaymatrix, directions, ranges, postFilter, preFilter,
                                                            meanEnergyRangeMultiplier,
                                                            maxEnergyRangeThresholdMultiplier,
                                                            pdmEnable, preFilterEnable, matchedFilterEnable,
                                                            beamformingEnable, postFilterEnable,
                                                            enveloppeEnable, cleanEnable, preloadToggle,
                                                            microphoneLayout, disableList, configName=configName)
            else:
                logger.error("Could not load custom processing files. " +
                             "Please make sure to use correct path and filenames.")
                raise FileNotFoundError("Could not load custom processing files. " +
                                        "Please make sure to use correct path and filenames.")
        else:

            if not SETTINGS:
                raise RTISSettingsError
            if configName not in SETTINGS:
                raise RTISSettingsByIDNotFoundError

            microphoneSampleFrequency = SETTINGS[configName].microphoneSampleFrequency

            delaymatrix, directions, ranges = __generate_valid_processing_settings(PACKAGE_DIRECTORY, microphoneLayout,
                                                                                   mode, directions, minRange, maxRange,
                                                                                   10, microphoneSampleFrequency,
                                                                                   azimuthLowLimit, azimuthHighLimit,
                                                                                   elevationLowLimit,
                                                                                   elevationHighLimit)

            disableList = get_disabled_microphone_list(PACKAGE_DIRECTORY, microphoneLayout)

            return __set_and_verify_processing_settings(delaymatrix, directions, ranges, postFilter, preFilter,
                                                        meanEnergyRangeMultiplier, maxEnergyRangeThresholdMultiplier,
                                                        pdmEnable, preFilterEnable, matchedFilterEnable,
                                                        beamformingEnable, postFilterEnable,
                                                        enveloppeEnable, cleanEnable, preloadToggle,
                                                        microphoneLayout, disableList, configName=configName)
    if premade and jsonPath:
        raise RTISPremadeAndJsonSettingsError
    elif premade:

        if not SETTINGS:
            raise RTISSettingsError
        if configName not in SETTINGS:
            raise RTISSettingsByIDNotFoundError

        microphoneSampleFrequency = SETTINGS[configName].microphoneSampleFrequency

        if os.path.isfile(PACKAGE_DIRECTORY + '/config/premadeSettings/processing/'
                          + premade + '.json'):
            with open(PACKAGE_DIRECTORY + '/config/premadeSettings/processing/'
                      + premade + '.json') as json_file:
                processingConfig = json.load(json_file)

                (delaymatrix, directions, ranges, microphoneLayout, disableList) = \
                    __load_processing_settings_from_json(processingConfig, microphoneSampleFrequency)
                return __set_and_verify_processing_settings(delaymatrix, directions, ranges, postFilter, preFilter,
                                                            meanEnergyRangeMultiplier,
                                                            maxEnergyRangeThresholdMultiplier,
                                                            pdmEnable, preFilterEnable, matchedFilterEnable,
                                                            beamformingEnable, postFilterEnable,
                                                            enveloppeEnable, cleanEnable, preloadToggle,
                                                            microphoneLayout, disableList, configName=configName)
        else:
            raise RTISPremadeProcessingSettingsError(premade)
    elif jsonPath:

        if not SETTINGS:
            raise RTISSettingsError
        if configName not in SETTINGS:
            raise RTISSettingsByIDNotFoundError

        microphoneSampleFrequency = SETTINGS[configName].microphoneSampleFrequency

        if os.path.isfile(jsonPath):
            with open(jsonPath) as json_file:
                processingConfig = json.load(json_file)
                (delaymatrix, directions, ranges, microphoneLayout, disableList) = \
                    __load_processing_settings_from_json(processingConfig, microphoneSampleFrequency)
                return __set_and_verify_processing_settings(delaymatrix, directions, ranges, postFilter, preFilter,
                                                            meanEnergyRangeMultiplier,
                                                            maxEnergyRangeThresholdMultiplier,
                                                            pdmEnable, preFilterEnable, matchedFilterEnable,
                                                            beamformingEnable, postFilterEnable,
                                                            enveloppeEnable, cleanEnable, preloadToggle,
                                                            microphoneLayout, disableList, configName=configName)
        else:
            logger.error("Could not load processing settings json file. "
                         "Please make sure to use correct path and filename.")
            raise FileNotFoundError("Could not load processing settings json file. "
                                    "Please make sure to use correct path and filename.")


def get_current_settings_config_name_list() -> List[str]:
    """Get a list of names of all the currently loaded configurations.

       Returns
       -------
       configNames : list[str]
           A list holding all the names of currently loaded RTISSettings.
    """

    return list(SETTINGS.keys())


def get_current_settings(configName: str = "") -> RTISSettings:
    """Returns all(dict) or a single `RTISSettings` object of the current settings for processing and recording.

       Parameters
       ----------
       configName : String
           String to identify these settings with. If given will only return this settings configuration if found.
           If not provided will return a dict of all RTISSettings objects identified by their own config name.

       Returns
       -------
       settings : RTISSettings or dict
           If the configName parameter is given, it will only return the complete class containing
           all RTIS settings for recording and processing. If this argument is not given it will return
           a dict of all RTISSettings objects identified by their own config name. If there is only one settings object
           defined it will return this one instead of a dict. Returns 'None' or
           will raise an exception on failure.
       """

    global SETTINGS

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            return deepcopy(list(SETTINGS.values())[0])
        else:
            return deepcopy(SETTINGS)
    else:
        if configName in SETTINGS:
            return deepcopy(SETTINGS[configName])
        else:
            raise RTISSettingsByIDNotFoundError


def clear_current_settings(configName: str = ""):
    """Clear all or the current applied `RTISSettings` configuration depending on setting the configName parameter.

       Parameters
       ----------
       configName: string
           The identity of the settings configuration to be cleared. If not given it will clear all settings.
    """

    global SETTINGS

    if configName == "":
        try:
            __unload_all()
        except RTISCUDAError:
            pass
        SETTINGS.clear()
    else:
        if configName in SETTINGS:
            SETTINGS.pop(configName)
            try:
                __unload_one(configName)
            except RTISCUDAError:
                pass
        else:
            raise RTISSettingsByIDNotFoundError


def get_settings(recordingPremade: str = None, recordingJsonPath: str = None, recordingCallCustom: str = None,
                 processingPremade: str = None, processingJsonPath: str = None, processingCustomPath: str = None,
                 microphoneSamples: int = 163840, microphoneSampleFrequency: int = 4500000,
                 callSampleFrequency: int = 450000, callDuration: float = 2.5, callMinimumFrequency: int = 25000,
                 callMaximumFrequency: int = 50000, callEmissions: int = 1,
                 microphoneLayout: str = "eRTIS_v3D1", mode: int = 1, directions: int = 181,
                 azimuthLowLimit: float = -90, azimuthHighLimit: float = 90,
                 elevationLowLimit: float = -90, elevationHighLimit: float = 90,
                 minRange: float = 0.5, maxRange: float = 5, pdmEnable: bool = True, preFilterEnable: bool = False,
                 matchedFilterEnable: bool = True, beamformingEnable: bool = True, postFilterEnable: bool = False,
                 enveloppeEnable: bool = True, cleanEnable: bool = True, preloadToggle: bool = True,
                 preFilter: np.ndarray = None, postFilter: np.ndarray = None,
                 meanEnergyRangeMultiplier: float = 2, maxEnergyRangeThresholdMultiplier: float = 0.5,
                 configName: str = "") -> RTISSettings:
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
       settings : RTISSettings
           The complete class containing all RTIS settings for recording and processing. Returns 'None' or
           will raise an exception on failure.
       """

    if not recordingPremade and not recordingJsonPath:
        if recordingCallCustom:
            if os.path.isfile(recordingCallCustom):
                sigADC = genfromtxt(recordingCallCustom, delimiter=',')
                sigDAC = sigADC
            else:
                logger.error("Could not load custom call file. Please make sure to use correct path and filename.")
                raise FileNotFoundError("Could not load custom call file. " +
                                        " Please make sure to use correct path and filename.")
        else:
            sigADC, sigDAC = generate_recording_settings(callSampleFrequency,
                                                         callDuration,
                                                         callMinimumFrequency,
                                                         callMaximumFrequency)
    elif recordingPremade and recordingJsonPath:
        raise RTISPremadeAndJsonSettingsError
    elif recordingPremade:
        if os.path.isfile(PACKAGE_DIRECTORY + '/config/premadeSettings/recording/'
                          + recordingPremade + '.json'):
            with open(PACKAGE_DIRECTORY + '/config/premadeSettings/recording/'
                      + recordingPremade + '.json') as json_file:
                recordingConfig = json.load(json_file)
                (sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                 microphoneSamples, callDuration, callMinimumFrequency, callMaximumFrequency, callEmissions) \
                    = __load_recording_settings_from_json(recordingConfig)

        else:
            raise RTISPremadeRecordingSettingsError(recordingPremade)
    elif recordingJsonPath:
        if os.path.isfile(recordingJsonPath):
            with open(recordingJsonPath) as json_file:
                recordingConfig = json.load(json_file)
                (sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                 microphoneSamples, callDuration, callMinimumFrequency, callMaximumFrequency, callEmissions) \
                    = __load_recording_settings_from_json(recordingConfig)

        else:
            logger.error("Could not load recording settings json file. "
                         "Please make sure to use correct path and filename.")
            raise FileNotFoundError("Could not load recording settings json file. "
                                    "Please make sure to use correct path and filename.")
    if not processingPremade and not processingJsonPath:
        if processingCustomPath:
            if (os.path.isfile(processingCustomPath + "/delaymatrix.csv") and os.path.isfile(
                    processingCustomPath + "/directions.csv")
                    and os.path.isfile(processingCustomPath + "/ranges.csv")):
                delaymatrix = (
                    genfromtxt(processingCustomPath + "/delaymatrix.csv", delimiter=',', dtype=np.int32)).copy()
                directions = (genfromtxt(processingCustomPath + "/directions.csv", delimiter=',')).copy()
                ranges = genfromtxt(processingCustomPath + "/ranges.csv", delimiter=',')
            else:
                logger.error("Could not load custom processing files. " +
                             "Please make sure to use correct path and filenames.")
                raise FileNotFoundError("Could not load custom processing files. " +
                                        "Please make sure to use correct path and filenames.")
        else:
            delaymatrix, directions, ranges = __generate_valid_processing_settings(PACKAGE_DIRECTORY, microphoneLayout,
                                                                                   mode, directions, minRange, maxRange,
                                                                                   10, microphoneSampleFrequency,
                                                                                   azimuthLowLimit, azimuthHighLimit,
                                                                                   elevationLowLimit,
                                                                                   elevationHighLimit)

    elif processingPremade and processingJsonPath:
        raise RTISPremadeAndJsonSettingsError
    elif processingPremade:
        if os.path.isfile(PACKAGE_DIRECTORY + '/config/premadeSettings/processing/'
                          + processingPremade + '.json'):
            with open(PACKAGE_DIRECTORY + '/config/premadeSettings/processing/'
                      + processingPremade + '.json') as json_file:
                processingConfig = json.load(json_file)

                (delaymatrix, directions, ranges, microphoneLayout, disableList) = \
                    __load_processing_settings_from_json(processingConfig, microphoneSampleFrequency)
        else:
            raise RTISPremadeProcessingSettingsError(processingPremade)
    elif processingJsonPath:
        if os.path.isfile(processingJsonPath):
            with open(processingJsonPath) as json_file:
                processingConfig = json.load(json_file)
                (delaymatrix, directions, ranges, microphoneLayout, disableList) = \
                    __load_processing_settings_from_json(processingConfig, microphoneSampleFrequency)
        else:
            logger.error("Could not load processing settings json file. "
                         "Please make sure to use correct path and filename.")
            raise FileNotFoundError("Could not load processing settings json file. "
                                    "Please make sure to use correct path and filename.")

    if configName == "":
        configName = __make_valid_config_name("c" + uuid.uuid4().hex)
    else:
        configName = __make_valid_config_name(configName)

    return __return_and_verify_all_settings(sigADC, sigDAC, microphoneSampleFrequency, callSampleFrequency,
                                            microphoneSamples, callDuration, callMinimumFrequency,
                                            callMaximumFrequency, callEmissions, delaymatrix, directions, ranges,
                                            preFilter, postFilter, meanEnergyRangeMultiplier,
                                            maxEnergyRangeThresholdMultiplier, pdmEnable, preFilterEnable,
                                            matchedFilterEnable, beamformingEnable, postFilterEnable, enveloppeEnable,
                                            cleanEnable, preloadToggle, microphoneLayout, configName)


def set_settings_from_class(settings: RTISSettings, applyToDevice: bool = True) -> bool:
    """Set the wanted settings from an `RTISSettings` object. These can be created
       with the `get_settings()` or `get_current_settings()` methods.

       Parameters
       ----------
       settings : RTISSettings
           The complete class containing all RTIS settings for recording and processing that needs to be set.

       applyToDevice : bool (default = True)
           A configuration toggle to optionally disable applying the recording settings to the RTIS Device.

       Returns
       -------
       success : bool
           returns `True` on successful completion, returns `False` or will raise an exception on failure.
    """

    global SETTINGS

    if isinstance(settings, RTISSettings):
        if settings.configName in SETTINGS:
            logger.warning("Settings with this configuration name '" + settings.configName +
                           "' already exist. They will be overwritten.")
            try:
                __unload_one(settings.configName)
            except RTISCUDAError:
                pass
        SETTINGS[settings.configName] = settings
        if applyToDevice:
            __configure_rtis_device(settings)
        if settings.processingSettings:
            if settings.preloadToggle:
                __preload(settings)
        return True
    else:
        logger.error("Your settings are faulty. Make sure to use an RTISSettings object.")
        raise TypeError("Your settings are faulty. Make sure to use an RTISSettings object.")


def get_premade_processing_settings_list() -> List[str]:
    """Get a list of names of all the available premade settings for processing.

       Returns
       -------
       recordingSettings : list[str]
           A list holding all the names of available settings that can be loaded.
    """

    processingSettings = [item.split(".json")[0] for item in
                          os.listdir(PACKAGE_DIRECTORY + '/config/premadeSettings/processing')
                          if item.endswith(".json")]
    return processingSettings


def get_premade_recording_settings_list() -> List[str]:
    """Get a list of names of all the available premade settings for recording.

       Returns
       -------
       recordingSettings : list[str]
           A list holding all the names of available settings that can be loaded.
    """

    recordingSettings = [item.split(".json")[0] for item in
                         os.listdir(PACKAGE_DIRECTORY + '/config/premadeSettings/recording')
                         if item.endswith(".json")]
    return recordingSettings


def get_microphone_layout_list() -> List[str]:
    """Get a list of names of all the available microphone layouts that are available for recording.

       Returns
       -------
       microphoneLayouts : list[str]
           A list holding all the names of available microphone layouts that can be loaded.
    """

    microphoneLayouts = [f.name for f in os.scandir(PACKAGE_DIRECTORY + '/config/microphoneLayouts')
                         if f.is_dir()]
    return microphoneLayouts


def prepare_processing(configName: str = "") -> bool:
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

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    if configName in SETTINGS:
        if configName not in WORKERS:
            if SETTINGS[configName].processingSettings:
                __preload(SETTINGS[configName])
                return True
            else:
                raise RTISProcessingSettingsError
        else:
            logger.error("Could not prepare processing: A worker is already running with configuration '" + configName
                         + "'. Use unload_processing() before starting a new worker.")
            return False
    else:
        raise RTISSettingsByIDNotFoundError


def unload_processing(configName: str = "") -> bool:
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

    if configName == "":
        __unload_all()
    else:
        __unload_one(configName)
    return True


def get_raw_measurement(behaviour: bool = False, configName: str = "") -> RTISMeasurement:
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
       measurement : RTISMeasurement
           The data class holding the raw measurement of the RTIS device with the raw binary data under
           `measurement.rawData`.

       Examples
       --------
       Create a connection, set recording settings and make a raw measurement with passive behaviour::

           >>> import rtisdev
           >>> rtisdev.open_connection()
           >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
           >>> measurement = rtisdev.get_raw_measurement(True, configName=config_uuid)

       Note that when multiple recording configurations are loaded, the module will automatically
       load the settings as asked for by the configName argument to the RTIS device before performing a new measurement.
    """

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    return __measure(behaviour, SETTINGS[configName])


def get_signal_measurement(behaviour: bool = False, configName: str = "") -> RTISMeasurement:
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
       measurement : RTISMeasurement
           The data class holding the signal measurement of the RTIS device under `measurement.processedData`
           and the raw binary data under `measurement.rawData`.

       Examples
       --------
       Create a connection, set recording and processing settings and make a signal measurement with active behaviour::

           >>> import rtisdev
           >>> rtisdev.open_connection()
           >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
           >>> signal_measurement = rtisdev.get_signal_measurement(True, configName=config_uuid)

       Note that when multiple recording configurations are loaded, the module will automatically
       load the settings as asked for by the configName argument to the RTIS device before performing a new measurement.
    """

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    return __process(__measure(behaviour, SETTINGS[configName]), None, configName, True)


def get_processed_measurement(behaviour: bool = False, configName: str = "") -> RTISMeasurement:
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
       measurement : RTISMeasurement
           The data class holding the processed measurement (the microphone signals)
           of the RTIS device under `measurement.processedData`
           and the raw binary data under `measurement.rawData`.

       Examples
       --------
       Create a connection, set recording and processing settings and make
       a processed measurement with active behaviour::

           >>> import rtisdev
           >>> rtisdev.open_connection()
           >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
           >>> rtisdev.set_processing_settings(directions=91, configName=config_uuid)
           >>> processed_measurement = rtisdev.get_processed_measurement(True, configName=config_uuid)

       Note that when multiple recording configurations are loaded, the module will automatically
       load the settings as asked for by the configName argument to the RTIS device before performing a new measurement.
    """

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    if SETTINGS[configName].processingSettings:
        packageIn = __measure(behaviour, SETTINGS[configName])
        packageOut = __process(packageIn, None, configName, False)
        return packageOut
    else:
        raise RTISProcessingSettingsError


def process_measurement(measurement: RTISMeasurement, configName: str = "") -> RTISMeasurement:
    """Process a previously recorded raw RTIS sonar measurement from a `RTISMeasurement` object
       and return same measurement with processed data in a new `RTISMeasurement` object.

       Parameters
       ----------
       measurement : RTISMeasurement
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

           >>> import rtisdev
           >>> rtisdev.open_connection()
           >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
           >>> rtisdev.set_processing_settings(directions=91, configName=config_uuid)
           >>> measurement = rtisdev.get_raw_measurement(True, configName=config_uuid)
           >>> processed_measurement = rtisdev.process_measurement(measurement, configName=config_uuid)
    """

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    if SETTINGS[configName].processingSettings:
        return __process(measurement, None, configName, False)
    else:
        raise RTISProcessingSettingsError


def set_counter(newCount: int = 0) -> bool:
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

    global DEBUG_COUNTER
    if DEBUG:
        logger.warning("Setting virtual counter in debug mode. Make sure to use open_connection().")
        DEBUG_COUNTER = newCount
        return True
    else:
        return __set_measurement_counter(newCount)


def set_behaviour(mode: bool) -> bool:
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

    mode = int(mode)
    if DEBUG:
        logger.warning("Setting virtual behaviour in debug mode. Make sure to use open_connection().")
    return __set_sonar_behaviour(mode)


def get_firmware_version() -> str:
    """Get the firmware version of the internal RTIS firmware used on the device.

       Returns
       -------
       firmwareVersion : string
           returns the firmware version as a string in 'vMajor.Minor.Bugfix' format. Returns 'undefined' or will
           raise an exception on failure.
    """

    if DEBUG:
        logger.warning("Getting firmware version in debug mode. Make sure to use open_connection().")
    return __get_firmware_version()


def create_measure_external_trigger_queue(dataQueue: Queue, configName: str = "") -> MeasureExternalTriggerQueueThread:
    """This will create and return a Multiprocessing Process
       that will be waiting for an external trigger to measure from
       the RTIS Device and afterward put this measurement on a data queue.
       This method will return a `MeasureExternalTriggerQueueThread`.

       Parameters
       ----------
       dataQueue : multiprocessing.Manager.Queue
           On this queue the `RTISMeasurement` objects will be put after an external trigger starts a new measurement.

       configName: string
           The identity of the settings configuration to be used. If not given it will assume only one
           settings configuration is defined within RTIS Dev.

       Returns
       -------
       measure_process : MeasureExternalTriggerQueueThread
           Class instance of the Multiprocessing Process super class that can then be started with '.start()'
           and waited for with `.join()` for example. It can be closed gracefully with the '.stop_thread()' function.
           This will also be done automatically when `signal.SIGINT` (ex. CTRL+C) is triggered.

       Examples
       --------
       Create a queue to save the measurement to and assign it to the process::

           >>> from multiprocessing import Manager
           >>> import rtisdev
           >>> rtisdev.open_connection()
           >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
           >>> rtisdev.set_processing_settings(directions=91,configName=config_uuid)
           >>> manager = Manager()
           >>> dataQueue = manager.Queue()
           >>> measure_thread = rtisdev.create_measure_external_trigger_queue(dataQueue, config_uuid)
           >>> measure_thread.start()
           >>> measure_thread.join()
    """
    latestTimestamp = Value('d', 0.0)
    useTimestampRecorder = True

    if os.name == 'nt':
        useTimestampRecorder = False
        logger.warning("Could not start secondary timestamp recorder process with GPIO listener."
                       "Timestamps will be taken after the measurement is completed.")
    else:
        try:
            with open(os.devnull, "w") as devNull:
                original = sys.stderr
                sys.stderr = devNull
                import Jetson.GPIO as GPIO
                sys.stderr = original
                GPIO.cleanup()
                timestamp_process = TimeStampRecorderProcess()
                timestamp_process.set_configuration(latestTimestamp, logger, DEBUG)
                timestamp_process.start()
        except Exception:
            useTimestampRecorder = False
            logger.warning("Could not start secondary timestamp recorder process with GPIO listener."
                           "Timestamps will be taken after the measurement is completed.")

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    measure_process = MeasureExternalTriggerQueueThread()
    measure_process.set_configuration(dataQueue, SETTINGS[configName], DEBUG_COUNTER, BEHAVIOUR, ID,
                                      logger, DEBUG, latestTimestamp, useTimestampRecorder)
    signal.signal(signal.SIGINT, __gracefully_close_measure_processes)
    return measure_process


def create_measure_external_trigger_callback(callback: Callable[[RTISMeasurement], any], configName: str = "") \
        -> MeasureExternalTriggerCallbackThread:
    """This will create and return a Multiprocessing Process
       that will be waiting for an external trigger to measure from
       the RTIS Device and afterward put this measurement on a data queue.
       This method will return a `MeasureExternalTriggerCallbackThread`.

       Parameters
       ----------
       callback : method with one argument of type RTISMeasurement
           This is the method that will be used as a callback when a new measurement is triggered by the
           external trigger. This function should only require one argument,
           the `RTISMeasurement` object containing the measurement data.

       configName: string
           The identity of the settings configuration to be used. If not given it will assume only one
           settings configuration is defined within RTIS Dev.

       Returns
       -------
       measure_process : MeasureExternalTriggerCallbackThread
           Class instance of the Multiprocessing Process super class that can then be started with `.start()`
           and waited for with `.join()` for example. It can be closed gracefully with the `.stop_thread()` function.
           This will also be done automatically when _signal.SIGINT_ (ex. CTRL+C) is triggered.

       Examples
       --------
       Create a callback to save the measurement to disk::

           >>> import rtisdev
           >>> rtisdev.open_connection()
           >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
           >>> rtisdev.set_processing_settings(directions=91, configName=config_uuid)
           >>> index = 0
           >>> def save_callback(measurement=None):
           ...     if measurement is not None :
           ...         if measurement.rawData is not None:
           ...             data_sonar = measurement.rawData.tobytes()
           ...             file_handle_data = open(str(index) + ".bin","wb")
           ...             file_handle_data.write(data_sonar)
           ...             file_handle_data.close()
           ...             index = index + 1
           >>> measure_thread = rtisdev.create_measure_external_trigger_callback(save_callback, config_uuid)
           >>> measure_thread.start()
           >>> measure_thread.join()
    """

    latestTimestamp = Value('d', 0.0)
    useTimestampRecorder = True
    if os.name == 'nt':
        useTimestampRecorder = False
        logger.warning("Could not start secondary timestamp recorder process with GPIO listener."
                       "Timestamps will be taken after the measurement is completed.")
    else:
        try:
            with open(os.devnull, "w") as devNull:
                original = sys.stderr
                sys.stderr = devNull
                import Jetson.GPIO as GPIO
                sys.stderr = original
                GPIO.cleanup()
                timestamp_process = TimeStampRecorderProcess()
                timestamp_process.set_configuration(latestTimestamp, logger, DEBUG)
                timestamp_process.start()
        except Exception:
            useTimestampRecorder = False
            logger.warning("Could not start secondary timestamp recorder process with GPIO listener."
                           "Timestamps will be taken after the measurement is completed.")

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    measure_process = MeasureExternalTriggerCallbackThread()
    measure_process.set_configuration(callback, SETTINGS[configName], DEBUG_COUNTER, BEHAVIOUR, ID,
                                      logger, DEBUG, latestTimestamp, useTimestampRecorder)
    signal.signal(signal.SIGINT, __gracefully_close_measure_processes)
    return measure_process


def create_processing_workers(workerCount: int, inputQueue: Queue, outputQueue: Queue, configName: str = "") -> Pool:
    """This will create and return a Multiprocessing Pool that will generate a chosen amount of processing
       workers to handle incoming `RTISMeasurement` objects on the input Multiprocessing Queue
       and after processing place them on the output Multiprocessing Queue.

       Please set the `preloadToggle` argument to `False` when using `set_processing_settings()`
       and/or make sure to not use `prepare_processing()` before this point as it will cause an error or result in a
       potential crash of RTIS Dev!

       Parameters
       ----------
       workerCount : int
           The amount of worker processes to create and keep active in the Pool.

       inputQueue : multiprocessing.Manager.Queue
           This is the data queue that will be used to receive the recorded `RTISMeasurement` objects on.

       outputQueue : multiprocessing.Manager.Queue
           This is the data queue that will be used to store the processed `RTISMeasurement` objects on.

       configName: string
           The identity of the settings configuration to be used. If not given it will assume only one
           settings configuration is defined within RTIS Dev.

       Returns
       -------
       workersPool : multiprocessing.Pool
           Class instance of the Pool super class. It can be closed gracefully with the `.terminate()` function.
           This will also be done automatically when _signal.SIGINT_ (ex. CTRL+C) is triggered.
           The workers will be automatically started when calling this function.

       Examples
       --------
       Create the data queues, set up the worker pool with 4 workers, generate some measurements and afterward parse
       all these measurements by getting them from the output queue.
       Once the work is done, terminate the workers gracefully::

           >>> from multiprocessing import Manager
           >>> import rtisdev
           >>> rtisdev.open_connection()
           >>> config_uuid = rtisdev.set_recording_settings(callMinimumFrequency=25000, callMaximumFrequency=50000)
           >>> rtisdev.set_processing_settings(directions=91, configName=config_uuid, preloadToggle=False)
           >>> manager = Manager()
           >>> inputQueue = manager.Queue()
           >>> outputQueue = manager.Queue()
           >>> workersPool = rtisdev.create_processing_workers(4, inputQueue, outputQueue, config_uuid)
           >>> for measurement_index in range(0, 30):
           ...     measurement = rtisdev.get_raw_measurement(configName=config_uuid)
           ...     inputQueue.put(measurement)
           >>> for measurement_index in range(0, 30):
           ...     measurement = outputQueue.get()
           >>> workersPool.terminate()
    """
    global logger

    if len(SETTINGS) == 0:
        raise RTISSettingsError
    if configName == "":
        if len(SETTINGS) == 1:
            configName = list(SETTINGS.values())[0].configName
        else:
            raise RTISMultipleSettingsFoundError

    if not SETTINGS[configName].processingSettings:
        raise RTISProcessingSettingsError
    else:
        if CUDA_USED:
            raise RTISWorkerError
        else:
            multiprocessing_logging.install_mp_handler()
            workersPool = Pool(workerCount, __processing_worker,
                               [SETTINGS[configName], inputQueue, outputQueue, logger])
        return workersPool


def toggle_amplifier(mode: bool) -> bool:
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

    mode = int(mode)
    if DEBUG:
        logger.warning("Setting amplifier mode in debug mode. Make sure to use open_connection().")
    return __toggle_amplifier(mode)


def toggle_external_triggers(mode: bool, pin: int = 1) -> bool:
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

    mode = int(mode)
    if DEBUG:
        logger.warning("Setting external trigger mode in debug mode. Make sure to use open_connection().")
    return __toggle_external_trigger(mode, pin)


def custom_command(command: str) -> int:
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

    if DEBUG:
        logger.warning("Setting external trigger mode in debug mode. Make sure to use open_connection().")
    return __custom_command(command)


def reset_device(stm32pin: int = 7) -> bool:
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

    if DEBUG:
        logger.warning("Debug mode is enabled. No device to reset. Make sure to use open_connection().")
        return True
    else:
        try:
            with open(os.devnull, "w") as devNull:
                original = sys.stderr
                sys.stderr = devNull
                import Jetson.GPIO as GPIO
                sys.stderr = original
                GPIO.setmode(GPIO.BOARD)

                stm32_nrst = stm32pin

                logger.info("Preparing to reset...")
                GPIO.setup(stm32_nrst, GPIO.OUT, initial=GPIO.HIGH)
                logger.info("Resetting...")
                logger.debug("Pulling RESET Low STM32...")
                GPIO.output(stm32_nrst, GPIO.LOW)
                time.sleep(1)
                logger.debug("Pulling RESET High STM32...")
                GPIO.output(stm32_nrst, GPIO.HIGH)
                logger.debug("Starting reboot sleep...")
                time.sleep(60)
                logger.info("RTIS hardware device reset completed.")
                return True
        except Exception as ex:
            logger.error("Could not reset RTIS Device due to unknown error: " + str(ex))
            raise


def set_log_mode(mode: int):
    """The function to set the logging level of the RTIS Dev module.

       Parameters
       ----------
       mode : int
           Disable or configure log the level. 0 = off, 1 = only warnings and errors, 2(default) = includes info,
           3 = includes debug
    """

    global logger

    logger = logging.getLogger("RTISDev " + ID)

    if mode == 3:
        logger.setLevel(logging.DEBUG)
    elif mode == 2:
        logger.setLevel(logging.INFO)
    elif mode == 1:
        logger.setLevel(logging.WARNING)
    elif mode == 0:
        logger.setLevel(logging.CRITICAL)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    logger.debug("Set logging mode to " + logging.getLevelName(logger.getEffectiveLevel()) + ".")
    multiprocessing_logging.install_mp_handler()


def set_custom_logger(customLogger: logging.Logger):
    """The function to set a custom logger to be used by RTIS Dev.

       Parameters
       ----------
       customLogger : logging.Logger
           The custom logger to be used by RTIS Dev.
    """

    global logger
    logger = customLogger
