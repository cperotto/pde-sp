import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

sp_hexagons = pd.read_csv("../data/address/ipea_destinations__2013.csv")
sp_hexagons = sp_hexagons.loc[sp_hexagons.name_muni=="Sao Paulo"]
print(sp_hexagons.T001.sum(), 2013)
sp_hexagons = sp_hexagons.id_hex.unique()

YEAR = "2013" # 2013 ou 2021

def removeOutliers(df):
    p99 = df['T001'].quantile(0.9999)

    return df[df['T001'] <= p99]

_usecols = ["id_hex", "T001"]
df1 = pd.read_csv(f"../data/address/_destinations__{YEAR}.csv", usecols=["id_hex", "T001"], sep=';')
df2 = pd.read_csv(f"../data/address/_destinations2__{YEAR}.csv", usecols=_usecols, sep=';')


merged = pd.concat([df1, df2])
print(merged.T001.sum())
merged = removeOutliers(merged)
merged = merged.groupby("id_hex").agg({'T001': 'sum'}).reset_index()
#print(len(merged))
merged = merged.loc[merged.id_hex.isin(sp_hexagons)]
#print(len(merged), merged.T001.sum())

print(merged.T001.sum())
print()
print(merged.T001.describe())

merged.to_csv(f"../data/address/destinations__{YEAR}.csv", sep=';', index=False)