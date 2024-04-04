# OKN TOOL PYTHON PACKAGE LIBRARY MANUAL
## Description
This program will draw the graph image in the ABI eye research group web experience recording folder according to config file information and plot type input. 
Moreover, it can also produce va table csv and html files for both individual and summary data folder.

There are 8 types of okn tool which are:
1.  **Trial** plot which represents sensor timestamp vs pupil displacement/movement graph for each trial.
2.  **Summary** plot which is the combination of all trial plots with the same x and y axis scales.
3.  **Staircase/progress** plot which is the graph image to visualize whether there is okn or not and the visual acuity etdrs calculation steps.
4.  **Tidy** plot, the special plot for all trial protocol in which borders and boundaries are drawn in tidest format.
5.  **Simpler** plot, the special plot for face detection and eye tracker related OKNs.
6.  **indi_va_table** which will create **indi_va_table.csv** and **indi_va_table.html** depand on whether there is okn or not in each trials.
7.  **sum_va_table** which will create **sum_va_table.csv** and **sum_va_table.html** by using **indi_va_table.csv** of each folder which is produced by **indi_va_table** okn tool type.
8.  **pnm_video_splitter** which will split **pnm_eye_video.mp4** into **pnm_left_eye_video** and **pnm_right_eye_video**.
9.  **overlay_pupil_detection** which will overlay pupil detection on eye videos of **opm** and **plm** manager recording.

## Installation requirements and guide
### Anaconda
To install this program, `Anaconda python distributing program` and `Anaconda Powershell Prompt` are needed.  
If you do not have `Anaconda`, please use the following links to download and install:  
Download link: https://www.anaconda.com/products/distribution  
Installation guide link: https://docs.anaconda.com/anaconda/install/  
### PIP install
To install `okntool`, you have to use `Anaconda Powershell Prompt`.  
After that, you can use the `okntool` from any command prompt.  
In `Anaconda Powershell Prompt`:
```
pip install okntool
```  
## Usage guide
### Example usage
```
okntool -t "(plot_type)" -d "(directory to the folder)" -c "(directory to config file)" -r "(referenced csv)"
```
plot_type: "trial", "summary" or "staircase"  
If you are using "trial" plot type, please -d "(directory to trial folder)".  
If you are using "summary" or "staircase" plot type, please -d "(directory to pim_recorded_folder/trials)".  
**-r** is only for "simpler" plot type.  

There is a example folder under `development` folder.  
If you want to test this program, you can clone this repository, install `okntool` and run the following command:  
**For trial plot**
```
okntool -t "trial" -d "development/example/trials/trials/trial-1-1_disk-condition-1-1"
```

**For summary plot**
```
okntool -t "summary" -d "development/example/trials/trials"
```

**For staircase/progress plot**
```
okntool -t "staircase" -d "development/example/trials/trials"
```
or
```
okntool -t "progress" -d "development/example/trials/trials"
```

**For tidy plot**
```
okntool -t "tidy" -d "development/example/trials/trials"
```

**For simpler plot**
```
okntool -t "simpler" -d "(folders which clip folders)"
```
or
```
okntool -t "simpler" -d "(folders which clip folders)" -c (simpler plot configuration) -r (referenced csv)
```
The **-c** and **-r** arguments are optional. The okntool has its own built-in config and default referenced csv location which is two folder back of input folder directory.
i.e. If the input folder diectory is "(example/result/okn)", the default referenced csv location is "(example/protocol.simpler.csv)". 

**For indi_va_table**
```
okntool -t "indi_va_table" -d "(folder which contains clip folders each contains decider.json)"
```
or
```
okntool -t "indi_va_table" -d "(folder which contains clip folders each contains decider.json)" -p "(template html file)" -n "(decider file name)" -r "(referenced csv)" -o "(output location)"
```
The **-p**, **-n**, **-r** and **-o** arguments are optional. The okntool has its own built-in template html, default decider file name and default referenced csv location which is two folder back of input folder directory.
i.e. If the input folder diectory is "(example/result/okn)", the default referenced csv location is "(example/protocol.simpler.csv)".  

**For sum_va_table**
```
okntool -t "sum_va_table" -d "(folder which contains folders each contains indi_va_table.csv)"
```
or
```
okntool -t "sum_va_table" -d "(folder which contains folders each contains indi_va_table.csv)" -p "(template html file)" -o "(output location)"
```
The **-p** and **-o** arguments are optional. The okntool has its own built-in template html.    

**For pnm_video_splitter**
```
okntool -t "pnm_video_splitter" -d "(location of pnm_eye_video.mp4)"
```
**For split_video**
```
okntool -t "split_video" -d "(recording folder directory)"
```
(or)
```
okntool -t "sv" -d "(recording folder directory)"
```
**For overlay_pupil_detection**
```
okntool -t "overlay_pupil_detection" -d "(recording folder directory)"
```
(or)
```
okntool -t "opd" -d "(recording folder directory)"
```
If you wanna use **okn_detector_summary.csv** outside of the recording folder,  
```
okntool -t "overlay_pupil_detection" -d "(recording folder directory)" -sc "(directory to summary csv)"
```
(or)
```
okntool -t "opd" -d "(recording folder directory)" -sc "(directory to summary csv)"
```
### oknserver_graph_plot_config.json
This is a built-in config file which contains the information how trial plot, summary plot and progress plot will be drawn.  
Please read more details about them in TRIAL_PLOT_README.md, SUMMARY_PLOT_README.md, PROGRESS_PLOT_README.md and TIDY_PLOT_README.md.
If you wanna change the parameters of config file, copy and paste the built-in config file into a different directory.
After that modify the config file and run the okntool with optional argument `-c (directory to new config file)`.  
```
okntool -t "(plot_type)" -d "(directory to the folder)" -c "(directory to new config file)"
```

### simpler_plot_config.json
This is a built-in config file which contains the information how simpler plot will be drawn.  
Please read more details in SIMLER_PLOT_README.md.
If you wanna change the parameters of config file, copy and paste the built-in config file into a different directory.

### To upgrade version  
In `Anaconda Powershell Prompt`,
```
pip install -U okntool
```
or
```
pip install --upgrade okntool
```
