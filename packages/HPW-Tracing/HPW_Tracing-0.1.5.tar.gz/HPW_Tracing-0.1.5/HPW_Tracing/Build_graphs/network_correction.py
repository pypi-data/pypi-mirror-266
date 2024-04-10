from geopandas import GeoDataFrame
from shapely import Point, LineString
import geopandas as gpd
import pandas as pd
import os

#Main function
def correct_network(gm_shp_gdf: GeoDataFrame, fm_shp_gdf: GeoDataFrame, mh_shp_gdf: GeoDataFrame, cleanout_shp_gdf: GeoDataFrame, db) -> tuple:
    """
    Perform network correction on the GIS data to fix UFID issues and merge the manholes and cleanout.
    :param gm_shp_gdf: GeoDataFrame containing gravity mains.
    :param fm_shp_gdf: GeoDataFrame containing force mains.
    :param mh_shp_gdf: GeoDataFrame containing manholes.
    :param cleanout_shp_gdf: GeoDataFrame containing cleanouts.
    :return: Tuple containing the corrected
    gravity mains and force mains GeoDataFrames, and the merged manholes and cleanouts GeoDataFrame.
    """

    print(f'-------------------------------------------------------------------------')
    print(f'Performing network correction to provide corrected upstream and downstream manholes for each link.')
    # Load the data
    gm_fm_gdf, mh_clean_out_gdf = gis_data_processing(db,mh_shp_gdf, gm_shp_gdf, cleanout_shp_gdf, fm_shp_gdf)

    start_node_buffer = create_node_buffer(gm_fm_gdf, 'start', 1)
    end_node_buffer = create_node_buffer(gm_fm_gdf, 'end', 1)

    # Find the upstream and downstream manholes for each link
    upstream_mh = match_mh_to_link(mh_clean_out_gdf, start_node_buffer, 'upstream')
    downstream_mh = match_mh_to_link(mh_clean_out_gdf, end_node_buffer, 'downstream')

    # Merge the upstream and downstream manholes, so that each link will have both upstream and downstream manholes
    mh_links = pd.merge(downstream_mh, upstream_mh, on='UFID', how='outer')

    # append the upstream and downstream manhole columns to original gm_fm_gdf
    links_merged = pd.merge(gm_fm_gdf, mh_links, on='UFID', how='left')

    corrected_network_data = fix_missing_mh_names(links_merged)
    print(f'Network correction completed.')

    # save the corrected_network_data to the database as a pickle
    corrected_network_data.to_pickle(os.path.join(db, 'corrected_network_data.pkl'))
    print(f'corrected_network_data saved to {os.path.join(db, "corrected_network_data.pkl")}')

    return corrected_network_data



def gis_data_processing(db,mh_gdf : GeoDataFrame, gm_gdf: GeoDataFrame, cleanout_gdf: GeoDataFrame, fm_gdf: GeoDataFrame) -> tuple:
    """
    Process the GIS data to fix the UFID issue and merge the manholes and cleanout.
    :param mh_gdf:
    :param gm_gdf:
    :param cleanout_gdf:
    :param fm_gdf:
    :return:
    """
    gm_gdf = fix_based_gis_case(gm_gdf, mh_gdf)
    gm_gdf['type'] = 'GM'
    gm_gdf = gm_gdf[['UFID', 'geometry', 'type']]

    # convert UFID to string
    gm_gdf['UFID'] = gm_gdf['UFID'].astype(str)

    fm_gdf['type'] = 'FM'
    fm_gdf = fm_gdf[['UFID', 'geometry', 'type']]
    # convert UFID to string
    fm_gdf['UFID'] = fm_gdf['UFID'].astype(str)

    # merge the gravity mains and force mains
    gm_fm_gdf = pd.concat([gm_gdf, fm_gdf], axis=0, ignore_index=True)
    #add length column
    gm_fm_gdf['length'] = gm_fm_gdf['geometry'].length

    mh_gdf = mh_gdf[['UFID', 'geometry','MH_NUMBER']]
    # convert UFID to string
    mh_gdf['UFID'] = mh_gdf['UFID'].astype(str)

    cleanout_gdf = cleanout_gdf[['UFID', 'geometry','MH_NUMBER']]
    # convert UFID to string
    cleanout_gdf['UFID'] = cleanout_gdf['UFID'].astype(str)

    # merge the manholes and cleanout
    mh_clean_out_gdf = pd.concat([mh_gdf, cleanout_gdf], axis=0, ignore_index=True)

    # save the gdfs to pickle files in the report folder
    gm_fm_gdf.to_pickle(os.path.join(db, 'gm_fm_gdf.pkl'))
    mh_clean_out_gdf.to_pickle(os.path.join(db, 'mh_clean_out_gdf.pkl'))

    # mh_clean_out_df = mh_clean_out_gdf.drop(columns=['geometry'])
    # mh_clean_out_gdf = mh_clean_out_gdf.drop(columns=['MH_NUMBER'])

    return gm_fm_gdf, mh_clean_out_gdf

