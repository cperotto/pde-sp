from glob import glob
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import mapclassify
import h3pandas
import numpy as np
import json
import math
import os

k = 8

vMin = 1
vMax = 7459430739.0

TIME_THROSHOLD = 60

sp = gpd.read_file("../data/sp.geojson")
eetu = gpd.read_file("../data/eetu/activeEETU.geojson")
economicZones = gpd.read_file("../data/economicZones/economicZones.geojson")

with open('../scenarios.json') as json_data:
    scenarios = json.load(json_data)

def decayFunction(travelTime): # verificar isso... parâmetro está decrescendo muito rápido
    # https://findingspress.org/article/32444-cumulative-versus-gravity-based-accessibility-measures-which-one-to-use

    """
    Then we calculated eight gravity-based measures of accessibility derived 
    from the decay parameters previously estimated and another one assuming a 
    fixed negative exponential decay coefficient of 0.01, which is often used 
    in research when travel behavior data is not available.    
    """

    #LAMBDA = -1/0.01
    LAMBDA = 0
    return math.e ** (travelTime*LAMBDA)

def plotHexMap(gdf, col, accessType, vMax, bins_2013=False):

        gdf = gdf.set_index("h3_09")
        gdf = gdf.h3.h3_to_geo_boundary()

        path = f'../plots/scenarios/{title}/{accessType}.png'

        if norm==False:
            ax = gdf.plot(col, cmap='coolwarm_r', legend=True, scheme='quantiles', k=k, 
                        legend_kwds={'bbox_to_anchor': (1.5, 0.5)}, edgecolor='face')
            sp.plot(ax=ax, alpha=0.4, color='white', edgecolor='gray', linewidth=0.5)
            #ax.legend(title=f'Acessibilidade (x10e4)')
        
        if norm==True:
            #bins = [1, 3.6 * 10e6, 10e7,  3 * 10e7, 7 * 10e7, 1.3 * 10e8, 3 * 10e8, 7.5 * 10e9]
            gdf["_class"] = pd.cut(gdf[col], bins=bins_2013, include_lowest=True)
            print(bins_2013)
            cmap = plt.get_cmap('coolwarm_r', k)
            colors = [cmap(i) for i in range(cmap.N)]

            labels = [f'{bins_2013[i]:.1f} – {bins_2013[i+1]:.1f}' for i in range(len(bins_2013) - 1)]
            patches = [Patch(color=colors[i], label=labels[i]) for i in range(len(labels))]
            
            """
            ax = gdf.plot(
                col, cmap='coolwarm_r', legend=True, legend_kwds={'bbox_to_anchor': (1.5, 0.5)},
                edgecolor='face', scheme='UserDefined', vmin=1/SCALE_ADJUSTMENT, classification_kwds={'bins': bins}
            )
            
            """
            ax = gdf.plot(column='_class', cmap=cmap, edgecolor='face')
            ax.legend(handles=patches, loc='lower right', frameon=True, bbox_to_anchor=(1.5, 0.5), fontsize=9, title_fontsize=10) #
            sp.plot(ax=ax, alpha=0.4, color='white', edgecolor='gray', linewidth=0.5)

            path = f'../plots/scenarios/{title}/{accessType}__norm.png'

        #plt.title(accessType)
        plt.axis('off')
        #plt.tight_layout()
        plt.savefig(path, dpi=800)
        plt.close()
        
        return vMax

tableMetrics = []
bins_2013_pond_T001 = None

