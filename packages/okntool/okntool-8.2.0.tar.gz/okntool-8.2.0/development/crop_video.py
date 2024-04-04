import csv
import os
import json


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


if __name__ == '__main__':
    gaze_dir = r"C:\Users\zawli\Desktop\ABI\zlin_05_07_2023_long_left_eye_with_p_1_1\gaze.csv"
    video_dir = r"C:\Users\zawli\Desktop\ABI\zlin_05_07_2023_long_left_eye_with_p_1_1\left_video.mp4"
    output_dir = r"C:\Users\zawli\Desktop\ABI\zlin_05_07_2023_long_left_eye_with_p_1_1\cropped"

    file_to_open = open(gaze_dir)
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
    end_time = 0
    trial_id = ""
    event_arr = []
    for row in rows:
        if row[es_position] != " ":
            temp_dict = json.loads(row[es_position])
            if temp_dict["trial_type"] != "animation":
                if temp_dict["type"] == "start_marker":
                    start_time = float(row[ts_position])
                    trial_id = temp_dict["trial_id"]
                else:
                    end_time = float(row[ts_position])
                    duration = round((end_time - start_time), 2)
                    event_arr.append({"trial_id": trial_id, "start_time": round(start_time, 2), "duration": duration})
                data_arr.append([row[ts_position], row[es_position]])

    dir_exist = os.path.isdir(output_dir)
    if not dir_exist:
        os.makedirs(output_dir)
    os.chdir(output_dir)

    for event in event_arr:
        e_trial_id = event["trial_id"]
        e_start_time = event["start_time"]
        e_duration = event["duration"]
        print(event)
        out_v_name = f"{e_trial_id}_cropped.mp4"
        command = f"ffmpeg -i {video_dir} " \
                  f"-ss {e_start_time} " \
                  f"-t {e_duration} " \
                  f"-b:v 10M -c:a copy {out_v_name} -y"
        os.system(command)
