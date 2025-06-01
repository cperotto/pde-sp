import geopandas as gpd
import pandas as pd
import h3pandas

filepath = "../../data/eetu/raw/"
first = gpd.read_file(filepath+'sirgas_PDE_3-Eixos-EETU.shp')
late = gpd.read_file(filepath+'SIRGAS_SHP_eixoativodecreto_polygon.shp')

first['year'] = 2014
late['year'] = late.ed_decreto.apply(lambda string: int(string.split('/')[-1]))
eetu = pd.concat([first[['geometry', 'year']], late[['geometry', 'year']]])
eetu = gpd.GeoDataFrame(eetu)
eetu = eetu.set_crs(31983, allow_override=True)
eetu = eetu.to_crs(4326)
eetu['centroid'] = eetu.geometry.centroid
eetu = eetu.rename(columns={'geometry': 'blocks'})
eetu = eetu.rename(columns={'centroid': 'geometry'})
eetu = eetu.h3.geo_to_h3(9).reset_index()

eetu = eetu.drop_duplicates("h3_09")

eetu.drop(columns=['geometry']).to_file('../../data/eetu/activeEETU.geojson', driver='GeoJSON')