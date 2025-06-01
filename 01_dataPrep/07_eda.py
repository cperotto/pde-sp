from glob import glob
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import h3pandas
import numpy as np
import mapclassify

annotations = []

sp = gpd.read_file("../data/sp.geojson")

eetu = gpd.read_file("../data/eetu/activeEETU.geojson")
hexEETU = eetu.h3_09.unique()
del eetu

economicZones = gpd.read_file("../data/economicZones/economicZones.geojson")
hexEconomicZones = economicZones.h3_09.unique()
del economicZones

def plotHexMap(gdf, col, title, path, _bins=[]):
    
    gdf = gdf.loc[(~gdf[col].isna())]
    gdf = gdf.set_index("h3_09")
    gdf = gdf.h3.h3_to_geo_boundary()

    #m = gpd.GeoDataFrame(gdf.loc[~gdf[col].isna()]).explore(column=col, cmap='coolwarm_r')
    #m.save(f"./check_{title}.html")
    
    shouldShowLegend = True

    if len(_bins)==0:
        ax = gdf.plot(
            col, cmap='coolwarm_r', legend=True,  zorder=10,
            scheme='quantiles', k=7, edgecolor="none",
            legend_kwds={'bbox_to_anchor': (1.25, 0.5)}
        )
        

    else:
        #if '2013' in title: shouldShowLegend = False
        ax = gdf.plot(
            col, cmap='coolwarm_r', legend=shouldShowLegend,  zorder=10,
            scheme='UserDefined', classification_kwds={'bins': _bins}, edgecolor="none",
            legend_kwds={'bbox_to_anchor': (1.25, 0.5)}
        )
        

        
    
    sp.plot(ax=ax, alpha=0.4, color='white', edgecolor='gray', linewidth=0.5, zorder=1)
    if "DELTA" in col:
        plt.title("(A)   Variação absoluta", fontfamily="Times New Roman")

    if "2022" in title:
        plt.title("(C)   Quantidade (2022)", fontfamily="Times New Roman")

    if "2013" in title:
        plt.title("(C)   Quantidade (2013)", fontfamily="Times New Roman")
    
    plt.tight_layout()
    plt.axis('off')
    plt.savefig(f'{path}{title}.png', dpi=900)
   
    return 

panel = pd.DataFrame()
dfs = {}

bins_2013 = None

for YEAR in ['2013', '2022']:

    path = f'../plots/EDA__{YEAR}/'

    origins = pd.read_csv(f"../data/address/origins__{YEAR}.csv", sep=';')
    origins = origins.groupby('h3_09').agg({'N_HOUSING': 'sum'}).reset_index()

    print(origins.h3_09.nunique(), "N HEXAGONOS h309")

    _YEAR = YEAR
    if YEAR == "2022": 
        _YEAR = "2021"

    destinations = pd.read_csv(
        f"../data/address/destinations__{_YEAR}.csv", sep=';', 
        usecols=['T001', 'id_hex']).rename(columns={'id_hex': 'h3_09'})
    destinations = destinations.groupby('h3_09').agg({'T001': 'sum'}).reset_index()
    
    print(destinations.h3_09.nunique(), "N HEXAGONOS h309")

    if YEAR=='2013': 
        bins_T001_2013 = mapclassify.Quantiles(destinations['T001'], k=7).bins
        bins_housing_2013 = mapclassify.Quantiles(origins['N_HOUSING'], k=7).bins
        
    
    

    """
    destinations = pd.read_csv(
        f"../data/address/ipea_destinations__{YEAR}.csv", 
        usecols=['T001', 'id_hex', 'name_muni']).rename(columns={'id_hex': 'h3_09'})
    destinations = destinations.loc[destinations.name_muni=='Sao Paulo']
    """
    
    merged = origins.merge(destinations, on='h3_09', how="outer")
    merged = merged.replace(np.nan, 0)
    merged = merged.replace(np.inf, np.nan)
    merged = merged.replace(-np.inf, np.nan)
    
    merged['JOB_BY_HOUSING'] = merged.T001/merged.N_HOUSING

    plotHexMap(origins, 'N_HOUSING', f'Unidades Habitacionais ({YEAR})', path, bins_housing_2013)
    plotHexMap(destinations, 'T001', f'Empregos ({YEAR})', path, bins_T001_2013)
    

    dfs[YEAR] = merged

