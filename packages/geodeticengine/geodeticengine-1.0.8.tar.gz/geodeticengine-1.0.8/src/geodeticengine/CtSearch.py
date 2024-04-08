from geodeticengine.ege_api import EGE

EGE = EGE()

class CtSearch():
    """
    Class to query Equinor named CRSs based on polygon filter, crs types, target crs and usage scopes.
    The polygon filter must be defined with a list of WGS84 longitude, latitude coordinates.

    """
    def __init__(self,types:list[str], polygon_coords:list[float], source_crs:str, target_crs:str):
        """
        Examples:
        >>> ct_query = CtSearch(types=["transformation","concatenated operation"], polygon_coords=[[1.278828871805691,58.07568845044884],[3.690287338364835,59.20344381800123],[2.274239008972083,60.12176489296384],[-0.1274790229401068,59.8722761692493]], source_crs="ST_ED50_G4230", target_crs="ST_WGS84_G4326")
        """
        self.types = types
        self.polygon_coords = polygon_coords
        self.source_crs = source_crs
        self.target_crs = target_crs

    def get_entities(self):
        return EGE.ct_search(self.types, self.polygon_coords, self.source_crs, self.target_crs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()