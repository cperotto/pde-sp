import pandas as pd
import geopandas as gpd
from glob import glob
import numpy as np

#from _06_access___scenarios import calcActiveAccess

TIME_THROSHOLD = 60

import os
import json 
with open('../scenarios.json') as json_data:
    scenarios = json.load(json_data)

eetu = gpd.read_file("../data/eetu/activeEETU.geojson")
eetu_hexs = eetu.h3_09.unique()

economicZones = gpd.read_file("../data/economicZones/economicZones.geojson")
economicZones_hexs = economicZones.h3_09.unique()

def calcActiveAccess(tt, _origins, currentDestinations, TIME_THROSHOLD):
        
        tt = tt.loc[tt.travel_time<=TIME_THROSHOLD]
        grouped = tt.groupby('from_id').agg({'to_id': 'unique'}).reset_index() #[:1000]

        T001 = []
        
        for i, row in grouped.iterrows():
            _destinations = currentDestinations.loc[currentDestinations.h3_09.isin(row.to_id)]
            T001.append(_destinations["T001"].sum())
        
        grouped["T001"] = T001
        
        grouped = grouped.rename(columns={'from_id': 'h3_09'}).drop(columns=["to_id"])
        grouped = grouped.merge(_origins, on='h3_09', how="left")
        grouped["N_HOUSING"] = grouped["N_HOUSING"].replace(np.nan, 1)
        grouped["N_HOUSING"] = grouped["N_HOUSING"].replace(np.inf, 1)
        grouped["T001"] = grouped["T001"].replace(np.nan, 1)
        #grouped["elast_T001"] = grouped["elast_T001"].replace(np.nan, 1)
        #print(len(grouped), 'after merging origins!')
        grouped["pond_T001"] = grouped["T001"]*grouped["N_HOUSING"]

        #print(grouped.pond_T001.sum())
        #print('try::', grouped.N_HOUSING.sum(), grouped.pond_T001.sum()/grouped.N_HOUSING.sum())

        noZeroes = grouped[grouped.N_HOUSING>0]
        
        ACTIVE_IDX = noZeroes.T001.mean()
        WEIGHTED_ACTIVE_IDX = noZeroes.pond_T001.sum()/noZeroes.N_HOUSING.sum()
        grouped_economicZones = noZeroes.loc[noZeroes.h3_09.isin(economicZones_hexs)]
        ACTIVE_IDX___ECONOMICZONES = grouped_economicZones.T001.mean()
        WEIGHTED_ACTIVE_IDX___ECONOMICZONES = grouped_economicZones.pond_T001.sum()/grouped_economicZones.N_HOUSING.sum()
        grouped_eetu = noZeroes.loc[noZeroes.h3_09.isin(eetu_hexs)]
        ACTIVE_IDX___EETU = grouped_eetu.T001.mean()
        WEIGHTED_ACTIVE_IDX___EETU = grouped_eetu.pond_T001.sum()/grouped_eetu.N_HOUSING.sum()
        
        return grouped, ACTIVE_IDX, ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU, ACTIVE_IDX___ECONOMICZONES, WEIGHTED_ACTIVE_IDX___ECONOMICZONES