for scenario in scenarios:

    mainMetrics = {}

    title = scenario['_id']
    
    print(title, 'starting now!')
    print("****************")

    newpath = f'../data/access/{title}'
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    if not os.path.exists(f'../plots/scenarios/{title}'):
        os.makedirs(f'../plots/scenarios/{title}')

    origins = pd.read_csv(f"../data/address/origins__{scenario['origins']}.csv", sep=';')
    origins = origins.groupby('h3_09').agg({'N_HOUSING': 'sum'}).reset_index()

    destinations = pd.read_csv(
        f"../data/address/destinations__{scenario['destinations']}.csv", sep=';', 
        usecols=['T001', 'id_hex']).rename(columns={'id_hex': 'h3_09'})

    """
    destinations = pd.read_csv(
        # SHOULD CHANGE.... NOW READING IPEA
        f"../data/address/ipea_destinations__{scenario['destinations']}.csv", #sep=';', 
        usecols=['T001', 'id_hex', 'name_muni']).rename(columns={'id_hex': 'h3_09'})
    destinations = destinations.loc[destinations.name_muni=='Sao Paulo']
    """

    destinations['elast_T001'] = destinations.T001.copy()
    destinations.loc[destinations.h3_09.isin(economicZones.h3_09.unique()), 'elast_T001'] = 1.01*destinations.loc[destinations.h3_09.isin(economicZones.h3_09.unique()), 'T001']

    #filepaths = glob(f"../data/travelTimes/tt___{scenario['network']}_*.parquet")
    filepaths = glob(f"../data/test_travelTimes/tt___{scenario['network']}_*.parquet")
    dfs = []

    for file in filepaths: dfs.append(pd.read_parquet(file))

    tt = pd.concat(dfs)

    print('done tt mega df!')
    
    tt['travel_time_decay'] = tt.travel_time.apply(decayFunction)

    def calcActiveAccess(tt, origins, destinations, TIME_THROSHOLD):
        
        tt = tt.loc[tt.travel_time<=TIME_THROSHOLD]
        grouped = tt.groupby('from_id').agg({'to_id': 'unique'}).reset_index()

        print('starting T001 data!')
        
        T001 = []
        T001___elast = []
        
        for i, row in grouped.iterrows():
            _destinations = destinations.loc[destinations.h3_09.isin(row.to_id)]
            #_destinations['elast_T001'] = _destinations.T001.copy()
            #_destinations.loc[_destinations.h3_09.isin(economicZones.h3_09.unique()), 'elast_T001'] = 1.01*_destinations.loc[_destinations.h3_09.isin(economicZones.h3_09.unique()), 'T001']
            T001.append(_destinations.T001.sum())
            T001___elast.append(_destinations.elast_T001.sum())

        print('done merging T001 data!')
        
        grouped["T001"] = T001
        #grouped["elast_T001"] = T001___elast
        grouped = grouped.rename(columns={'from_id': 'h3_09'}).drop(columns=["to_id"])
        print(len(grouped), 'before!')
        grouped = grouped.merge(origins, on='h3_09', how="left")
        grouped["N_HOUSING"] = grouped["N_HOUSING"].replace(np.nan, 1)
        grouped["T001"] = grouped["T001"].replace(np.nan, 1)
        #grouped["elast_T001"] = grouped["elast_T001"].replace(np.nan, 1)
        print(len(grouped), 'after merging origins!')
        grouped["pond_T001"] = grouped["T001"]*grouped["N_HOUSING"]
        #grouped["pond_T001_elast"] = grouped["elast_T001"]*grouped["N_HOUSING"]
        
        ACTIVE_IDX = grouped.T001.mean()
        WEIGHTED_ACTIVE_IDX = grouped.pond_T001.sum()/grouped.N_HOUSING.sum()

        grouped_economicZones = grouped.loc[grouped.h3_09.isin(economicZones.h3_09.unique())]
        ACTIVE_IDX___ECONOMICZONES = grouped_economicZones.T001.mean()
        WEIGHTED_ACTIVE_IDX___ECONOMICZONES = grouped_economicZones.pond_T001.sum()/grouped_economicZones.N_HOUSING.sum()

        grouped_eetu = grouped.loc[grouped.h3_09.isin(eetu.h3_09.unique())]
        ACTIVE_IDX___EETU = grouped_eetu.T001.mean()
        WEIGHTED_ACTIVE_IDX___EETU = grouped_eetu.pond_T001.sum()/grouped_eetu.N_HOUSING.sum()
        
        return grouped, ACTIVE_IDX, ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU, ACTIVE_IDX___ECONOMICZONES, WEIGHTED_ACTIVE_IDX___ECONOMICZONES

    """
    def calcActiveAccess(tt, origins, destinations, TIME_THROSHOLD):
        tt = tt.loc[tt.travel_time<=TIME_THROSHOLD]
        print("len tt", len(tt), tt.to_id.nunique())
        merged = tt.merge(destinations, right_on='h3_09', left_on='to_id') #, how="left"
        print(len(merged))
        #vMax = plotHexMap(active, 'T001', f'Hexágonos acessíveis a partir de um hexágono', 162)
        
        merged["T001"] = merged["T001"]*merged['travel_time_decay']
        grouped = merged.groupby('from_id').agg({'T001': 'sum'}).reset_index()
        grouped = grouped.rename(columns={'from_id': 'h3_09'})
        ACTIVE_IDX = grouped.T001.mean()
        grouped = grouped.merge(origins, left_on='h3_09', right_on='h3_09')
        grouped['pond_T001'] = grouped.T001*grouped.N_HOUSING
        grouped_eetu = grouped.loc[grouped.h3_09.isin(eetu.h3_09.unique())]
        WEIGHTED_ACTIVE_IDX = grouped.pond_T001.sum()/grouped.N_HOUSING.sum()
        WEIGHTED_ACTIVE_IDX___EETU = grouped_eetu.pond_T001.sum()/grouped_eetu.N_HOUSING.sum()
        ACTIVE_IDX___EETU = grouped_eetu.T001.mean()
        grouped.to_csv(f"../data/access/{title}/active.csv", sep=';', index=False)
        print("saved active.csv")
        return grouped, ACTIVE_IDX, ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU
    """
    
    active, ACTIVE_IDX, ACTIVE_IDX___EETU, WEIGHTED_ACTIVE_IDX, WEIGHTED_ACTIVE_IDX___EETU, ACTIVE_IDX___ECONOMICZONES, WEIGHTED_ACTIVE_IDX___ECONOMICZONES = calcActiveAccess(tt, origins, destinations, TIME_THROSHOLD)
    active.to_csv(f"../data/access/{title}/active.csv", sep=';', index=False)
    mainMetrics['ACTIVE_IDX'] = ACTIVE_IDX
    mainMetrics['ACTIVE_IDX___EETU'] = ACTIVE_IDX___EETU
    mainMetrics['WEIGHTED_ACTIVE_IDX'] = WEIGHTED_ACTIVE_IDX
    mainMetrics['WEIGHTED_ACTIVE_IDX___EETU'] = WEIGHTED_ACTIVE_IDX___EETU
    mainMetrics['WEIGHTED_ACTIVE_IDX___ECONOMICZONES'] = WEIGHTED_ACTIVE_IDX___ECONOMICZONES
    mainMetrics['ACTIVE_IDX___ECONOMICZONES'] = ACTIVE_IDX___ECONOMICZONES

    def calcPassiveAccess(tt, origins, destinations, TIME_THROSHOLD):
        tt = tt.loc[tt.travel_time<=TIME_THROSHOLD]
        merged = tt.merge(origins, right_on='h3_09', left_on='to_id')
        grouped = merged.groupby('to_id').agg({'N_HOUSING': 'sum'}).reset_index()
        grouped = grouped.rename(columns={'to_id': 'h3_09'})
        PASSIVE_IDX = grouped.N_HOUSING.mean()
        grouped = grouped.merge(destinations, left_on='h3_09', right_on='h3_09')
        grouped['pond_N_HOUSING'] = grouped.T001*grouped.N_HOUSING
        grouped_eetu = grouped.loc[grouped.h3_09.isin(eetu.h3_09.unique())]
        WEIGHTED_PASSIVE_IDX = grouped.pond_N_HOUSING.sum()/grouped.T001.sum()
        WEIGHTED_PASSIVE_IDX___EETU = grouped_eetu.pond_N_HOUSING.sum()/grouped_eetu.T001.sum()
        PASSIVE_IDX___EETU = grouped_eetu.N_HOUSING.mean()
        grouped.to_csv(f"../data/access/{title}/passive.csv", sep=';', index=False)
        return grouped, PASSIVE_IDX, PASSIVE_IDX___EETU, WEIGHTED_PASSIVE_IDX, WEIGHTED_PASSIVE_IDX___EETU

    """
    passive, PASSIVE_IDX, PASSIVE_IDX___EETU, WEIGHTED_PASSIVE_IDX, WEIGHTED_PASSIVE_IDX___EETU = calcPassiveAccess(tt, origins, destinations, TIME_THROSHOLD)
        
    #print(PASSIVE_IDX, 'PASSIVE_IDX')
    #print(WEIGHTED_PASSIVE_IDX, 'WEIGHTED_PASSIVE_IDX')
    mainMetrics['PASSIVE_IDX'] = PASSIVE_IDX
    mainMetrics['WEIGHTED_PASSIVE_IDX'] = WEIGHTED_PASSIVE_IDX

    mainMetrics['PASSIVE_IDX___EETU'] = PASSIVE_IDX___EETU
    mainMetrics['WEIGHTED_PASSIVE_IDX___EETU'] = WEIGHTED_PASSIVE_IDX___EETU
    """

    with open(f"../data/access/{title}/summary.json", 'w') as f:
        json.dump(mainMetrics, f, indent=4)
        #print(mainMetrics)
        _df = pd.DataFrame([mainMetrics])
        _df["SCENARIO"] = title
        tableMetrics.append(_df)

        hist = active.loc[active['T001']!=0].hist(bins=10)
        plt.savefig(f'../plots/scenarios/{title}/hist__active.png', dpi=750)

        if '2013' in title: bins_2013_pond_T001 = np.quantile(active["pond_T001"], q=np.linspace(0, 1, k+1))
        if '2013' in title: bins_2013_T001 = np.quantile(active["T001"], q=np.linspace(0, 1, k+1))

        active = active.loc[active["pond_T001"]>0]

        SCALE_ADJUSTMENT = 10e4

        active["pond_T001"] = active["pond_T001"]/SCALE_ADJUSTMENT

        print('start plotHexMap')
       
        plotHexMap(active, 'T001', f'N empregos acessíveis a partir de um hexágono')
        #plotHexMap(active.loc[active.h3_09.isin(eetu.h3_09)], 'T001', f'[EETU] N empregos acessíveis a partir de um hexágono')
        plotHexMap(active.loc[active.h3_09.isin(eetu.h3_09)], 'pond_T001', f'[EETU] N conexões a partir de um hexágono (pond.)')
   
        #plotHexMap(active, 'pond_T001', f'N conexões a partir de um hexágono (pond.)', vMax, True, bins_2013=bins_2013_pond_T001)
        #plotHexMap(active, 'pond_T001', f'N conexões a partir de um hexágono (pond.)', vMax)
        #plotHexMap(passive, 'N_HOUSING', f'Hexágono (firma) acessível a partir de N u.h', vMax)

        #plotHexMap(active.loc[active.h3_09.isin(eetu.h3_09)], 'pond_T001', f'[EETU] N conexões a partir de um hexágono (pond.)', vMax, True)
    

print("VMAX CALCULADO NOS CENÁRIOS É::::", vMax)

df = pd.concat(tableMetrics)
df.to_csv("../data/access/summary.csv", sep=';', index=False, decimal=',')
