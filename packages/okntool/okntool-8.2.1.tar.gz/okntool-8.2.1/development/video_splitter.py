import os
import csv
import json
import subprocess


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
                if temp_dict["trial_type"] != "animation":
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
    else:
        print("Invalid manager type.")


def check_manager_type(gaze_dir_input):
    temp_dir = os.listdir(gaze_dir_input)
    left_video_exist = True if "left_video.mp4" in temp_dir else False
    right_video_exist = True if "right_video.mp4" in temp_dir else False
    pnm_eye_video_exist = True if "pnm_eye_video.mp4" in temp_dir else False
    plm_video_exist = True if "PLM_video.mp4" in temp_dir else False
    pgm_video_exist = True if "PGM_video.mp4" in temp_dir else False
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
        else:
            if not left_video_exist:
                print(f"left_video.mp4 file could not be found in {gaze_dir_input}.")
            elif not right_video_exist:
                print(f"right_video.mp4 file could not be found in {gaze_dir_input}.")
            elif not pnm_eye_video_exist:
                print(f"pnm_eye_video.mp4 file could not be found in {gaze_dir_input}.")
            elif not plm_video_exist:
                print(f"PLM_video.mp4 file could not be found in {gaze_dir_input}.")
            elif not pgm_video_exist:
                print(f"PGM_video.mp4 file could not be found in {gaze_dir_input}.")
            print("Therefore, the process will not be continued and it will stop here.")
            return None
    else:
        print(f"gaze.csv file could not be found in {gaze_dir_input}.")
        print("Therefore, the process will not be continued and it will stop here.")
        return None


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


if __name__ == '__main__':
    directory_input = input("Please give the link.")
    ffmpeg_exist = check_ffmpeg()
    if ffmpeg_exist:
        manager_type = check_manager_type(directory_input)
        print(f"manager_type: {manager_type}")
        if manager_type:
            split_video(directory_input, manager_type)
    else:
        print("")
        print("Essential software, ffmpeg is not found.")
        print("Please read how to install ffmpeg from links below.")
        print("For windows: https://www.wikihow.com/Install-FFmpeg-on-Windows")
        print("For mac: https://bbc.github.io/bbcat-orchestration-docs/installation-mac-manual/")
