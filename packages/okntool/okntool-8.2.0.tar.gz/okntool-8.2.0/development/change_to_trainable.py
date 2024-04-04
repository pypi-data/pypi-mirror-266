import csv
import os
import json
import cv2


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


# This function is to change from frame count to frame time to be used as pupil time
def frame_to_time(frame_number_input, frame_rate_input):
    return frame_number_input / frame_rate_input


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

    x_position = get_index("x_nom", header_array)
    y_position = get_index("y_nom", header_array)
    ts_position = get_index("record_timestamp", header_array)
    es_position = get_index("event_string", header_array)

    data_arr = []
    start_time = 0
    end_time = 0
    trial_id = ""
    event_arr = []
    gaze_data_arr = []
    collecting = False
    for row in rows:
        if collecting:
            t_dict = {}
            t_dict["x"] = float(row[x_position])
            t_dict["y"] = float(row[y_position])
            t_dict["rt"] = round(float(row[ts_position]), 2)
            gaze_data_arr.append(t_dict)
        if row[es_position] != " ":
            temp_dict = json.loads(row[es_position])
            if temp_dict["trial_type"] != "animation":
                if temp_dict["type"] == "start_marker":
                    start_time = float(row[ts_position])
                    trial_id = temp_dict["trial_id"]
                    t_dict = {}
                    t_dict["x"] = float(row[x_position])
                    t_dict["y"] = float(row[y_position])
                    t_dict["rt"] = round(float(row[ts_position]), 2)
                    gaze_data_arr.append(t_dict)
                    collecting = True
                else:
                    end_time = float(row[ts_position])
                    duration = round((end_time - start_time), 2)
                    t_dict = {}
                    t_dict["x"] = float(row[x_position])
                    t_dict["y"] = float(row[y_position])
                    t_dict["rt"] = round(float(row[ts_position]), 2)
                    gaze_data_arr.append(t_dict)
                    collecting = False
                    event_arr.append({"trial_id": trial_id, "start_time": round(start_time, 2),
                                      "duration": duration, "data_array": gaze_data_arr})
                    gaze_data_arr = []
                data_arr.append([row[ts_position], row[es_position]])

    for e in event_arr:
        trial_id = e["trial_id"]
        data_array = e["data_array"]
        v_folder_location = r"C:\Users\zawli\Desktop\ABI\zlin_05_07_2023_long_left_eye_with_p_1_1\cropped"
        v_location = os.path.join(v_folder_location, f"{trial_id}_cropped.mp4")
        out_v_location = os.path.join(v_folder_location, f"{trial_id}_trainable.mp4")

        input_video = cv2.VideoCapture(v_location)
        frame_width = input_video.get(cv2.CAP_PROP_FRAME_WIDTH)
        print("Input frame width:", frame_width)
        frame_height = input_video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print("Input frame height:", frame_height)
        frame_rate = input_video.get(cv2.CAP_PROP_FPS)
        print("Input frame rate:", frame_rate)
        frame_count = input_video.get(cv2.CAP_PROP_FRAME_COUNT)
        print("Input frame count:", frame_count)

        count = 0
        ind = 0
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        print(out_v_location)
        v_writer = cv2.VideoWriter(out_v_location, fourcc, int(frame_rate), (int(frame_width), int(frame_height)))
        array_length = len(data_array)
        v_start_time = e["start_time"]
        while True:
            ret, frame = input_video.read()
            if ret:
                count += 1
                pupil_time = frame_to_time(count, frame_rate)
                black_frame = frame
                black_frame.fill(0)
                if ind < array_length:
                    # print(data_array[ind]["rt"] - v_start_time)
                    # print(pupil_time)
                    if pupil_time >= (data_array[ind]["rt"] - v_start_time):
                        # print("here")
                        # Show world video with gaze overlay
                        gaze_data = (int(data_array[ind]["x"] * frame_width), int(data_array[ind]["y"] * frame_height))
                        cv2.circle(
                            black_frame,
                            gaze_data,
                            50, (255, 255, 255), -1
                        )
                        ind += 1
                        # cv2.imshow("Frame", black_frame)
                v_writer.write(black_frame)

            # When there is no frame to read
            else:
                input_video.release()
                cv2.destroyAllWindows()
                v_writer.release()
                break
