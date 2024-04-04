import cv2
import csv
import os
import numpy as np
from ehdg_tools.ehdg_plotter import get_folder_name_from_dir


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


if __name__ == '__main__':
    recording_dir = r"C:\Users\zawli\Desktop\ABI\cfra_opm_testing_rerun"
    out_v_dir = overlay_pupil_detection(recording_dir, manager_type="opm")
    # recording_dir = r"C:\Users\zawli\Downloads\1Mar2024\test_right_eye_v_1_4_1_OD_x3_left_sweep"
    # out_v_dir = overlay_pupil_detection(recording_dir, manager_type="plm")
