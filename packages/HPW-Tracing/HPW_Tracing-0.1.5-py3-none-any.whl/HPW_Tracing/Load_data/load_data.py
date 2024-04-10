
import warnings
warnings.filterwarnings("ignore")
import os
import pandas as pd
import geopandas as gpd
import pickle

def load_data(db, datawarehouse, update=False):
    mh_shp = os.path.join(datawarehouse, 'Sewer_Network', 'Manholes.shp')
    cleanout_shp = os.path.join(datawarehouse, 'Sewer_Network', 'CleanOut.shp')
    fm_shp = os.path.join(datawarehouse, 'Force_Mains', 'Force_Mains.shp')
    gm_shp = os.path.join(datawarehouse, 'Sewer_Network', 'Gravity_Mains.shp')

    result_folder = db

    # remove the pickle files if update is True
    if update:
        print('Removing the pre-existing pickle files')
        for file in os.listdir(result_folder):
            if file.endswith('.pkl'):
                os.remove(os.path.join(result_folder, file))


    # if GeoDataFrame (gdf) already exists, load them from the pickle files
    if os.path.exists(os.path.join(result_folder, 'gm_shp_gdf.pkl')):
        print('Loading the GeoDataFrames from the pickle files...')
        gm_shp_gdf = pd.read_pickle(os.path.join(result_folder, 'gm_shp_gdf.pkl'))
        fm_shp_gdf = pd.read_pickle(os.path.join(result_folder, 'fm_shp_gdf.pkl'))
        mh_shp_gdf = pd.read_pickle(os.path.join(result_folder, 'mh_shp_gdf.pkl'))
        cleanout_shp_gdf = pd.read_pickle(os.path.join(result_folder, 'cleanout_shp_gdf.pkl'))
    else:
        print('Loading the GeoDataFrames from the shapefiles...')
        gm_shp_gdf = gpd.read_file(gm_shp)
        fm_shp_gdf = gpd.read_file(fm_shp)
        mh_shp_gdf = gpd.read_file(mh_shp)
        cleanout_shp_gdf = gpd.read_file(cleanout_shp)

        # convert UFID column to string
        mh_shp_gdf['UFID'] = mh_shp_gdf['UFID'].astype(str)
        cleanout_shp_gdf['UFID'] = cleanout_shp_gdf['UFID'].astype(str)
        gm_shp_gdf['UFID'] = gm_shp_gdf['UFID'].astype(str)
        fm_shp_gdf['UFID'] = fm_shp_gdf['UFID'].astype(str)

        # save the gdfs to pickle files in the report folder
        print('Saving the GeoDataFrames to pickle files...')
        gm_shp_gdf.to_pickle(os.path.join(result_folder, 'gm_shp_gdf.pkl'))
        fm_shp_gdf.to_pickle(os.path.join(result_folder, 'fm_shp_gdf.pkl'))
        mh_shp_gdf.to_pickle(os.path.join(result_folder, 'mh_shp_gdf.pkl'))
        cleanout_shp_gdf.to_pickle(os.path.join(result_folder, 'cleanout_shp_gdf.pkl'))

    print('GeoDataFrames loaded successfully.')
    return gm_shp_gdf, fm_shp_gdf, mh_shp_gdf, cleanout_shp_gdf

