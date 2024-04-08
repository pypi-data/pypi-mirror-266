"""
Module for running automated tests on the pytyhon package using a test data set with expected values transformed using Blue Marbel's Geographic Calculator.
The test data set is downloaded from Azure Blob Store
"""

import os
import sys
import pytest
import ast
import pandas as pd
import numpy as np
from pygeodesy.ellipsoidalVincenty import LatLon
from pyproj import CRS
from azure.storage.blob import BlobServiceClient
import io
from os import environ as env
from dotenv import load_dotenv
load_dotenv(override=True)

path_to_api = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../api'))
path_to_pypack = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(path_to_api)
sys.path.append(path_to_pypack)

from geodeticengine import CoordTrans

CONTAINER_NAME = 'test-data'
AZ_CONNECTION_STRING = env["AZ_CONNECTION_STRING"]
blob_name = 'test_data_ege.csv'

# Download the test data set from Azure Blob store
CONTAINER_NAME = 'test-data'
blob_name = 'test_data_ege.csv'
blob_service = BlobServiceClient.from_connection_string(AZ_CONNECTION_STRING)
blob = blob_service.get_blob_client(CONTAINER_NAME, blob_name)
downloaded_data = blob.download_blob().readall().decode('utf-8')
# Create a DataFrame
DF_ALL = pd.read_csv(io.StringIO(downloaded_data), delimiter=';')


### - Run through the test dataset and compaire agains Geographic Calculator
def get_dist_on_ellipsoid_between_points(transformed_coords: np.ndarray, reference_points: np.ndarray) -> float:
    """
    Find the distance on the ellipsoid between two points defined
    by geographic coordinates.
    """
    lon = transformed_coords[:,0]; lat = transformed_coords[:,1]
    lon_ref = reference_points[:,0]; lat_ref = reference_points[:,1]
    diff_lst = []
    for p in range(len(transformed_coords)):
        if (lat[p] == 0 and lon[p]== 0 and lat_ref[p] == 0 and lon_ref[p] == 0) \
            or ((abs(lat[p])==90 or abs(lon[p])==180) and (abs(lat_ref[p])==90 or abs(lon_ref[p])==180)): # check if they are all zero (to prevent pygeodesy.ellipsoidalVincenty.VincentyError: ambiguous: LatLon(00°00′00.0″N, 000°00′00.0″E) antipodal to  LatLon(00°00′00.0″N, 000°00′00.0″E)
            diff_lst.append(0)
            continue
        point_transformed = LatLon(lat[p], lon[p])
        point_reference = LatLon(lat_ref[p], lon_ref[p])
        diff_lst.append(point_transformed.distanceTo(point_reference))
    return np.array(diff_lst)


# # Build up the payload
df = DF_ALL[DF_ALL["CRS_Type"] != "engineering"]
PAYLOAD_XY = []
for idx, row in df.iterrows():
    # Extract the data from the current row
    coords_to_transform = ast.literal_eval(row['Expected_Results'])
    crs_from = "EPSG:4326"
    crs_to = row['CRS_Code']
    ct_authcode = row['Transformation_Code']
    crs_type = row['CRS_Type']
    expected_coords = ast.literal_eval(row['Points_To_Transform'])
    error_threshold = row['Error_Threshold']
    # Build up the payload tuple
    payload = ({"coordinates_from": [coords_to_transform], "crs_from": crs_from, "crs_to": crs_to,
                 "ct_authcode": ct_authcode, "crs_type":crs_type, "error_threshold": error_threshold }, expected_coords)
    PAYLOAD_XY.append(payload)

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("payload, expected_coords ", PAYLOAD_XY)
def test_coordinate_transform(payload, expected_coords):
    param_dict = payload
    crs_from = param_dict["crs_from"]
    crs_to = param_dict["crs_to"]
    ct_authcode = param_dict["ct_authcode"]
    crs_type = param_dict["crs_type"]
    error_threshold = param_dict["error_threshold"]
    if not isinstance(ct_authcode,str) and np.isnan(ct_authcode):
        ct_authcode = None
    lst_of_point = param_dict["coordinates_from"][0]
    # Transform first step (Projceted CRS -> WGS84)
    ct_geog = CoordTrans(crs_from=crs_to, crs_to=crs_from, ct_from=ct_authcode, points=lst_of_point)
    transformed_coords_geog = ct_geog.transform_pointlist()
    if CRS.from_user_input(crs_from).is_geographic:
        diff = get_dist_on_ellipsoid_between_points(np.array(transformed_coords_geog), np.array(expected_coords))
    else:
        diff = np.abs(np.array(transformed_coords_geog) - np.array(expected_coords))
    assert (diff < error_threshold).all() == True, f"Test case failed for CRS: {crs_to}, transformation:{ct_authcode}, max difference: {np.round(np.max(diff),3)}, threshold: {error_threshold}"
    # Transform second step (WGS84 -> Projceted CRS)
    ct = CoordTrans(crs_from=crs_from, crs_to=crs_to, ct_to=ct_authcode, points=transformed_coords_geog)
    transformed_coords = np.array(ct.transform_pointlist())
    # Compare agaist the input coordinates
    if 'geographic' in crs_type:
        diff = get_dist_on_ellipsoid_between_points(transformed_coords, np.array(lst_of_point))
    else:
        diff = np.abs(transformed_coords - np.array(lst_of_point))
    # Check if difference is greater than threshold value
    assert (diff < error_threshold).all() == True, f"Test case failed for CRS: {crs_to}, transformation:{ct_authcode}, max difference: {np.round(np.max(diff),3)}, threshold: {error_threshold}"




