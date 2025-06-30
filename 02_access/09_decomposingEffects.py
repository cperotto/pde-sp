from matplotlib import pyplot as plt
import pandas as pd
import h3pandas
import geopandas as gpd
import json
import os

eetu = gpd.read_file("../data/eetu/activeEETU.geojson")

sp = gpd.read_file("../data/sp.geojson")

def plotHexMap(gdf, col, title, accessIDX_name):

    SCALE_ADJUSTMENT = 10e4

    gdf[col] = gdf[col]/SCALE_ADJUSTMENT
    
    gdf = gdf.set_index("h3_09")
    gdf = gdf.h3.h3_to_geo_boundary()
    """
    ax = gdf.loc[gdf[col]!=0].plot(col, cmap='coolwarm_r', legend=True, scheme='quantiles', k=6, 
                      legend_kwds={'bbox_to_anchor': (1.5, 0.5)}, edgecolor='none', zorder=5)
    """
    gdf['z_score'] = (gdf[col] - gdf[col].mean()) / gdf[col].std()
    #gdf['z_score'] = np.log(gdf[col])
    print(len(gdf[gdf.z_score<0]), 'NEGATIVOS!')


    ax = gdf.plot(column='z_score', cmap="coolwarm_r", legend=True, 
                  legend_kwds={'bbox_to_anchor': (1.5, 0.5)},
                  edgecolor='face', zorder=3, scheme='quantiles', k=5)
    sp.plot(ax=ax, alpha=0.4, color='white', edgecolor='gray', linewidth=0.5, zorder=1)
    
    #plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    
    if not os.path.exists(f'../plots/componentsDeltas/{accessIDX_name}'):
        os.makedirs(f'../plots/componentsDeltas/{accessIDX_name}')
    
    plt.savefig(f'../plots/componentsDeltas/{accessIDX_name}/{title}.png', dpi=900)
    plt.close()
        
    return 

import numpy as np

def plotHexMap__perc(gdf, col, title, accessIDX_name):

    gdf.replace([np.inf, -np.inf], np.nan, inplace=True)
    gdf = gdf.loc[~gdf[col].isna()]

    vmin=-100 
    vmax=100

    #print(gdf[col].min(), gdf[col].max(), 'SOLO jobs RESULTS::::: CHECK FOR SCALE', title)
    #print(gdf[col].describe())
    #print(len(gdf[gdf[col]>70]), len(gdf))

    useLegend=False
    _title = None

    if "SoloJobs" in title: 
        _title = "(A)   Cenário I (Δ Empregos)"
        print(gdf[col].min(), gdf[col].max(), 'SOLO HOUSING RESULTS::::: CHECK FOR SCALE', title)
        vmin=-70
        vmax=70

    if "SoloHousing" in title: 
        _title = "(B)   Cenário II (Δ População)"
        vmin=-70
        vmax=70

    if "SoloNetwork" in title: 
        _title = "(C)   Cenário III (Δ Transporte)"
        vmin=-70
        vmax=70
        useLegend=True

    else: 
        useLegend=True

    #print(gdf.loc[~gdf[col].isna()].max(), gdf.loc[gdf[col]!=0].min(), 'MÁXIMOS E MINIMOS', title)
    
    gdf = gdf.set_index("h3_09")
    gdf = gdf.h3.h3_to_geo_boundary()
    ax = gdf.loc[gdf[col]!=0].plot(col, cmap='coolwarm_r', legend=useLegend, 
                       edgecolor='none', vmin=vmin, vmax=vmax, zorder=5)
    
    sp.plot(ax=ax, alpha=0.4, color='white', edgecolor='gray', linewidth=0.5, zorder=1)
    
    plt.title(_title, fontfamily='Times New Roman')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f'../plots/componentsDeltas/{accessIDX_name}/{title}.png', dpi=900)
    plt.close()
    #plt.show()
        
    return 


azul = "#4151c1"
laranja = '#f7a88a'
vermelho = "#c40229"
azul_claro = '#8badfd'
"""

#azul = "#062151"
azul = "#0A3379"
laranja = "#f79067"
vermelho = "#BE0900"
azul_claro = "#91bbf3"
"""

def classificar_cor(current_var, delta_real):
    if current_var > 0 and delta_real < 0:
        return  laranja # current_var contribuiu para aumento, mas delta_real caiu
    elif current_var < 0 and delta_real < 0:
        return vermelho     # current_var contribuiu para redução e delta_real caiu
    elif current_var < 0 and delta_real > 0:
        return azul_claro     # current_var contribuiu para redução, mas delta_real aumentou
    elif current_var > 0 and delta_real > 0:
        #return '#3b4cc0'    # current_var contribuiu para aumento e delta_real  aumentou
        return azul #2439c3    # current_var contribuiu para aumento e delta_real  aumentou
    else:
        return 'lightgray' 

import matplotlib.patches as mpatches

