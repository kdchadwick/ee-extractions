# shell code for deficit calculations


#asset_layer, output_directory, -point_csv, -wshd, -gage
#python code/api_extractions/ee_extractions.py data/layers_test.csv test_dir_points_2 -point_csv data/coordinates.csv -wshd False -gage 11475560


#input_timeseries.csv, output_directory, -single_site -new_directory, -show_modis, -interpolate, -xtra_imports, -snow_correction, -snow_frac
python code/deficit_calcs/deficit_main.py watershed_11475560/ee_extractions/exports/watershed_extractions_w_merge_on_date.csv watershed_11475560 -single_site True -new_directory False -show_modis True -interpolate True -xtra_imports False

