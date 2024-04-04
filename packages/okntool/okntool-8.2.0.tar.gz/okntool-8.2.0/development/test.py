# to use temp place to make version testing
# import pkg_resources
#
# DATA_PATH = pkg_resources.resource_filename("okntool", "oknserver_graph_plot_config.json")
# # DB_FILE = pkg_resources.resource_filename('<package name>', 'data/sqlite.db')
# print(DATA_PATH)

import importlib.resources as config_resources
import os

config_exist = config_resources.is_resource("okntool", "oknserver_graph_plot_config.json")
# DB_FILE = pkg_resources.resource_filename('<package name>', 'data/sqlite.db')
with config_resources.path("okntool", "oknserver_graph_plot_config.json") as p:
    p = p
print(config_exist)
print(p)

raw_file_name = "./clip-2-trial-1-2-disks.mp4"
print(raw_file_name)
folder_name = raw_file_name[raw_file_name.find("./") + 2:raw_file_name.find(".mp4")]
print(folder_name)

# import os
#
# referenced_csv_name = "protocol.simpler.csv"
# directory_input = r"C:\Users\zawli\Desktop\ABI\jtur_10_01_23_long\results\okn"
# input_folder_name = os.path.basename(directory_input)
# one_folder_back_dir = os.path.abspath(os.path.join(directory_input, os.pardir))
# two_folder_back_dir = os.path.abspath(os.path.join(one_folder_back_dir, os.pardir))
# referenced_csv_dir = os.path.join(two_folder_back_dir, referenced_csv_name)
# print(one_folder_back_dir)
# print(two_folder_back_dir)
# print(referenced_csv_dir)

# ending = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']
# test_name = "name.gif"
# end_or_not = True if any([end in test_name for end in ending]) else False
# print(end_or_not)
#
# output_dir = r"C:\Users\zlin341\Documents\GitHub\okntool\development"
# output_folder = os.path.join(output_dir, os.pardir)
# output_folder_exist = os.path.isdir(output_folder)
# if output_folder_exist:
#     output_file_name = os.path.basename(output_dir)
# print(output_file_name)

ex_dir = r"C:\Users\zawli\Desktop\ABI"

print("***")
sub_folders = [name for name in os.listdir(ex_dir) if os.path.isdir(os.path.join(ex_dir, name))]
for d in sub_folders:
    print(d)

ex_dir = r"C:\Users\zawli\Desktop\ABI\jtur_10_01_23_long"

print("***")
sub_folders = [name for name in os.listdir(ex_dir) if os.path.isdir(os.path.join(ex_dir, name))]
for d in sub_folders:
    print(d)

print(os.path.isdir(ex_dir))
print(os.path.isfile(ex_dir))
