# Summary Plot
This plot is the summary combination of all trial plots to visualize the whole recording whether there is okn or not.    
The following parameters are customizable in the summary plot section of `oknserver_graph_plot_config.json`.

### x_label
The x axis label of the graph

### y_label
The y axis label of the graph

### x_data_column_name
The column name of x axis data in the updated trial csv

### y_data_column_name
The column name of y axis data in the updated trial csv

### x_axis_limit
The limit of x axis which will be used in manual axis adjustment type.  
It is an array which contains lower limit and upper limit of x axis.

### y_axis_limit
The limit of y axis which will be used in manual axis adjustment type.  
It is an array which contains lower limit and upper limit of y axis.

### mean_offset
The mean offset value to be used in mean_offset axis adjustment type.  

### axis_adjustment_types
The types of axis adjustment currently available in the oknserver.  
It is a python dictionary which stores the axis adjustment types along with string numbers in order to be retrieved easily by number.

### axis_adjustment_type_number
The number to retrieve the type of axis adjustment to be used in summary graph plot.  

### graph_line_color
The line color of the graph

### graph_line_thickness
The line thickness of the graph

### image_scale
The size adjustment factor of the output image.  
The bigger the number, the bigger the size of output image.  

### signal_csv_folder_name
The folder name where the signal csv is located.

### signal_csv_name
The name of signal csv

### sp_column_name
The column name of slow phase data in the signal csv

### qp_column_name
The column name of quick phase data in the signal csv

### sp_line_color
The line color of slow phase in the graph

### sp_line_thickness
The line thickness of slow phase in the graph

### qp_line_color
The line color of quick phase in the graph

### qp_line_thickness
The line thickness of quick phase in the graph

### summary_csv_name
The name of summary csv file that will be used to extract the information of all trial.

### output_image_name
The name of output image  
It must be ended with image file type such as `.png` and `.jpeg`.
