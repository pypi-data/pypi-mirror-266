from geodeticengine import CoordTrans, CrsSearch, CtSearch

### Example 1
print("Engineering")
points = [[8911.832,5139.165]]
crs_from = "EQUINOR:4100002"
ct_from = "EQUINOR:3100002"
crs_to = "EPSG:25832"
ct = CoordTrans(crs_from=crs_from, crs_to=crs_to, ct_from=ct_from, points=points)
print(f"from:{ct.transform_pointlist()}")
points_to=[[283341.96397220856,6748519.897517173]]
ct = CoordTrans(crs_from=crs_to, crs_to=crs_from, ct_to=ct_from, points=points_to)
print(f"from:{ct.transform_pointlist()}")




### Example 2
points = [[10, 60]]
crs_from = "EPSG:4230"
crs_to = "EPSG:4326"
ct_from = "EPSG:1612"

# Transform coordinates
ct = CoordTrans(crs_from=crs_from, crs_to=crs_to, ct_from=ct_from, points=points)
print(f"Transformed coordinates:{ct.transform_pointlist()}")

# Get transformation pipeline
pipeline = ct.get_pipeline()
print(f"Transformation pipeline: {pipeline}")

### Example 3
points = [[9,65],[12,70]]
crs_from = "ST_ED50_T1133"
crs_to = "ST_WGS84_G4326"

# Transform coordinates
ct = CoordTrans(crs_from=crs_from, crs_to=crs_to, points=points)
print(f"Transformed coordinates:{ct.transform_pointlist()}")

# Get transformation pipeline
pipeline =  ct.get_pipeline()
print(f"Transformation pipeline: {pipeline}")

#crs_query = CrsSearch(types=["bound projected","projected"], polygon_coords=[[1.278828871805691,58.07568845044884],[3.690287338364835,59.20344381800123],[2.274239008972083,60.12176489296384],[-0.1274790229401068, 59.8722761692493]], target_crs="ST_WGS84_G4326")
#print(crs_query.get_entities())

#ct_query = CtSearch(types=["transformation","concatenated operation"], polygon_coords=[[1.278828871805691,58.07568845044884],[3.690287338364835,59.20344381800123],[2.274239008972083,60.12176489296384],[-0.1274790229401068,59.8722761692493]], source_crs="ST_ED50_G4230", target_crs="ST_WGS84_G4326")
#print(ct_query.get_entities())