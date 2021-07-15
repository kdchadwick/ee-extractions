# shell code for: 
#Diret/Indirect Storage 

python3 code/api_extractions/ee_extractions.py data/layers_test.csv projects/putah_dir2 -wshd True -gage 11453500

python3 code/direct_storage/direct_storage.py projects/putah_dir2 projects/putah_dir2/extractions_w_merge_on_date.csv  11453500  -basin_name PutahCreek -disturbance_date 07-22-15 -plot_year 2013 -plot_year_postdisturb 2016
