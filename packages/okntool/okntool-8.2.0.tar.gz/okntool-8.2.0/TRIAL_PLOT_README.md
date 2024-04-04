# Trial Plot
This plot is to visualize the signal csv data whether there is okn or not by using overlay colors on the graph in which green represents slow phase of okn and red represents quick phase.  
The following parameters are customizable in the trial plot section of `oknserver_graph_plot_config.json`.  

### title
The title of the graph

### x_label
The x axis label of the graph

### y_label
The y axis label of the graph

### x_data_column_name
The column name of x axis data in the updated trial csv

### y_data_column_name
The column name of y axis data in the updated trial csv

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

### output_image_name
The name of output image  
It must be ended with image file type such as `.png` and `.jpeg`.
