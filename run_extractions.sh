# shell code for: 
#running extractions, 
#outputting them as csvs merged by dates, 
#and interpolating based on data reporting intervals

python code/api_extractions/ee_extractions.py data/layers_test.csv test_dir_points_2 -point_csv data/coordinates.csv -wshd False -gage 11475560

