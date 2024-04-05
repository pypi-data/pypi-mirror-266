"""RTIS Generate Settings

This is a collection of methods used to generate recording and processing files for usage in RTIS DEV.

By Cosys-Lab, University of Antwerp
Contributors:
Wouter Jansen
Arne Aerts
Dennis Laurijssen
Jan Steckel
"""

import numpy as np
import scipy.io
import scipy.signal
import math

#######################################################
# Recursive Zonal Equal Area (EQ) Sphere Partitioning #
#######################################################
# Only usage of 2 dimensions (N=2) is supported.
# Translation to Python of MATLAB Toolbox
# eq_sphere_partitions by Penguian (2021)
# https://github.com/penguian/eq_sphere_partitions


def sradius_of_cap(area):
    return 2 * np.arcsin(np.sqrt(area / np.pi) / 2)


def area_of_ideal_region(N):
    power = (2 + 1) / 2
    return (np.divide(2 * pow(np.pi, power), scipy.special.gamma(power))) / N


def ideal_collar_angle(N):
    return pow(area_of_ideal_region(N), 1 / 2)


def num_collars(N, cpolar, angle):
    if angle > 0 and N > 2:
        return np.max([1, int(np.round((np.pi - 2 * cpolar) / angle))])
    else:
        return 0


def area_of_cap(scap):
    return 4 * np.pi * pow(np.sin(scap / 2), 2)


def area_of_collar(atop, abot):
    return area_of_cap(abot) - area_of_cap(atop)


def ideal_region_list(N, cpolar, ncollars):
    rregions = np.zeros((2 + ncollars,))
    rregions[0] = 1
    if ncollars > 0:
        afitting = (np.pi - 2 * cpolar) / ncollars
        area = area_of_ideal_region(N)
        for collarn_idx in range(0, ncollars):
            idealcollararea = area_of_collar(cpolar + collarn_idx * afitting, cpolar + (collarn_idx + 1) * afitting)
            rregions[1 + collarn_idx] = idealcollararea / area
    rregions[1 + ncollars] = 1
    return rregions


def round_to_naturals(N, rregions):
    nregions = np.copy(rregions)
    discrepancy = 0
    for zone_idx in range(0, rregions.size):
        nregions[zone_idx] = np.round(rregions[zone_idx] + discrepancy)
        discrepancy = discrepancy + rregions[zone_idx] - nregions[zone_idx]
    return nregions


def c_polar(N):
    if N == 1:
        return np.pi
    elif N == 2:
        return np.pi / 2
    else:
        area = area_of_ideal_region(N)
        s_cap = 2 * np.arcsin(np.sqrt(area / np.pi) / 2)
        return s_cap


def cap_colats(N, cpolar, nregions):
    ccaps = np.zeros((nregions.size,))
    ccaps[0] = cpolar
    idearegionarea = area_of_ideal_region(N)
    ncollars = nregions.size - 2
    subtotal = 1
    for collar_idx in range(0, ncollars):
        subtotal = int(subtotal + nregions[collar_idx + 1])
        ccaps[collar_idx + 1] = sradius_of_cap(subtotal * idearegionarea)

    ccaps[ncollars + 1] = np.pi
    return ccaps


def eq_caps(dim, N):
    if dim == 1:
        sector = np.arange(1, int(N) + 1)
        scap = sector * 2 * np.pi / N
        nregions = np.ones((sector.size,))
        return scap, nregions
    elif N == 1:
        return np.pi, 1
    else:
        cpolar = c_polar(N)
        angle = ideal_collar_angle(N)
        ncollars = num_collars(N, cpolar, angle)
        rregions = ideal_region_list(N, cpolar, ncollars)
        nregions = round_to_naturals(N, rregions)
        scap = cap_colats(N, cpolar, nregions)
        return scap, nregions


def circle_offset(ntop, nbot):
    return (1 / nbot - 1 / ntop) / 2 + math.gcd(ntop, nbot) / (2 * ntop * nbot)