"""
mapa_cores = {
        'Delta cenário > 0; Delta real > 0': '#6565b9',
        'Delta cenário < 0; Delta real > 0': '#cde7ef',
        'Delta cenário > 0; Delta real < 0': '#ffc865',
        'Delta cenário < 0; Delta real < 0': '#ff6565',
}
"""
mapa_cores = {
        'Δ cenário > 0; Δ observado > 0': azul,
        'Δ cenário < 0; Δ observado > 0': azul_claro,
        'Δ cenário > 0; Δ observado < 0': laranja,
        'Δ cenário < 0; Δ observado < 0': vermelho,
}
_mapa_cores = []
for item in mapa_cores.keys():
    _mapa_cores.append({"label": item, "cor": mapa_cores[item]})


_mapa_cores = pd.DataFrame(_mapa_cores)


import matplotlib.cm as cm
import matplotlib.colors as mcolors
cmap = cm.get_cmap('coolwarm')
cores = [mcolors.to_hex(cmap(i)) for i in [0.1, 0.4, 0.67, 0.88]]
print(cores)


#['#5977e3', '#c0d4f5', '#f7b79b', '#dc5d4a']

def plotHexMap__dotProduct(gdf, col, title, accessIDX_name, printLegend):

    gdf.replace([np.inf, -np.inf], np.nan, inplace=True)
    gdf = gdf.loc[~gdf[col].isna()]

    

    # orages: variável atual contribuiu para AUMENTO da acessibilidade, mas delta real CAIU
    # reds: (worst case): variável atual contribuiu para REDUÇÃO da acessibilidade e delta real também CAIU
    # reds: (worst case): variável atual contribuiu para REDUÇÃO da acessibilidade, mas delta real também AUMENTOU
    # blues: (worst case): variável atual contribuiu para AUMENTO da acessibilidade e delta real também AUMENTOU
    
    """
    fazer intersecção com hexágonos de eixos e zonas ec. para verificar comportamento/tipologia típica
    """

    gdf['cor'] = gdf.apply(lambda row: classificar_cor(row[col], row['polaridade_delta_real']), axis=1)
    gdf = gdf.set_index("h3_09")
    gdf = gdf.h3.h3_to_geo_boundary()
    ax = gdf.plot(color=gdf['cor'], edgecolor='none', zorder=5)
    sp.plot(ax=ax, alpha=0.4, color='white', edgecolor='gray', linewidth=0.5, zorder=1)

    gdf = gdf.merge(_mapa_cores, on="cor")

    if printLegend==True:

        legenda = [
            mpatches.Patch(color=cor, label=label)
                for label, cor in mapa_cores.items()
        ]

        # Adicionar legenda ao gráfico
        ax.legend(handles=legenda, title='Polaridades', bbox_to_anchor=(1.51, 0.5), fontsize=8)
    plt.title(title, fontfamily='Times New Roman')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f'../plots/componentsDeltas/{accessIDX_name}/{title}.png', dpi=900)
    plt.close()
    return


