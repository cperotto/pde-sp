from ___aux.___travelTimes import computeCommutings, buildNetwork, removeNetworkCache

import pandas as pd
import h3pandas

# DONE (2013, 2022)

aop = pd.read_csv("/Users/camillaperotto/Downloads/aop_landuse_2017_v2.csv").rename(columns={'id_hex': 'h3_09'})
aop = aop.loc[aop.name_muni=='Sao Paulo']
print(len(aop), aop.h3_09.nunique())
aop = aop.set_index('h3_09').h3.h3_to_geo_boundary().reset_index().rename(columns={'h3_09': 'id'})
aop['_centroid'] = aop.centroid
aop = aop.drop(columns=['geometry']).rename(columns={'_centroid': 'geometry'})


#YEAR_TO_COMPUTE = [2013, 2022]
YEAR_TO_COMPUTE = [2022]

CHUNCKSIZE = 1250

for year in YEAR_TO_COMPUTE:

    removeNetworkCache()

    print('should build network!')
    network = buildNetwork(year)
    print('built network!')

    length = len(aop)

    i = 0

    while True:

        if i*CHUNCKSIZE>length: break

        Matrix = computeCommutings(network, aop, aop.iloc[i*CHUNCKSIZE:(i+1)*CHUNCKSIZE], year)

        #Matrix = Matrix.loc[Matrix.travel_time>=0]
        Matrix = Matrix.loc[(~Matrix.travel_time.isna()) & (Matrix.travel_time>0)]
        print('should save now!', len(Matrix), year, i)
        Matrix.to_parquet(f"../data/test_travelTimes/tt___{year}_{i}.parquet", index=True)
        
        print(f'done {year}, chunk {i} completed')
        print()
        print()

        i += 1

    removeNetworkCache()