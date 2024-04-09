import os

import rtisdev
import time
import sys
import logging
import unittest
import scipy.signal
import numpy as np
from multiprocessing import Manager, Pool

""" Test RTIS Dev

Some small testing of the library.

By Cosys-Lab, University of Antwerp
Contributors:
Wouter Jansen
Arne Aerts
Dennis Laurijssen
Jan Steckel
"""


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
logger = logging.getLogger("RTISDev TESTING")
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


def assert_exit(condition, err_message):
    try:
        assert condition
    except AssertionError:
        sys.exit(err_message)


class TestRTISDev(unittest.TestCase):

    # OPEN CONNECTION

    def test_0_connection(self):

        logger.info(' TEST UPDATE - Opening connection')
        rtisdev.open_connection('/dev/ttyACM0', allowDebugMode=True)

    # SPECIAL COMMANDS

    def test_a_amplifier_toggle(self):
        logger.info(' TEST UPDATE - toggling amplifier modes')
        self.assertEqual(rtisdev.toggle_amplifier(False), True)
        self.assertEqual(rtisdev.toggle_amplifier(True), True)

    def test_b_external_trigger_toggle(self):
        logger.info(' TEST UPDATE - toggling external trigger modes')
        self.assertEqual(rtisdev.toggle_external_triggers(False), True)
        self.assertEqual(rtisdev.toggle_external_triggers(True), True)

    # FIRMWARE

    def test_c_get_firmware(self):
        logger.info(' TEST UPDATE - toggling external trigger mode ON')
        self.assertIsNot(rtisdev.get_firmware_version(), "undefined")

    # SETTINGS WITHOUT APPLYING

    def test_d_get_settings(self):
        logger.info(' TEST UPDATE - Generating and returning settings')
        rtisdev.clear_current_settings()
        self.assertIsInstance(rtisdev.get_settings(recordingPremade="default_20_80"), rtisdev.RTISSettings)
        self.assertIsInstance(rtisdev.get_settings(
            recordingJsonPath="../rtisdev/config/premadeSettings/recording/flutter.json", pdmEnable=False,
            matchedFilterEnable=False, beamformingEnable=False, cleanEnable=False, enveloppeEnable=False,
            preloadToggle=False), rtisdev.RTISSettings)
        self.assertIsInstance(rtisdev.get_settings(
            recordingCallCustom="../rtisdev/config/premadeSettings/recording/flutter.csv", pdmEnable=False,
            matchedFilterEnable=False, beamformingEnable=False, cleanEnable=False, enveloppeEnable=False,
            preloadToggle=False), rtisdev.RTISSettings)
        self.assertIsInstance(rtisdev.get_settings(recordingPremade="default_25_50"), rtisdev.RTISSettings)
        self.assertIsInstance(rtisdev.get_settings(processingPremade="2D_5m_181"), rtisdev.RTISSettings)
        self.assertIsInstance(rtisdev.get_settings(
            processingJsonPath="../rtisdev/config/premadeSettings/processing/custom_example_2D_5m_91.json"),
            rtisdev.RTISSettings)
        self.assertIsInstance(rtisdev.get_settings(processingCustomPath="../rtisdev/config/premadeSettings/processing"),
                              rtisdev.RTISSettings)
        self.assertIsInstance(rtisdev.get_settings(processingPremade="2D_5m_181"), rtisdev.RTISSettings)

    def test_e_get_settings_exceptions(self):
        logger.info(' TEST UPDATE - Generating and returning settings and trigger exceptions')
        rtisdev.clear_current_settings()
        self.assertRaises(rtisdev.RTISPremadeRecordingSettingsError, rtisdev.get_settings,
                          recordingPremade="faultypremadename")
        self.assertRaises(FileNotFoundError, rtisdev.get_settings, recordingJsonPath="faultypath")
        self.assertRaises(FileNotFoundError, rtisdev.get_settings, recordingCallCustom="faultypath")
        self.assertRaises(ValueError, rtisdev.get_settings, microphoneSamples=32768 * 4 + 2)
        self.assertRaises(ValueError, rtisdev.get_settings, microphoneSampleFrequency=32768)
        self.assertRaises(ValueError, rtisdev.get_settings, microphoneSamples=16809984)
        self.assertRaises(ValueError, rtisdev.get_settings, callSampleFrequency=130000)
        self.assertRaises(ValueError, rtisdev.get_settings, callSampleFrequency=2000000 + 1)
        self.assertRaises(rtisdev.RTISPremadeAndJsonSettingsError, rtisdev.get_settings,
                          recordingPremade="faultypremadename", recordingJsonPath="faultypath")
        self.assertRaises(rtisdev.RTISPremadeProcessingSettingsError, rtisdev.get_settings,
                          processingPremade="faultypremadename")
        self.assertRaises(FileNotFoundError, rtisdev.get_settings, processingJsonPath="faultypath")
        self.assertRaises(FileNotFoundError, rtisdev.get_settings, processingCustomPath="faultypath")
        self.assertRaises(ValueError, rtisdev.get_settings, maxRange=20)
        self.assertRaises(ValueError, rtisdev.get_settings, minRange=20, maxRange=40)
        self.assertRaises(rtisdev.RTISPremadeAndJsonSettingsError, rtisdev.get_settings,
                          processingPremade="faultypremadename", processingJsonPath="faultypath")

    # GETTING  LISTS

    def test_f_get_current_settings_config_name_list(self):
        logger.info(' TEST UPDATE - Getting current settings config name list')
        self.assertIsInstance(rtisdev.get_current_settings_config_name_list(), list)

    def test_g1_get_recording_premade_list(self):
        logger.info(' TEST UPDATE - Getting recording premade list')
        self.assertIsInstance(rtisdev.get_premade_recording_settings_list(), list)

    def test_g2_get_processing_premade_list(self):
        logger.info(' TEST UPDATE - Getting processing premade list')
        self.assertIsInstance(rtisdev.get_premade_processing_settings_list(), list)

    def test_g3_get_microphone_layout_list(self):
        logger.info(' TEST UPDATE - Getting microphone layouts list')
        self.assertIsInstance(rtisdev.get_microphone_layout_list(), list)

    # GETTING SETTINGS

    def test_h_getting_settings_without_set(self):
        logger.info(' TEST UPDATE - Getting settigns without setting any')
        rtisdev.clear_current_settings()
        self.assertRaises(rtisdev.RTISSettingsError, rtisdev.get_current_settings)

    # RECORDING SETTINGS WITH APPLYING

    def test_i_set_recording_settings_exceptions(self):
        logger.info(' TEST UPDATE - Generating and setting recording settings and trigger exceptions')
        rtisdev.clear_current_settings()
        self.assertRaises(rtisdev.RTISPremadeRecordingSettingsError, rtisdev.set_recording_settings,
                          premade="faultypremadename")
        self.assertRaises(FileNotFoundError, rtisdev.set_recording_settings, jsonPath="faultypath")
        self.assertRaises(FileNotFoundError, rtisdev.set_recording_settings, callCustom="faultypath")
        self.assertRaises(ValueError, rtisdev.set_recording_settings, microphoneSamples=32768 * 4 + 2)
        self.assertRaises(ValueError, rtisdev.set_recording_settings, microphoneSampleFrequency=32768)
        self.assertRaises(ValueError, rtisdev.set_recording_settings, microphoneSamples=16809984)
        self.assertRaises(ValueError, rtisdev.set_recording_settings, callSampleFrequency=130000)
        self.assertRaises(ValueError, rtisdev.set_recording_settings, callSampleFrequency=2000000 + 1)
        self.assertRaises(rtisdev.RTISPremadeAndJsonSettingsError, rtisdev.set_recording_settings,
                          premade="faultypremadename",
                          jsonPath="faultypath")

    def test_j_set_recording_settings(self):
        logger.info(' TEST UPDATE - Generating and setting recording settings')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="flutter", configName="test"), 'test')
        self.assertEqual(rtisdev.set_recording_settings(jsonPath="../rtisdev/config/premadeSettings/recording/flutter.json",
                         configName="test"), 'test')
        self.assertEqual(rtisdev.set_recording_settings(callCustom="../rtisdev/config/premadeSettings/recording/flutter.csv",
                         configName="test"), "test")
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")

    # MEASUREMENT TYPES WITHOUT SETTINGS

    def test_k_set_measurement_no_processing_settings(self):
        logger.info(' TEST UPDATE - measuring types without setting processing configuration in settings')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
        self.assertRaises(rtisdev.RTISProcessingSettingsError, rtisdev.prepare_processing)
        self.assertRaises(rtisdev.RTISProcessingSettingsError, rtisdev.get_processed_measurement, False)
        self.assertIsInstance(rtisdev.get_signal_measurement(False), rtisdev.RTISMeasurement)
        self.assertIsInstance(rtisdev.get_raw_measurement(False), rtisdev.RTISMeasurement)

    # PROCESSING SETTINGS WITH APPLYING

    def test_l_set_processing_settings_exceptions(self):
        logger.info(' TEST UPDATE - Generating and setting processing settings and trigger exceptions')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
        self.assertRaises(rtisdev.RTISPremadeProcessingSettingsError, rtisdev.set_processing_settings,
                          premade="faultypremadename",
                          configName="test")
        self.assertRaises(FileNotFoundError, rtisdev.set_processing_settings, jsonPath="faultypath", configName="test")
        self.assertRaises(FileNotFoundError, rtisdev.set_processing_settings, customPath="faultypath",
                          configName="test")
        self.assertRaises(FileNotFoundError, rtisdev.set_processing_settings, microphoneLayout="brokenLayout",
                          configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, azimuthLowLimit=-100, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, azimuthLowLimit=100,  configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, azimuthHighLimit=-100, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, azimuthHighLimit=100, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, elevationLowLimit=-100, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, elevationLowLimit=100, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, elevationHighLimit=-100, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, elevationHighLimit=100, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, minRange=-5, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, minRange=5, maxRange=4, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, maxRange=-5, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, mode=-5, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, mode="2d", configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, directions=1, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, maxRange=20, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, minRange=20, maxRange=40, configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, postFilter=None, postFilterEnable=True,
                          configName="test")
        self.assertRaises(ValueError, rtisdev.set_processing_settings, preFilter=None, preFilterEnable=True,
                          configName="test")
        self.assertRaises(rtisdev.RTISPremadeAndJsonSettingsError, rtisdev.set_processing_settings,
                          premade="faultypremadename",
                          jsonPath="faultypath",
                          configName="test")
        self.assertRaises(TypeError, rtisdev.set_processing_settings, preFilter=None)
        self.assertRaises(TypeError, rtisdev.set_processing_settings, postFilter=None)

    def test_m_set_processing_settings(self):
        logger.info(' TEST UPDATE - Generating and setting processing settings')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", configName="test"), True)
        self.assertEqual(rtisdev.set_processing_settings(
                         jsonPath="../rtisdev/config/premadeSettings/processing/custom_example_2D_5m_91.json",
                         configName="test"), True)
        self.assertEqual(rtisdev.set_processing_settings(
                         customPath="../rtisdev/config/premadeSettings/processing", configName="test"), True)
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", configName="test"), True)
        pref = scipy.signal.firwin(513, 20000 / (450000 / 2), pass_zero=False).astype(np.float32)
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", preFilter=pref,
                                                         preFilterEnable=True, configName="test"), True)
        postf = scipy.signal.firwin(512, [40000 / (450000 / 2), 50000 / (450000 / 2)],
                                    pass_zero=False).astype(np.float32)
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", postFilter=postf,
                                                         postFilterEnable=True, configName="test"), True)

    # SETTING SETTINGS FROM CLASS

    def test_n_set_from_class(self):
        logger.info(' TEST UPDATE - Generating and setting settings from class')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", configName="test"), True)
        self.assertIsInstance(rtisdev.get_current_settings(), rtisdev.RTISSettings)
        curSettings = rtisdev.get_current_settings()
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_settings_from_class(curSettings), True)

    # PROCESSING (UN)LOAD

    def test_o_processing(self):
        logger.info(' TEST UPDATE - preparing and unloading processing')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", configName="test"), True)
        self.assertEqual(rtisdev.prepare_processing(), False)
        self.assertEqual(rtisdev.unload_processing(), True)
        self.assertEqual(rtisdev.prepare_processing(), True)

    # MEASUREMENTS

    def test_p_measurements(self):
        logger.info(' TEST UPDATE - measurement types')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", configName="test"), True)
        self.assertIsInstance(rtisdev.get_raw_measurement(False), rtisdev.RTISMeasurement)
        self.assertIsInstance(rtisdev.get_signal_measurement(False), rtisdev.RTISMeasurement)
        self.assertIsInstance(rtisdev.get_processed_measurement(False), rtisdev.RTISMeasurement)
        self.assertEqual(rtisdev.unload_processing(), True)
        self.assertIsInstance(rtisdev.get_processed_measurement(False), rtisdev.RTISMeasurement)
        curMeasurement = rtisdev.get_raw_measurement(False)
        self.assertIsInstance(rtisdev.process_measurement(curMeasurement), rtisdev.RTISMeasurement)
        self.assertEqual(rtisdev.unload_processing(), True)
        self.assertIsInstance(rtisdev.process_measurement(curMeasurement), rtisdev.RTISMeasurement)
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test2"), "test2")
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", configName="test2"), True)
        self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", configName="test2"), True)
        self.assertRaises(rtisdev.RTISMultipleSettingsFoundError, rtisdev.process_measurement, curMeasurement)
    # COUNTER

    def test_q_counter(self):
        logger.info(' TEST UPDATE - setting counter')
        rtisdev.clear_current_settings()
        self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
        self.assertEqual(rtisdev.set_counter(), True)
        self.assertEqual(rtisdev.get_raw_measurement(False).index, 0)
        self.assertEqual(rtisdev.set_counter(420), True)
        self.assertEqual(rtisdev.get_raw_measurement(False).index, 420)

    # SET UP MULTIPLE WORKERS

    def test_r_workers(self):
        if os.name == 'nt':
            logger.info(' TEST UPDATE - setting up multiple processing workers')
            rtisdev.clear_current_settings()
            managerTest = Manager()
            inputQueueTest = managerTest.Queue()
            outputQueueTest = managerTest.Queue()
            self.assertRaises(rtisdev.RTISSettingsError, rtisdev.create_processing_workers, 2,
                              inputQueueTest, outputQueueTest)
            self.assertEqual(rtisdev.set_recording_settings(premade="default_25_50", configName="test"), "test")
            self.assertRaises(rtisdev.RTISProcessingSettingsError, rtisdev.create_processing_workers, 2,
                              inputQueueTest,
                              outputQueueTest)
            rtisdev.unload_processing()
            self.assertEqual(rtisdev.set_processing_settings(premade="2D_5m_181", preloadToggle=False,
                                                             configName="test"), True)
            workerPoolTest = rtisdev.create_processing_workers(2, inputQueueTest, outputQueueTest, "test")
            for _ in range(0, 5):
                measurementTest = rtisdev.get_raw_measurement()
                self.assertIsInstance(measurementTest, rtisdev.RTISMeasurement)
                inputQueueTest.put(measurementTest)
            for _ in range(0, 5):
                measurementTest = outputQueueTest.get()
                self.assertIsInstance(measurementTest, rtisdev.RTISMeasurement)
            workerPoolTest.terminate()

    # TEST CONFIG NAME VALIDATION
    def test_s_config_name_validation(self):
        logger.info(' TEST UPDATE - config name validation')
        rtisdev.clear_current_settings()
        rtisdev.unload_processing()
        generatedConfigName = rtisdev.set_recording_settings()
        self.assertRaises(rtisdev.RTISSettingsByIDNotFoundError, rtisdev.set_processing_settings, 'test')
        self.assertEqual(rtisdev.set_processing_settings(configName=generatedConfigName), True)
        self.assertEqual(rtisdev.set_recording_settings(configName="test"), 'test')
        self.assertEqual(rtisdev.set_recording_settings(configName="teSSt5Sst"), 'teSSt5Sst')
        self.assertEqual(rtisdev.set_recording_settings(configName="5test"), 'c5test')
        self.assertEqual(rtisdev.set_recording_settings(configName="5 test"), 'c5test')
        self.assertEqual(rtisdev.set_recording_settings(configName="5 t_est"), 'c5t_est')
        self.assertEqual(rtisdev.set_recording_settings(configName="5 t_e&*st"), 'c5t_est')

    # CLOSE CONNECTION

    def test_t_close(self):
        logger.info(' TEST UPDATE - closing connection')
        self.assertEqual(rtisdev.unload_processing(), True)
        self.assertEqual(rtisdev.close_connection(), True)


######################################
# Main RTIS Dev Process (For testing) #
#######################################

if __name__ == '__main__':

    # SETUP
    logger.info(" TEST - Starting tests...")
    rtisdev.set_log_mode(2)
    rtisdev.set_custom_logger(logger)

    # Testing this outside unit test system as otherwise it will crash on linux due to forking child processes
    if not os.name == 'nt':
        logger.info(' TEST UPDATE - setting up multiple processing workers')
        rtisdev.open_connection(allowDebugMode=True)
        rtisdev.clear_current_settings()
        manager = Manager()
        inputQueue = manager.Queue()
        outputQueue = manager.Queue()
        rtisdev.set_recording_settings(premade="default_25_50", configName="test")
        rtisdev.set_processing_settings(premade="2D_5m_181", preloadToggle=False, configName="test")
        workerPool = rtisdev.create_processing_workers(2, inputQueue, outputQueue, "test")
        for measurement_index in range(0, 5):
            measurement = rtisdev.get_raw_measurement()
            inputQueue.put(measurement)
        for measurement_index in range(0, 5):
            measurement = outputQueue.get()
        workerPool.terminate()
        rtisdev.close_connection()

    # UNIT TESTS
    unittest.main()
