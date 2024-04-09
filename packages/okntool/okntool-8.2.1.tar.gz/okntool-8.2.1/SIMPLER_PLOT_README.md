# Simpler Plot
This plot is to visualize the **face detection and eye tracker related trials and OKNs**.  
It is very similar to tidy plot and their differences are just in the code on how to retrieve the data and use the referenced csv.  
The following parameters are customizable in the simpler plot section of `simpler_plot_config.json`.  

### x_label
The x axis label of the graph.

### x_label_x_position  
The x coordinate position of x axis label.  

### x_label_y_position  
The y coordinate position of x axis label.  

### x_label_alignment  
The alignment of x axis label such as center, right or left.  

### x_label_rotation  
The rotation of x axis label such as 0, 90, 180 or -90.
It is rotating clockwise when the input is positive number.  
It is rotating counterclockwise when the input is negative number.  

### x_label_weight  
The font weight of x axis label.  

### x_label_font_size  
The font size of x axis label.  

### y_label
The y axis label of the graph.  

### y_label_x_position  
The x coordinate position of y axis label.  

### y_label_y_position  
The y coordinate position of y axis label.  

### y_label_alignment  
The alignment of y axis label such as center, right or left. 

### y_label_rotation  
The rotation of y axis label such as 0, 90, 180 or -90.
It is rotating clockwise when the input is positive number.  
It is rotating counterclockwise when the input is negative number.  

### y_label_weight  
The font weight of y axis label.  

### y_label_font_size  
The font size of y axis label.  

### main_boundary_position  
The start x and y coordinates of main rectangle boundary of the graph image.  
The input is decimal number which represents the percentage location of the graph image.  
For example: **[0.12, 0.11]** means the main boundary will be drawn from left 12% and bottom 11% in the graph image.  

### main_boundary_width  
The width of main rectangle boundary.  
The input is decimal number which represents the percentage of the graph image.  
For example: **0.80** means the main boundary width will be 80% of the graph image.  

### main_boundary_height  
The height of main rectangle boundary.  
The input is decimal number which represents the percentage of the graph image.  
For example: **0.78** means the main boundary width will be 78% of the graph image.  

### main_boundary_color  
The color of main rectangle boundary.

### main_boundary_line_thickness  
The link thickness of main rectangle boundary.

### x_data_column_name
The column name of x axis data in the updated trial csv.

### y_data_column_name
The column name of y axis data in the updated trial csv.

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

### axis_y_label_rotation  
The rotation of y axis small label for each trials.  
It is rotating clockwise when the input is positive number.  
It is rotating counterclockwise when the input is negative number.  

### axis_y_label_weight  
The font weight of y axis small label for each trials.  

### axis_y_label_font_size  
The font size of y axis small label for each trials.  

### axis_y_label_pad  
The padding between main boundary and y axis small label for each trials.  

### axis_right_top_left_bottom_borders  
The array which determines whether showing the borders of subplots or not.  
The input must be array and element data type must be boolean.  
There also must be exact 4 elements in the array which represents right, top, left and bottom in order.  
If it is true, then the border will be shown.  
If it is false, it will be hidden.  

### subplots_space_adjustment  
The boolean input to adjust spaces between subplots.  
It it is true, `subplots_width_space` and `subplots_height_space` will be used.    

### subplots_width_space  
The horizontal space between subplots.  
`subplots_space_adjustment` must be true in order to use this value.  

### subplots_height_space  
The vertical space between subplots.  
`subplots_space_adjustment` must be true in order to use this value.  

### mid_line  
The mid horizontal line in the subplots.  
If it is true, then the mid line will be drawn.  

### mid_line_level  
The line level of mid line.  
If it is zero, it will be in the zero level.  
If it is plus number, it will move above zero level.  
If it is minus number, it will move below zero level.  
But the value must not be larger `mean_offset` value and smaller than minus `mean_offset` value.  
For example: If the `mean_offset` is **0.1**, the mid line level input must not be larger than **0.1** and smaller than **-0.1**.  

### mid_line_color  
The color of the mid line of subplots.  

### mid_line_style  
The line style of the mid line of subplots.  
It can be `solid`, `dashed`, `dash-dot` or `dotted`.  

### mid_line_thickness
The link thickness of the mid line of subplots.  

### graph_line_color
The line color of the graph.  

### graph_line_thickness
The line thickness of the graph.  

### image_scale
The size adjustment factor of the output image.  
The bigger the number, the bigger the size of output image.  

### signal_csv_folder_name
The folder name where the signal csv is located.

### signal_csv_name
The name of signal csv.  

### sp_column_name
The column name of slow phase data in the signal csv.  

### qp_column_name
The column name of quick phase data in the signal csv.  

### sp_line_color
The line color of slow phase in the graph.  

### sp_line_thickness
The line thickness of slow phase in the graph.  

### qp_line_color
The line color of quick phase in the graph.  

### qp_line_thickness
The line thickness of quick phase in the graph.  

### time_notation  
The time notation label of the graph.  
If it is "none", the label, line and boundary of time notation will not be drawn.  

### time_notation_text_position  
The x and y coordinates of the time notation text.  
The input is decimal number which represents the percentage location of the graph image.  
For example: **[0.815, 0.918]** means the text will be shown from left 81.5% and bottom 91.8% in the graph image.  

### time_notation_text_weight  
The font weight of the time notation text.  

### time_notation_text_font_size  
The font size of the time notation text.  

### time_line_x_position_start_end  
The start and end x coordinates of the line of time notation.  
The input is decimal number which represents the percentage location of the graph image.  
For example: **[0.766, 0.9]** means the x coordinate of start point is at 76.6% from left and the x coordinate of end point is at 90% from left of the graph image.   

### time_line_y_position_start_end  
The start and end y coordinates of the line of time notation.  
The input is decimal number which represents the percentage location of the graph image.  
For example: **[0.94, 0.94]** means the y coordinate of start point is at 94% from bottom and the y coordinate of end point is at 94% from bottom of the graph image.     

### time_line_style  
The time notation line style.  

### time_line_color  
The time notation line color.   

### time_line_thickness  
The time notation line thickness.  

### time_boundary_position  
The start x and y coordinates of the rectangle of time notation of the graph image.  
The input is decimal number which represents the percentage location of the graph image.  
For example: **[0.749, 0.91]** means the main boundary will be drawn from left 74.8% and bottom 91% in the graph image.  

### time_boundary_width  
The width of time notation rectangle boundary.  
The input is decimal number which represents the percentage of the graph image.  
For example: **0.172** means the main boundary width will be 17.2% of the graph image.  

### time_boundary_height  
The height of time notation rectangle boundary.  
The input is decimal number which represents the percentage of the graph image.  
For example: **0.05** means the main boundary width will be 5% of the graph image.  

### time_boundary_color  
The time notation rectangle boundary color.  

### time_boundary_line_thickness  
The time notation rectangle boundary line thickness.  

### summary_csv_name
The name of csv file that will be used to extract the information of all trial.  

### output_image_name
The name of output image.    
It must be ended with image file type such as `.png` and `.jpeg`.  
