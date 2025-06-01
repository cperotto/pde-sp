from libpysal.weights.contiguity import Queen
from splot.esda import plot_local_autocorrelation
from esda.moran import Moran_Local_BV, Moran_Local

from matplotlib import pyplot as plt

import pandas as pd
import h3pandas
import numpy as np

#for variable in ['T001', 'pond_T001']:
for variable in ['pond_T001']:

    df = pd.read_csv(f"../data/effects/{variable}_effects.csv", sep=';', decimal=',')
    df = df.set_index("h3_09")
    gdf = df.h3.h3_to_geo_boundary()

    gdf = gdf.loc[(gdf.AAreal___deltaPerc!=-np.inf) & (gdf.AAreal___deltaPerc!=+np.inf) & (~gdf.AAreal___deltaPerc.isna())]

    y = gdf.AAreal___deltaPerc.values

    print(gdf[gdf.AAreal___deltaPerc.isna()])

    print(gdf.AAreal___deltaPerc.sum(), gdf.AAreal___deltaPerc.count(), 'check unique')

    print(y.mean(), 'check')

    w = Queen.from_dataframe(gdf)
    w.transform = 'r'

    #print(gdf.loc[gdf.AAreal___deltaPerc.isna()], y.mean(), 'check')

    moranLoc = Moran_Local(y, w)
    realDeltas = plot_local_autocorrelation(moranLoc, gdf, 'AAreal___deltaPerc')
    plt.savefig(f'../plots/localMorans/AAreal___deltaPerc/{variable}/AAreal___deltaPerc.png', dpi=750)
    
    for _x in ['AAdev2013__fromSoloJobs__perc', 'AAdev2013__fromSoloNetwork__perc', 'AAdev2013__fromSoloHousing__perc']:
        x = gdf[_x].values
        moranLocBV = Moran_Local_BV(x, y, w)
        plot_local_autocorrelation(moranLocBV, gdf, _x)
        plt.savefig(f'../plots/localMorans/AAreal___deltaPerc/{variable}/{_x}.png', dpi=750)

#for variable in ['T001', 'pond_T001']:
for variable in ['pond_T001']:
    print(variable)

    df = pd.read_csv(f"../data/effects/{variable}_effects.csv", sep=';', decimal=',')
    df = df.set_index("h3_09")
    gdf = df.h3.h3_to_geo_boundary()

    gdf = gdf.loc[(gdf.AAreal___delta!=-np.inf) & (gdf.AAreal___delta!=+np.inf) & (gdf.AAreal___delta!=np.nan)]

    y = gdf.AAreal___delta.values

    w = Queen.from_dataframe(gdf)
    w.transform = 'r'

    moranLoc = Moran_Local(y, w)
    realDeltas = plot_local_autocorrelation(moranLoc, gdf, 'AAreal___delta')
    plt.savefig(f'../plots/localMorans/AAreal___delta/{variable}/AAreal___delta.png', dpi=750)

    for _x in ['AAdev2013__fromSoloJobs', 'AAdev2013__fromSoloNetwork', 'AAdev2013__fromSoloHousing']:
        _gdf = gdf.loc[~gdf[_x].isna()]
        x = _gdf[_x].values
        _y = _gdf.AAreal___delta.values
        _w = Queen.from_dataframe(_gdf)
        _w.transform = 'r'
        moranLocBV = Moran_Local_BV(x, _y, _w)
        plot_local_autocorrelation(moranLocBV, _gdf, _x)
        plt.savefig(f'../plots/localMorans/AAreal___delta/{variable}/{_x}.png', dpi=750)