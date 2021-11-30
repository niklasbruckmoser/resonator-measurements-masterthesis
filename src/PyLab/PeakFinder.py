import numpy as np

def find_peaks(f_data, s21_data, num_peaks):
    """
    Find resonator peaks (or dips)
    :param f_data: the corresponding frecuencies
    :param delay_data: the data as delay (derivative)
    :param num_peaks: the number of peaks that will be marked
    :return: a list containing the frequencies of the peaks
    """
    threshold = 100  # threshold value as number of points (in both directions)

    # delay_data = []
    delay_data = np.diff(s21_data)
    delay_data = np.append(delay_data, 0)

    peak_pos = []

    for _ in range(num_peaks):
        max_val = -1
        max_pos = 0


        for i in range(len(delay_data)):

            delay = delay_data[i]

            # skip points in the vicinity of other peaks
            skip = False
            for peak in peak_pos:
                if abs(i-peak) < threshold:
                    skip = True
                    break

            if skip:
                continue

            if abs(delay) > max_val:
                max_val = abs(delay)
                max_pos = i

        peak_pos.append(max_pos)

    frequencies = []
    for i in peak_pos:
        frequencies.append(f_data[i])

    frequencies.sort()

    return frequencies  # old sorting was by highest derivative, not by frequency