def create_node_buffer(gdf, node_type, buffer_distance) -> GeoDataFrame:
    """
    Create a GeoDataFrame for start or end node polygons.

    :param gdf: The original GeoDataFrame with line geometries.
    :param node_type: 'start' or 'end' to specify which node type to process.
    :param buffer_distance: The buffer distance for the node polygon.
    :return: A GeoDataFrame containing the node polygons and their UFIDs.
    """
    if node_type not in ['start', 'end']:
        raise ValueError("node_type must be 'start' or 'end'")

    # Select the first or last coordinate based on node_type
    coord_index = 0 if node_type == 'start' else -1
    node_column = f'{node_type}_node_polygon'

    # Create the node polygon column
    gdf[node_column] = gdf['geometry'].apply(lambda x: Point(x.coords[coord_index]).buffer(buffer_distance))

    # Create the node GeoDataFrame
    node_gdf = gdf[['UFID', node_column]].copy()
    node_gdf = gpd.GeoDataFrame(node_gdf, geometry=node_column)
    node_gdf.crs = gdf.crs

    return node_gdf


def find_links(gdf, node_gdf, link_type):
    """
    Perform a spatial join to find links between lines and node buffers.

    :param gdf: GeoDataFrame with line geometries.
    :param node_gdf: GeoDataFrame with node buffer geometries.
    :param link_type: 'downstream' or 'upstream' to specify the type of link.
    :return: GeoDataFrame with identified links.
    """
    # Perform spatial join to find intersections
    links = gpd.sjoin(gdf, node_gdf, how='left', predicate='intersects')

    # Rename columns based on link type
    if link_type == 'downstream':
        links = links.rename(columns={'UFID_left': 'UFID', 'UFID_right': 'ds_UFID'})
    elif link_type == 'upstream':
        links = links.rename(columns={'UFID_left': 'UFID', 'UFID_right': 'us_UFID'})
    else:
        raise ValueError("link_type must be 'downstream' or 'upstream'")

    # Remove duplicates if UFID and link UFID are the same
    link_ufid = 'ds_UFID' if link_type == 'downstream' else 'us_UFID'
    links = links[links['UFID'] != links[link_ufid]]

    # Drop the 'index_right' column as it is no longer needed
    links.drop(columns=['index_right'], inplace=True)

    return links

def match_mh_to_link(mh_gdf: GeoDataFrame, node_gdf: GeoDataFrame, link_type: str) -> GeoDataFrame:
    """
    Find which manholes intersect with specified node buffers.

    :param mh_gdf: GeoDataFrame containing manhole geometries.
    :param node_gdf: GeoDataFrame containing node buffer geometries.
    :param link_type: 'upstream' or 'downstream' to specify the type of manhole link.
    :return: GeoDataFrame with manhole links.
    """
    if link_type not in ['upstream', 'downstream']:
        raise ValueError("link_type must be 'upstream' or 'downstream'")


    # remove the mh_number column
    mh_gdf = mh_gdf.copy().drop(columns=['MH_NUMBER'])

    # Perform spatial join to find intersections
    links = gpd.sjoin(mh_gdf, node_gdf, how='inner', predicate='intersects')

    # Rename columns based on link type
    column_name = 'start_mh' if link_type == 'upstream' else 'end_mh'
    links = links.rename(columns={'UFID_left': column_name, 'UFID_right': 'UFID'})

    # Select and rename columns
    links = links[['UFID', column_name]]

    # Convert to string
    links[column_name] = links[column_name].astype(str)

    return links






