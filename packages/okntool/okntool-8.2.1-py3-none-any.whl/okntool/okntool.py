import sys
import argparse
import json
import csv
import os
import importlib.resources as okntool_resources
import chevron
import cv2
import subprocess
import numpy as np
from ehdg_tools.ehdg_buffers import TinyFillBuffer
from ehdg_tools.ehdg_plotter import trial_plot, summary_plot, progress_plot, \
    tidy_plot, simpler_plot, get_folder_name_from_dir


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


# This function is to get built-in file location in legacy old way
# There is a new way in using new way along with pyproject.toml
def get_resource_file_location(file_name_input):
    resource_file_exist = okntool_resources.is_resource("okntool", file_name_input)
    if resource_file_exist:
        with okntool_resources.path("okntool", file_name_input) as p:
            resource_file_location = p
    else:
        resource_file_location = None
    return resource_file_location


# This function is to check whether input file has valid file name or not
# by comparing the valid string array
def check_file_name(file_name_input, ending_array_input):
    return True if any([end in file_name_input for end in ending_array_input]) else False


# This function is to create individual va table html
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


# This function is the sub function of create_indi_va_table_html
# This function is to store data in csv before creating html table
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


# This function is the sub function of create_indi_va_table_html
# This function is to read csv data and create va table in html form
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


# This function is the sub function of read_folder_and_create_indi_csv_data
# This function is to produce info array from given folder directory
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


# This function is the sub function of get_info_array_for_ind_va_table
# This function is to retrieve whether there is okn or not from given folder directory
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


# This is the main function to create summary va table in html form
def create_sum_va_table_html(dir_input, template_input, output_file_dir_input=None):
    if output_file_dir_input:
        csv_dir = os.path.join(output_file_dir_input, "sum_va_table.csv")
        html_dir = os.path.join(output_file_dir_input, "sum_va_table.html")
    else:
        csv_dir = os.path.join(dir_input, "sum_va_table.csv")
        html_dir = os.path.join(dir_input, "sum_va_table.html")
    read_folder_and_create_sum_csv_data(dir_input, csv_dir)
    read_csv_data_and_create_sum_va_table_html(csv_dir, template_input, html_dir)


# This function is the sub function of create_sum_va_table_html
# This function is to store data in csv before creating html table
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


# This function is the sub function of create_sum_va_table_html
# This function is to read csv data and create va table in html form
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


# This function is to split pnm joint eye video into separate eye videos
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


# This function is to determine what manager was used in recording
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


# This function is to retrieve all events' info from gaze csv
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

    ts_position = get_index("sensor_timestamp", header_array)
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
                        event_arr.append({"trial_folder_name": trial_folder_name, "start_time": start_time,
                                          "end_time": end_time, "duration": duration})
                    data_arr.append([row[ts_position], row[es_position]])

    return event_arr


# This function is to get timestamp info array from given csv
def get_timestamp_array_from_csv(timestamp_csv_in, header_input):
    timestamp_csv_opened = open(timestamp_csv_in)
    csv_reader = csv.reader(timestamp_csv_opened)
    header_array = []
    rows = []
    count_one = 0

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    timestamp_position = get_index(header_input, header_array)

    timestamp_array = []

    for row in rows:
        timestamp_array.append(float(row[timestamp_position]))

    return timestamp_array


def get_frame_count(nearest_sensor_time, timestamp_array_in):
    for ind, value in enumerate(timestamp_array_in):
        if value >= nearest_sensor_time:
            return ind + 1
    return None


def get_frame_rate(video_dir_input):
    cap_video = cv2.VideoCapture(video_dir_input)
    frame_rate = cap_video.get(cv2.CAP_PROP_FPS)
    return frame_rate


