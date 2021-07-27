# shell code for deficit calculations

for ws in 11046300 11046360 11111500 11132500 11134800 11141280 11151300 11154700 11172945 11176400 11180825 11180900 11180960 11182500 11224500 11253310 11284400 11299600 11379500 11449500 11469000 11475560 11475800 11476600 ; do
#11111500 11284400 11475800 
    #asset_layer, output_directory, -point_csv, -wshd, -gage
    python3 code/api_extractions/ee_extractions.py data/layers_short_contemporary.csv watershed_$ws -gage $ws -wshd True

    #input_timeseries.csv, output_directory, -single_site -new_directory, -show_modis, -interpolate, -xtra_imports, -snow_correction, -snow_frac
    python3 code/deficit_calcs/deficit_main.py watershed_$ws/ee_extractions/exports/watershed_extractions_w_merge_on_date.csv watershed_$ws -single_site True -new_directory False -show_modis True -interpolate True -xtra_imports False;
done 



