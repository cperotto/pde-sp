import geopandas as gpd
import pandas as pd
import h3pandas

from tobler.area_weighted import area_interpolate

sp = gpd.read_file("/Users/camillaperotto/Documents/pde-sp/01_AccessPipeline/data/sp.geojson")
poligono_sp = sp.iloc[0].geometry

for year in ["2010", "2022"]:

    grade = gpd.read_file(f"../data/grade_estatistica/{year}.gpkg")
    grade = grade[grade.intersects(poligono_sp)]
    print(grade.columns)
    if "POP" in grade.columns: grade = grade.rename(columns={"POP": 'TOTAL'})
    #if "POP" in grade.columns: grade = grade.rename(columns={"DOM_OCU": 'TOTAL'})
    print(grade.columns, grade.TOTAL.sum())
    grade = grade.loc[grade.TOTAL>0]
    print(grade.head(3))
    print(grade.crs)


    aop = pd.read_csv("/Users/camillaperotto/Downloads/aop_landuse_2017_v2.csv").rename(columns={'id_hex': 'h3_09'})
    aop = aop.loc[aop.name_muni=='Sao Paulo']
    print(len(aop), aop.h3_09.nunique())
    print(aop.head(5))
    aop = aop.set_index('h3_09').h3.h3_to_geo_boundary().reset_index() #.rename(columns={'h3_09': 'id'})
    aop = gpd.GeoDataFrame(aop)


    if grade.crs != aop.crs:
        aop = aop.to_crs(grade.crs)

    # Realiza interpolação areal da variável 'domicilios' de grade para aop
    aop_interpolado = area_interpolate(
        source_df=grade,
        target_df=aop,
        extensive_variables=["TOTAL"],  # variável a ser interpolada
        allocate_total=True
    )

    aop['N_HOUSING'] = aop_interpolado['TOTAL'].values
    aop['N_HOUSING'] = aop['N_HOUSING'].round(decimals=0)
    aop = aop.loc[aop.N_HOUSING>0]
    print(aop.N_HOUSING.sum())
    if year == '2010': year = "2013"
    aop[["h3_09", "N_HOUSING"]].to_csv(f"../data/address/origins__{year}.csv", sep=';', index=False)
