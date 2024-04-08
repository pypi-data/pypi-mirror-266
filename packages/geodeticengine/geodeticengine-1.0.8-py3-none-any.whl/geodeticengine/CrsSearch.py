from geodeticengine.ege_api import EGE

EGE = EGE()

class CrsSearch():
    """
    Class to query Equinor named CRSs based on polygon filter, crs types, target crs and usage scopes.
    The polygon filter must be defined with a list of WGS84 longitude, latitude coordinates.

    """
    def __init__(self,types:list[str], polygon_coords:list[float], target_crs:str):
        """
        Examples:
        >>> crs_search = CrsSearch(types=["bound projected","projected"], polygon_coords=[[1.278828871805691,58.07568845044884],[3.690287338364835,59.20344381800123],[2.274239008972083,60.12176489296384],[-0.1274790229401068, 59.8722761692493]], target_crs="ST_WGS84_G4326")
        """
        self.types = types
        self.polygon_coords = polygon_coords
        self.target_crs = target_crs

    def get_entities(self):
        return EGE.crs_search(self.types, self.polygon_coords, self.target_crs)

if __name__ == "__main__":
    import doctest
    doctest.testmod()