def crop_video(trial_info_input, timestamp_array_input, frame_rate, main_v_dir, out_v_dir):
    e_start_time = trial_info_input["start_time"]
    e_end_time = trial_info_input["end_time"]
    # e_duration = trial_info_input["duration"]
    start_frame_count = get_frame_count(float(e_start_time), timestamp_array_input)
    if start_frame_count is None:
        raise ValueError("start frame count could not be found in eye timestamp csv.")
    end_frame_count = get_frame_count(float(e_end_time), timestamp_array_input)
    if end_frame_count is None:
        raise ValueError("end frame count could not be found in eye timestamp csv.")
    duration_frame_count = end_frame_count - start_frame_count
    duration_by_frame = round(duration_frame_count / frame_rate, 2)
    frame_start_time = round(start_frame_count / frame_rate, 2)
    command = f"ffmpeg -i {main_v_dir} " \
              f"-ss {frame_start_time} " \
              f"-t {duration_by_frame} " \
              f"-b:v 10M -c:a copy {out_v_dir} -y"
    os.system(command)


# This function is split main eye videos into trial eye videos
def split_video(record_folder_dir, record_type):
    if record_type == "pim":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        left_video_dir = os.path.join(record_folder_dir, "left_video.mp4")
        right_video_dir = os.path.join(record_folder_dir, "right_video.mp4")
        left_v_frame_rate = get_frame_rate(left_video_dir)
        right_v_frame_rate = get_frame_rate(right_video_dir)
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)
        left_timestamp_csv_dir = os.path.join(record_folder_dir, "left_eye_timestamp.csv")
        right_timestamp_csv_dir = os.path.join(record_folder_dir, "right_eye_timestamp.csv")
        left_timestamp_array = get_timestamp_array_from_csv(left_timestamp_csv_dir, "left_eye_timestamp")
        right_timestamp_array = get_timestamp_array_from_csv(right_timestamp_csv_dir, "right_eye_timestamp")

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                out_v_name = os.path.join(trial_folder_dir, f"left_{trial_folder_name}_cropped.mp4")
                crop_video(trial_info, left_timestamp_array, left_v_frame_rate, left_video_dir, out_v_name)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                out_v_name = os.path.join(trial_folder_dir, f"right_{trial_folder_name}_cropped.mp4")
                crop_video(trial_info, right_timestamp_array, right_v_frame_rate, right_video_dir, out_v_name)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")

    elif record_type == "pnm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "pnm_eye_video.mp4")
        v_frame_rate = get_frame_rate(video_dir)
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)
        timestamp_csv_dir = os.path.join(record_folder_dir, "pnm_eye_video_timestamp.csv")
        timestamp_array = get_timestamp_array_from_csv(timestamp_csv_dir, "eye_timestamp")

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                crop_video(trial_info, timestamp_array, v_frame_rate, video_dir, out_v_name)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")

    elif record_type == "plm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "PLM_video.mp4")
        v_frame_rate = get_frame_rate(video_dir)
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)
        timestamp_csv_dir = os.path.join(record_folder_dir, "PLM_video_timestamp.csv")
        timestamp_array = get_timestamp_array_from_csv(timestamp_csv_dir, "eye_timestamp")

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                crop_video(trial_info, timestamp_array, v_frame_rate, video_dir, out_v_name)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")
    elif record_type == "pgm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "PGM_video.mp4")
        v_frame_rate = get_frame_rate(video_dir)
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)
        timestamp_csv_dir = os.path.join(record_folder_dir, "PGM_video_timestamp.csv")
        timestamp_array = get_timestamp_array_from_csv(timestamp_csv_dir, "eye_timestamp")

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                crop_video(trial_info, timestamp_array, v_frame_rate, video_dir, out_v_name)
            else:
                raise FileNotFoundError(f"{trial_folder_dir} could not be found.")
    elif record_type == "opm":
        gaze_csv_dir = os.path.join(record_folder_dir, "gaze.csv")
        video_dir = os.path.join(record_folder_dir, "OPM_video.mp4")
        v_frame_rate = get_frame_rate(video_dir)
        trial_info_array = get_event_info_from_gaze(gaze_csv_dir)
        timestamp_csv_dir = os.path.join(record_folder_dir, "OPM_video_timestamp.csv")
        timestamp_array = get_timestamp_array_from_csv(timestamp_csv_dir, "eye_timestamp")

        for trial_info in trial_info_array:
            trial_folder_name = trial_info["trial_folder_name"]
            trial_folder_dir = os.path.join(record_folder_dir, "trials", trial_folder_name)
            dir_exist = os.path.isdir(trial_folder_dir)
            if dir_exist:
                out_v_name = os.path.join(trial_folder_dir, f"{trial_folder_name}_cropped.mp4")
                crop_video(trial_info, timestamp_array, v_frame_rate, video_dir, out_v_name)
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