panel = dfs['2013'].merge(dfs['2022'], on='h3_09', suffixes=['___2013', '___2022'])

panel['DELTA_T001'] = panel.T001___2022-panel.T001___2013
panel['DELTA_N_HOUSING'] = panel.N_HOUSING___2022-panel.N_HOUSING___2013
panel['DELTA_N_HOUSING___PERC'] = 100*panel['DELTA_N_HOUSING']/panel.N_HOUSING___2013
panel['DELTA_JOB_BY_HOUSING'] = panel.JOB_BY_HOUSING___2022-panel.JOB_BY_HOUSING___2013
panel['DELTA_T001___PERC'] = 100*panel['DELTA_T001']/panel.T001___2013

path = f'../plots/EDA__DELTAS/'

eetuPanel = panel.loc[panel.h3_09.isin(hexEETU)]
economicZonesPanel = panel.loc[panel.h3_09.isin(hexEconomicZones)]


for col in ['DELTA_T001', 'DELTA_N_HOUSING']:
    plotHexMap(panel, col, col, path)
    plotHexMap(eetuPanel, col, "[EETU] "+col, path)
    plotHexMap(economicZonesPanel, col, "[Zonas Econ.] "+col, path)


def plotHexMap__perc(gdf, col, titleLabel, accessIDX_name):
    
    gdf = gdf.set_index("h3_09")
    gdf = gdf.h3.h3_to_geo_boundary()

    def getCat(value):
        if value <= -60: return "X ≤ -60%"
        if value <= -30: return "-60% < X ≤ -30%"
        if value <= 0: return "-30% < X ≤ 0%"
        if value <= 30: return "0% < X ≤ 30%"
        if value <= 60: return "30% < X ≤ 60%"
        if value <= 100: return "60% < X ≤ 100%"
        if value > 100: return "X > 100%"

    #gdf = gdf.sort_values(col)
    #gdf['categoria'] = gdf[col].apply(getCat)
    
    MAX_PERC_VALUE = 120
    
    ax = gdf.loc[gdf[col]<MAX_PERC_VALUE].plot(
        col, cmap='coolwarm_r', legend=True, edgecolor='none', vmin=-50, 
        vmax=50, zorder=4 #legend_kwds={'bbox_to_anchor': (1.25, 0.5)}
    ) 
    ax.legend(bbox_to_anchor=(1.25, 0.5))
    
    """
    ax = gdf.loc[gdf[col]<MAX_PERC_VALUE].plot(col, cmap='coolwarm_r', legend=True, 
                       edgecolor='face', scheme="equal_interval", k=7, vmax=MAX_PERC_VALUE) #vmin=-100, vmax=100, "
    """
    """

    ax = gdf.plot('categoria', cmap='coolwarm_r', legend=True, 
                       edgecolor='face', categorical=True, legend_kwds={'bbox_to_anchor': (1.5, 0.5)}) "
    """
    sp.plot(ax=ax, alpha=0.4, color='white', edgecolor='gray', linewidth=0.5, zorder=1)
    plt.title("(B)   Variação percentual", fontfamily="Times New Roman")
    plt.axis('off')
    plt.tight_layout()
    path = f'../plots/EDA__DELTAS/'
    plt.savefig(f'{path}{titleLabel}.png', dpi=800)
    #plt.show()
        
    return 


for col in ['DELTA_T001___PERC', 'DELTA_N_HOUSING___PERC']:
    plotHexMap__perc(panel.loc[abs(panel[col])!=np.inf], col, col, path)
    plotHexMap__perc(eetuPanel.loc[abs(eetuPanel[col])!=np.inf], col, "[EETU] "+col, path)
    plotHexMap__perc(economicZonesPanel.loc[abs(economicZonesPanel[col])!=np.inf], col, "[Zonas Econ.] "+col, path)


def calcAggVariable(df, variable):
    filteredDF = df.loc[abs(df[f'DELTA_{variable}___PERC'])!=np.inf]
    return 100*filteredDF[f'DELTA_{variable}'].sum()/filteredDF[f'{variable}___2013'].sum()

