import math
import sys
import argparse
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
import os
import importlib.resources as okntool_resources
from matplotlib.lines import Line2D
import chevron
import cv2
import subprocess
from ehdg_tools.ehdg_buffers import TinyFillBuffer

logmar_level_array = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2,
                      "no logMAR", "right_down", "right_up", "left_down", "left_up"]


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


# This function is to translate disk condition string to logmar value
def disk_to_logmar(disk_string_input):
    disk_logmar_equivalent = {"disk-condition-1-1": 1.0, "disk-condition-1-2": 1.0, "disk-condition-2-1": 0.9,
                              "disk-condition-2-2": 0.9, "disk-condition-3-1": 0.8, "disk-condition-3-2": 0.8,
                              "disk-condition-4-1": 0.7, "disk-condition-4-2": 0.7, "disk-condition-5-1": 0.6,
                              "disk-condition-5-2": 0.6, "disk-condition-6-1": 0.5, "disk-condition-6-2": 0.5,
                              "disk-condition-7-1": 0.4, "disk-condition-7-2": 0.4, "disk-condition-8-1": 0.3,
                              "disk-condition-8-2": 0.3, "disk-condition-9-1": 0.2, "disk-condition-9-2": 0.2,
                              "disk-condition-10-1": 0.1, "disk-condition-10-2": 0.1, "disk-condition-11-1": 0.0,
                              "disk-condition-11-2": 0.0, "disk-condition-12-1": -0.1, "disk-condition-12-2": -0.1,
                              "disk-condition-13-1": -0.2, "disk-condition-13-2": -0.2,
                              "no-disk-condition": "no logMAR",
                              "right_down": "right_down", "right_up": "right_up",
                              "left_down": "left_down", "left_up": "left_up"}

    try:
        out_string = disk_logmar_equivalent[disk_string_input]
    except KeyError:
        out_string = disk_string_input
    if out_string not in logmar_level_array:
        logmar_level_array.append(out_string)

    return out_string


# This function is to get trial id, disk_string, logmar_level from the given dir string
def get_trial_id_name(string_input):
    start_index = string_input.find("trial-")
    end_index = string_input.find(r"\result")
    trial_disk_string = string_input[start_index:end_index]
    trial_string, disk_string = str(trial_disk_string).split("_", 1)
    logmar_level = disk_to_logmar(disk_string)
    return trial_string, disk_string, logmar_level


# This function is to produce okn detector summary csv directory from the given dir string
def get_okn_detector_summary_csv_dir(string_input):
    start_index = 0
    end_marker = "trials"
    end_index = string_input.find(end_marker) + len(end_marker)
    output_string = os.path.join(string_input[start_index:end_index], "okn_detector_summary.csv")
    print(f"okn detector summary csv dir {output_string}")
    return output_string


# This function is to draw a graph with slow phase and quick phase overlay from the given config info
def draw_graph_with_overlay(input_dir, trial_plot_info_input, signal_dir_input, output_file_dir_input=None):
    title = trial_plot_info_input["title"]
    x_label = trial_plot_info_input["x_label"]
    y_label = trial_plot_info_input["y_label"]
    x_data_column_name = trial_plot_info_input["x_data_column_name"]
    y_data_column_name = trial_plot_info_input["y_data_column_name"]
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
    trial_id, condition = str(folder_name).split("_", 1)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xlim(x_lower_limit, x_upper_limit)
    plt.ylim(y_upper_limit, y_lower_limit)
    x_axis_array = np.arange(start=min(x_array), stop=max(x_array), step=1)
    plt.xticks(x_axis_array)
    event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
    if event_marker_exist:
        event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
        for marker_time in event_marker_info:
            plt.axvline(x=float(marker_time), color=graph_line_color,
                        linestyle=":",
                        linewidth=graph_line_thickness, label=f"{marker_time}")
    csv_name = os.path.basename(input_dir)
    output_dir = input_dir.replace(csv_name, "")
    display_output_dir = os.path.join(output_dir, output_image_name)
    if output_file_dir_input:
        display_output_dir = output_file_dir_input
        output_image_name = os.path.basename(output_file_dir_input)
        output_dir = os.path.join(output_file_dir_input, os.pardir)
    os.chdir(output_dir)
    plt.savefig(output_image_name)
    plt.close()

    print(f"Trial plot has been saved at:{display_output_dir}")


# This function is to produce a plan as an array from the given folder to be used in drawing combined summary plot
def get_plot_info(data_dir, plot_info_input):
    x_label = plot_info_input["x_label"]
    y_label = plot_info_input["y_label"]
    x_data_column_name = plot_info_input["x_data_column_name"]
    y_data_column_name = plot_info_input["y_data_column_name"]
    x_axis_limit = plot_info_input["x_axis_limit"]
    y_axis_limit = plot_info_input["y_axis_limit"]
    mean_offset = plot_info_input["mean_offset"]
    axis_adjustment_types = plot_info_input["axis_adjustment_types"]
    axis_adjustment_type_number = plot_info_input["axis_adjustment_type_number"]
    signal_csv_folder_name = plot_info_input["signal_csv_folder_name"]
    signal_csv_name = plot_info_input["signal_csv_name"]
    sp_column_name = plot_info_input["sp_column_name"]
    qp_column_name = plot_info_input["qp_column_name"]
    sp_line_color = plot_info_input["sp_line_color"]
    sp_line_thickness = plot_info_input["sp_line_thickness"]
    qp_line_color = plot_info_input["qp_line_color"]
    qp_line_thickness = plot_info_input["qp_line_thickness"]
    summary_csv_name = plot_info_input["summary_csv_name"]
    folder_array = get_folder_name_from_dir(data_dir, "trial_id", "disk_condition", summary_csv_name)

    adjustment_type = axis_adjustment_types[str(axis_adjustment_type_number)]
    if adjustment_type == "mean_offset":
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, None,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out that folder name from the folder array
        if ignore_folder_array:
            folder_array = [folder for folder in folder_array if folder not in ignore_folder_array]
        for folder_name in folder_array:
            trial_id, disk_condition = str(folder_name).split("_", 1)
            data_dir_to_be_used = os.path.join(data_dir, folder_name, f"updated_{folder_name}.csv")
            x_array = get_data_array(data_dir_to_be_used, x_data_column_name)
            y_array = get_data_array(data_dir_to_be_used, y_data_column_name)
            y_mean = np.nanmean(y_array)
            y_array = [value - y_mean for value in y_array]
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_folder_name, signal_csv_name)
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": disk_condition,
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(disk_condition)}
            plot_info_array.append(plot_info)
    else:
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, None,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out that folder name from the folder array
        if ignore_folder_array:
            folder_array = [folder for folder in folder_array if folder not in ignore_folder_array]
        for folder_name in folder_array:
            trial_id, disk_condition = str(folder_name).split("_", 1)
            data_dir_to_be_used = os.path.join(data_dir, folder_name, f"updated_{folder_name}.csv")
            x_array = get_data_array(data_dir_to_be_used, x_data_column_name)
            y_array = get_data_array(data_dir_to_be_used, y_data_column_name)
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_folder_name, signal_csv_name)
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": disk_condition,
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(disk_condition)}
            plot_info_array.append(plot_info)

    return plot_info_array, adjust_limit_dict


# This function is to retrieve folder names from the given csv
def get_folder_name_from_dir(dir_input, trial_id_header_input, disk_condition_header_input,
                             summary_csv_name_input):
    csv_dir = os.path.join(dir_input, summary_csv_name_input)

    file_to_open = open(csv_dir)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count_one = 0
    output_array = []

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    trial_id_header_position = get_index(trial_id_header_input, header_array)
    disk_condition_header_position = get_index(disk_condition_header_input, header_array)

    for row in rows:
        trial_string_raw = row[trial_id_header_position]
        disk_string_raw = row[disk_condition_header_position]
        folder_name_input = f"{trial_string_raw}_{disk_string_raw}"
        output_array.append(folder_name_input)

    return output_array


# This function is to retrieve the data array from the given csv and header name
def get_data_array(data_dir, header_name_input):
    file_to_open = open(data_dir)
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

    header_position = get_index(header_name_input, header_array)

    output_array = []
    first_value_recorded = False
    first_value = 0

    if "timestamp" in str(header_name_input):
        for row in rows:
            raw_value = float(row[header_position])
            if not first_value_recorded:
                first_value = raw_value
                first_value_recorded = True
            value_input = raw_value - first_value
            output_array.append(value_input)
    else:
        for row in rows:
            output_array.append(float(row[header_position]))

    return output_array


# This function is to retrieve the slow phase and quick phase data arrays from the given signal csv
def get_sp_and_qp_array(signal_dir_input, sp_column_name_input, qp_column_name_input, y_data_array_input):
    sp_array = []
    qp_array = []
    file_to_open = open(signal_dir_input)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count = 0

    for row in csv_reader:
        if count <= 0:
            header_array = row
            count += 1
        else:
            rows.append(row)

    slow_phase_position = get_index(sp_column_name_input, header_array)
    quick_phase_position = get_index(qp_column_name_input, header_array)

    for row in rows:
        sp_value = row[slow_phase_position]
        qp_value = row[quick_phase_position]
        sp_array.append(str(sp_value).lower())
        qp_array.append(str(qp_value).lower())

    for ind in range(len(sp_array)):
        if sp_array[ind] == "true":
            sp_array[ind] = y_data_array_input[ind]
        else:
            sp_array[ind] = np.nan

    for ind in range(len(qp_array)):
        if qp_array[ind] == "true":
            qp_array[ind] = y_data_array_input[ind]
            previous_ind = ind - 1
            if previous_ind >= 0:
                qp_array[ind - 1] = y_data_array_input[ind - 1]
        else:
            qp_array[ind] = np.nan

    return sp_array, qp_array