# This function is to fill tiny holes in csv by using given tiny fill buffer
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


# This function is to find trial timestamp start and end index from given trial csv
def get_trial_start_end_index(trial_csv_dir_input, timestamp_array_input, sensor_timestamp_name):
    trial_csv_opened = open(trial_csv_dir_input)
    trial_csv_reader = csv.reader(trial_csv_opened)
    trial_csv_header_array = []
    trial_rows = []
    trial_counter = 0

    for row in trial_csv_reader:
        if trial_counter <= 0:
            trial_csv_header_array = row
            trial_counter += 1
        else:
            trial_rows.append(row)

    sensor_timestamp_position = get_index(sensor_timestamp_name, trial_csv_header_array)

    trial_timestamp_array = []

    for row in trial_rows:
        trial_timestamp_array.append(float(row[sensor_timestamp_position]))

    try:
        start_time = round(trial_timestamp_array[0], 2)
        end_time = round(trial_timestamp_array[-1], 2)
    except IndexError:
        print(f"Error in retrieving start end index from trial:{trial_csv_dir_input}.")
        return False, False

    start_index = False
    end_index = False
    start_index_found = False

    for ind, time in enumerate(timestamp_array_input):
        time = round(time, 2)
        if time == start_time:
            if not start_index_found:
                start_index = ind
                start_index_found = True
        elif time == end_time:
            end_index = ind
            break

    return start_index, end_index