## Test engineering
df_engineering = DF_ALL[DF_ALL["CRS_Type"]=="engineering"]
PAYLOAD_ENGINEERING = []
for idx, row in df_engineering.iterrows():
    # Extract the data from the current row
    coords_to_transform = ast.literal_eval(row['Points_To_Transform'])
    crs_from = row['CRS_Code']
    crs_to = row['ENG_CRS_To']
    ct_authcode = row['Transformation_Code']
    expected_coords = ast.literal_eval(row['Expected_Results'])
    error_threshold = row['Error_Threshold']
    # Build up the payload tuple
    payload = ({"points_to_transform": [coords_to_transform], "crs_from": crs_from, "crs_to": crs_to,
                 "ct_authcode": ct_authcode, "error_threshold": error_threshold }, expected_coords)
    PAYLOAD_ENGINEERING.append(payload)

@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("payload_engineering, expected_coords ", PAYLOAD_ENGINEERING)
def test_engineering_transform(payload_engineering, expected_coords):
    param_dict = payload_engineering
    crs_from = param_dict["crs_from"]
    crs_to = param_dict["crs_to"]
    ct_authcode = param_dict["ct_authcode"]
    error_threshold = param_dict["error_threshold"]
    points_to_transform = param_dict["points_to_transform"][0]
    # Transform first step (Engineering CRS -> Global CRS like WGS84)
    ct_eng2glob = CoordTrans(crs_from=crs_from, crs_to=crs_to, ct_from=ct_authcode, points=points_to_transform)
    transformed_coords_glob = ct_eng2glob.transform_pointlist()
    if CRS.from_user_input(crs_to).is_geographic:
        diff = get_dist_on_ellipsoid_between_points(np.array(transformed_coords_glob), np.array(expected_coords))
    else:
        diff = np.abs(np.array(transformed_coords_glob) - np.array(expected_coords))
    assert (diff < error_threshold).all() == True, f"Test case failed for CRS: {crs_to}, transformation:{ct_authcode}, max difference: {np.round(np.max(diff),3)}, threshold: {error_threshold}"
    # Transform second step (Global CRS like WGS84 -> Engineering CRS)
    ct_glob2eng = CoordTrans(crs_from=crs_to, crs_to=crs_from, ct_to=ct_authcode, points=transformed_coords_glob)
    transformed_coords = np.array(ct_glob2eng.transform_pointlist())
    # Compare agaist the input coordinates
    diff = np.abs(transformed_coords - np.array(points_to_transform))
    # Check if difference is greater than threshold value
    assert (diff < error_threshold).all() == True, f"Test case failed for CRS: {crs_to}, transformation:{ct_authcode}, max difference: {np.round(np.max(diff),3)}, threshold: {error_threshold}"

