import math
import sys
import argparse
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import os
import importlib.resources as config_resources
from matplotlib.lines import Line2D


# This function is to get header position from the given array
def get_index(search_input, array_in):
    idx_found = False
    return_idx = None
    for idx, val in enumerate(array_in):
        if val == search_input:
            idx_found = True
            return_idx = idx
            break

    if not idx_found:
        print(f"{search_input} can not be found!")

    return return_idx


def get_draw_info_for_trial_plot(config_info_input, x_array_input, y_array_input):
    x_axis_limit = config_info_input["x_axis_limit"]
    y_axis_limit = config_info_input["y_axis_limit"]
    mean_offset = config_info_input["mean_offset"]
    mean_offset = 1
    axis_adjustment_types = config_info_input["axis_adjustment_types"]
    axis_adjustment_type_number = config_info_input["axis_adjustment_type_number"]
    adjustment_type = axis_adjustment_types[str(axis_adjustment_type_number)]
    print(f"axis_adjustment_type:{adjustment_type}")
    if adjustment_type == "manual":
        x_adjust_limit = {"lower_limit": x_axis_limit[0], "upper_limit": x_axis_limit[1]}
        y_adjust_limit = {"lower_limit": y_axis_limit[0], "upper_limit": y_axis_limit[1]}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    elif adjustment_type == "mean_offset":
        x_adjust_limit = {"lower_limit": int(min(x_array_input)),
                          "upper_limit": int(max(x_array_input))}
        y_adjust_limit = {"lower_limit": round(float(- mean_offset), 2),
                          "upper_limit": round(float(mean_offset), 2)}

        y_mean = np.nanmean(y_array_input)
        temp_array = []
        for num in y_array_input:
            if not np.isnan(num):
                temp_number = num - y_mean
                temp_array.append(temp_number)
            else:
                temp_array.append(num)
        y_array_input = temp_array

        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    else:
        x_adjust_limit = {"lower_limit": int(min(x_array_input)),
                          "upper_limit": int(max(x_array_input))}
        y_adjust_limit = {"lower_limit": round(min(y_array_input), 2),
                          "upper_limit": round(max(y_array_input), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    return x_adjust_limit, y_adjust_limit, x_array_input, y_array_input


def draw_graph_with_overlay(input_dir, trial_plot_info_input, signal_dir_input):
    title = trial_plot_info_input["title"]
    x_label = trial_plot_info_input["x_label"]
    y_label = trial_plot_info_input["y_label"]
    x_data_column_name = "t"
    y_data_column_name = "x"
    graph_line_color = trial_plot_info_input["graph_line_color"]
    graph_line_thickness = trial_plot_info_input["graph_line_thickness"]
    # image_scale = trial_plot_info_input["image_scale"]
    sp_column_name = trial_plot_info_input["sp_column_name"]
    qp_column_name = trial_plot_info_input["qp_column_name"]
    sp_line_color = trial_plot_info_input["sp_line_color"]
    sp_line_thickness = trial_plot_info_input["sp_line_thickness"]
    qp_line_color = trial_plot_info_input["qp_line_color"]
    qp_line_thickness = trial_plot_info_input["qp_line_thickness"]
    output_image_name = trial_plot_info_input["output_image_name"]
    file_to_open = open(input_dir)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count_one = 0

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    x_header_position = get_index(x_data_column_name, header_array)
    y_header_position = get_index(y_data_column_name, header_array)

    x_array = []
    y_array = []
    first_value_recorded = False
    first_value = 0

    for row in rows:
        raw_value = float(row[x_header_position])
        if not first_value_recorded:
            first_value = raw_value
            first_value_recorded = True
        value_input = raw_value - first_value
        x_array.append(value_input)

        y_array.append(float(row[y_header_position]))

    x_limits, y_limits, x_array, y_array = get_draw_info_for_trial_plot(trial_plot_info_input, x_array, y_array)

    x_lower_limit = x_limits["lower_limit"]
    x_upper_limit = x_limits["upper_limit"]
    y_lower_limit = y_limits["lower_limit"]
    y_upper_limit = y_limits["upper_limit"]

    file_to_open = open(signal_dir_input)
    csv_reader2 = csv.reader(file_to_open)
    header_array2 = []
    rows2 = []
    count_one2 = 0

    for row in csv_reader2:
        if count_one2 <= 0:
            header_array2 = row
            count_one2 += 1
        else:
            rows2.append(row)

    # print(header_array2)
    slow_phase_position = get_index(sp_column_name, header_array2)
    quick_phase_position = get_index(qp_column_name, header_array2)

    sp_array = []
    qp_array = []

    for row in rows2:
        sp_value = row[slow_phase_position]
        qp_value = row[quick_phase_position]
        sp_array.append(str(sp_value).lower())
        qp_array.append(str(qp_value).lower())

    # for ind in range(len(sp_array)):
    #     print(sp_array[ind], qp_array[ind])
    #     if sp_array[ind] == "false" and qp_array[ind] == "false":
    #         print("both false")

    for ind in range(len(sp_array)):
        if sp_array[ind] == "true":
            sp_array[ind] = y_array[ind]
        else:
            sp_array[ind] = np.nan

    for ind in range(len(qp_array)):
        if qp_array[ind] == "true":
            qp_array[ind] = y_array[ind]
            previous_ind = ind - 1
            if previous_ind >= 0:
                qp_array[ind - 1] = y_array[ind - 1]

        else:
            qp_array[ind] = np.nan

    # Check maximum of x_array to decide whether it needs to be expended or not
    x_array_max = math.ceil(max(x_array))
    # default figsize 6.4 and 4.8
    if x_array_max >= 10:
        plt.figure(figsize=(x_array_max, 4.8))
    plt.plot(x_array, y_array, color=graph_line_color, linewidth=graph_line_thickness)
    plt.plot(x_array, sp_array, color=sp_line_color, linewidth=sp_line_thickness)
    plt.plot(x_array, qp_array, color=qp_line_color, linewidth=qp_line_thickness)
    gaze_csv_dir = os.path.join(os.path.split(os.path.split(os.path.split(input_dir)[0])[0])[0], "gaze.csv")
    folder_name = os.path.basename(os.path.split(input_dir)[0])
    # trial_id, condition = str(folder_name).split("_", 1)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xlim(x_lower_limit, x_upper_limit)
    plt.ylim(y_upper_limit, y_lower_limit)
    x_axis_array = np.arange(start=min(x_array), stop=max(x_array), step=1)
    plt.xticks(x_axis_array)
    # event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
    # if event_marker_exist:
    #     event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
    #     for marker_time in event_marker_info:
    #         plt.axvline(x=float(marker_time), color=graph_line_color,
    #                     linestyle=":",
    #                     linewidth=graph_line_thickness, label=f"{marker_time}")
    csv_name = os.path.basename(input_dir)
    output_dir = input_dir.replace(csv_name, "")
    display_output_dir = os.path.join(output_dir, output_image_name)
    os.chdir(output_dir)
    plt.savefig(output_image_name)
    plt.close()

    print(f"Trial plot has been saved at:{display_output_dir}")


if __name__ == '__main__':
    folder_dir = r"C:\Users\zawli\Desktop\ABI\jtur_10_01_23_long\results\okn\clip-2-trial-1-2-disks"
    config_dir = r"C:\Users\zawli\Documents\GitHub\okntool\development\oknserver_graph_plot_config.json"
    signal_csv_dir = r"C:\Users\zawli\Desktop\ABI\jtur_10_01_23_long\results\okn\clip-2-trial-1-2-disks\signal.csv"
    with open(config_dir) as f:
        plot_config_info = json.load(f)
    config_info = plot_config_info["trial_plot"]
    draw_graph_with_overlay(signal_csv_dir, config_info, signal_csv_dir)

