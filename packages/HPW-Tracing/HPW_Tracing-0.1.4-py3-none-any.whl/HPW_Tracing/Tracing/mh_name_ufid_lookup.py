import os
import pickle
import pandas as pd

def create_mhNum_UFID_dict(db) -> pd.DataFrame:
    """
    Create a dictionary that maps MH_NUMBER to UFID
    :param db:
    :return:
    """
    # Read in the data
    # man_df = pd.read_parquet(os.path.join(db_folder, 'Manholes.parquet'))
    try:
        with open(os.path.join(db, 'mh_clean_out_gdf.pkl'), 'rb') as handle:
            mh_df = pickle.load(handle)
    except:
        print('Manhole data not found in the database folder. True Force update to create the data.')
        return

    mh_df.drop(columns=['geometry'], inplace=True)
    columns = ['MH_NUMBER', 'UFID']
    UFID_NAME_DICT = mh_df[columns]

    # fillna in the 'MH_NUMBER' column with 'UFID' values
    UFID_NAME_DICT['MH_NUMBER'] = UFID_NAME_DICT['MH_NUMBER'].fillna(UFID_NAME_DICT['UFID'])

    # Drop any rows with missing values
    mhNAME_UFID_dict = UFID_NAME_DICT.dropna()
    # convert all columns to string
    mhNAME_UFID_dict = mhNAME_UFID_dict.astype(str)
    return mhNAME_UFID_dict