def fix_based_gis_case(gravityMain: GeoDataFrame, manholes: GeoDataFrame) -> GeoDataFrame:
    """
    Fix the based on GIS case:

    """
    print('-------------------------------------------------------------------------')

    print("""
    fixing the based on GIS case by correcting the UNITID2 in gravityMain based
    on the correct manhole UFID.
      bad_gis_case = {
        '2361191': '7853045',
        '4153751': '4188067'
    }
    """)


    bad_gis_case = {
        '2361191': '7853045',
        '4153751': '4188067'
    }

    # find rows of UNITID OR UNITID2 in gravityMain that are in bad_gis_case
    bad_gis = gravityMain[
        gravityMain['UNIT_ID'].isin(bad_gis_case.keys()) | gravityMain['UNITID2'].isin(bad_gis_case.keys())]

    # find the manholes in the bad gis case,
    correct_mh = [value for value in bad_gis_case.values()]
    correct_mh_gis = manholes[manholes['UFID'].isin(correct_mh)]

    # get the correct UFID and coordinate from correct_mh_gis
    correct_mh_gis = correct_mh_gis[['UFID', 'geometry']]

    # corrected the UNITID2 in gravityMain

    # Assuming manholes' 'UFID' column is unique
    manholes_dict = manholes.set_index('UFID')['geometry'].to_dict()

    # Correcting UNITID2 in gravityMain
    for key, value in bad_gis_case.items():
        gravityMain.loc[gravityMain['UNITID2'] == key, 'UNITID2'] = value

    for key, value in bad_gis_case.items():
        bad_gis.loc[bad_gis['UNITID2'] == key, 'UNITID2'] = value

    # Function to create a LineString for a row in bad_gis

    def create_line(row):
        start_point = manholes_dict.get(row['UNIT_ID'])
        end_point = manholes_dict.get(row['UNITID2'])


        if start_point and end_point:
            start_point_coord = start_point.coords[0]
            end_point_coord = end_point.coords[0]
            return LineString([start_point_coord, end_point_coord])
        else:
            return None

    # Apply the function to create lines
    if len(bad_gis)==0:
        print("no row needs to be fixed.")
        return gravityMain
    else:
        print(f'fixing the geometry for {len(bad_gis)} rows in gravityMain that are in bad_gis_case')
        bad_gis['geometry'] = bad_gis.apply(create_line, axis=1)


    # Update the geometries back in gravityMain if needed
    for idx, row in bad_gis.iterrows():
        gravityMain.loc[idx, 'geometry'] = row['geometry']

    # remove the rows with null geometry
    gravityMain = gravityMain[gravityMain['geometry'].notnull()]

    #check again if still any rows in the bad_gis
    bad_gis = gravityMain[
        gravityMain['UNIT_ID'].isin(bad_gis_case.keys()) | gravityMain['UNITID2'].isin(bad_gis_case.keys())]

    if len(bad_gis)==0:
        print("All rows fixed.")


    """
    case 2: duplicated link UFID,
    In this case, we found two duplicated UFID in gravityMai for UFID '3287741'
    after looking at the GIS, we need to remove the row 124003
    """
    print('-------------------------------------------------------------------------')
    print('checking for duplicated UFID in gravityMain')
    # duplicated UFID in the gravityMain
    duplicated_UFID = gravityMain[gravityMain.duplicated(subset=['UFID'], keep=False)]

    # by looking at the gis, we need to remove the first row in the duplicates
    # search for row with UFID '3287741' where index is 124003
    if duplicated_UFID[duplicated_UFID['UFID'] == '3287741'].index[0] == 124003:
        gravityMain.drop(index=124003, inplace=True)

    print( "In this case, we found two duplicated UFID in gravityMai for UFID '3287741' after looking at the GIS, we need to remove the row 124003")


    return gravityMain

def fix_missing_mh_names(links_merged: GeoDataFrame):
    # create a list of start node and end node polygons
    # Combine 'start_node_polygon' and 'end_node_polygon' and then find unique values
    # note this process can be slow due to the large number of polygons and hash table lookups clusterings
    print('-------------------------------------------------------------------------')
    print('fixing the missing manhole names in the links')
    print('Those manholes will be named as temp_0, temp_1, temp_2, ... etc.')

    start_node_list = links_merged['start_node_polygon'].tolist()
    end_node_list = links_merged['end_node_polygon'].tolist()
    unique_polygons = list(set(start_node_list + end_node_list))

    # save the unique polygons to a shapefile
    unique_polygons_gdf = gpd.GeoDataFrame(geometry=unique_polygons)
    unique_polygons_gdf.crs = links_merged.crs

    # create a dictionary of unique polygons given a name starting with 'tmp_' plus a number
    poly_dict = {poly: f'temp_{i}' for i, poly in enumerate(unique_polygons)}

    # in the links dataframe, if there is nan start_mh, replace with nan with poly_dict with the start_node_polygon
    links_merged['start_mh'] = links_merged['start_mh'].fillna(links_merged['start_node_polygon'].map(poly_dict))
    # in the links dataframe, if there is nan end_mh, replace with nan with poly_dict with the end_node_polygon
    links_merged['end_mh'] = links_merged['end_mh'].fillna(links_merged['end_node_polygon'].map(poly_dict))

    # remove duplicates
    links_merged.drop_duplicates(subset=['UFID', 'start_mh', 'end_mh'], inplace=True)

    # drop empty geometries
    links_merged = links_merged[links_merged['geometry'].notnull()]

    # drop polygons for the links_merged
    links_merged.drop(columns=['start_node_polygon', 'end_node_polygon'], inplace=True)

    print('All missing manhole names have been fixed.')
    # save the links_merged

    return links_merged