# This function is to overlay both gaze and trial data onto individual videos.
def overlay_pupil_detection(recording_dir_input,
                            x_value_name="x_value",
                            y_value_name="y_value",
                            ellipse_axis_a_name="ellipse_axis_a",
                            ellipse_axis_b_name="ellipse_axis_b",
                            ellipse_angle_name="ellipse_angle",
                            sensor_timestamp_name="sensor_timestamp",
                            eye_timestamp_column_name="eye_timestamp",
                            summary_csv_input=None,
                            manager_type="plm"):
    gaze_csv_input = os.path.join(recording_dir_input, "gaze.csv")
    timestamp_csv_input = os.path.join(recording_dir_input, f"{str(manager_type).upper()}_video_timestamp.csv")
    video_input = os.path.join(recording_dir_input, f"{str(manager_type).upper()}_video.mp4")
    out_video_dir_input = os.path.join(recording_dir_input, f"{str(manager_type).upper()}_video_overlaid.mp4")
    timestamp_csv_opened = open(timestamp_csv_input)
    csv_reader = csv.reader(timestamp_csv_opened)
    header_array = []
    rows = []
    count_one = 0

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    timestamp_position = get_index(eye_timestamp_column_name, header_array)

    timestamp_array = []

    for row in rows:
        timestamp_array.append(float(row[timestamp_position]))

    gaze_csv_opened = open(gaze_csv_input)
    gaze_csv_reader = csv.reader(gaze_csv_opened)
    gaze_csv_header_array = []
    gaze_rows = []
    gaze_counter = 0

    for row in gaze_csv_reader:
        if gaze_counter <= 0:
            gaze_csv_header_array = row
            gaze_counter += 1
        else:
            gaze_rows.append(row)

    sensor_timestamp_position = get_index(sensor_timestamp_name, gaze_csv_header_array)
    x_position = get_index(x_value_name, gaze_csv_header_array)
    y_position = get_index(y_value_name, gaze_csv_header_array)
    axis_a_position = get_index(ellipse_axis_a_name, gaze_csv_header_array)
    axis_b_position = get_index(ellipse_axis_b_name, gaze_csv_header_array)
    angle_position = get_index(ellipse_angle_name, gaze_csv_header_array)

    overlay_data_array = []

    start_timestamp = round(timestamp_array[0], 2)
    last_timestamp = round(timestamp_array[-1], 2)
    start_index = False
    start_index_found = False
    end_index = False

    for ind, row in enumerate(gaze_rows):
        sensor_timestamp = round(float(row[sensor_timestamp_position]), 2)
        if sensor_timestamp == start_timestamp:
            if not start_index_found:
                start_index = ind
                start_index_found = True
        elif sensor_timestamp == last_timestamp:
            end_index = ind
            break

    cut_gaze_rows = gaze_rows[start_index:end_index + 1]

    for row in cut_gaze_rows:
        sensor_timestamp = float(row[sensor_timestamp_position])
        temp_dict = {}
        temp_dict["timestamp"] = sensor_timestamp
        try:
            temp_dict["center_of_pupil"] = (int(float(row[x_position])), int(float(row[y_position])))
        except ValueError:
            temp_dict["center_of_pupil"] = (0, 0)
        try:
            temp_dict["axes_of_pupil"] = (int(float(row[axis_a_position])), int(float(row[axis_b_position])))
        except ValueError:
            temp_dict["axes_of_pupil"] = (0, 0)
        try:
            temp_dict["angle_of_pupil"] = int(float(row[angle_position]))
        except ValueError:
            temp_dict["angle_of_pupil"] = 0
        overlay_data_array.append(temp_dict)

    input_video = cv2.VideoCapture(video_input)
    frame_width = input_video.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = input_video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_rate = input_video.get(cv2.CAP_PROP_FPS)

    print(f"Start creating pupil detection overlaid video for the whole experiment.")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    v_writer = cv2.VideoWriter(out_video_dir_input, fourcc, int(frame_rate), (int(frame_width), int(frame_height)))
    count = 0

    while True:
        ret, frame = input_video.read()

        if ret:
            detected_frame = np.copy(frame)
            try:
                current_data = overlay_data_array[count]
            except IndexError:
                print(f"Index Error at: {count}")
                return
            center_of_pupil = current_data["center_of_pupil"]
            axes_of_pupil = current_data["axes_of_pupil"]
            angle_of_pupil = current_data["angle_of_pupil"]

            if center_of_pupil != (0, 0):
                cv2.ellipse(
                    detected_frame,
                    center_of_pupil,
                    axes_of_pupil,
                    angle_of_pupil,
                    0, 360,  # start/end angle for drawing
                    (0, 0, 255)  # color (BGR): red
                )
            v_writer.write(detected_frame)
            count += 1
        else:
            v_writer.release()
            break

    trials_folder_dir = os.path.join(recording_dir_input, "trials")

    if summary_csv_input is None:
        summary_csv_input = os.path.join(trials_folder_dir, "okn_detector_summary.csv")
    else:
        if not str(summary_csv_input).lower().endswith(".csv"):
            print("Invalid summary csv.")
            return

    folder_name_array = get_folder_name_from_dir(summary_csv_input)

    for folder_name in folder_name_array:
        print(f"Start creating pupil detection overlaid video for trial:{folder_name}.")
        trial_csv_dir = os.path.join(trials_folder_dir, folder_name, f"{folder_name}.csv")
        trial_out_v_dir = os.path.join(trials_folder_dir, folder_name, f"{folder_name}_overlaid.mp4")
        # tsa = timestamp array
        tsa_start_index, tsa_end_index = get_trial_start_end_index(trial_csv_dir,
                                                                   timestamp_array,
                                                                   sensor_timestamp_name)

        trial_video = cv2.VideoCapture(video_input)
        frame_width = trial_video.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = trial_video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        frame_rate = trial_video.get(cv2.CAP_PROP_FPS)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        trial_v_writer = cv2.VideoWriter(trial_out_v_dir, fourcc,
                                         int(frame_rate),
                                         (int(frame_width), int(frame_height)))
        count = 0

        while True:
            trial_ret, trial_frame = trial_video.read()

            if trial_ret:
                detected_frame = np.copy(trial_frame)
                current_data = overlay_data_array[count]
                center_of_pupil = current_data["center_of_pupil"]
                axes_of_pupil = current_data["axes_of_pupil"]
                angle_of_pupil = current_data["angle_of_pupil"]

                if center_of_pupil != (0, 0):
                    cv2.ellipse(
                        detected_frame,
                        center_of_pupil,
                        axes_of_pupil,
                        angle_of_pupil,
                        0, 360,  # start/end angle for drawing
                        (0, 0, 255)  # color (BGR): red
                    )
                if tsa_start_index <= count <= tsa_end_index:
                    trial_v_writer.write(detected_frame)
                else:
                    if count > tsa_end_index:
                        trial_v_writer.release()
                        break
                count += 1
            else:
                trial_v_writer.release()
                break
        print(f"{trial_out_v_dir} is created.")

    return out_video_dir_input


