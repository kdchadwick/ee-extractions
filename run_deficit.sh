# shell code for deficit calculations


#asset_layer, output_directory, -point_csv, -wshd, -gage
#python code/api_extractions/ee_extractions.py data/layers_test.csv test_dir_points_2 -point_csv data/coordinates.csv -wshd False -gage 11475560


python3 code/deficit_calcs/deficit_main.py data/timeseries/ca_sites/ca_sites.csv dir_deficit -new_directory True -interpolate True -xtra_imports False
