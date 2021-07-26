import rasterio, warnings, re, os, subprocess
import numpy as np
import pandas as pd
import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
import rasterstats as rs
import matplotlib.pyplot as plt
from osgeo import gdal, osr
warnings.filterwarnings('ignore')




def main():
    raster_output_path = os.path.join('Hahm_Unmasked_Areas', 'basin_vis', 'exports','rasters')
    subprocess.call('mkdir ' + os.path.join(raster_output_path), shell=True)
    shp_output_path = 'output'
    target_epsg = 32610 # WGS84 UTM 10N for CA
    target_res = 30
    raster_path = '/Volumes/GoogleDrive/My Drive/Datasets/California/statewide/CWC'
    basin_path = os.path.join('Hahm_Unmasked_Areas', 'basin_vis', 'exports')

    #gdf = gpd.read_file('/Users/kdchadwick/GitHub/ee-extractions/Hahm_Unmasked_Areas/basin_vis/exports/sites_USGS_11475560.geojson')
    #print(type(gdf))
    all_basins = [j for j in os.listdir(basin_path) if j.endswith('.geojson')]
    for j in range(len(all_basins)):
        print(os.path.join(basin_path, all_basins[j]))
        rasters = [i for i in os.listdir(raster_path) if i.endswith('.tif')]
        print('clipping all rasters for ', all_basins[j],' basin')
        reproject_rasters(epsg_out=target_epsg, ext=all_basins[j], rasters=rasters, raster_path=raster_path, output_path=raster_output_path, basin_path=basin_path, target_res=target_res)

    # plot_shapes = reproject_shapes(epsg_out=target_epsg, plot_csv='plot_surveys_w_ids.csv', plot_path='output', output_path=shp_output_path)

    # points = extract_raster_data_to_point(points=plot_shapes, raster_path=raster_output_path,
    #                                       output_path=shp_output_path, output_shp_name='raster_extracts_20210527')


def reproject_rasters(epsg_out, ext, rasters, raster_path, output_path, basin_path, target_res):
    ext_name = ext.replace('.geojson', '')
    gdf = gpd.read_file(os.path.join(basin_path, ext)) 
    print('converting geojson from ', str(gdf.crs), ' to ', str(epsg_out))
    gdf = gdf.to_crs(epsg=epsg_out)
    gdf.to_file(os.path.join(basin_path, ext_name + "_projected.geojson"), driver='GeoJSON')
    subprocess.call('mkdir ' + os.path.join(output_path, ext_name), shell=True)
    for r in rasters:    
        print('reprojecting and clipping '+r+' to: '+ ext_name)
        dst_srs = 'EPSG:'+str(epsg_out)
        src_srs = 'EPSG:'+str(osr.SpatialReference(wkt=gdal.Open(os.path.join(raster_path, r)).GetProjection()).GetAttrValue('AUTHORITY',1))
        gdal.Warp(destNameOrDestDS=os.path.join(output_path, ext_name, r), srcDSOrSrcDSTab=os.path.join(raster_path, r),
                  options=gdal.WarpOptions(srcSRS=src_srs,  dstSRS=dst_srs, format='GTiff',
                                           cutlineDSName=os.path.join(basin_path, ext_name + "_projected.geojson"), cropToCutline=True,
                                           overviewLevel='NONE', resampleAlg=gdal.GRA_NearestNeighbour,
                                           xRes=target_res, yRes=target_res, dstNodata=-9999, creationOptions=['COMPRESS=LZW']))


def reproject_shapes(epsg_out, plot_csv, plot_path, output_path):
    plts = pd.read_csv(os.path.join(plot_path, plot_csv))
    plts = plts[['LON', 'LAT', 'PLT_KEY']].drop_duplicates()
    gdf = gpd.GeoDataFrame(plts, geometry=gpd.points_from_xy(plts.LON, plts.LAT))
    gdf = gdf.set_crs(epsg=4326)
    gdf = gdf.to_crs(epsg=epsg_out)
    gdf.to_file(os.path.join(output_path, "plots_projected.geojson"), driver='GeoJSON')
    # fig = plt.figure(figsize=(6, 6))
    # ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    # gdf.plot(ax=ax, column='PLT_KEY', edgecolor='none', markersize=5, alpha=0.75,
    #          legend=True, legend_kwds={'label': 'plots', 'orientation': "horizontal"}, zorder=2)
    # plt.savefig('figs/reprojected_plts.png')
    return gdf


def extract_raster_data_to_point(points, raster_path, output_path, output_shp_name):
    #coords = [(x, y) for x, y in zip(points.LAT, points.LON)]
    rasters = [i for i in os.listdir(raster_path) if i.endswith('.tif')]

    # Open the raster and store metadata
    for r in rasters:
        print(r)
        #src = rasterio.open(os.path.join(raster_path, r))
        name = re.sub('\.tif$', '', r)
        points[name] = rs.point_query(os.path.join(output_path, "plots_projected.geojson"),
                                      os.path.join(raster_path, r))

    points = points.replace(-9999, np.nan)
    points.to_file(os.path.join(output_path, output_shp_name+'_w_tif_vals.geojson'), driver='GeoJSON')
    # fig = plt.figure(figsize=(6, 6))
    # ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    # points.plot(ax=ax, column='Sbedrock', edgecolor='none', markersize=5, alpha=0.75,
    #          legend=True, legend_kwds={'label': 'plots', 'orientation': "horizontal"}, zorder=2)
    # plt.savefig('figs/reprojected_plts_extracted.png')

    return points


if __name__ == '__main__':
    main()