# The main function to plot the combined graph with plan array/plot info
# If max graph in a row is "none", there is no limitation of graph number in a row
def plot_combined_graph(folder_dir_input, summary_plot_info_input, output_file_dir_input=None):
    graph_line_color = summary_plot_info_input["graph_line_color"]
    graph_line_thickness = summary_plot_info_input["graph_line_thickness"]
    max_graph_in_a_row = summary_plot_info_input["max_graph_in_a_row"]
    image_scale = summary_plot_info_input["image_scale"]

    plot_data_array, auto_adjust_info = get_plot_info(folder_dir_input, summary_plot_info_input)

    x_adjust_limit = auto_adjust_info["x_adjust_limit"]
    x_lower_limit = x_adjust_limit["lower_limit"]
    x_upper_limit = x_adjust_limit["upper_limit"]
    y_adjust_limit = auto_adjust_info["y_adjust_limit"]
    y_lower_limit = y_adjust_limit["lower_limit"]
    y_upper_limit = y_adjust_limit["upper_limit"]

    output_image_name = summary_plot_info_input["output_image_name"]
    display_output_dir = os.path.join(folder_dir_input, output_image_name)
    gaze_csv_dir = str(folder_dir_input).replace(os.path.basename(folder_dir_input), "gaze.csv")
    output_dir = folder_dir_input
    if output_file_dir_input:
        display_output_dir = output_file_dir_input
        output_image_name = os.path.basename(output_file_dir_input)
        output_dir = os.path.join(output_file_dir_input, os.pardir)
    print(f"Gaze csv dir:{gaze_csv_dir}")

    if type(max_graph_in_a_row) == str and str(max_graph_in_a_row).lower() == "none":
        final_plot_array = []
        for logmar_level in logmar_level_array:
            temp_logmar_info_array = []

            for info in plot_data_array:
                if info["logmar"] == logmar_level:
                    temp_logmar_info_array.append(info)

            if len(temp_logmar_info_array) > 0:
                temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
                final_plot_array.append(temp_dict)

        if len(final_plot_array) > 0:
            final_row_length = len(final_plot_array)
            final_column_length = 0
            for plot_info in final_plot_array:
                info_array = plot_info["info_array"]
                if len(info_array) > final_column_length:
                    final_column_length = len(info_array)

            # print(final_row_length)
            # print(final_column_length)
            if final_row_length <= 1:
                plot_info_len = len(final_plot_array)
                if plot_info_len <= 1:
                    if len(final_plot_array[0]["info_array"]) <= 1:
                        plot_info = final_plot_array[0]
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info = info_array[0]
                        x_array = info["x_array"]
                        y_array = info["y_array"]
                        x_label = info["x_label"]
                        y_label = info["y_label"]
                        sp_array = info["sp_array"]
                        sp_line_color = info["sp_line_color"]
                        sp_line_thickness = info["sp_line_thickness"]
                        qp_array = info["qp_array"]
                        qp_line_color = info["qp_line_color"]
                        qp_line_thickness = info["qp_line_thickness"]
                        trial_id = info["trial_id"]
                        if type(logmar_level) is float:
                            axs_title = f"{trial_id}(logMAR {logmar_level})"
                        else:
                            axs_title = f"{trial_id}({logmar_level})"
                        plt.plot(x_array, y_array, color=graph_line_color, linewidth=graph_line_thickness)
                        plt.plot(x_array, sp_array, color=sp_line_color, linewidth=sp_line_thickness)
                        plt.plot(x_array, qp_array, color=qp_line_color, linewidth=qp_line_thickness)
                        plt.title(axs_title)
                        plt.xlabel(x_label)
                        plt.ylabel(y_label)
                        os.chdir(output_dir)
                        plt.savefig(output_image_name)
                        plt.close()
                    else:
                        fig, axs = plt.subplots(final_row_length, final_column_length,
                                                figsize=(final_column_length * image_scale,
                                                         final_row_length * image_scale))
                        for row_index, plot_info in enumerate(final_plot_array):
                            # print(row_index)
                            logmar_level = plot_info["logmar_level"]
                            info_array = plot_info["info_array"]
                            info_array_length = len(info_array)
                            num_plot_to_be_deleted = 0
                            if info_array_length < int(final_column_length):
                                num_plot_to_be_deleted = final_column_length - info_array_length
                            for column_index, info in enumerate(info_array):
                                # print(column_index)
                                x_array = info["x_array"]
                                y_array = info["y_array"]
                                x_label = info["x_label"]
                                y_label = info["y_label"]
                                sp_array = info["sp_array"]
                                sp_line_color = info["sp_line_color"]
                                sp_line_thickness = info["sp_line_thickness"]
                                qp_array = info["qp_array"]
                                qp_line_color = info["qp_line_color"]
                                qp_line_thickness = info["qp_line_thickness"]
                                trial_id = info["trial_id"]
                                if type(logmar_level) is float:
                                    axs_title = f"{trial_id}(logMAR {logmar_level})"
                                else:
                                    axs_title = f"{trial_id}({logmar_level})"
                                axs[column_index].plot(x_array, y_array, color=graph_line_color,
                                                       linewidth=graph_line_thickness)
                                axs[column_index].plot(x_array, sp_array, color=sp_line_color,
                                                       linewidth=sp_line_thickness)
                                axs[column_index].plot(x_array, qp_array, color=qp_line_color,
                                                       linewidth=qp_line_thickness)
                                axs[column_index].set_title(axs_title)
                                axs[column_index].set_xlim([x_lower_limit, x_upper_limit])
                                axs[column_index].set_ylim([y_lower_limit, y_upper_limit])
                                x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                                axs[column_index].set_xticks(x_axis_array)
                                # # Hide the right and top spines
                                # axs.spines.right.set_visible(False)
                                # axs.spines.top.set_visible(False)
                                for ax in axs.flat:
                                    ax.set(xlabel=x_label, ylabel=y_label)

                            if num_plot_to_be_deleted > 0:
                                for index in range(num_plot_to_be_deleted):
                                    # print(int(final_column_length) - index)
                                    column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                    axs[row_index, column_index_to_be_deleted].set_axis_off()

                            # Hide x labels and tick labels for top plots and y ticks for right plots.
                            for ax in axs.flat:
                                ax.label_outer()

                        plt.tight_layout()
                        os.chdir(output_dir)
                        fig.savefig(output_image_name)
                        plt.close()
                else:
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_scale,
                                                     final_row_length * image_scale))
                    for row_index, plot_info in enumerate(final_plot_array):
                        # print(row_index)
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            # print(column_index)
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                axs_title = f"{trial_id}({logmar_level})"
                            axs[column_index].plot(x_array, y_array, color=graph_line_color,
                                                   linewidth=graph_line_thickness)
                            axs[column_index].plot(x_array, sp_array, color=sp_line_color, linewidth=sp_line_thickness)
                            axs[column_index].plot(x_array, qp_array, color=qp_line_color, linewidth=qp_line_thickness)
                            axs[column_index].set_title(axs_title)
                            axs[column_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[column_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[column_index].set_xticks(x_axis_array)
                            # # Hide the right and top spines
                            # axs.spines.right.set_visible(False)
                            # axs.spines.top.set_visible(False)
                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
            else:
                if final_column_length <= 1:
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_scale,
                                                     final_row_length * image_scale))

                    for row_index, plot_info in enumerate(final_plot_array):
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                axs_title = f"{trial_id}({logmar_level})"
                            # Check maximum of x_array to decide whether it needs to be expended or not
                            x_array_max = math.ceil(max(x_array))
                            # default figsize 6.4 and 4.8
                            if x_array_max >= 10:
                                # axs[row_index].figure(figsize=(x_array_max, 4.8))
                                fig.set_figwidth((x_array_max * image_scale) / 8)
                                fig.set_figheight((final_row_length * image_scale) / 2)
                            axs[row_index].plot(x_array, y_array, color=graph_line_color,
                                                linewidth=graph_line_thickness)
                            axs[row_index].plot(x_array, sp_array, color=sp_line_color,
                                                linewidth=sp_line_thickness)
                            axs[row_index].plot(x_array, qp_array, color=qp_line_color,
                                                linewidth=qp_line_thickness)
                            axs[row_index].set_title(axs_title)
                            axs[row_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[row_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[row_index].set_xticks(x_axis_array)
                            event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                            if event_marker_exist:
                                event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                for marker_time in event_marker_info:
                                    axs[row_index].axvline(x=float(marker_time),
                                                           color=graph_line_color,
                                                           linestyle=":",
                                                           linewidth=graph_line_thickness)

                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
                else:
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_scale,
                                                     final_row_length * image_scale))

                    for row_index, plot_info in enumerate(final_plot_array):
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                axs_title = f"{trial_id}({logmar_level})"
                            axs[row_index, column_index].plot(x_array, y_array, color=graph_line_color,
                                                              linewidth=graph_line_thickness)
                            axs[row_index, column_index].plot(x_array, sp_array, color=sp_line_color,
                                                              linewidth=sp_line_thickness)
                            axs[row_index, column_index].plot(x_array, qp_array, color=qp_line_color,
                                                              linewidth=qp_line_thickness)
                            axs[row_index, column_index].set_title(axs_title)
                            axs[row_index, column_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[row_index, column_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[row_index, column_index].set_xticks(x_axis_array)

                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
            print(f"Summary plot has been saved at:{display_output_dir}")
        else:
            print("There is nothing to plot")
    else:
        if int(max_graph_in_a_row) <= 0:
            print(f"Max graph in a row must be greater than zero but the input is {int(max_graph_in_a_row)}")
        else:
            final_plot_array = []
            for logmar_level in logmar_level_array:
                temp_logmar_info_array = []

                for info in plot_data_array:
                    if info["logmar"] == logmar_level:
                        if len(temp_logmar_info_array) >= max_graph_in_a_row:
                            temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
                            final_plot_array.append(temp_dict)
                            temp_logmar_info_array = [info]
                        else:
                            temp_logmar_info_array.append(info)

                if len(temp_logmar_info_array) > 0:
                    temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
                    final_plot_array.append(temp_dict)

            if len(final_plot_array) > 0:
                final_row_length = len(final_plot_array)
                final_column_length = 0
                for plot_info in final_plot_array:
                    info_array = plot_info["info_array"]
                    if len(info_array) > final_column_length:
                        final_column_length = len(info_array)

                # print(final_row_length)
                # print(final_column_length)
                fig, axs = plt.subplots(final_row_length, final_column_length,
                                        figsize=(10 * final_row_length, final_column_length))

                for row_index, plot_info in enumerate(final_plot_array):
                    logmar_level = plot_info["logmar_level"]
                    info_array = plot_info["info_array"]
                    info_array_length = len(info_array)
                    num_plot_to_be_deleted = 0
                    if info_array_length < int(max_graph_in_a_row):
                        num_plot_to_be_deleted = max_graph_in_a_row - info_array_length
                    for column_index, info in enumerate(info_array):
                        x_array = info["x_array"]
                        y_array = info["y_array"]
                        x_label = info["x_label"]
                        y_label = info["y_label"]
                        trial_id = info["trial_id"]
                        if type(logmar_level) is float:
                            axs_title = f"{trial_id}(logMAR {logmar_level})"
                        else:
                            axs_title = f"{trial_id}({logmar_level})"
                        axs[row_index, column_index].plot(x_array, y_array, color="black", linewidth=1)
                        axs[row_index, column_index].set_title(axs_title)
                        axs[row_index, column_index].set_ylim([0.4, 0.5])
                        # # Hide the right and top spines
                        # axs[row_index, column_index].spines['right'].set_visible(False)
                        # axs[row_index, column_index].spines['top'].set_visible(False)
                        for ax in axs.flat:
                            ax.set(xlabel=x_label, ylabel=y_label)

                    if num_plot_to_be_deleted > 0:
                        for index in range(num_plot_to_be_deleted):
                            # print(int(max_graph_in_a_row_input) - index)
                            column_index_to_be_deleted = int(max_graph_in_a_row) - (index + 1)
                            axs[row_index, column_index_to_be_deleted].set_axis_off()

                    # Hide x labels and tick labels for top plots and y ticks for right plots.
                    for ax in axs.flat:
                        ax.label_outer()

                plt.tight_layout()
                os.chdir(output_dir)
                fig.savefig(f"okn_detector_summary.png")
                plt.close()
                print(f"Summary plot has been saved at:{display_output_dir}")
            else:
                print("There is nothing to plot")


# The main function to plot the combined tidy graph with plan array/plot info
def draw_tidy_graph(folder_dir_input, tidy_plot_info_input, output_file_dir_input=None):
    graph_line_color = tidy_plot_info_input["graph_line_color"]
    graph_line_thickness = tidy_plot_info_input["graph_line_thickness"]
    x_label = tidy_plot_info_input["x_label"]
    x_label_x_position = tidy_plot_info_input["x_label_x_position"]
    x_label_y_position = tidy_plot_info_input["x_label_y_position"]
    x_label_alignment = tidy_plot_info_input["x_label_alignment"]
    x_label_rotation = tidy_plot_info_input["x_label_rotation"]
    x_label_weight = tidy_plot_info_input["x_label_weight"]
    x_label_font_size = tidy_plot_info_input["x_label_font_size"]
    y_label = tidy_plot_info_input["y_label"]
    y_label_x_position = tidy_plot_info_input["y_label_x_position"]
    y_label_y_position = tidy_plot_info_input["y_label_y_position"]
    y_label_alignment = tidy_plot_info_input["y_label_alignment"]
    y_label_rotation = tidy_plot_info_input["y_label_rotation"]
    y_label_weight = tidy_plot_info_input["y_label_weight"]
    y_label_font_size = tidy_plot_info_input["y_label_font_size"]
    main_boundary_position = tidy_plot_info_input["main_boundary_position"]
    main_boundary_width = tidy_plot_info_input["main_boundary_width"]
    main_boundary_height = tidy_plot_info_input["main_boundary_height"]
    main_boundary_color = tidy_plot_info_input["main_boundary_color"]
    main_boundary_line_thickness = tidy_plot_info_input["main_boundary_line_thickness"]
    image_scale = tidy_plot_info_input["image_scale"]
    axis_y_label_rotation = tidy_plot_info_input["axis_y_label_rotation"]
    axis_y_label_weight = tidy_plot_info_input["axis_y_label_weight"]
    axis_y_label_font_size = tidy_plot_info_input["axis_y_label_font_size"]
    axis_y_label_pad = tidy_plot_info_input["axis_y_label_pad"]
    mid_line = tidy_plot_info_input["mid_line"]
    mid_line_level = tidy_plot_info_input["mid_line_level"]
    mid_line_color = tidy_plot_info_input["mid_line_color"]
    mid_line_style = tidy_plot_info_input["mid_line_style"]
    mid_line_thickness = tidy_plot_info_input["mid_line_thickness"]
    axis_right_top_left_bottom_borders = tidy_plot_info_input["axis_right_top_left_bottom_borders"]
    subplots_space_adjustment = tidy_plot_info_input["subplots_space_adjustment"]
    subplots_width_space = tidy_plot_info_input["subplots_width_space"]
    subplots_height_space = tidy_plot_info_input["subplots_height_space"]
    time_notation = tidy_plot_info_input["time_notation"]
    time_notation_text_position = tidy_plot_info_input["time_notation_text_position"]
    time_notation_text_weight = tidy_plot_info_input["time_notation_text_weight"]
    time_notation_text_font_size = tidy_plot_info_input["time_notation_text_font_size"]
    time_line_x_position_start_end = tidy_plot_info_input["time_line_x_position_start_end"]
    time_line_y_position_start_end = tidy_plot_info_input["time_line_y_position_start_end"]
    time_line_style = tidy_plot_info_input["time_line_style"]
    time_line_color = tidy_plot_info_input["time_line_color"]
    time_line_thickness = tidy_plot_info_input["time_line_thickness"]
    time_boundary_position = tidy_plot_info_input["time_boundary_position"]
    time_boundary_width = tidy_plot_info_input["time_boundary_width"]
    time_boundary_height = tidy_plot_info_input["time_boundary_height"]
    time_boundary_color = tidy_plot_info_input["time_boundary_color"]
    time_boundary_line_thickness = tidy_plot_info_input["time_boundary_line_thickness"]

    plot_info, adjust_limit_info = get_plot_info(folder_dir_input, tidy_plot_info_input)

    x_adjust_limit = adjust_limit_info["x_adjust_limit"]
    x_lower_limit = x_adjust_limit["lower_limit"]
    x_upper_limit = x_adjust_limit["upper_limit"]
    y_adjust_limit = adjust_limit_info["y_adjust_limit"]
    y_lower_limit = y_adjust_limit["lower_limit"]
    y_upper_limit = y_adjust_limit["upper_limit"]

    output_image_name = tidy_plot_info_input["output_image_name"]
    display_output_dir = os.path.join(folder_dir_input, output_image_name)
    output_dir = folder_dir_input
    if output_file_dir_input:
        display_output_dir = output_file_dir_input
        output_image_name = os.path.basename(output_file_dir_input)
        output_dir = os.path.join(output_file_dir_input, os.pardir)

    final_plot_array = []
    for logmar_level in logmar_level_array:
        temp_logmar_info_array = []

        for info in plot_info:
            if info["logmar"] == logmar_level:
                temp_logmar_info_array.append(info)

        if len(temp_logmar_info_array) > 0:
            temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
            final_plot_array.append(temp_dict)

    if len(final_plot_array) > 0:
        final_row_length = len(final_plot_array)
        final_column_length = 0
        for plot_info in final_plot_array:
            info_array = plot_info["info_array"]
            if len(info_array) > final_column_length:
                final_column_length = len(info_array)

        if final_row_length > 1:
            plot_info_len = len(final_plot_array)
            if plot_info_len <= 1:
                print("There is only 1 logmar level in the given data.")
                print("Therefore, we cannot draw tidy graph. It needs at least 2 logmar level.")
            else:
                fig, axs = plt.subplots(final_row_length, final_column_length,
                                        figsize=(final_column_length * image_scale,
                                                 final_row_length * image_scale * 0.4))

                for row_index, plot_info in enumerate(final_plot_array):
                    logmar_level = plot_info["logmar_level"]
                    info_array = plot_info["info_array"]
                    info_array_length = len(info_array)
                    num_plot_to_be_deleted = 0
                    if info_array_length < int(final_column_length):
                        num_plot_to_be_deleted = final_column_length - info_array_length
                    for column_index, info in enumerate(info_array):
                        x_array = info["x_array"]
                        y_array = info["y_array"]
                        sp_array = info["sp_array"]
                        sp_line_color = info["sp_line_color"]
                        sp_line_thickness = info["sp_line_thickness"]
                        qp_array = info["qp_array"]
                        qp_line_color = info["qp_line_color"]
                        qp_line_thickness = info["qp_line_thickness"]
                        axs[row_index, column_index].plot(x_array, y_array, color=graph_line_color,
                                                          linewidth=graph_line_thickness)
                        axs[row_index, column_index].plot(x_array, sp_array, color=sp_line_color,
                                                          linewidth=sp_line_thickness)
                        axs[row_index, column_index].plot(x_array, qp_array, color=qp_line_color,
                                                          linewidth=qp_line_thickness)
                        axs[row_index, column_index].set_xlim([x_lower_limit, x_upper_limit])
                        axs[row_index, column_index].set_ylim([y_lower_limit, y_upper_limit])
                        if type(logmar_level) is int or type(logmar_level) is float:
                            axs[row_index, column_index].set_ylabel(str(logmar_level),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        else:
                            axs[row_index, column_index].set_ylabel(str("None  "),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        axs[row_index, column_index].set_xticks([])
                        axs[row_index, column_index].set_yticks([])
                        if mid_line:
                            axs[row_index, column_index].axhline(y=mid_line_level, color=mid_line_color,
                                                                 linestyle=mid_line_style,
                                                                 linewidth=mid_line_thickness)

                        # Hide/Show the borders/spines
                        for axx in axs.flat:
                            axx.spines['right'].set_visible(axis_right_top_left_bottom_borders[0])
                            axx.spines['top'].set_visible(axis_right_top_left_bottom_borders[1])
                            axx.spines['left'].set_visible(axis_right_top_left_bottom_borders[2])
                            axx.spines['bottom'].set_visible(axis_right_top_left_bottom_borders[3])

                    if num_plot_to_be_deleted > 0:
                        for index in range(num_plot_to_be_deleted):
                            column_index_to_be_deleted = int(final_column_length) - (index + 1)
                            axs[row_index, column_index_to_be_deleted].set_axis_off()

                    # Hide all x axis labels inside the combined graph and show left and outside.
                    for ax in axs.flat:
                        ax.label_outer()

                plt.tick_params(
                    axis='x',  # changes apply to the x-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.tick_params(
                    axis='y',  # changes apply to the y-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.xticks([]), plt.yticks([])

                if subplots_space_adjustment:
                    plt.subplots_adjust(wspace=subplots_width_space, hspace=subplots_height_space)

                fig.text(x_label_x_position, x_label_y_position, x_label,
                         ha=x_label_alignment, rotation=x_label_rotation,
                         weight=x_label_weight, fontsize=x_label_font_size)
                fig.text(y_label_x_position, y_label_y_position, y_label,
                         va=y_label_alignment, rotation=y_label_rotation,
                         weight=y_label_weight, fontsize=y_label_font_size)
                main_boundary = plt.Rectangle(
                    # (x,y at lower-left corner), width, height
                    (main_boundary_position[0], main_boundary_position[1]),
                    main_boundary_width, main_boundary_height,
                    fill=False, color=main_boundary_color,
                    lw=main_boundary_line_thickness,
                    zorder=1000, transform=fig.transFigure,
                    figure=fig
                )
                if time_notation and time_notation != "none":
                    fig.text(time_notation_text_position[0],
                             time_notation_text_position[1],
                             time_notation,
                             weight=time_notation_text_weight,
                             fontsize=time_notation_text_font_size)
                    fig.add_artist(Line2D(time_line_x_position_start_end, time_line_y_position_start_end,
                                          linestyle=time_line_style, color=time_line_color,
                                          linewidth=time_line_thickness))
                    time_notation_boundary = plt.Rectangle(
                        # (x,y at lower-left corner), width, height
                        (time_boundary_position[0], time_boundary_position[1]),
                        time_boundary_width, time_boundary_height,
                        fill=False, color=time_boundary_color,
                        lw=time_boundary_line_thickness,
                        zorder=1000, transform=fig.transFigure,
                        figure=fig
                    )
                    fig.patches.extend([main_boundary, time_notation_boundary])
                else:
                    fig.patches.extend([main_boundary])
                os.chdir(output_dir)
                fig.savefig(output_image_name)
                plt.close()
            print(f"Tidy plot has been saved at:{display_output_dir}")
        else:
            print("There is only 1 logmar level in the given data.")
            print("Therefore, we cannot draw tidy graph. It needs at least 2 logmar level.")
    else:
        print("There is nothing to plot")


# This function is to draw va testing progress graph from the given config info
def draw_progress_graph(folder_dir_input, progress_plot_info_input, output_file_dir_input=None):
    x_label = progress_plot_info_input["x_label"]
    y_label = progress_plot_info_input["y_label"]
    x_data_column_name = progress_plot_info_input["x_data_column_name"]
    y_data_column_name = progress_plot_info_input["y_data_column_name"]
    okn_matlab_column_name = progress_plot_info_input["okn_matlab_column_name"]
    phase_column_name = progress_plot_info_input["phase_column_name"]
    final_logmar_column_name = progress_plot_info_input["final_logmar_column_name"]
    graph_line_color = progress_plot_info_input["graph_line_color"]
    graph_line_thickness = progress_plot_info_input["graph_line_thickness"]
    graph_line_style = progress_plot_info_input["graph_line_style"]
    summary_csv_name = progress_plot_info_input["summary_csv_name"]
    trial_summary_csv_name = progress_plot_info_input["trial_summary_csv_name"]
    output_image_name = progress_plot_info_input["output_image_name"]
    marker_type_equivalent = progress_plot_info_input["marker_type_equivalent"]
    marker_type = progress_plot_info_input["marker_type"]
    marker_size = progress_plot_info_input["marker_size"]
    okn_marker_color = progress_plot_info_input["okn_marker_color"]
    okn_marker_edge_color = progress_plot_info_input["okn_marker_edge_color"]
    okn_legend_label = progress_plot_info_input["okn_legend_label"]
    non_okn_marker_color = progress_plot_info_input["non_okn_marker_color"]
    non_okn_marker_edge_color = progress_plot_info_input["non_okn_marker_edge_color"]
    non_okn_legend_label = progress_plot_info_input["non_okn_legend_label"]
    best_va_line = progress_plot_info_input["best_va_line"]
    best_va_line_color = progress_plot_info_input["best_va_line_color"]
    best_va_line_thickness = progress_plot_info_input["best_va_line_thickness"]
    best_va_line_style = progress_plot_info_input["best_va_line_style"]
    best_va_line_legend_label = progress_plot_info_input["best_va_line_legend_label"]
    final_va_line = progress_plot_info_input["final_va_line"]
    final_va_line_color = progress_plot_info_input["final_va_line_color"]
    final_va_line_thickness = progress_plot_info_input["final_va_line_thickness"]
    final_va_line_style = progress_plot_info_input["final_va_line_style"]
    final_va_line_legend_label = progress_plot_info_input["final_va_line_legend_label"]
    legend_background_color = progress_plot_info_input["legend_background_color"]
    legend_edge_color = progress_plot_info_input["legend_edge_color"]
    legend_location = progress_plot_info_input["legend_location"]
    legend_font_size = progress_plot_info_input["legend_font_size"]
    legend_icon_size = progress_plot_info_input["legend_icon_size"]
    line_style_equivalent = progress_plot_info_input["line_style_equivalent"]

    summary_csv_dir = os.path.join(folder_dir_input, summary_csv_name)

    trial_data_csv_dir = os.path.join(folder_dir_input, trial_summary_csv_name)

    display_output_dir = os.path.join(folder_dir_input, output_image_name)

    file_to_open = open(summary_csv_dir)
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
    okn_header_position = get_index(okn_matlab_column_name, header_array)
    # print(x_header_position)
    # print(y_header_position)
    x_array = []
    y_array = []
    okn_array = []
    x_index_array = []

    for row in rows:
        x_array.append(row[x_header_position])
        y_array.append(float(row[y_header_position]))
        okn_array.append(int(float(row[okn_header_position])))

    for ind in range(len(x_array)):
        x_index_array.append(str(ind + 1))

    # print(x_array)
    # print(y_array)
    # print(okn_array)
    overlay_x_array = []
    overlay_y_array = []
    # final_va_line_level = y_array[-1]

    for ind, value in enumerate(okn_array):
        if value >= 1:
            overlay_x_array.append(x_index_array[ind])
            overlay_y_array.append(y_array[ind])

    bot_limit = min(y_array) - 0.2
    top_limit = max(y_array) + 0.1

    plt.plot(x_index_array, y_array, line_style_equivalent[graph_line_style],
             marker=marker_type_equivalent[marker_type], markersize=marker_size, fillstyle='full',
             color=graph_line_color, linewidth=graph_line_thickness,
             markerfacecolor=non_okn_marker_color, markeredgecolor=non_okn_marker_edge_color)
    plt.plot(overlay_x_array, overlay_y_array, ' ', marker=marker_type_equivalent[marker_type],
             markersize=marker_size, fillstyle='full', color=graph_line_color,
             linewidth=graph_line_thickness, markerfacecolor=okn_marker_color,
             markeredgecolor=okn_marker_edge_color)

    default_va = 1
    if best_va_line:
        best_va_line_level = get_va_by_phase_name(trial_data_csv_dir, phase_column_name,
                                                  final_logmar_column_name, "best")
        if not best_va_line_level:
            best_va_line_level = default_va
            default_va = best_va_line_level
        else:
            default_va = best_va_line_level
        plt.axhline(y=best_va_line_level, color=best_va_line_color,
                    linestyle=line_style_equivalent[best_va_line_style],
                    linewidth=best_va_line_thickness)
    if final_va_line:
        final_va_line_level = get_va_by_phase_name(trial_data_csv_dir, phase_column_name,
                                                   final_logmar_column_name, "final")
        if not final_va_line_level:
            final_va_line_level = default_va
        plt.axhline(y=final_va_line_level, color=final_va_line_color,
                    linestyle=line_style_equivalent[final_va_line_style],
                    linewidth=final_va_line_thickness)
    plt.ylim(bot_limit, top_limit)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    # plt.xticks(rotation=90)
    y_axis_array = np.arange(start=top_limit, stop=bot_limit, step=-0.1)
    plt.yticks(y_axis_array)
    plt.tight_layout()

    legend_array = []
    okn_marker = Line2D([0], [0], marker=marker_type_equivalent[marker_type],
                        color=legend_background_color, label=okn_legend_label,
                        markerfacecolor=okn_marker_color, markeredgecolor=okn_marker_edge_color,
                        markersize=legend_icon_size)
    legend_array.append(okn_marker)
    non_okn_marker = Line2D([0], [0], marker=marker_type_equivalent[marker_type],
                            color=legend_background_color, label=non_okn_legend_label,
                            markerfacecolor=non_okn_marker_color, markeredgecolor=non_okn_marker_edge_color,
                            markersize=legend_icon_size)
    legend_array.append(non_okn_marker)
    if best_va_line:
        best_va_line = Line2D([0], [0], linestyle=line_style_equivalent[best_va_line_style],
                              color=best_va_line_color, label=best_va_line_legend_label,
                              linewidth=best_va_line_thickness)
        legend_array.append(best_va_line)
    if final_va_line:
        final_va_line = Line2D([0], [0], linestyle=line_style_equivalent[final_va_line_style],
                               color=final_va_line_color, label=final_va_line_legend_label,
                               linewidth=final_va_line_thickness)
        legend_array.append(final_va_line)
    # legend_array = [okn_marker, non_okn_marker, final_va_line]
    legend = plt.legend(handles=legend_array, loc=legend_location, fontsize=legend_font_size, fancybox=True)
    frame = legend.get_frame()
    frame.set_facecolor(legend_background_color)
    frame.set_edgecolor(legend_edge_color)
    frame.set_alpha(1)
    output_dir = folder_dir_input
    if output_file_dir_input:
        display_output_dir = output_file_dir_input
        output_image_name = os.path.basename(output_file_dir_input)
        output_dir = os.path.join(output_file_dir_input, os.pardir)
    os.chdir(output_dir)
    plt.savefig(output_image_name)
    # plt.show()
    plt.close()
    print(f"Staircase/progress plot has been saved at:{display_output_dir}")


# This function is to produce x and y adjustment limits according the type of adjustment
# Type comes into the function as int number and is converted into string to be used
# to retrieve the string type from adjustment dictionary
def get_adjust_limit(data_dir_input, csv_name, x_header_input, y_header_input, folder_array_input,
                     x_axis_limit_input, y_axis_limit_input, mean_offset_input,
                     axis_adjustment_types_input, axis_adjustment_type_number_input):
    adjustment_type = axis_adjustment_types_input[str(axis_adjustment_type_number_input)]
    ignore_folder_array = []
    print(f"axis_adjustment_type:{adjustment_type}")
    if adjustment_type == "manual":
        x_adjust_limit = {"lower_limit": x_axis_limit_input[0], "upper_limit": x_axis_limit_input[1]}
        y_adjust_limit = {"lower_limit": y_axis_limit_input[0], "upper_limit": y_axis_limit_input[1]}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    elif adjustment_type == "min_max_mean":
        x_lower_limit_array = []
        x_upper_limit_array = []
        y_lower_limit_array = []
        y_upper_limit_array = []
        for folder in folder_array_input:
            if not csv_name:
                # Default csv name
                updated_csv_name = f"updated_{folder}.csv"
            else:
                updated_csv_name = csv_name
            # Error handling for value error
            # IF there is value error that that folder, its name will be put into the ignore_folder_array
            try:
                data_dir_to_be_used = os.path.join(data_dir_input, folder, updated_csv_name)
                x_array = get_data_array(data_dir_to_be_used, x_header_input)
                x_lower_limit_array.append(min(x_array))
                x_upper_limit_array.append(max(x_array))
                y_array = get_data_array(data_dir_to_be_used, y_header_input)
                y_lower_limit_array.append(min(y_array))
                y_upper_limit_array.append(max(y_array))
            except ValueError:
                ignore_folder_array.append(folder)

        x_adjust_limit = {"lower_limit": int(min(x_lower_limit_array)),
                          "upper_limit": int(max(x_upper_limit_array))}
        y_adjust_limit = {"lower_limit": round(np.nanmean(y_lower_limit_array), 2),
                          "upper_limit": round(np.nanmean(y_upper_limit_array), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    elif adjustment_type == "mean_offset":
        x_lower_limit_array = []
        x_upper_limit_array = []
        for folder in folder_array_input:
            if not csv_name:
                # Default csv name
                updated_csv_name = f"updated_{folder}.csv"
            else:
                updated_csv_name = csv_name
            # Error handling for value error
            # IF there is value error that that folder, its name will be put into the ignore_folder_array
            try:
                data_dir_to_be_used = os.path.join(data_dir_input, folder, updated_csv_name)
                x_array = get_data_array(data_dir_to_be_used, x_header_input)
                # print(data_dir_to_be_used)
                x_lower_limit_array.append(min(x_array))
                x_upper_limit_array.append(max(x_array))
                y_array = get_data_array(data_dir_to_be_used, y_header_input)
            except ValueError:
                ignore_folder_array.append(folder)

        x_adjust_limit = {"lower_limit": int(min(x_lower_limit_array)),
                          "upper_limit": int(max(x_upper_limit_array))}
        y_adjust_limit = {"lower_limit": round(float(- mean_offset_input), 2),
                          "upper_limit": round(float(mean_offset_input), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    else:
        x_lower_limit_array = []
        x_upper_limit_array = []
        y_lower_limit_array = []
        y_upper_limit_array = []
        for folder in folder_array_input:
            if not csv_name:
                # Default csv name
                updated_csv_name = f"updated_{folder}.csv"
            else:
                updated_csv_name = csv_name
            # Error handling for value error
            # IF there is value error that that folder, its name will be put into the ignore_folder_array
            try:
                data_dir_to_be_used = os.path.join(data_dir_input, folder, updated_csv_name)
                x_array = get_data_array(data_dir_to_be_used, x_header_input)
                x_lower_limit_array.append(min(x_array))
                x_upper_limit_array.append(max(x_array))
                y_array = get_data_array(data_dir_to_be_used, y_header_input)
                y_lower_limit_array.append(min(y_array))
                y_upper_limit_array.append(max(y_array))
            except ValueError:
                ignore_folder_array.append(folder)

        x_adjust_limit = {"lower_limit": int(min(x_lower_limit_array)),
                          "upper_limit": int(max(x_upper_limit_array))}
        y_adjust_limit = {"lower_limit": round(min(y_lower_limit_array), 2),
                          "upper_limit": round(max(y_upper_limit_array), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")
        if ignore_folder_array:
            num_of_ignore_folder = len(ignore_folder_array)
            if num_of_ignore_folder > 1:
                print(f"{num_of_ignore_folder} folders are ignored because of value error.")
            else:
                print(f"{num_of_ignore_folder} folder is ignored because of value error.")

    return x_adjust_limit, y_adjust_limit, ignore_folder_array


def get_draw_info_for_trial_plot(config_info_input, x_array_input, y_array_input):
    x_axis_limit = config_info_input["x_axis_limit"]
    y_axis_limit = config_info_input["y_axis_limit"]
    mean_offset = config_info_input["mean_offset"]
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


def get_va_by_phase_name(csv_dir_input, phase_header_input, final_logmar_header_input, phase_name_input):
    file_to_open = open(csv_dir_input)
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

    phase_header_position = get_index(phase_header_input, header_array)
    final_logmar_header_position = get_index(final_logmar_header_input, header_array)

    va_output = None

    for row in rows:
        if row[phase_header_position] == phase_name_input:
            va_output = float(row[final_logmar_header_position])

    return va_output


def string_exist(string_to_check, csv_to_check, column_to_check):
    file_to_open = open(csv_to_check)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count = 0

    for row in csv_reader:
        if count <= 0:
            header_array = row
            count += 1
        else:
            rows.append(row)

    event_marker_position = get_index(column_to_check, header_array)
    for row in rows:
        if str(string_to_check) in row[event_marker_position]:
            return True

    return False


def get_event_marker_info(gaze_csv_input, trial_id_input):
    file_to_open = open(gaze_csv_input)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count = 0

    for row in csv_reader:
        if count <= 0:
            header_array = row
            count += 1
        else:
            rows.append(row)

    # sts = sensor timestamp
    event_string_position = get_index("event_string", header_array)
    sts_position = get_index("sensor_timestamp", header_array)

    event_marker_array = []
    start_marker = None
    for row in rows:
        event_string = row[event_string_position]
        if start_marker is None:
            if "start_marker" in event_string and str(trial_id_input) in event_string:
                start_marker = float(row[sts_position])
        else:
            if "event_marker" in event_string and str(trial_id_input) in event_string:
                event_marker_sts = float(row[sts_position])
                # event_marker_time_i = int(event_marker_sts - start_marker)
                # event_marker_time_f = float(event_marker_sts - start_marker)
                # print(event_marker_time_f - event_marker_time_i)
                event_marker_array.append(float(event_marker_sts - start_marker))

    return event_marker_array


def get_resource_file_location(file_name_input):
    resource_file_exist = okntool_resources.is_resource("okntool", file_name_input)
    if resource_file_exist:
        with okntool_resources.path("okntool", file_name_input) as p:
            resource_file_location = p
    else:
        resource_file_location = None
    return resource_file_location


def draw_simpler_graph(folder_dir_input, config_input, referenced_csv_to_be_used, output_file_dir_input=None):
    graph_line_color = config_input["graph_line_color"]
    graph_line_thickness = config_input["graph_line_thickness"]
    x_label = config_input["x_label"]
    x_label_x_position = config_input["x_label_x_position"]
    x_label_y_position = config_input["x_label_y_position"]
    x_label_alignment = config_input["x_label_alignment"]
    x_label_rotation = config_input["x_label_rotation"]
    x_label_weight = config_input["x_label_weight"]
    x_label_font_size = config_input["x_label_font_size"]
    y_label = config_input["y_label"]
    y_label_x_position = config_input["y_label_x_position"]
    y_label_y_position = config_input["y_label_y_position"]
    y_label_alignment = config_input["y_label_alignment"]
    y_label_rotation = config_input["y_label_rotation"]
    y_label_weight = config_input["y_label_weight"]
    y_label_font_size = config_input["y_label_font_size"]
    main_boundary_position = config_input["main_boundary_position"]
    main_boundary_width = config_input["main_boundary_width"]
    main_boundary_height = config_input["main_boundary_height"]
    main_boundary_color = config_input["main_boundary_color"]
    main_boundary_line_thickness = config_input["main_boundary_line_thickness"]
    image_scale = config_input["image_scale"]
    axis_y_label_rotation = config_input["axis_y_label_rotation"]
    axis_y_label_weight = config_input["axis_y_label_weight"]
    axis_y_label_font_size = config_input["axis_y_label_font_size"]
    axis_y_label_pad = config_input["axis_y_label_pad"]
    mid_line = config_input["mid_line"]
    mid_line_level = config_input["mid_line_level"]
    mid_line_color = config_input["mid_line_color"]
    mid_line_style = config_input["mid_line_style"]
    mid_line_thickness = config_input["mid_line_thickness"]
    axis_right_top_left_bottom_borders = config_input["axis_right_top_left_bottom_borders"]
    subplots_space_adjustment = config_input["subplots_space_adjustment"]
    subplots_width_space = config_input["subplots_width_space"]
    subplots_height_space = config_input["subplots_height_space"]
    time_notation = config_input["time_notation"]
    time_notation_text_position = config_input["time_notation_text_position"]
    time_notation_text_weight = config_input["time_notation_text_weight"]
    time_notation_text_font_size = config_input["time_notation_text_font_size"]
    time_line_x_position_start_end = config_input["time_line_x_position_start_end"]
    time_line_y_position_start_end = config_input["time_line_y_position_start_end"]
    time_line_style = config_input["time_line_style"]
    time_line_color = config_input["time_line_color"]
    time_line_thickness = config_input["time_line_thickness"]
    time_boundary_position = config_input["time_boundary_position"]
    time_boundary_width = config_input["time_boundary_width"]
    time_boundary_height = config_input["time_boundary_height"]
    time_boundary_color = config_input["time_boundary_color"]
    time_boundary_line_thickness = config_input["time_boundary_line_thickness"]

    plot_info, adjust_limit_info = get_plot_info_for_simpler(folder_dir_input, config_input, referenced_csv_to_be_used)

    x_adjust_limit = adjust_limit_info["x_adjust_limit"]
    x_lower_limit = x_adjust_limit["lower_limit"]
    x_upper_limit = x_adjust_limit["upper_limit"]
    y_adjust_limit = adjust_limit_info["y_adjust_limit"]
    y_lower_limit = y_adjust_limit["lower_limit"]
    y_upper_limit = y_adjust_limit["upper_limit"]

    output_image_name = config_input["output_image_name"]
    display_output_dir = os.path.join(folder_dir_input, output_image_name)
    output_dir = folder_dir_input
    if output_file_dir_input:
        display_output_dir = output_file_dir_input
        output_image_name = os.path.basename(output_file_dir_input)
        output_dir = os.path.join(output_file_dir_input, os.pardir)

    final_plot_array = []
    for logmar_level in logmar_level_array:
        temp_logmar_info_array = []

        for info in plot_info:
            if info["logmar"] == logmar_level:
                temp_logmar_info_array.append(info)

        if len(temp_logmar_info_array) > 0:
            temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
            final_plot_array.append(temp_dict)

    if len(final_plot_array) > 0:
        final_row_length = len(final_plot_array)
        final_column_length = 0
        for plot_info in final_plot_array:
            info_array = plot_info["info_array"]
            if len(info_array) > final_column_length:
                final_column_length = len(info_array)

        if final_row_length > 1:
            plot_info_len = len(final_plot_array)
            if plot_info_len <= 1:
                print("There is only 1 logmar level in the given data.")
                print("Therefore, we cannot draw simpler graph. It needs at least 2 logmar level.")
            else:
                fig, axs = plt.subplots(final_row_length, final_column_length,
                                        figsize=(final_column_length * image_scale * 1,
                                                 final_row_length * image_scale * 1))

                for row_index, plot_info in enumerate(final_plot_array):
                    logmar_level = plot_info["logmar_level"]
                    info_array = plot_info["info_array"]
                    info_array_length = len(info_array)
                    num_plot_to_be_deleted = 0
                    if info_array_length < int(final_column_length):
                        num_plot_to_be_deleted = final_column_length - info_array_length
                    for column_index, info in enumerate(info_array):
                        x_array = info["x_array"]
                        y_array = info["y_array"]
                        sp_array = info["sp_array"]
                        sp_line_color = info["sp_line_color"]
                        sp_line_thickness = info["sp_line_thickness"]
                        qp_array = info["qp_array"]
                        qp_line_color = info["qp_line_color"]
                        qp_line_thickness = info["qp_line_thickness"]
                        axs[row_index, column_index].plot(x_array, y_array, color=graph_line_color,
                                                          linewidth=graph_line_thickness)
                        axs[row_index, column_index].plot(x_array, sp_array, color=sp_line_color,
                                                          linewidth=sp_line_thickness)
                        axs[row_index, column_index].plot(x_array, qp_array, color=qp_line_color,
                                                          linewidth=qp_line_thickness)
                        axs[row_index, column_index].set_xlim([x_lower_limit, x_upper_limit])
                        axs[row_index, column_index].set_ylim([y_lower_limit, y_upper_limit])
                        if type(logmar_level) is int or type(logmar_level) is float:
                            axs[row_index, column_index].set_ylabel(str(logmar_level),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        else:
                            axs[row_index, column_index].set_ylabel(str("None  "),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        axs[row_index, column_index].set_xticks([])
                        axs[row_index, column_index].set_yticks([])
                        if mid_line:
                            axs[row_index, column_index].axhline(y=mid_line_level, color=mid_line_color,
                                                                 linestyle=mid_line_style,
                                                                 linewidth=mid_line_thickness)

                        # Hide/Show the borders/spines
                        for axx in axs.flat:
                            axx.spines['right'].set_visible(axis_right_top_left_bottom_borders[0])
                            axx.spines['top'].set_visible(axis_right_top_left_bottom_borders[1])
                            axx.spines['left'].set_visible(axis_right_top_left_bottom_borders[2])
                            axx.spines['bottom'].set_visible(axis_right_top_left_bottom_borders[3])

                    if num_plot_to_be_deleted > 0:
                        for index in range(num_plot_to_be_deleted):
                            column_index_to_be_deleted = int(final_column_length) - (index + 1)
                            axs[row_index, column_index_to_be_deleted].set_axis_off()

                    # Hide all x axis labels inside the combined graph and show left and outside.
                    for ax in axs.flat:
                        ax.label_outer()

                plt.tick_params(
                    axis='x',  # changes apply to the x-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.tick_params(
                    axis='y',  # changes apply to the y-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.xticks([]), plt.yticks([])

                if subplots_space_adjustment:
                    plt.subplots_adjust(wspace=subplots_width_space, hspace=subplots_height_space)

                fig.text(x_label_x_position, x_label_y_position, x_label,
                         ha=x_label_alignment, rotation=x_label_rotation,
                         weight=x_label_weight, fontsize=x_label_font_size)
                fig.text(y_label_x_position, y_label_y_position, y_label,
                         va=y_label_alignment, rotation=y_label_rotation,
                         weight=y_label_weight, fontsize=y_label_font_size)
                main_boundary = plt.Rectangle(
                    # (x,y at lower-left corner), width, height
                    (main_boundary_position[0], main_boundary_position[1]),
                    main_boundary_width, main_boundary_height,
                    fill=False, color=main_boundary_color,
                    lw=main_boundary_line_thickness,
                    zorder=1000, transform=fig.transFigure,
                    figure=fig
                )
                if time_notation and time_notation != "none":
                    fig.text(time_notation_text_position[0],
                             time_notation_text_position[1],
                             time_notation,
                             weight=time_notation_text_weight,
                             fontsize=time_notation_text_font_size)
                    fig.add_artist(Line2D(time_line_x_position_start_end, time_line_y_position_start_end,
                                          linestyle=time_line_style, color=time_line_color,
                                          linewidth=time_line_thickness))
                    time_notation_boundary = plt.Rectangle(
                        # (x,y at lower-left corner), width, height
                        (time_boundary_position[0], time_boundary_position[1]),
                        time_boundary_width, time_boundary_height,
                        fill=False, color=time_boundary_color,
                        lw=time_boundary_line_thickness,
                        zorder=1000, transform=fig.transFigure,
                        figure=fig
                    )
                    fig.patches.extend([main_boundary, time_notation_boundary])
                else:
                    fig.patches.extend([main_boundary])
                os.chdir(output_dir)
                fig.savefig(output_image_name)
                plt.close()
            print(f"Simpler plot has been saved at:{display_output_dir}")
        else:
            print("There is only 1 logmar level in the given data.")
            print("Therefore, we cannot draw simpler graph. It needs at least 2 logmar level.")
    else:
        print("There is nothing to plot")


def get_plot_info_for_simpler(data_dir, plot_info_input, referenced_csv_dir_input):
    x_label = plot_info_input["x_label"]
    y_label = plot_info_input["y_label"]
    x_data_column_name = plot_info_input["x_data_column_name"]
    y_data_column_name = plot_info_input["y_data_column_name"]
    x_axis_limit = plot_info_input["x_axis_limit"]
    y_axis_limit = plot_info_input["y_axis_limit"]
    mean_offset = plot_info_input["mean_offset"]
    axis_adjustment_types = plot_info_input["axis_adjustment_types"]
    axis_adjustment_type_number = plot_info_input["axis_adjustment_type_number"]
    # signal_csv_folder_name = plot_info_input["signal_csv_folder_name"]
    signal_csv_name = plot_info_input["signal_csv_name"]
    sp_column_name = plot_info_input["sp_column_name"]
    qp_column_name = plot_info_input["qp_column_name"]
    sp_line_color = plot_info_input["sp_line_color"]
    sp_line_thickness = plot_info_input["sp_line_thickness"]
    qp_line_color = plot_info_input["qp_line_color"]
    qp_line_thickness = plot_info_input["qp_line_thickness"]
    info_array = get_info_array_for_simpler_plot(referenced_csv_dir_input, "logMAR", "filename")
    # Get the folder away from info dictionary array in which index is 2
    folder_array = [info[2] for info in info_array]
    # print(folder_array)

    adjustment_type = axis_adjustment_types[str(axis_adjustment_type_number)]
    if adjustment_type == "mean_offset":
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, signal_csv_name,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out the info dictionary for that folder from info array
        if ignore_folder_array:
            info_array = [info for info in info_array if info[2] not in ignore_folder_array]
        for trial_id, logmar_level, folder_name in info_array:
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_name)
            x_array = get_data_array(signal_csv_dir, x_data_column_name)
            y_array = get_data_array(signal_csv_dir, y_data_column_name)
            y_mean = np.nanmean(y_array)
            y_array = [value - y_mean for value in y_array]
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": str(logmar_level),
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(logmar_level)}
            plot_info_array.append(plot_info)
    else:
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, signal_csv_name,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out the info dictionary for that folder from info array
        if ignore_folder_array:
            info_array = [info for info in info_array if info[2] not in ignore_folder_array]
        for trial_id, logmar_level, folder_name in info_array:
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_name)
            x_array = get_data_array(signal_csv_dir, x_data_column_name)
            y_array = get_data_array(signal_csv_dir, y_data_column_name)
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": logmar_level,
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(logmar_level)}
            plot_info_array.append(plot_info)

    return plot_info_array, adjust_limit_dict


def get_info_array_for_simpler_plot(referenced_csv_dir, logmar_header_input, file_name_header_input):
    file_to_open = open(referenced_csv_dir)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count_one = 0
    output_array = []

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    file_name_header_position = get_index(file_name_header_input, header_array)
    logmar_header_position = get_index(logmar_header_input, header_array)

    for row in rows:
        raw_file_name = str(row[file_name_header_position])
        logmar_level = float(row[logmar_header_position])
        folder_name = raw_file_name[raw_file_name.find("./") + 2:raw_file_name.find(".mp4")]
        trial_id = folder_name[folder_name.find("trial-"):folder_name.find("-disks")]
        output_array.append([trial_id, logmar_level, folder_name])

    return output_array


def check_file_name(file_name_input, ending_array_input):
    return True if any([end in file_name_input for end in ending_array_input]) else False


def create_indi_va_table_html(dir_input, referenced_csv, template_input,
                              decider_name_input, output_file_dir_input=None):
    if output_file_dir_input:
        csv_dir = os.path.join(output_file_dir_input, "indi_va_table.csv")
        html_dir = os.path.join(output_file_dir_input, "indi_va_table.html")
    else:
        csv_dir = os.path.join(dir_input, "indi_va_table.csv")
        html_dir = os.path.join(dir_input, "indi_va_table.html")
    read_folder_and_create_indi_csv_data(dir_input, referenced_csv, csv_dir, decider_name_input)
    read_csv_data_and_create_indi_va_table_html(csv_dir, template_input, html_dir)


def read_folder_and_create_indi_csv_data(dir_input, referenced_csv, csv_dir, decider_name_input):
    info_array = get_info_array_for_ind_va_table(dir_input, referenced_csv, "logMAR", "filename", decider_name_input)
    logmar_level = None
    index = 1
    okn_index_array = []
    temp_dict = {}
    total_count = 0

    for info_index, info in enumerate(info_array):
        if logmar_level != info["logmar_level"]:
            logmar_level = info["logmar_level"]
            if index == 1:
                trial_string = f"trial_{index}"
                temp_dict["logMAR"] = logmar_level
                okn_result = info["okn"]
                if okn_result == 1:
                    total_count += 1
                temp_dict[trial_string] = okn_result
            else:
                temp_dict["total"] = total_count
                okn_index_array.append(temp_dict)
                temp_dict = {}
                index = 1
                total_count = 0
                trial_string = f"trial_{index}"
                temp_dict["logMAR"] = logmar_level
                okn_result = info["okn"]
                if okn_result == 1:
                    total_count += 1
                temp_dict[trial_string] = okn_result
        else:
            index += 1
            trial_string = f"trial_{index}"
            okn_result = info["okn"]
            if okn_result == 1:
                total_count += 1
            temp_dict[trial_string] = okn_result
            if info_index == len(info_array) - 1:
                temp_dict["total"] = total_count
                okn_index_array.append(temp_dict)

    header_array = ["logMAR", "trial_1", "trial_2", "trial_3", "trial_4", "trial_5", "total"]
    with open(csv_dir, mode='w', newline="") as destination_file:
        csv_writer = csv.DictWriter(destination_file, fieldnames=header_array)
        csv_writer.writeheader()

        for d in okn_index_array:
            csv_writer.writerow(d)
        print(f"Individual va table csv is successfully created in {csv_dir}")
        destination_file.close()


def read_csv_data_and_create_indi_va_table_html(csv_dir_input, template_html_input, output_file_dir_input):
    if os.path.isfile(csv_dir_input):
        file_to_open = open(csv_dir_input)
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

        logmar_position = get_index("logMAR", header_array)
        trial_one_position = get_index("trial_1", header_array)
        trial_two_position = get_index("trial_2", header_array)
        trial_three_position = get_index("trial_3", header_array)
        trial_four_position = get_index("trial_4", header_array)
        trial_five_position = get_index("trial_5", header_array)
        total_position = get_index("total", header_array)

        total_okn = 0
        data_array = []
        for row in rows:
            temp_dict = {}
            logmar_level = row[logmar_position]
            temp_dict["logMAR"] = logmar_level
            trial_one = row[trial_one_position]
            if trial_one == 1:
                total_okn += 1
                temp_dict["trial_1_unicode"] = "&#x2713;"
            else:
                temp_dict["trial_1_unicode"] = "&#x0058;"
            trial_two = int(row[trial_two_position])
            if trial_two == 1:
                total_okn += 1
                temp_dict["trial_2_unicode"] = "&#x2713;"
            else:
                temp_dict["trial_2_unicode"] = "&#x0058;"
            trial_three = int(row[trial_three_position])
            if trial_three == 1:
                total_okn += 1
                temp_dict["trial_3_unicode"] = "&#x2713;"
            else:
                temp_dict["trial_3_unicode"] = "&#x0058;"
            trial_four = int(row[trial_four_position])
            if trial_four == 1:
                total_okn += 1
                temp_dict["trial_4_unicode"] = "&#x2713;"
            else:
                temp_dict["trial_4_unicode"] = "&#x0058;"
            trial_five = int(row[trial_five_position])
            if trial_five == 1:
                total_okn += 1
                temp_dict["trial_5_unicode"] = "&#x2713;"
            else:
                temp_dict["trial_5_unicode"] = "&#x0058;"
            total = row[total_position]
            temp_dict["Total"] = total
            data_array.append(temp_dict)

        final_va = round(1.1 - (total_okn * 0.02), 2)
        okn_index_data = {"data": data_array, "letter_score": total_okn, "va": {"VA": final_va, "bestline_VA": None}}

        with open(template_html_input, 'r') as template:
            html_data = chevron.render(template, okn_index_data)

        with open(output_file_dir_input, 'w') as output_html_file:
            output_html_file.write(html_data)
            print(f"Individual va table html is successfully created in {output_file_dir_input}")

        template.close()
        output_html_file.close()
    else:
        print(f"Individual va table csv could not be found in {csv_dir_input}.")


def get_info_array_for_ind_va_table(dir_input, referenced_csv_dir, logmar_header_input,
                                    file_name_header_input, decider_name_input):
    file_to_open = open(referenced_csv_dir)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count_one = 0
    output_array = []

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    file_name_header_position = get_index(file_name_header_input, header_array)
    logmar_header_position = get_index(logmar_header_input, header_array)

    for row in rows:
        raw_file_name = str(row[file_name_header_position])
        logmar_level = float(row[logmar_header_position])
        folder_name = raw_file_name[raw_file_name.find("./") + 2:raw_file_name.find(".mp4")]
        trial_id = folder_name[folder_name.find("trial-"):folder_name.find("-disks")]
        is_there_okn = get_okn_result_from_signal_file(dir_input, folder_name, decider_name_input)
        if is_there_okn is not None:
            temp_dict = {"trial_id": trial_id, "logmar_level": logmar_level, "folder_name": folder_name,
                         "okn": is_there_okn}
            output_array.append(temp_dict)

    return output_array


def get_okn_result_from_signal_file(dir_input, folder_name_input, decider_file_name_input):
    decider_file_dir = os.path.join(dir_input, folder_name_input, decider_file_name_input)
    try:
        # Opening oknserver graph plot config
        with open(decider_file_dir) as f:
            info = json.load(f)
    except FileNotFoundError:
        print(f"There is no {decider_file_name_input} in {decider_file_dir}")
        info = None

    if info:
        is_there_okn = info["okn_present"]
        if is_there_okn is True:
            return 1
        else:
            return 0
    else:
        return None


def create_sum_va_table_html(dir_input, template_input, output_file_dir_input=None):
    if output_file_dir_input:
        csv_dir = os.path.join(output_file_dir_input, "sum_va_table.csv")
        html_dir = os.path.join(output_file_dir_input, "sum_va_table.html")
    else:
        csv_dir = os.path.join(dir_input, "sum_va_table.csv")
        html_dir = os.path.join(dir_input, "sum_va_table.html")
    read_folder_and_create_sum_csv_data(dir_input, csv_dir)
    read_csv_data_and_create_sum_va_table_html(csv_dir, template_input, html_dir)


def read_folder_and_create_sum_csv_data(dir_input, output_dir):
    folder_array = [name for name in os.listdir(dir_input) if os.path.isdir(os.path.join(dir_input, name))]
    info_array = []
    for name in folder_array:
        indi_csv_dir = os.path.join(dir_input, name, "indi_va_table.csv")
        file_to_open = open(indi_csv_dir)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count_one = 0
        total = 0
        temp_dict = {}
        temp_dict["folder"] = name

        for row in csv_reader:
            if count_one <= 0:
                header_array = row
                count_one += 1
            else:
                rows.append(row)

        logmar_position = get_index("logMAR", header_array)
        total_position = get_index("total", header_array)

        for row in rows:
            logmar_level = row[logmar_position]
            if float(logmar_level) == 1.0:
                logmar_level = 1
            elif float(logmar_level) == 0.0:
                logmar_level = 0
            else:
                logmar_level = str(logmar_level).replace(".", "_")
            logmar_string = f"log_{logmar_level}"
            logmar_total = int(row[total_position])
            total += logmar_total
            temp_dict[logmar_string] = logmar_total
        temp_dict["Total"] = total
        info_array.append(temp_dict)

    csv_header_array = ["folder", "log_1", "log_0_9", "log_0_8", "log_0_7", "log_0_6",
                        "log_0_5", "log_0_4", "log_0_3", "log_0_2", "log_0_1", "log_0", "Total"]
    with open(output_dir, mode='w', newline="") as destination_file:
        csv_writer = csv.DictWriter(destination_file, fieldnames=csv_header_array)
        csv_writer.writeheader()

        for info in info_array:
            csv_writer.writerow(info)
        print(f"Summary va table csv is successfully created in {output_dir}")
        destination_file.close()


def read_csv_data_and_create_sum_va_table_html(csv_dir_input, template_html_input, output_dir):
    if os.path.isfile(csv_dir_input):
        file_to_open = open(csv_dir_input)
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

        folder_name_position = get_index("folder", header_array)
        log_1_position = get_index("log_1", header_array)
        log_0_9_position = get_index("log_0_9", header_array)
        log_0_8_position = get_index("log_0_8", header_array)
        log_0_7_position = get_index("log_0_7", header_array)
        log_0_6_position = get_index("log_0_6", header_array)
        log_0_5_position = get_index("log_0_5", header_array)
        log_0_4_position = get_index("log_0_4", header_array)
        log_0_3_position = get_index("log_0_3", header_array)
        log_0_2_position = get_index("log_0_2", header_array)
        log_0_1_position = get_index("log_0_1", header_array)
        log_0_position = get_index("log_0", header_array)
        total_position = get_index("Total", header_array)

        log_1_okn = 0
        log_0_9_okn = 0
        log_0_8_okn = 0
        log_0_7_okn = 0
        log_0_6_okn = 0
        log_0_5_okn = 0
        log_0_4_okn = 0
        log_0_3_okn = 0
        log_0_2_okn = 0
        log_0_1_okn = 0
        log_0_okn = 0

        data_array = []
        for row in rows:
            temp_dict = {}
            temp_dict["folder"] = row[folder_name_position]
            temp_dict["log_1"] = row[log_1_position]
            temp_dict["log_0_9"] = row[log_0_9_position]
            temp_dict["log_0_8"] = row[log_0_8_position]
            temp_dict["log_0_7"] = row[log_0_7_position]
            temp_dict["log_0_6"] = row[log_0_6_position]
            temp_dict["log_0_5"] = row[log_0_5_position]
            temp_dict["log_0_4"] = row[log_0_4_position]
            temp_dict["log_0_3"] = row[log_0_3_position]
            temp_dict["log_0_2"] = row[log_0_2_position]
            temp_dict["log_0_1"] = row[log_0_1_position]
            temp_dict["log_0"] = row[log_0_position]
            temp_dict["Total"] = row[total_position]
            data_array.append(temp_dict)
            log_1_okn += int(row[log_1_position])
            log_0_9_okn += int(row[log_0_9_position])
            log_0_8_okn += int(row[log_0_8_position])
            log_0_7_okn += int(row[log_0_7_position])
            log_0_6_okn += int(row[log_0_6_position])
            log_0_5_okn += int(row[log_0_5_position])
            log_0_4_okn += int(row[log_0_4_position])
            log_0_3_okn += int(row[log_0_3_position])
            log_0_2_okn += int(row[log_0_2_position])
            log_0_1_okn += int(row[log_0_1_position])
            log_0_okn += int(row[log_0_position])

        total_dict = {
            "total_1": log_1_okn,
            "total_0_9": log_0_9_okn,
            "total_0_8": log_0_8_okn,
            "total_0_7": log_0_7_okn,
            "total_0_6": log_0_6_okn,
            "total_0_5": log_0_5_okn,
            "total_0_4": log_0_4_okn,
            "total_0_3": log_0_3_okn,
            "total_0_2": log_0_2_okn,
            "total_0_1": log_0_1_okn,
            "total_0": log_0_okn,
        }
        okn_index_data = {"data": data_array, "total": total_dict}

        with open(template_html_input, 'r') as template:
            html_data = chevron.render(template, okn_index_data)

        with open(output_dir, 'w') as output_html_file:
            output_html_file.write(html_data)
            print(f"Individual va table html is successfully created in {output_dir}")

        template.close()
        output_html_file.close()
    else:
        print(f"Summary va table csv could not be found in {csv_dir_input}.")


def split_pnm_video(file_input):
    print("Input file name:", file_input)
    input_video = cv2.VideoCapture(file_input)
    frame_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH) / 2)
    print("Input frame width:", frame_width)
    frame_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("Input frame height:", frame_height)
    frame_rate = input_video.get(cv2.CAP_PROP_FPS)
    print("Input frame rate:", frame_rate)
    frame_count = int(input_video.get(cv2.CAP_PROP_FRAME_COUNT))
    print("Input frame count:", frame_count)
    fourcc = int(cv2.VideoWriter_fourcc(*'mp4v'))
    frame_size = (frame_width, frame_height)
    left_v_dir = str(file_input).replace("pnm_eye_video.mp4", "pnm_left_eye_video.mp4")
    right_v_dir = str(file_input).replace("pnm_eye_video.mp4", "pnm_right_eye_video.mp4")
    is_color = False
    left_v_writer = cv2.VideoWriter(left_v_dir, fourcc, frame_rate, frame_size, is_color)
    right_v_writer = cv2.VideoWriter(right_v_dir, fourcc, frame_rate, frame_size, is_color)

    print("Please wait...")
    while True:
        ret, frame = input_video.read()

        # When there is frame to read
        if ret:
            height, width, channels = frame.shape
            half_width = width // 2

            left_section = frame[:, :half_width]
            right_section = frame[:, half_width:]
            left_gray = cv2.cvtColor(left_section, cv2.COLOR_BGR2GRAY)
            right_gray = cv2.cvtColor(right_section, cv2.COLOR_BGR2GRAY)
            left_v_writer.write(left_gray)
            right_v_writer.write(right_gray)
        else:
            left_v_writer.release()
            right_v_writer.release()
            break

    return left_v_dir, right_v_dir


def check_manager_type(gaze_dir_input):
    temp_dir = os.listdir(gaze_dir_input)
    left_video_exist = True if "left_video.mp4" in temp_dir else False
    right_video_exist = True if "right_video.mp4" in temp_dir else False
    pnm_eye_video_exist = True if "pnm_eye_video.mp4" in temp_dir else False
    plm_video_exist = True if "PLM_video.mp4" in temp_dir else False
    pgm_video_exist = True if "PGM_video.mp4" in temp_dir else False
    opm_video_exist = True if "OPM_video.mp4" in temp_dir else False
    gaze_exist = True if "gaze.csv" in temp_dir else False
    if gaze_exist:
        if left_video_exist and right_video_exist:
            return "pim"
        elif pnm_eye_video_exist:
            return "pnm"
        elif plm_video_exist:
            return "plm"
        elif pgm_video_exist:
            return "pgm"
        elif opm_video_exist:
            return "opm"
        else:
            print("Any known manager video file could not be found.")
            print("Therefore, the process will not be continued and it will stop here.")
            return None
    else:
        print(f"gaze.csv file could not be found in {gaze_dir_input}.")
        print("Therefore, the process will not be continued and it will stop here.")
        return None


def get_event_info_from_gaze(gaze_dir_input):
    file_to_open = open(gaze_dir_input)
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

    ts_position = get_index("record_timestamp", header_array)
    es_position = get_index("event_string", header_array)

    data_arr = []
    start_time = 0
    trial_folder_name = ""
    event_arr = []
    for row in rows:
        if row[es_position] != " ":
            print(row[es_position])
            try:
                temp_dict = json.loads(row[es_position])
            except json.decoder.JSONDecodeError:
                temp_dict = None
            if temp_dict:
                try:
                    trial_type = temp_dict["trial_type"]
                except KeyError:
                    trial_type = None
                if trial_type is not None and trial_type != "animation":
                    if temp_dict["type"] == "start_marker":
                        start_time = float(row[ts_position])
                        trial_id = temp_dict["trial_id"]
                        trial_index = temp_dict["trial_index"]
                        trial_folder_name = f"{trial_id}_{trial_index}"
                    else:
                        end_time = float(row[ts_position])
                        duration = round((end_time - start_time), 2)
                        event_arr.append({"trial_folder_name": trial_folder_name, "start_time": round(start_time, 2),
                                          "end_time": round(end_time, 2), "duration": duration})
                    data_arr.append([row[ts_position], row[es_position]])

    return event_arr


def split_video(record_folder_dir, record_type):
    if record_type == "pim":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        left_video_dir = os.path.join(record_folder_dir, "left_video.mp4")
        right_video_dir = os.path.join(record_folder_dir, "right_video.mp4")
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                e_start_time = trial_info["start_time"]
                e_duration = trial_info["duration"]
                out_v_name = os.path.join(trial_folder_dir, f"left_{trial_folder_name}_cropped.mp4")
                command = f"ffmpeg -i {left_video_dir} " \
                          f"-ss {e_start_time} " \
                          f"-t {e_duration} " \
                          f"-b:v 10M -c:a copy {out_v_name} -y"
                os.system(command)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                e_start_time = trial_info["start_time"]
                e_duration = trial_info["duration"]
                out_v_name = os.path.join(trial_folder_dir, f"right_{trial_folder_name}_cropped.mp4")
                command = f"ffmpeg -i {right_video_dir} " \
                          f"-ss {e_start_time} " \
                          f"-t {e_duration} " \
                          f"-b:v 10M -c:a copy {out_v_name} -y"
                os.system(command)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")

    elif record_type == "pnm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "pnm_eye_video.mp4")
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                e_start_time = trial_info["start_time"]
                e_duration = trial_info["duration"]
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                command = f"ffmpeg -i {video_dir} " \
                          f"-ss {e_start_time} " \
                          f"-t {e_duration} " \
                          f"-b:v 10M -c:a copy {out_v_name} -y"
                os.system(command)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")

    elif record_type == "plm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "PLM_video.mp4")
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                e_start_time = trial_info["start_time"]
                e_duration = trial_info["duration"]
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                command = f"ffmpeg -i {video_dir} " \
                          f"-ss {e_start_time} " \
                          f"-t {e_duration} " \
                          f"-b:v 10M -c:a copy {out_v_name} -y"
                os.system(command)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")
    elif record_type == "pgm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "PGM_video.mp4")
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                e_start_time = trial_info["start_time"]
                e_duration = trial_info["duration"]
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                command = f"ffmpeg -i {video_dir} " \
                          f"-ss {e_start_time} " \
                          f"-t {e_duration} " \
                          f"-b:v 10M -c:a copy {out_v_name} -y"
                os.system(command)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")
    elif record_type == "opm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "OPM_video.mp4")
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                e_start_time = trial_info["start_time"]
                e_duration = trial_info["duration"]
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                command = f"ffmpeg -i {video_dir} " \
                          f"-ss {e_start_time} " \
                          f"-t {e_duration} " \
                          f"-b:v 10M -c:a copy {out_v_name} -y"
                os.system(command)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")
    else:
        print("Invalid manager type.")


# check whether there is ffmpeg or not
def check_ffmpeg():
    ffmpeg_check_cmd = "ffmpeg -version"
    try:
        ffmpeg_check_output = subprocess.check_output(ffmpeg_check_cmd, shell=True)
        ffmpeg_check_output = ffmpeg_check_output.decode('utf-8')
        print(ffmpeg_check_output)
        is_there_ffmpeg = True
        print("ffmpeg is found.")
    except Exception as error:
        print(error)
        is_there_ffmpeg = False
    return is_there_ffmpeg


def fill_tiny_in_csv(buffer_input, csv_dir_input):
    file_to_open = open(csv_dir_input)
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

    data_dict_array = []
    for row in rows:
        temp_dict = {}
        for ind, data in enumerate(row):
            temp_dict[header_array[ind]] = data
        data_dict_array.append(temp_dict)

    input_csv_file_name = os.path.basename(csv_dir_input)
    csv_dir_output = str(csv_dir_input).replace(input_csv_file_name, f"Filled_{input_csv_file_name}")
    with open(csv_dir_output, mode='w', newline="") as destination_file:
        csv_writer = csv.DictWriter(destination_file, fieldnames=header_array)
        csv_writer.writeheader()
        got_first_data = False
        for dd in data_dict_array:
            return_data = buffer_input.add(dd)
            if return_data is not None:
                csv_writer.writerow(return_data)

        for dd in buffer_input.buffer:
            if not got_first_data:
                got_first_data = True
            else:
                csv_writer.writerow(dd)
    destination_file.close()
    print(f"{os.path.basename(csv_dir_output)} is successfully created in {csv_dir_output}.")


def main():
    parser = argparse.ArgumentParser(prog='okntool',
                                     description='okn related graphs plotting program.')
    parser.add_argument('--version', action='version', version='7.0.3'),
    parser.add_argument("-t", dest="tool_type", required=True, default=sys.stdin,
                        help="tool type", metavar="tool type")
    parser.add_argument("-d", dest="directory_input", required=True, default=sys.stdin,
                        help="directory folder to be processed", metavar="directory")
    parser.add_argument("-c", dest="config_dir", required=False, default=sys.stdin,
                        help="config or resource file", metavar="config location")
    parser.add_argument("-r", dest="referenced_csv", required=False, default=sys.stdin,
                        help="referenced csv file to be referenced", metavar="referenced csv")
    parser.add_argument("-o", dest="output", required=False, default=sys.stdin,
                        help="output folder or file directory", metavar="output")
    parser.add_argument("-p", dest="template", required=False, default=sys.stdin,
                        help="template file location or file name", metavar="template")
    parser.add_argument("-n", dest="decider_name", required=False, default=sys.stdin,
                        help="decider name for each sub folder", metavar="decider name")
    parser.add_argument("-b", dest="buffer_length", required=False, default=sys.stdin,
                        help="tiny fill buffer length", metavar="buffer length")

    args = parser.parse_args()
    directory_input = str(args.directory_input)
    type_input = str(args.tool_type)
    config_file_location = str(args.config_dir)
    referenced_csv_dir = str(args.referenced_csv)
    output_dir = str(args.output)
    template_dir = str(args.template)
    decider_name = str(args.decider_name)
    buffer_length = str(args.buffer_length)
    buffer_length_input = False if "_io.TextIOWrapper" in buffer_length else True
    if buffer_length_input:
        try:
            buffer_length = int(args.buffer_length)
            if buffer_length <= 2:
                buffer_length = 7
                print("Invalid buffer length input.")
                print(f"Therefore default buffer length: {buffer_length} will be used.")
            else:
                if buffer_length >= 50:
                    print("Warning!!!")
                    print(f"Using big buffer length {buffer_length}.")
        except ValueError:
            buffer_length = 7
            print("Invalid buffer length input.")
            print(f"Therefore default buffer length: {buffer_length} will be used.")

    config_input = False if "_io.TextIOWrapper" in config_file_location else True
    referenced_csv_input = False if "_io.TextIOWrapper" in referenced_csv_dir else True
    output_dir_input = False if "_io.TextIOWrapper" in output_dir else True
    template_dir_input = False if "_io.TextIOWrapper" in template_dir else True
    decider_name_input = False if "_io.TextIOWrapper" in decider_name else True
    image_file_ending_array = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    va_table_related_file_ending_array = ['.csv', '.html']
    output_file_name = None
    if output_dir_input:
        output_folder = os.path.join(output_dir, os.pardir)
        output_folder_exist = os.path.isdir(output_folder)
        if output_folder_exist:
            output_file_name = os.path.basename(output_dir)
    else:
        output_folder_exist = False
    # config_name_dict = {}
    # config_name_dict["trial"] = "oknserver_graph_plot_config.json"
    # config_name_dict["summary"] = "oknserver_graph_plot_config.json"
    # config_name_dict["staircase"] = "oknserver_graph_plot_config.json"
    # config_name_dict["progress"] = "oknserver_graph_plot_config.json"
    # config_name_dict["tidy"] = "oknserver_graph_plot_config.json"
    # config_name_dict["simpler"] = "simpler_plot_config.json"

    # Dictionary to retrieve the name of config file according the type
    resource_name_dict = {"trial": "oknserver_graph_plot_config.json",
                          "summary": "oknserver_graph_plot_config.json",
                          "staircase": "oknserver_graph_plot_config.json",
                          "progress": "oknserver_graph_plot_config.json",
                          "tidy": "oknserver_graph_plot_config.json",
                          "simpler": "simpler_plot_config.json",
                          "indi_va_table": "indi_va_table_template.html",
                          "sum_va_table": "sum_va_table_template.html",
                          "pnm_video_splitter": None,
                          "split_video": None,
                          "sv": None,
                          "fill_csv": None,
                          "fc": None}

    resource_name = resource_name_dict[type_input]

    # print(config_file_location)
    resource_location = None
    resource_dir_exist = False
    if config_input:
        resource_dir_exist = os.path.isfile(config_file_location)
        if resource_dir_exist:
            resource_location = config_file_location
            print(f"Config/resource location input:{resource_location} is valid.")
        else:
            resource_location = None
            print(f"Config/resource location input:{config_file_location} does not exist.")
            return
    else:
        if resource_name:
            print("There is no config input.")
            resource_location = get_resource_file_location(resource_name)
            if resource_location:
                print(f"Therefore, okntool is using built-in config: {resource_location}.")
                resource_dir_exist = True
            else:
                print(f"Error in retrieving config:{resource_location}.")
                return
        else:
            if type_input == "split_video" or type_input == "sv":
                print("------------------")
                print(f"OKN TOOL INFO")
                print(f"Input directory:{directory_input}")
                print(f"Tool type:{type_input}")
                ffmpeg_exist = check_ffmpeg()
                if ffmpeg_exist:
                    manager_type = check_manager_type(directory_input)
                    print(f"manager_type: {manager_type}")
                    if manager_type:
                        split_video(directory_input, manager_type)
                        return
                    else:
                        return
                else:
                    print("")
                    print("Essential software, ffmpeg is not found.")
                    print("Please read how to install ffmpeg from links below.")
                    print("For windows: https://www.wikihow.com/Install-FFmpeg-on-Windows")
                    print("For mac: https://bbc.github.io/bbcat-orchestration-docs/installation-mac-manual/")
                    return
            elif type_input == "fill_csv" or type_input == "fc":
                print("------------------")
                print(f"OKN TOOL INFO")
                print(f"Input directory:{directory_input}")
                print(f"Tool type:{type_input}")
                dir_is_file = os.path.isfile(directory_input)
                valid_file_name = str(directory_input).endswith(".csv") or ".x" in str(directory_input)
                if dir_is_file and valid_file_name:
                    if buffer_length_input:
                        fill_buffer = TinyFillBuffer(int(buffer_length))
                        fill_tiny_in_csv(fill_buffer, directory_input)
                    else:
                        fill_buffer = TinyFillBuffer(7)
                        fill_tiny_in_csv(fill_buffer, directory_input)
                else:
                    print("Invalid directory or file type.")
                    print("Directory must be csv file or excel file.")
                return

    print("------------------")
    print(f"OKN TOOL INFO")
    print(f"Input directory:{directory_input}")
    print(f"Tool type:{type_input}")
    if resource_name:
        print(f"Config/resource: {resource_location}")

    # check whether input directory exists or not
    dir_exist = os.path.isdir(directory_input)
    if not dir_exist:
        is_file = os.path.isfile(directory_input)
        if is_file:
            if type_input == "pnm_video_splitter":
                left_video_dir, right_video_dir = split_pnm_video(directory_input)
                print(f"{left_video_dir} and {right_video_dir}"
                      f" are successfully produced by splitting {directory_input}.")
                return
            else:
                print("Directory input must be directory for this tool type.")
        else:
            print(f"Directory input:{directory_input} does not exist.")
            print(f"Therefore, okntool could not process {type_input}")
            return
    else:
        print(f"Directory input:{directory_input} is valid.")

    type_does_not_need_config = ["indi_va_table", "sum_va_table"]

    if type_input in type_does_not_need_config:
        plot_config_info = {"config_need": False}
    else:
        if resource_dir_exist and dir_exist:
            try:
                # Opening oknserver graph plot config
                with open(resource_location) as f:
                    plot_config_info = json.load(f)
            except FileNotFoundError:
                plot_config_info = None
            if plot_config_info is not None:
                print(f"{resource_name} is found.")
            else:
                print(f"Essential config file:{resource_name} is missing.")
        else:
            plot_config_info = None

    if output_dir_input:
        if output_folder_exist:
            print("Output file location input is found and output folder exists.")
        else:
            print("Output file location input is found but output folder does not exist.")
            print("Therefore, default output location will be used.")
    else:
        print("There is no output file location input.")
        print("Therefore, default output location will be used.")

    if resource_dir_exist and dir_exist and plot_config_info is not None:
        if type_input == "trial":
            # Retrieve trial plot info from config
            trial_plot_info = plot_config_info["trial_plot"]

            csv_name = f"updated_{os.path.basename(directory_input)}.csv"
            print(f"csv name {csv_name}")
            updated_csv_dir = os.path.join(directory_input, csv_name)
            print(f"update csv dir {updated_csv_dir}")
            signal_csv_folder_name = trial_plot_info["signal_csv_folder_name"]
            signal_csv_name = trial_plot_info["signal_csv_name"]
            signal_csv_dir = os.path.join(directory_input, signal_csv_folder_name, signal_csv_name)
            print(f"signal csv dir {signal_csv_dir}")
            if output_folder_exist:
                file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                if file_name_valid:
                    draw_graph_with_overlay(updated_csv_dir, trial_plot_info, signal_csv_dir, output_dir)
                else:
                    print("Invalid image file name")
                    return
            else:
                draw_graph_with_overlay(updated_csv_dir, trial_plot_info, signal_csv_dir)
        elif type_input == "summary":
            # Retrieve summary plot info from config
            summary_plot_info = plot_config_info["summary_plot"]

            if output_folder_exist:
                file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                if file_name_valid:
                    plot_combined_graph(directory_input, summary_plot_info, output_dir)
                else:
                    print("Invalid image file name")
                    return
            else:
                plot_combined_graph(directory_input, summary_plot_info)
        elif type_input == "staircase" or type_input == "progress":
            # Retrieve progress plot info from config
            progress_plot_info = plot_config_info["progress_plot"]

            if output_folder_exist:
                file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                if file_name_valid:
                    draw_progress_graph(directory_input, progress_plot_info, output_dir)
                else:
                    print("Invalid image file name")
                    return
            else:
                draw_progress_graph(directory_input, progress_plot_info)
        elif type_input == "tidy":
            # Retrieve progress plot info from config
            tidy_plot_info = plot_config_info["tidy_plot"]

            if output_folder_exist:
                file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                if file_name_valid:
                    draw_tidy_graph(directory_input, tidy_plot_info, output_dir)
                else:
                    print("Invalid image file name")
                    return
            else:
                draw_tidy_graph(directory_input, tidy_plot_info)
        elif type_input == "simpler":
            # Retrieve simpler plot info from config
            simpler_plot_info = plot_config_info["simpler_plot"]
            if referenced_csv_input:
                if output_folder_exist:
                    file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                    if file_name_valid:
                        draw_simpler_graph(directory_input, simpler_plot_info, referenced_csv_dir, output_dir)
                    else:
                        print("Invalid image file name")
                        return
                else:
                    draw_simpler_graph(directory_input, simpler_plot_info, referenced_csv_dir)
            else:
                print("There is no referenced csv input in the commandline.")
                try:
                    referenced_csv_name = simpler_plot_info["summary_csv_name"]
                except KeyError:
                    print("There is no referenced csv info in the config.")
                    referenced_csv_name = "protocol.simpler.csv"
                    print(f"Therefore using default name => {referenced_csv_name} as default referenced csv")
                # os.path.abspath(os.path.join(directory_input, os.pardir)) == retrieve the parent path
                one_folder_back_dir = os.path.abspath(os.path.join(directory_input, os.pardir))
                two_folder_back_dir = os.path.abspath(os.path.join(one_folder_back_dir, os.pardir))
                referenced_csv_dir = os.path.join(two_folder_back_dir, referenced_csv_name)
                referenced_csv_dir_exist = os.path.isfile(referenced_csv_dir)
                if referenced_csv_dir_exist:
                    print(f"Default referenced csv location:{referenced_csv_dir} is found.")
                    print("Start plotting simpler plot...")
                    if output_folder_exist:
                        file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                        if file_name_valid:
                            draw_simpler_graph(directory_input, simpler_plot_info, referenced_csv_dir, output_dir)
                        else:
                            print("Invalid image file name")
                            return
                    else:
                        draw_simpler_graph(directory_input, simpler_plot_info, referenced_csv_dir)
                else:
                    print(f"Default referenced csv location:{referenced_csv_dir} cannot be found.")
        elif type_input == "indi_va_table":
            if template_dir_input:
                if os.path.isfile(template_dir):
                    print(f"Template file:{template_dir} is found.")
                else:
                    print(f"Template file:{template_dir} could not be found.")
            else:
                print("There is no template file input.")
                print("Therefore, retrieving default template file.")
                template_dir = get_resource_file_location("indi_va_table_template.html")
                if template_dir:
                    print("Retrieving template file is successful.")
                else:
                    print("Error in retrieving template file.")
                    return
            if decider_name_input:
                print(f"Decider file name input:{decider_name} is found.")
            else:
                decider_name = "decider.json"
                print("There is no decide file name input.")
                print(f"Therefore, using default decide file name:{decider_name}")
            if referenced_csv_input:
                if output_dir_input:
                    if os.path.isdir(output_dir):
                        create_indi_va_table_html(directory_input, referenced_csv_dir,
                                                  template_dir, decider_name, output_dir)
                    else:
                        print("Output location input must be directory for \"va_table\" type.")
                        print("Not file directory")
                        return
                else:
                    create_indi_va_table_html(directory_input, referenced_csv_dir, template_dir, decider_name)
            else:
                print("There is no referenced csv input in the commandline.")
                referenced_csv_name = "protocol.simpler.csv"
                print(f"Therefore using default name => {referenced_csv_name} as default referenced csv")
                # os.path.abspath(os.path.join(directory_input, os.pardir)) == retrieve the parent path
                one_folder_back_dir = os.path.abspath(os.path.join(directory_input, os.pardir))
                two_folder_back_dir = os.path.abspath(os.path.join(one_folder_back_dir, os.pardir))
                referenced_csv_dir = os.path.join(two_folder_back_dir, referenced_csv_name)
                referenced_csv_dir_exist = os.path.isfile(referenced_csv_dir)
                if referenced_csv_dir_exist:
                    print(f"Default referenced csv location:{referenced_csv_dir} is found.")
                    if output_dir_input:
                        if os.path.isdir(output_dir):
                            create_indi_va_table_html(directory_input, referenced_csv_dir,
                                                      template_dir, decider_name, output_dir)
                        else:
                            print("Output location input must be directory for \"va_table\" type.")
                            print("Not file directory")
                            return
                    else:
                        create_indi_va_table_html(directory_input, referenced_csv_dir, template_dir, decider_name)
                else:
                    print(f"Default referenced csv location:{referenced_csv_dir} cannot be found.")
        elif type_input == "sum_va_table":
            if template_dir_input:
                if os.path.isfile(template_dir):
                    print(f"Template file:{template_dir} is found.")
                else:
                    print(f"Template file:{template_dir} could not be found.")
            else:
                print("There is no template file input.")
                print("Therefore, retrieving default template file.")
                template_dir = get_resource_file_location("sum_va_table_template.html")
                if template_dir:
                    print("Retrieving template file is successful.")
                else:
                    print("Error in retrieving template file.")
                    return
            if output_dir_input:
                if os.path.isdir(output_dir):
                    create_sum_va_table_html(directory_input, template_dir, output_dir)
                else:
                    print("Output location input must be directory for \"va_table\" type.")
                    print("Not file directory")
                    return
            else:
                create_sum_va_table_html(directory_input, template_dir)
        else:
            print("wrong tool type or invalid tool type.")
    else:
        return
