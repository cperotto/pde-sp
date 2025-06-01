import geopandas as gpd
import pandas as pd
import h3pandas
from glob import glob

from matplotlib import pyplot as plt

filepath = "../../data/economicZones/raw/"
print(glob(filepath+"Z*/*.shp", recursive=True))
gdf = []

for _filepath in glob(filepath+"*/*.shp", recursive=True):
    gdf.append(gpd.read_file(_filepath).reset_index()[["index", "geometry"]])
    
gdf = gpd.GeoDataFrame(pd.concat(gdf)) #[:400]
gdf = gdf.set_crs(31983, allow_override=True)
gdf = gdf.to_crs(4326)

myPolygons = pd.read_csv(filepath+"perimetros_criativa.csv")
myPolygons = myPolygons.reset_index()
myPolygons["geometry"] = gpd.GeoSeries.from_wkt(myPolygons.WKT)
myPolygons = gpd.GeoDataFrame(myPolygons[["index", "geometry"]])
gdf = gpd.GeoDataFrame(pd.concat([myPolygons, gdf])) #[:400]

print(len(gdf))
ax = gdf.plot()
plt.savefig("zonas_economicas.png")

gdf['centroid'] = gdf.geometry.centroid
gdf = gdf.rename(columns={'geometry': 'blocks'})
gdf = gdf.rename(columns={'centroid': 'geometry'})
print(len(gdf))
gdf.drop(columns=['blocks']).to_file('../../data/economicZones/economicZones.geojson', driver='GeoJSON')
gdf = gdf.h3.geo_to_h3(9).reset_index()
print(len(gdf), 'final!')

gdf = gdf.drop_duplicates("h3_09")

gdf.drop(columns=['geometry']).to_file('../../data/economicZones/economicZones.geojson', driver='GeoJSON')