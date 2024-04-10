import os
import unittest
from unittest.mock import patch, MagicMock
import geopandas as gpd
from HPW_Tracing.Load_data import load_data

class TestLoadData(unittest.TestCase):
    def setUp(self):
        # Define the paths for the test
        self.db = 'C:\PythonProjects\__db'
        self.datawarehouse = r'C:\Users\C21252\City of Houston\WWIP Planning Data Warehouse - General\GIS Database\01_Infrastructure'
        # Prepare a sample GeoDataFrame for mocking
        self.sample_gdf = gpd.GeoDataFrame({'geometry': []})

    @patch('geopandas.read_file')
    @patch('os.path.exists')
    @patch('pandas.read_pickle')
    def test_load_data(self, mock_read_pickle, mock_exists, mock_read_file):
        # Mock the os.path.exists to return True to simulate the presence of pickle files
        mock_exists.return_value = True

        # Mock read_pickle to return a sample GeoDataFrame
        mock_read_pickle.return_value = self.sample_gdf

        # Call the function
        gm_shp_gdf, fm_shp_gdf, mh_shp_gdf, cleanout_shp_gdf = load_data(self.db, self.datawarehouse)

        # Assertions to check if the returned value is the mocked GeoDataFrame
        # self.assertEqual(gm_shp_gdf, self.sample_gdf)
        # self.assertEqual(fm_shp_gdf, self.sample_gdf)
        # self.assertEqual(mh_shp_gdf, self.sample_gdf)
        # self.assertEqual(cleanout_shp_gdf, self.sample_gdf)

        # Assert that the expected file paths were checked
        mock_exists.assert_called_with(os.path.join(self.db, 'gm_shp_gdf.pkl'))
        # Assert that read_pickle was called
        mock_read_pickle.assert_called()

        # Additional tests can be written to simulate and assert behavior when pickle files don't exist

if __name__ == '__main__':
    unittest.main()