annotations = [

    # whole city
    ["Empregos Total 2013", panel.T001___2013.sum()], ["Empregos Total 2022", panel.T001___2022.sum()],
    ["Empregos Média 2013", panel.T001___2013.mean()], ["Empregos Média 2022", panel.T001___2022.mean()],
    ["Empregos Mediana 2013", panel.T001___2013.median()], ["Empregos Mediana 2022", panel.T001___2022.median()],
    ["Empregos Max 2013", panel.T001___2013.max()], ["Empregos Max 2022", panel.T001___2022.max()],
    ["Empregos Std 2013", panel.T001___2013.std()], ["Empregos Std 2022", panel.T001___2022.std()],
    ["Delta Empregos", panel.DELTA_T001.sum()], ["Delta Moradias", panel.DELTA_N_HOUSING.sum()],
    ["Moradias Total 2013", panel.N_HOUSING___2013.sum()], ["Moradias Total 2022", panel.N_HOUSING___2022.sum()],
    ["Moradias Mediana 2013", panel.N_HOUSING___2013.median()], ["Moradias Mediana 2022", panel.N_HOUSING___2022.median()],
    ["Moradias Max 2013", panel.N_HOUSING___2013.max()], ["Moradias Max 2022", panel.N_HOUSING___2022.max()],
    ["Moradias Média 2013", panel.N_HOUSING___2013.mean()], ["Moradias Média 2022", panel.N_HOUSING___2022.mean()],
    ["Moradias Std 2013", panel.N_HOUSING___2013.std()], ["Moradias Std 2022", panel.N_HOUSING___2022.std()],

    ["Delta Moradias Perc", calcAggVariable(panel, 'N_HOUSING')], 
    ["Delta Empregos Perc", calcAggVariable(panel, 'T001')],

    # eetu regions
    ["Empregos Total 2013 [EETU]", eetuPanel.T001___2013.sum()], ["Empregos Total 2022 [EETU]", eetuPanel.T001___2022.sum()],
    ["Empregos Média 2013 [EETU]", eetuPanel.T001___2013.mean()], ["Empregos Média 2022 [EETU]", eetuPanel.T001___2022.mean()],
    ["Empregos Mediana 2013 [EETU]", eetuPanel.T001___2013.median()], ["Empregos Mediana 2022 [EETU]", eetuPanel.T001___2022.median()],
    ["Empregos Max 2013 [EETU]", eetuPanel.T001___2013.max()], ["Empregos Max 2022 [EETU]", eetuPanel.T001___2022.max()],
    ["Empregos Std 2013 [EETU]", eetuPanel.T001___2013.std()], ["Empregos Std 2022 [EETU]", eetuPanel.T001___2022.std()],
    ["Delta Empregos [EETU]", eetuPanel.DELTA_T001.sum()], ["Delta Moradias [EETU]", eetuPanel.DELTA_N_HOUSING.sum()],
    ["Moradias Total 2013 [EETU]", eetuPanel.N_HOUSING___2013.sum()], ["Moradias Total 2022 [EETU]", eetuPanel.N_HOUSING___2022.sum()],
    ["Moradias Mediana 2013 [EETU]", eetuPanel.N_HOUSING___2013.median()], ["Moradias Mediana 2022 [EETU]", eetuPanel.N_HOUSING___2022.median()],
    ["Moradias Max 2013 [EETU]", eetuPanel.N_HOUSING___2013.max()], ["Moradias Max 2022 [EETU]", eetuPanel.N_HOUSING___2022.max()],
    ["Moradias Média 2013 [EETU]", eetuPanel.N_HOUSING___2013.mean()], ["Moradias Média 2022 [EETU]", eetuPanel.N_HOUSING___2022.mean()],
    ["Moradias Std 2013 [EETU]", eetuPanel.N_HOUSING___2013.std()], ["Moradias Std 2022 [EETU]", eetuPanel.N_HOUSING___2022.std()],


    ["Delta Moradias Perc [EETU]", calcAggVariable(eetuPanel, 'N_HOUSING')], 
    ["Delta Empregos Perc [EETU]", calcAggVariable(eetuPanel, 'T001')],

    # zonas desenv. econômico
    ["Empregos 2013 [Z. EC.]", economicZonesPanel.T001___2013.sum()], ["Empregos 2022 [Z. EC.]", economicZonesPanel.T001___2022.sum()],
    ["Empregos Média 2013 [Z. EC.]", economicZonesPanel.T001___2013.mean()], ["Empregos Média 2022 [Z. EC.]", economicZonesPanel.T001___2022.mean()],
    ["Empregos Mediana 2013 [Z. EC.]", economicZonesPanel.T001___2013.median()], ["Empregos Mediana 2022 [Z. EC.]", economicZonesPanel.T001___2022.median()],
    ["Empregos Max 2013 [Z. EC.]", economicZonesPanel.T001___2013.max()], ["Empregos Max 2022 [Z. EC.]", economicZonesPanel.T001___2022.max()],
    ["Empregos Std 2013 [Z. EC.]", economicZonesPanel.T001___2013.std()], ["Empregos Std 2022 [Z. EC.]", economicZonesPanel.T001___2022.std()],
    
    ["Delta Empregos [Z. EC.]", economicZonesPanel.DELTA_T001.sum()], ["Delta Moradias [Z. EC.]", economicZonesPanel.DELTA_N_HOUSING.sum()],
    ["Moradias 2013 [Z. EC.]", economicZonesPanel.N_HOUSING___2013.sum()], ["Moradias 2022 [Z. EC.]", economicZonesPanel.N_HOUSING___2022.sum()],
    ["Moradias Mediana 2013 [Z. EC.]", economicZonesPanel.N_HOUSING___2013.median()], ["Moradias Mediana 2022 [Z. EC.]", economicZonesPanel.N_HOUSING___2022.median()],
    ["Moradias Max 2013 [Z. EC.]", economicZonesPanel.N_HOUSING___2013.max()], ["Moradias Max 2022 [Z. EC.]", economicZonesPanel.N_HOUSING___2022.max()],
    ["Moradias Média 2013 [Z. EC.]", economicZonesPanel.N_HOUSING___2013.mean()], ["Moradias Média 2022 [Z. EC.]", economicZonesPanel.N_HOUSING___2022.mean()],
    ["Moradias Std 2013 [Z. EC.]", economicZonesPanel.N_HOUSING___2013.std()], ["Moradias Std 2022 [Z. EC.]", economicZonesPanel.N_HOUSING___2022.std()],


    ["Delta Moradias Perc [Z. EC.]", calcAggVariable(economicZonesPanel, 'N_HOUSING')], 
    ["Delta Empregos Perc [Z. EC.]", calcAggVariable(economicZonesPanel, 'T001')],

    ["Delta Empregos Std", panel.DELTA_T001.std()],
    ["Delta Empregos Mediana", panel.DELTA_T001.median()],
    ["Delta Empregos Média", panel.DELTA_T001.mean()],

    ["Delta Moradias Std", panel.DELTA_N_HOUSING.std()],
    ["Delta Moradias Mediana", panel.DELTA_N_HOUSING.median()],
    ["Delta Moradias Média", panel.DELTA_N_HOUSING.mean()],

    ["Delta Empregos Std [EETU]", eetuPanel.DELTA_T001.std()],
    ["Delta Empregos Mediana [EETU]", eetuPanel.DELTA_T001.median()],
    ["Delta Empregos Média [EETU]", eetuPanel.DELTA_T001.mean()],

    ["Delta Moradias Std [EETU]", eetuPanel.DELTA_N_HOUSING.std()],
    ["Delta Moradias Mediana [EETU]", eetuPanel.DELTA_N_HOUSING.median()],
    ["Delta Moradias Média [EETU]", eetuPanel.DELTA_N_HOUSING.mean()],

    ["Delta Empregos Std [Z. EC.]", economicZonesPanel.DELTA_T001.std()],
    ["Delta Empregos Mediana [Z. EC.]", economicZonesPanel.DELTA_T001.median()],
    ["Delta Empregos Média [Z. EC.]", economicZonesPanel.DELTA_T001.mean()],

    ["Delta Moradias Std [Z. EC.]", economicZonesPanel.DELTA_N_HOUSING.std()],
    ["Delta Moradias Mediana [Z. EC.]", economicZonesPanel.DELTA_N_HOUSING.median()],
    ["Delta Moradias Média [Z. EC.]", economicZonesPanel.DELTA_N_HOUSING.mean()]


]

import csv

def localize_floats(row):
    return [
        str(el).replace('.', ',') if isinstance(el, float) else el 
        for el in row
    ]

with open("../data/eda_summary.txt", "w") as f:
    wr = csv.writer(f, delimiter=';')
    #wr.writerows(annotations)
    for row in annotations: wr.writerow(localize_floats(row))