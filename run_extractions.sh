# shell code for: 
#running extractions, 
#outputting them as csvs merged by dates, 
#and interpolating based on data reporting intervals (<- doesnt do this yet)

#asset_layer, output_directory, -point_csv, -wshd, -gage
# python code/api_extractions/ee_extractions.py data/layers_short_contemporary.csv dir_timeseries -gage 11465350 -wshd True

python code/api_extractions/ee_extractions.py data/layers_test.csv dir_timeseries -gage 11465350 -wshd True

