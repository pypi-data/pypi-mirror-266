# Progress Plot
This plot is to visualize the progression of the web experiment which shows whether there is okn or not in each trial, best va level and final va level.  
The following parameters are customizable in the progress plot section of `oknserver_graph_plot_config.json`.

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

### okn_matlab_column_name
The column name of okn_matlab which has okn or not shown as 1 or 0 in okn_detector_summary.csv.

### phase_column_name
The column name of phase in trial_data.csv

### final_logmar_column_name
The column name of final_logmar in trial_data.csv

### graph_line_color
The line color of the graph

### graph_line_thickness
The line thickness of the graph


### graph_line_style
The line style of the graph  
It can be `solid`, `dashed`, `dash-dot` or `dotted`.

### summary_csv_name
The name of summary csv

### trial_summary_csv_name
The name of trial data or trial summary csv

### output_image_name
The name of output image

### marker_type_equivalent
It is the python dictionary to retrieve the matlibplot symbol equivalent from the symbol string such as `circle` and `triangle`.

### marker_type
The type or style of marker  
It can be `circle`, `triangle`, `square`, `star`, `diamond`, `thin_diamond` and `plus`.

### marker_size
The size of marker

### okn_marker_color
The color of okn marker

### okn_marker_edge_color
The color of okn marker edge

### okn_legend_label
The label of okn marker legend

### non_okn_marker_color
The color of non okn marker

### non_okn_marker_edge_color
The color of non okn marker edge

### non_okn_legend_label"
The label of non okn marker legend

### best_va_line
If it is `true`, there will be best va line in the graph.

### best_va_line_color
The color of best va line

### best_va_line_thickness
The line thickness of best va line

### best_va_line_style
The line style of best va line  
It can be `solid`, `dashed`, `dash-dot` or `dotted`.

### best_va_line_legend_label
The label of best va line legend

### final_va_line
If it is `true`, there will be final va line in the graph.

### final_va_line_color
The color of final va line

### final_va_line_thickness
The line thickness of final va line

### final_va_line_style
The line style of final va line  
It can be `solid`, `dashed`, `dash-dot` or `dotted`.

### final_va_line_legend_label
The label of final va line legend

### legend_background_color
The color of legend background

### legend_edge_color
The color of legend edge

### legend_location
The location of legend
It can be `best`, `upper right`, `upper left`, `lower left`, `lower right`, `right`, `center left`, `center right`, `lower center`, `upper center` or `center`.

### legend_font_size
The font size of legend  
It can be `integer number`, `xx-small`, `x-small`, `small`, `medium`, `large`, `x-large` or `xx-large`.
### legend_icon_size
The size of marker in the legend

### line_style_equivalent
It is the python dictionary to retrieve the matlibplot line style equivalent from the line style strings which are `solid`, `dashed`, `dash-dot` and `dotted`.