def main():
    parser = argparse.ArgumentParser(prog='okntool',
                                     description='okn related graphs plotting program.')
    parser.add_argument('--version', action='version', version='8.2.1'),
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
    parser.add_argument("-in", dest="image_name", required=False, default=sys.stdin,
                        help="plot image name", metavar="plot image name")
    parser.add_argument("-gc", dest="gaze_csv_dir", required=False, default=sys.stdin,
                        help="gaze csv location", metavar="gaze csv location")
    parser.add_argument("-tn", dest="trial_name", required=False, default=sys.stdin,
                        help="trial name to search in gaze csv", metavar="trial name")
    parser.add_argument("-is", dest="is_sweep", required=False, default=sys.stdin,
                        help="Is it sweep?", metavar="Is it sweep?")
    parser.add_argument("-mr", dest="max_row", required=False, default=sys.stdin,
                        help="max row", metavar="max row")
    parser.add_argument("-sc", dest="summary_csv", required=False, default=sys.stdin,
                        help="summary csv", metavar="summary csv")

    args = parser.parse_args()
    directory_input = str(args.directory_input)
    type_input = str(args.tool_type)
    config_file_location = str(args.config_dir)
    referenced_csv_dir = str(args.referenced_csv)
    output_dir = str(args.output)
    template_dir = str(args.template)
    decider_name = str(args.decider_name)
    buffer_length = str(args.buffer_length)
    image_name = str(args.image_name)
    gaze_csv_dir = str(args.gaze_csv_dir)
    trial_name = str(args.trial_name)
    is_sweep = str(args.is_sweep)
    max_row = str(args.max_row)
    summary_csv = str(args.summary_csv)
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
    image_name_input = False if "_io.TextIOWrapper" in image_name else True
    gaze_csv_dir_input = False if "_io.TextIOWrapper" in gaze_csv_dir else True
    trial_name_input = False if "_io.TextIOWrapper" in trial_name else True
    is_sweep_input = False if "_io.TextIOWrapper" in trial_name else True
    max_row_input = False if "_io.TextIOWrapper" in max_row else True
    summary_csv_input = False if "_io.TextIOWrapper" in summary_csv else True
    output_dir = None if not output_dir_input else output_dir
    image_name = None if not image_name_input else image_name
    gaze_csv_dir = None if not gaze_csv_dir_input else gaze_csv_dir
    max_row = None if not max_row_input else max_row
    summary_csv = None if not summary_csv_input else summary_csv
    if gaze_csv_dir is not None:
        if "gaze.csv" in gaze_csv_dir and os.path.isfile(gaze_csv_dir):
            pass
        else:
            print("Invalid gaze csv dir input.")
            return
    if summary_csv is not None:
        if os.path.isfile(summary_csv) and ".csv" in str(summary_csv).lower():
            pass
        else:
            print("Invalid summary csv input.")
            return
    trial_name = None if not trial_name_input else trial_name
    image_file_ending_array = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
    # va_table_related_file_ending_array = ['.csv', '.html']
    sweep_yes_indicator = ["y", "yes", "true", "t", "1"]
    if is_sweep_input:
        is_sweep = True if str(is_sweep).lower() in sweep_yes_indicator else False
    else:
        is_sweep = True if "sweep" in str(directory_input).lower() else False
    if max_row is not None:
        try:
            max_row = int(max_row)
        except ValueError:
            print("Invalid max row input.")
            print("There will be no max row limit.")
            max_row = None
    output_file_name = None
    output_folder = None
    if output_dir_input:
        print("There is output directory input.")
        is_output_dir_file = os.path.isfile(output_dir)
        if is_output_dir_file:
            print("Output directory input is a file.")
            output_folder = os.path.join(output_dir, os.pardir)
            output_folder_exist = os.path.isdir(output_folder)
            if output_folder_exist:
                output_file_name = os.path.basename(output_dir)
                file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                if not file_name_valid:
                    print("Invalid output image file name")
                    return
                else:
                    image_name = output_file_name
        else:
            image_name = None
            is_output_dir_folder = os.path.isdir(output_dir)
            if is_output_dir_folder:
                print("Output directory input is a folder.")
                output_folder = output_dir
            else:
                print("Output directory input does not exist.")
                return
    else:
        pass

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
                          "fc": None,
                          "overlay_pupil_detection": None,
                          "opd": None
                          }

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
            # resource_location = None
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
                        print("Manager type could not be found.")
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
            elif type_input == "overlay_pupil_detection" or type_input == "opd":
                print("------------------")
                print(f"OKN TOOL INFO")
                print(f"Input directory:{directory_input}")
                print(f"Tool type:{type_input}")
                manager_type = check_manager_type(directory_input)
                print(f"manager_type: {manager_type}")
                if manager_type:
                    if manager_type == "plm" or manager_type == "opm":
                        out_v_dir = overlay_pupil_detection(directory_input,
                                                            summary_csv_input=summary_csv,
                                                            manager_type=manager_type)
                        print(f"{out_v_dir} is created.")
                        return
                    else:
                        print(f"{type_input} does not support manager type:{manager_type}.")
                        return
                else:
                    print("Manager type could not be found.")
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

    if resource_dir_exist and dir_exist and plot_config_info is not None:
        if type_input == "trial":
            # Retrieve trial plot info from config
            trial_plot_info = plot_config_info["trial_plot"]

            is_input_dir_file = os.path.isfile(directory_input)
            if is_input_dir_file:
                input_dir = os.path.join(directory_input, os.pardir)
            else:
                if os.path.isdir(directory_input):
                    input_dir = directory_input
                else:
                    print(f"Invalid directory input:{directory_input}.")
                    return
            signal_csv_folder_name = trial_plot_info["signal_csv_folder_name"]
            signal_csv_name = trial_plot_info["signal_csv_name"]
            signal_csv_dir = os.path.join(input_dir, signal_csv_folder_name, signal_csv_name)
            print(f"signal csv dir {signal_csv_dir}")
            print(f"output_folder: {output_folder}")
            trial_plot(trial_plot_info, signal_csv_dir, output_folder, image_name, gaze_csv_dir, trial_name)
        elif type_input == "summary":
            # Retrieve summary plot info from config
            summary_plot_info = plot_config_info["summary_plot"]
            if is_sweep and max_row is None:
                max_row = 2
                print("It is sweep plot but there is not max row input.")
                print(f"Therefore, using default max row value:{2}. ")
            summary_plot(directory_input, summary_plot_info, output_folder, image_name, gaze_csv_dir, max_row,
                         summary_csv, is_sweep)
        elif type_input == "staircase" or type_input == "progress":
            # Retrieve progress plot info from config
            progress_plot_info = plot_config_info["progress_plot"]
            progress_plot(directory_input, progress_plot_info, output_folder, image_name)
        elif type_input == "tidy":
            # Retrieve progress plot info from config
            tidy_plot_info = plot_config_info["tidy_plot"]
            tidy_plot(directory_input, tidy_plot_info, output_folder, image_name)
        elif type_input == "simpler":
            # Retrieve simpler plot info from config
            simpler_plot_info = plot_config_info["simpler_plot"]
            if referenced_csv_input:
                if output_dir_input:
                    file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                    if file_name_valid:
                        simpler_plot(directory_input, simpler_plot_info, referenced_csv_dir, output_dir)
                    else:
                        print("Invalid image file name")
                        return
                else:
                    simpler_plot(directory_input, simpler_plot_info, referenced_csv_dir)
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
                    if output_dir_input:
                        file_name_valid = check_file_name(output_file_name, image_file_ending_array)
                        if file_name_valid:
                            simpler_plot(directory_input, simpler_plot_info, referenced_csv_dir, output_dir)
                        else:
                            print("Invalid image file name")
                            return
                    else:
                        simpler_plot(directory_input, simpler_plot_info, referenced_csv_dir)
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
