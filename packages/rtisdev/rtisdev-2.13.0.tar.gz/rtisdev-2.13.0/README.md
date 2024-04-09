# RTIS Dev
This project is a Python Module to be used on an embedded platform connected to a RTIS sensor. It can be used for quick prototyping and developing
Python scripts related to the sensor data from RTIS sensors. It includes functions to measure and process sonar data. 

## Installation

### Dependencies
Version numbers are those used during this project, higher versions likely supported too unless otherwise specified. 
* Python 3.6 or higher with modules:
  * Numpy
  * Scipy
  * multiprocessing-logging
  * uuid
  * RTIS Serial on Linux systems (see [here](https://cosysgit.uantwerpen.be/rtis-software/rtisserial "RTIS Serial Git repository")) 
  * PySerial on Windows systems
  * RTIS CUDA 2.5.3 or higher if any processing is desired (see [here](https://cosysgit.uantwerpen.be/rtis-software/rtiscuda "RTIS CUDA Git repository"))

### Install from PyPI
You can install this module from the [PyPi repository](https://pypi.org/project/rtisdev/) like any other:
```bash
pip install rtisdev
```

### Install from source

#### A. Automatic installation using RTIS Update
To build and install RTIS Dev and keep it automatically up to date, please use the [RTIS Update](https://cosysgit.uantwerpen.be/rtis-software/rtisupdate) script.

#### B. Manual Installation
Install all dependencies listed above. We suggest to always use pip.
```bash
pip install MODULE_NAME
```

To install the Python Module so that you can use it in any Python script on Windows:
```bash
py -m pip install .
```

And on Linux:
```bash
pip install .
```

## Usage

All methods and classes are fully documented on the [wiki page](https://cosysgit.uantwerpen.be/rtis-software/rtisdev/-/wikis/home).
which has more information and examples.

#### 1) Import

If `rtisdev` is installed you can now import it in any Python script on the system as any other module:
```python
import rtisdev
```

Do note that due to RTIS Dev using [RTIS CUDA](https://cosysgit.uantwerpen.be/rtis-software/rtiscuda "RTIS CUDA Git repository"), you will need to add the folder where you installed RTIS CUDA to your library path for your script if you are using an IDEA that uses custom Python environments.
For example, using PyCharm IDE can have the issue of not being able to load RTIS CUDA library by not finding library path:
You will need to add `LD_LIBRARY_PATH` with value `/usr/lib/rtiscuda` (or your custom location) manually to your run configurations. 

#### 2) General Usage

There are several classes and methods available in RTIS Dev. Some general knowledge on RTIS sonar sensors is advised.
Here is a small example that goes over most basic steps:

 ```python
import rtisdev
import matplotlib.pyplot as plt
import numpy as np

# Open a connection to the RTIS Device over the default serial port.
success_connect = rtisdev.open_connection(allowDebugMode=True)

# Set the recording settings with 163840 samples and a call sweep between 25 and 50 KHz.
config_uuid = rtisdev.rtisdev.set_recording_settings(microphoneSamples=163840, callMinimumFrequency=25000, callMaximumFrequency=50000)

# Enable all processing steps and preload them with RTIS CUDA. This will produce a 2D energyscape with 91 directions
# with a maximum distance of 5m.
success_settings_processing = rtisdev.set_processing_settings(directions=91, maxRange=5, configName=config_uuid)

# Get the used settings as a RTISSettings object.
settings = rtisdev.get_current_settings(configName=config_uuid)

# Get an ACTIVE measurement (protect your ears!) in raw data.
measurement = rtisdev.get_raw_measurement(True, configName=config_uuid)

# Store the raw data of that measurement as a binary file. This can be opened in another application for further work.
# For an example in MATLAB, see below.
raw_data_sonar = measurement.rawData.tobytes()
file_handle_data = open("test_measurement_" + str(measurement.index) + ".bin", "wb")
file_handle_data.write(raw_data_sonar)
file_handle_data.close()

# Process that raw measurement to an energyscape using the configuration chosen earlier.
processed_measurement = rtisdev.process_measurement(measurement, configName=config_uuid)

# Get a new ACTIVE measurement (protect your ears!) in both raw and processed data formats directly.
new_processed_measurement = rtisdev.get_processed_measurement(True, configName=config_uuid)

# Plot the 2D energyscape of this processed measurement.
plt.imshow(np.transpose(new_processed_measurement.processedData), cmap="hot", interpolation='nearest')
plt.xlabel("Directions (degrees)")
plt.ylabel("Range (meters)")
indexes_x = np.arange(0, new_processed_measurement.processedData.shape[0], 20)
labels_x = np.round(np.rad2deg(settings.directions[indexes_x, 0])).astype(int)
indexes_y = np.arange(0, new_processed_measurement.processedData.shape[1], 100)
labels_y = settings.ranges[indexes_y]
fmt_x = lambda x: "{:.0f}°".format(x)
fmt_y = lambda x: "{:.2f}m".format(x)
plt.xticks(indexes_x, [fmt_x(i) for i in labels_x])
plt.yticks(indexes_y, [fmt_y(i) for i in labels_y])
plt.title("RTIS Dev - 2D Energyscape Example")
ax = plt.gca()
ax.invert_yaxis()
ax.set_aspect("auto")
plt.show()

# Get a new ACTIVE measurement (protect your ears!) in both raw and microphone signal format directly.
signal_measurement = rtisdev.get_signal_measurement(True, configName=config_uuid)

# Plot the microphone signals of this measurement.
fig, axs = plt.subplots(8, 4, figsize=(10,16), constrained_layout = True)
for microphone_index_i in range(0, 8):
    for microphone_index_j in range(0, 4):
        axs[microphone_index_i, microphone_index_j].set_title(str(microphone_index_j+(microphone_index_i*4)+1))
        axs[microphone_index_i, microphone_index_j].plot(signal_measurement.processedData[microphone_index_j+(microphone_index_i*4),:])
        if microphone_index_j != 0:
            plt.setp(axs[microphone_index_i, microphone_index_j], yticklabels=[])
        if microphone_index_i != 7:
            plt.setp(axs[microphone_index_i, microphone_index_j], xticklabels=[])
        if microphone_index_i == 7:
            axs[microphone_index_i, microphone_index_j].set_xlabel("Time (Samples)")
        if microphone_index_j == 0:
            axs[microphone_index_i, microphone_index_j].set_ylabel("Amplitude")
fig.suptitle("RTIS Dev - Microphone Signals")
plt.show()
```

In the example above, a binary file is saved of the recorded measurement. This can be opened in another application for further work.
In the example below, MATLAB is used to process the raw data to microphone signals and plot these.

```matlab
% Read binary data
file_name = 'test_measurement_0.bin';
f_id = fopen(file_name, 'rb');
rawData = fread(f_id, 'uint32');
fclose(f_id);
data =  de2bi(rawData, 32);

% Generate settings for converting to microphone signals. These have to match the recording settings!
fs_pdm = 450e4; % PDM samplefrequency
fs_mic = 450e3; % Microphone samplefrequency
r_min = 0.5; % Range minimum to show
r_max = 5; % Range maximum to show

% PDM demodulation.
[b_pdm, a_pdm] = butter(6, 100e3 / ( fs_pdm / 2));
[b_bpf, a_bpf] = butter(6, [20e3 80e3] / (fs_mic / 2));
data_filtered = (filter(b_pdm, a_pdm, data));
data_filtered_dec = data_filtered(1:10:end, :);
data_mics = filter(b_bpf, a_bpf, data_filtered_dec);

% Subselect the part between the minimum and maximum range wanted.
spl_start = round(r_min * 2 / 343 * fs_mic); 
spl_stop = round(r_max * 2 / 343 * fs_mic);
data_mics = data_mics(spl_start : spl_stop, :);
data_mics = data_mics - mean(data_mics);

%% Plot the recording microphone signals
figure()
for plotcounter = 1 : 16
    subplot(4, 4, plotcounter);
    sig_out1 = data_mics(:, plotcounter) - mean(data_mics(:,plotcounter));
    plot(sig_out1 + 1);
    hold on;
    sig_out2 = data_mics(:, plotcounter + 16) - mean(data_mics(:, plotcounter + 16));
    plot(sig_out2  - 1);
    ylim([-1.5 1.5])
    hold off;
    plottitle = sprintf('Microphone %d and %d', (plotcounter * 2) - 1, plotcounter * 2);
    title(plottitle);
end 
```