#for variable in ['T001', 'pond_T001']:
for variable in ['pond_T001']:

    if 'pond_' in variable:

        network__solo = pd.read_csv(f"../data/access/network___solo/active.csv", sep=';').drop(columns=['T001', 'N_HOUSING']).rename(columns={'pond_T001': 'T001'})
        jobs__solo = pd.read_csv(f"../data/access/jobs___solo/active.csv", sep=';').drop(columns=['T001', 'N_HOUSING']).rename(columns={'pond_T001': 'T001'})
        housing__solo = pd.read_csv(f"../data/access/housing___solo/active.csv", sep=';').drop(columns=['T001', 'N_HOUSING']).rename(columns={'pond_T001': 'T001'})

        real__2013 = pd.read_csv(f"../data/access/real___2013/active.csv", sep=';').drop(columns=['T001', 'N_HOUSING']).rename(columns={'pond_T001': 'T001'})
        real__2022 = pd.read_csv(f"../data/access/real___2022/active.csv", sep=';').drop(columns=['T001', 'N_HOUSING']).rename(columns={'pond_T001': 'T001'})
            
    else:

        network__solo = pd.read_csv(f"../data/access/network___solo/active.csv", sep=';').drop(columns=['pond_T001', 'N_HOUSING'])
        jobs__solo = pd.read_csv(f"../data/access/jobs___solo/active.csv", sep=';').drop(columns=['pond_T001', 'N_HOUSING'])
        housing__solo = pd.read_csv(f"../data/access/housing___solo/active.csv", sep=';').drop(columns=['pond_T001', 'N_HOUSING'])

        real__2013 = pd.read_csv(f"../data/access/real___2013/active.csv", sep=';').drop(columns=['pond_T001', 'N_HOUSING'])
        real__2022 = pd.read_csv(f"../data/access/real___2022/active.csv", sep=';').drop(columns=['pond_T001', 'N_HOUSING'])

    df__real = real__2022.merge(real__2013, on='h3_09', how='inner', suffixes=['__real__2013', '__real__2022'])
    df__solo = jobs__solo.merge(network__solo, on='h3_09', how='inner', suffixes=['__jobs__solo', '__network__solo'])
    
    housing_newCols = []
    
    for c in housing__solo.columns:
        if c=='h3_09': 
            housing_newCols.append('h3_09')
        else:
            housing_newCols.append(c+'__housing__solo')
    housing__solo.columns = housing_newCols
    
    df__solo = df__solo.merge(housing__solo, on='h3_09', how='inner')


    df = df__real.merge(df__solo, on='h3_09', how='inner') #.merge(housing__solo, on='h3_09', how='inner')

    df['AAreal___delta'] = df.T001__real__2022-df.T001__real__2013
    df['AAreal___deltaPerc'] = 100*df.AAreal___delta/df.T001__real__2013

    df['AAdev2013__fromSoloJobs'] = df.T001__jobs__solo-df.T001__real__2013 # results in 'non linear effect' -> comes from transportation network and interaction between variables
    df['AAdev2013__fromSoloJobs__perc'] = 100*df.AAdev2013__fromSoloJobs/df.T001__real__2013
    df['AAdev2013__fromSoloHousing'] = df.T001__housing__solo-df.T001__real__2013
    df['AAdev2013__fromSoloHousing__perc'] = 100*df.AAdev2013__fromSoloHousing/df.T001__real__2013
    df['AAdev2013__fromSoloNetwork'] = df.T001__network__solo-df.T001__real__2013
    df['AAdev2013__fromSoloNetwork__perc'] = 100*df.AAdev2013__fromSoloNetwork/df.T001__real__2013

    df['AAdev2022__fromSoloJobs'] = df.T001__jobs__solo-df.T001__real__2022 # results in 'non linear effect' -> comes from transportation network and interaction between variables
    df['AAdev2022__fromSoloJobs__perc'] = 100*df.T001__jobs__solo/df.T001__real__2022-100
    df['AAdev2022__fromSoloHousing'] = df.T001__housing__solo-df.T001__real__2022
    df['AAdev2022__fromSoloHousing__perc'] = 100*df.T001__housing__solo/df.T001__real__2022-100
    df['AAdev2022__fromSoloNetwork'] = df.T001__network__solo-df.T001__real__2022
    df['AAdev2022__fromSoloNetwork__perc'] = 100*df.T001__network__solo/df.T001__real__2022-100

    df['deltaComponent__fromSoloJobs__perc'] = 100*df.AAdev2013__fromSoloJobs/df['AAreal___delta']
    df['deltaComponent__fromSoloHousing__perc'] = 100*df.AAdev2013__fromSoloHousing/df['AAreal___delta']
    df['deltaComponent__fromSoloNetwork__perc'] = 100*df.AAdev2013__fromSoloNetwork/df['AAreal___delta']

    #print(df.AAdev2022__fromSoloHousing.describe(), 'DESCRIBE PROBLEM AT AAdev2022__fromSoloHousing')

    df.to_csv(f"../data/effects/{variable}_effects.csv", sep=';', index=False, decimal=',')

    
    for col in [
        'AAreal___delta', 
        #'AAdev2013__fromSoloJobs', 'AAdev2013__fromSoloHousing', 'AAdev2013__fromSoloNetwork',
        #'AAdev2022__fromSoloJobs', 'AAdev2022__fromSoloNetwork', 'AAdev2022__fromSoloHousing', 
    ]:
        plotHexMap(df, col, col, variable)

    i =2
    
    

    for col in [
        'AAreal___deltaPerc',
        'AAdev2013__fromSoloJobs__perc', 'AAdev2013__fromSoloHousing__perc', 'AAdev2013__fromSoloNetwork__perc',
        'AAdev2022__fromSoloJobs__perc', 'AAdev2022__fromSoloNetwork__perc', 'AAdev2022__fromSoloHousing__perc', 
    ]:
        plotHexMap__perc(df, col, col, variable)
    
    
    
    df["polaridade_delta_real"] = -1
    df.loc[df.AAreal___delta>0, "polaridade_delta_real"] = 1

    i = 0

    titles = {
        'AAdev2013__fromSoloJobs__perc': "(A)   Cenário I (Δ Empregos)",
        'AAdev2013__fromSoloHousing__perc': "(B)   Cenário II (Δ População)",
        'AAdev2013__fromSoloNetwork__perc': "(C)   Cenário III (Δ Transporte)"
    }
    
    for col in [
        #"deltaComponent__fromSoloJobs__perc", "deltaComponent__fromSoloHousing__perc", "deltaComponent__fromSoloNetwork__perc"
        'AAdev2013__fromSoloJobs__perc', 'AAdev2013__fromSoloHousing__perc', 'AAdev2013__fromSoloNetwork__perc',
    ]:
        print_legend = False
        if i==2: print_legend = True
        title = col.replace("AAdev2013", "polaridade")
        plotHexMap__dotProduct(df, col, titles[col], variable, print_legend)
        print("ok")
        i+=1

    
        