def eq_point_set_polar(dim, N):
    if N == 1:
        return np.zeros((2, 1))
    else:
        (acap, nregions) = eq_caps(dim, N)

        if dim == 1:
            return acap - np.pi / N
        else:
            ncollars = nregions.size - 2
            cachesize = int(np.floor(ncollars / 2))
            cache = [None] * (cachesize + 1)
            pointss = np.zeros((2, N))
            pointn = 2
            offset = 0

            for collar_idx in range(0, ncollars):
                atop = acap[collar_idx]
                abot = acap[collar_idx + 1]
                nincollar = nregions[collar_idx + 1]
                twincollar_idx = ncollars - collar_idx
                if twincollar_idx <= cachesize and cache[twincollar_idx - 1].size == nincollar:
                    pointsl = cache[twincollar_idx - 1]
                else:
                    pointsl = eq_point_set_polar(dim - 1, nincollar)
                    cache[collar_idx] = pointsl
                apoint = (atop + abot) / 2
                pointln = np.arange(0, pointsl.size)
                pointss[0, pointn + pointln - 1] = np.mod(pointsl[pointln] + 2 * np.pi * offset, np.pi * 2)
                offset = offset + circle_offset(int(nincollar), int(nregions[collar_idx + 2]))
                offset = offset - int(np.floor(offset))
                pointss[1, pointn + pointln - 1] = apoint
                pointn = pointn + pointsl.size
            pointss[:, pointn - 1] = 0
            pointss[1, pointn - 1] = np.pi
            return pointss


def polar2cart(points):
    dim = points.shape[0]
    n = points.shape[1]
    x = np.zeros((dim + 1, n))
    sinprod = 1
    for k in range(dim, 1, -1):
        x[k, :] = np.multiply(np.cos(points[1, :]), sinprod)
        sinprod = np.multiply(np.sin(points[1, :]), sinprod)
    x[1, :] = np.multiply(sinprod, np.sin(points[0, :]))
    x[0, :] = np.multiply(sinprod, np.cos(points[0, :]))
    r = np.sqrt(np.sum(np.power(x, 2), 0))
    mask = np.isin(r, 1)
    if r[mask].size > 0:
        x[:, mask] = np.divide(x[:, mask], np.ones((dim + 1, 1)) * r[mask])
    return x


#######################################################
# Additional functions #
#######################################################


def fm_sweep(maxf, minf, dacfs, duration, amplitude, winprct):
    duration = duration * pow(10, -3)
    t = np.arange(0, duration + 1 / dacfs, 1 / dacfs)
    sig = amplitude * (np.sin(2 * np.pi * (duration / (1 / minf - 1 / maxf)) * (
            np.log(1 / maxf + t * (1 / minf - 1 / maxf) / duration) - np.log(1 / maxf))))
    length_window = np.round(sig.size * 2 * winprct / 100)
    window_short = scipy.signal.windows.hann(int(length_window) + 2)
    window_short = window_short[1:-1]
    window_on = window_short[0: int(np.ceil(length_window / 2))]
    window_off = window_short[int(np.ceil(length_window / 2)):]
    window = np.ones(sig.size)
    window[0:window_on.size] = window_on
    window[window.size - window_off.size:] = window_off
    sig = np.multiply(sig, window)
    return sig


def azel_2_delayints(az_vec, el_vec, mic_coordinates, Fs_ADC):
    az_vec_d = np.deg2rad(az_vec)
    el_vec_d = np.deg2rad(el_vec)
    n_angles = az_vec.size
    n_mics = mic_coordinates.shape[0]
    [x_pos, y_pos, z_pos] = sph2cart(az_vec_d, el_vec_d, 100 * np.ones((1, n_angles)))

    dir_coordinates = np.transpose(np.concatenate((y_pos, z_pos, x_pos), axis=0))
    mic_coordinates_ok = mic_coordinates

    delay_matrix = np.zeros((n_angles, n_mics), dtype=int)
    error_matrix = np.zeros((n_angles, n_mics))
    for angle_cnt in range(0, n_angles):
        cur_dir_coord = dir_coordinates[angle_cnt, :]
        a = np.tile(cur_dir_coord, (n_mics, 1))
        b = mic_coordinates_ok - a
        dist_vec = np.sqrt(np.sum(np.power(b, 2), 1))
        dist_diff_vec = dist_vec - dist_vec[0]
        time_delay_vec = np.round(dist_diff_vec / 343 * Fs_ADC)
        error_vec = time_delay_vec - (dist_diff_vec / 343 * Fs_ADC)
        error_matrix[angle_cnt, :] = error_vec / Fs_ADC
        time_delay_vec = time_delay_vec - np.min(time_delay_vec)
        delay_matrix[angle_cnt, :] = time_delay_vec.astype(int)
    return delay_matrix, dir_coordinates, error_matrix


def cart2sph(x, y, z):
    azimuth = np.arctan2(y, x)
    elevation = np.arctan2(z, np.sqrt(x ** 2 + y ** 2))
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    return azimuth, elevation, r


def sph2cart(azimuth, elevation, r):
    x = r * np.cos(elevation) * np.cos(azimuth)
    y = r * np.cos(elevation) * np.sin(azimuth)
    z = r * np.sin(elevation)
    return x, y, z


