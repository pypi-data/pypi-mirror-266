"""
Misc useful functions
"""

import re
from geodeticengine import request_wkt_for_crs

def find_indices_of_attribute(ogc_wkt_str, attribute_name):
    """
    Function that loops through the input string and finds the
    start index and end index of a defined attribute in the WKT-string. Ex: "GEOGCS"
    The function keeps track of the nested brackets to ensure that it finds
    the correct "]]" that closes the defined attribute. This function finds all indices for every occurency of attribute_name

    Parameters
    ----------
    trans_ogc_wkt_str : The transformation WKT-string in the OGC dialect
    attribute_name : The attribute to find the indexes for (ex:"GEOGCS")

    Returns
    -------
    indices = A list of tuples containing start and stop index for every occurency of attribute name
    """
    indices = []
    start_index = ogc_wkt_str.find(f"{attribute_name}[")
    while start_index != -1:
        stack = [] # list for keeping track of the nested brackets
        for i, char in enumerate(ogc_wkt_str[start_index:]):
            if char == "[":
                stack.append(char)
            elif char == "]":
                stack.pop()
                if not stack:
                    end_index = start_index + i + 1
                    indices.append((start_index, end_index))
                    break
        start_index = ogc_wkt_str.find(f"{attribute_name}[", end_index)
    return indices



def extract_target_crscode_from_transWKT(trans_WKT_ogc) -> list:
    """
    Function that extracts EPSG code from the two CRSs that are
    included in the transformation string. Returns a tuple. (ex:('4202', '4326'))
    """
    if not "ENGCRS" in trans_WKT_ogc:
        indices = find_indices_of_attribute(trans_WKT_ogc, 'GEOGCS')
        epsg_codes = []
        for i in range(len(indices)):
            geo_str = trans_WKT_ogc[indices[i][0]:indices[i][1]]
            idx = geo_str.rindex('AUTHORITY[')
            epsg_codes.append(re.findall('[0-9]+', geo_str[idx:-1])[0])
        source_crs, target_crs = epsg_codes
        # return  source_crs, target_crs
        return [source_crs], [target_crs]
    else:
        return extract_target_crs_from_engineering_transWKT(trans_WKT_ogc)



def extract_geogcrs_codes_from_crs_wkt(ogc_wkt):
    """Function that extracts CRS code for the GEOGCS in WKT_GDAL."""
    epsg_codes = []
    for attribute in ['GEOGCS', 'PROJCS', 'LOCAL_CS']:
        indices = find_indices_of_attribute(ogc_wkt, attribute)
        for start, end in indices:
            geo_str = ogc_wkt[start:end]
            idx = geo_str.rindex('AUTHORITY[')
            epsg_code = re.findall('[0-9]+', geo_str[idx:-1])[0]
            epsg_codes.append(epsg_code)
    return epsg_codes


def extract_target_crs_from_engineering_transWKT(trans_WKT_ogc) -> list:
    """
    For engineering CRS only.
    Function that extracts authority code from the two CRSs that are
    included in the transformation string. Returns a tuple. (ex: ('4202', '4326'))
    """
    epsg_codes = []
    for attribute in ['ENGCRS', 'PROJCS']:
        indices = find_indices_of_attribute(trans_WKT_ogc, attribute)
        for start, end in indices:
            geo_str = trans_WKT_ogc[start:end]
            idx = geo_str.rindex('AUTHORITY[')
            epsg_code = re.findall('[0-9]+', geo_str[idx:-1])[0]
            epsg_codes.append(epsg_code)
    source_crs, target_crs = epsg_codes
    geogcs_ind = find_indices_of_attribute(trans_WKT_ogc, 'GEOGCS')
    geo_str = trans_WKT_ogc[geogcs_ind[0][0]:geogcs_ind[0][1]]
    idx = geo_str.rindex('AUTHORITY[')
    geogcs_code = re.findall('[0-9]+', geo_str[idx:-1])[0]
    return [source_crs], [target_crs, geogcs_code]


def get_wkt_gdal_for_crs(crs_authcode) -> str:
    return request_wkt_for_crs(crs_authcode, "WKT1_GDAL")['crs_wkt']


def get_wkt_gdal_for_ct(ct_authcode) -> str:
    # return request_wkt_for_crs(ct_authcode, "WKT1_GDAL")['transformation_wkt']
    return request_wkt_for_crs(ct_authcode, "WKT2_2019")['transformation_wkt']

def determine_trans_dir(crs_authcode, ct_authcode):
    is_inverse = False
    crs_wkt = get_wkt_gdal_for_crs(crs_authcode)
    ct_wkt = get_wkt_gdal_for_ct(ct_authcode)
    crs_base = extract_geogcrs_codes_from_crs_wkt(crs_wkt)
    source_crs, target_crs = extract_target_crscode_from_transWKT(ct_wkt)
    if set(crs_base).intersection(source_crs) and not set(crs_base).intersection(target_crs):
        is_inverse = False
    elif set(crs_base).intersection(target_crs) and not set(crs_base).intersection(source_crs):
        is_inverse = True
    else:
        raise ValueError("The base CRS of the CRS does not match neither the source or target CRS of the transformation.")
    return is_inverse



if __name__ == "__main__":
    is_inverse = determine_trans_dir("ESPG:4230", "EPSG:1612")
    print(is_inverse)