import matplotlib.pyplot as plt
import numpy as np
import os
import re


###############################
##### Variables to change #####
###############################


def get_fit_data(working_directories, key_str="Qi", attenuation=-66):

    #############################################
    ##### Core - doesn't need to be changed #####
    #############################################


    power_data = {}


    for directory in working_directories:

        match = re.search('((-)?\d+)dBm', directory)
        if match:
            attenuation = int(match.group(1))
        else:
            print("no match - assuming attenuation to -70")
            pass

        for filename in os.listdir(directory):
            if filename.endswith(".fit"):
                match = re.search('_((-)?\d+)dBm', filename)
                if not match:
                    continue
                power = int(match.group(1))

                dict = {}

                with open(f"{directory}/{filename}") as file:
                    for line in file:
                        sub = line.split("\t")
                        dict[sub[0]] = float(sub[1])

                power_data[power+attenuation] = dict


    power = []
    key_arr = []

    for key, dict in power_data.items():
        if key < -200 or key > -70:
            continue
        power.append(key)
        key_arr.append(dict[key_str])

    key_arr_sorted = [key_arr for _, key_arr in sorted(zip(power, key_arr))]
    power = sorted(power)

    return power, key_arr_sorted


# x_pre, y_pre, y_err_pre = get_res_data([f"/Users/niklas/Documents/Studium/MasterThesis/XLD/NB/B25-2v2/-10dBm_warm_detailed/Res1", f"/Users/niklas/Documents/Studium/MasterThesis/XLD/NB/B25-2v2/-60dBm_warm_detailed/Res1"], -60, 1e5)
# x_post, y_post, y_err_post = get_res_data([f"/Users/niklas/Documents/Studium/MasterThesis/XLD/NB/B25-2_post_hf/detailed_sweep_v2_-50dBm/Res2"], -60, 1e5)
# x_pre, y_pre, y_err_pre = get_res_data([f"/Users/niklas/Documents/Studium/MasterThesis/XLD/NB/W4-24_-10dBm_warm/Res1", f"/Users/niklas/Documents/Studium/MasterThesis/XLD/NB/W4-24_-60dBm_warm/Res1"], -60, 1e5)
# x_post, y_post, y_err_post = get_res_data([f"/Users/niklas/Documents/Studium/MasterThesis/XLD/NB/B25-2v2/-10dBm_warm_detailed/Res1", f"/Users/niklas/Documents/Studium/MasterThesis/XLD/NB/B25-2v2/-60dBm_warm_detailed/Res1"], -60, 1e5)

# res_id = 5

# for res_id in [1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
#
#     save_path = f"/home/measure/from windows PC/Measurements/Results/NB/P8-1/full_sweep_-70dBm/Res{res_id}"
#
#     pow, q_i = get_fit_data([f"/home/measure/from windows PC/Measurements/Results/NB/P8-1/full_sweep_-70dBm/Res{res_id}"], "Qi")
#     pow, q_i_err = get_fit_data([f"/home/measure/from windows PC/Measurements/Results/NB/P8-1/full_sweep_-70dBm/Res{res_id}"], "Qi_err")
#     # print(len(pow))
#     plt.figure(0)
#     plt.errorbar(pow, q_i, q_i_err)
#     plt.xlabel("Power in dBm (without cable losses)")
#     plt.ylabel("Internal quality factor")
#     plt.savefig(f"{save_path}/q_i_res{res_id}.pdf")
    # plt.show()


#plt.figure(0, [6, 3.8])
#plt.errorbar(x_pre, y_pre, y_err_pre, None, 'o', label="Without HF")
#plt.errorbar(x_post, y_post, y_err_post, None, 'o', label="With HF")
#plt.xlabel('Power (dBm)')
#plt.ylabel('Q_i')
#plt.ylim(0e5,7e5)
#plt.legend()
#plt.gca().ticklabel_format(axis='y', style='plain', useOffset=True)
# plt.ticklabel_format = "scientific"
# plt.savefig(f"{save_directory}/{save_name}.pdf")
#plt.show()