for scenario in scenarios:

    title = scenario['_id']
    if '__solo' in title: continue

    mainMetrics = {}

    origins = pd.read_csv(f"../data/address/origins__{scenario['origins']}.csv", sep=';')
    origins = origins.groupby('h3_09').agg({'N_HOUSING': 'sum'}).reset_index()

    origins['is_eetu'] = 1
    origins['is_economicZone'] = 1

    origins.loc[origins.h3_09.isin(eetu_hexs), 'is_eetu'] = 1.01
    origins.loc[origins.h3_09.isin(economicZones_hexs), 'is_economicZone'] = 1.01

    origins.loc[origins.h3_09.isin(eetu_hexs), 'is_eetu'] = 1.01
    origins.loc[origins.h3_09.isin(economicZones_hexs), 'is_economicZone'] = 1.01

    origins["N_HOUSING___elast_eetu"] = origins['is_eetu']*origins.N_HOUSING
    origins["N_HOUSING___elast_economicZone"] = origins['is_economicZone']*origins.N_HOUSING

    destinations = pd.read_csv(
        f"../data/address/destinations__{scenario['destinations']}.csv", sep=';', 
        usecols=['T001', 'id_hex']).rename(columns={'id_hex': 'h3_09'})
    
    destinations['is_eetu'] = 1
    destinations['is_economicZone'] = 1

    destinations.loc[destinations.h3_09.isin(eetu_hexs), 'is_eetu'] = 1.01
    destinations.loc[destinations.h3_09.isin(economicZones_hexs), 'is_economicZone'] = 1.01

    destinations["T001___elast_eetu"] = destinations['is_eetu']*destinations.T001 #np.ceil(destinations['is_eetu']*destinations.T001)
    destinations["T001___elast_economicZone"] = destinations['is_economicZone']*destinations.T001 #np.ceil(destinations['is_economicZone']*destinations.T001)

    newpath = f'../data/elasticities/{title}'
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    if not os.path.exists(f'../plots/elasticities/{title}'):
        os.makedirs(f'../plots/elasticities/{title}')

    filepaths = glob(f"../data/test_travelTimes/tt___{scenario['network']}_*.parquet")
    dfs = []

    for file in filepaths: dfs.append(pd.read_parquet(file))

    tt = pd.concat(dfs)

    originalT001 = destinations.T001.sum()
    originalN_HOUSING = origins.N_HOUSING.sum()

    for _col in ["T001___elast_eetu", "T001___elast_economicZone"]:
        #print(destinations.T001.sum(), destinations['T001'+_col].sum())
        originalCol = _col.split("___")[0]
        _dest = destinations.drop(columns=[originalCol]).rename(columns={_col: originalCol})
        active, ACTIVE_IDX, ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU, ACTIVE_IDX___ECONOMICZONES, WEIGHTED_ACTIVE_IDX___ECONOMICZONES = calcActiveAccess(tt, origins, _dest, TIME_THROSHOLD)
        #print(ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU, 'verificar o que retorna')
        mainMetrics['ACTIVE_IDX'] = ACTIVE_IDX
        mainMetrics['ACTIVE_IDX___EETU'] = ACTIVE_IDX___EETU
        mainMetrics['WEIGHTED_ACTIVE_IDX'] = np.ceil(WEIGHTED_ACTIVE_IDX)
        mainMetrics['WEIGHTED_ACTIVE_IDX___EETU'] = np.ceil(WEIGHTED_ACTIVE_IDX___EETU)
        mainMetrics['WEIGHTED_ACTIVE_IDX___ECONOMICZONES'] = np.ceil(WEIGHTED_ACTIVE_IDX___ECONOMICZONES)
        mainMetrics['ACTIVE_IDX___ECONOMICZONES'] = ACTIVE_IDX___ECONOMICZONES
        mainMetrics["SCENARIO_N_JOBS_1PERC"] = int(np.ceil(_dest[originalCol].sum()))
        mainMetrics["BASELINE_N_JOBS"] = int(originalT001)
        mainMetrics["DELTA_JOBS"] = int(mainMetrics["SCENARIO_N_JOBS_1PERC"] - mainMetrics["BASELINE_N_JOBS"])
        with open(f"../data/elasticities/{title}/summary___{_col}.json", 'w') as f:
            json.dump(mainMetrics, f, indent=4)

    for _col in ["N_HOUSING___elast_eetu", "N_HOUSING___elast_economicZone"]:
        #print(destinations.T001.sum(), destinations['T001'+_col].sum())
        originalCol = _col.split("___")[0]
        _origins = origins.drop(columns=[originalCol]).rename(columns={_col: originalCol})
        active, ACTIVE_IDX, ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU, ACTIVE_IDX___ECONOMICZONES, WEIGHTED_ACTIVE_IDX___ECONOMICZONES = calcActiveAccess(tt, _origins, destinations, TIME_THROSHOLD)
        #print(ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU, 'verificar o que retorna')
        mainMetrics['ACTIVE_IDX'] = ACTIVE_IDX
        mainMetrics['ACTIVE_IDX___EETU'] = ACTIVE_IDX___EETU
        mainMetrics['WEIGHTED_ACTIVE_IDX'] = np.ceil(WEIGHTED_ACTIVE_IDX)
        mainMetrics['WEIGHTED_ACTIVE_IDX___EETU'] = np.ceil(WEIGHTED_ACTIVE_IDX___EETU)
        mainMetrics['WEIGHTED_ACTIVE_IDX___ECONOMICZONES'] = np.ceil(WEIGHTED_ACTIVE_IDX___ECONOMICZONES)
        mainMetrics['ACTIVE_IDX___ECONOMICZONES'] = ACTIVE_IDX___ECONOMICZONES
        mainMetrics["SCENARIO_N_HOUSING_1PERC"] = int(np.ceil(origins[_col].sum()))
        mainMetrics["BASELINE_N_HOUSING"] = int(originalN_HOUSING)
        mainMetrics["DELTA_N_HOUSING"] = int(mainMetrics["SCENARIO_N_HOUSING_1PERC"] - mainMetrics["BASELINE_N_HOUSING"])

        with open(f"../data/elasticities/{title}/summary___{_col}.json", 'w') as f:
            json.dump(mainMetrics, f, indent=4)