def get_disabled_microphone_list(package_directory, mLayoutName="eRTIS_v3D1"):

    mat = scipy.io.loadmat(package_directory + "/config/microphoneLayouts/" + mLayoutName + "/mic_coordinates.mat")
    micCoordsFinal = mat["mic_pos_final_pos"]
    micCoordsFinal = np.divide(micCoordsFinal, 1000)

    disableList = []
    for i in range(0, micCoordsFinal.shape[0]):
        if np.isnan(micCoordsFinal[i, 0]) and np.isnan(micCoordsFinal[i, 1]):
            disableList.append(i)

    return disableList


def generate_processing_settings(package_directory, mLayoutName="eRTIS_v3D1", mode=1,
                                 directions=181, rMin=0.5, rMax=5, esSubFactor=10, adcFs=4500000,
                                 azimuthLowLimit=-90, azimuthHighLimit=90,
                                 elevationLowLimit=-90, elevationHighLimit=90):
    mat = scipy.io.loadmat(package_directory + "/config/microphoneLayouts/"
                           + mLayoutName + "/mic_coordinates.mat")
    micCoordsFinal = mat["mic_pos_final_pos"]
    micCoordsFinal = np.divide(micCoordsFinal, 1000)
    micCoordinates = np.concatenate((micCoordsFinal,
                                    np.zeros((micCoordsFinal.shape[0], 1), dtype=np.float64)), axis=1)
    micCoordinates[:, 0] = micCoordinates[:, 0] - np.nanmean(micCoordinates[:, 0])
    micCoordinates[:, 1] = micCoordinates[:, 1] - np.nanmean(micCoordinates[:, 1])
    micCoordinates[np.isnan(micCoordinates)] = 0

    adcFs = adcFs / 10

    if mode == 1:
        # 2D
        step = (azimuthHighLimit - azimuthLowLimit) / (directions - 1)
        azVecAzEl = np.arange(azimuthLowLimit, azimuthHighLimit + step, step)
        elVecAzEl = np.zeros((azVecAzEl.size,))
    else:
        # 3D
        surfacePart = (np.deg2rad(azimuthHighLimit) - np.deg2rad(azimuthLowLimit)) * (
                       np.sin(np.deg2rad(elevationHighLimit)) - np.sin(np.deg2rad(elevationLowLimit)))
        scaler = 4 * np.pi / surfacePart
        nEqPts = np.round(directions * scaler).astype(int)
        pointsPolar = eq_point_set_polar(2, nEqPts)
        pointsXYZ = polar2cart(pointsPolar)
        initialAZVec, initialElVec, initialRhoVec = cart2sph(pointsXYZ[0, :], pointsXYZ[1, :], pointsXYZ[2, :])
        idxsAllowed = ((np.deg2rad(azimuthLowLimit) < initialAZVec) &
                       (np.deg2rad(azimuthHighLimit) > initialAZVec) &
                       (np.deg2rad(elevationLowLimit) < initialElVec) &
                       (np.deg2rad(elevationHighLimit) > initialElVec) &
                       (pointsXYZ[0, :] > 0))
        pointsAllowed = pointsXYZ[:, idxsAllowed]
        azVec, elVec, rhoVec = cart2sph(pointsAllowed[0, :], pointsAllowed[1, :], pointsAllowed[2, :])
        azVecAzEl = np.rad2deg(azVec)
        elVecAzEl = np.rad2deg(elVec)

    delayMatrix, dirCoordinatesAzSlice, error_matrix = azel_2_delayints(azVecAzEl, elVecAzEl, micCoordinates, adcFs)

    splStart = int(np.round(rMin * 2 / 343 * adcFs))
    splStop = int(np.round(rMax * 2 / 343 * adcFs))
    nRanges = int(np.ceil((splStop - splStart + 1) / esSubFactor))
    rVecAzEl = np.linspace(rMin, rMax, nRanges)
    azVec = np.deg2rad(azVecAzEl)
    elVec = np.deg2rad(elVecAzEl)
    directionsMatrix = np.transpose(np.vstack((azVec, elVec)))

    return np.transpose(delayMatrix).astype(np.int32).copy(), directionsMatrix.copy(), rVecAzEl.copy()


def generate_recording_settings(dacFs=450000, callLength=2.5, callFMin=25000, callFMax=50000):
    sigDAC = fm_sweep(callFMax, callFMin, dacFs, callLength, 1, 10)
    sigADC = fm_sweep(callFMax, callFMin, dacFs, callLength, 1, 10)

    return sigADC, sigDAC
