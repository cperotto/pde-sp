import pandas as pd
import geopandas as gpd
from fuzzywuzzy import fuzz
import h3pandas

from unidecode import unidecode

from shapely.geometry import Point

def checkNames(row):
    return unidecode(row.NOM_SEGLOGR.lower()) in unidecode(row.NOME_LOG.lower())

import sys

YEAR = str(sys.argv[1])

jobs = None

if YEAR=="2013":
    jobs = pd.read_csv(f"../data/rais/2013.csv")

if YEAR=='2021':

    """
    ['cep', 'clascnae95', 'dtabertcom', 'dtbaixacom', 'dtenceror',
       'indceivinc', 'indpat', 'indraisneg', 'indsimples', 'municipio',
       'naturjur', 'endereco', 'numlograd', 'bairro', 'estoque', 'estcltout',
       'estoqueesta', 'tamestab', 'tipoestbl', 'ibgesubsetor', 'indativano',
       'clascnae20', 'sbclas20', 'id', 'ceivinc11d', 'verifceivincdv',
       'indceicnpj', 'matrizfilial', 'verifcnpjdv', 'cei11d', 'verifceidv',
       'codareatel', 'ceivinc_m', 'identificad_m', 'radiccnpj_m', 'email_m',
       'telcontato_m', 'razaosocial_m']
    """
    jobs = pd.read_stata(f"../data/rais/2021.dta")
    jobs['cep'] = jobs['cep'].str.strip()
    colsDict = {'endereco': 'nome_logradouro', 'numlograd': 'num_logradouro'}
    jobs = jobs.rename(columns=colsDict)[list(colsDict.values())+['cep', 'bairro', 'estoque']]
    jobs['estoque'] = jobs['estoque'].astype(int, errors='ignore') #.astype(str)
    print(jobs.estoque.unique())

jobs = jobs.loc[jobs.estoque>0]
jobs = jobs.groupby(['cep', 'nome_logradouro', 'num_logradouro', "bairro"]).agg({'estoque': 'sum'}).reset_index()
jobs['num_logradouro'] = jobs['num_logradouro'].astype(float)
print(jobs.estoque.sum(), 'ESTOQUE TOTAL...')
jobs = jobs.rename(columns={'num_logradouro': 'NUM_ENDERECO', 'cep': 'CEP'})
jobs['CEP'] = jobs['CEP'].astype(str)
jobs["CEP_LENGTH"] = jobs.CEP.apply(len)

jobs.loc[jobs.CEP_LENGTH==8, "CEP"] = jobs.loc[jobs.CEP_LENGTH==8, "CEP"].str[:-1]

usecols_address = [
    "LATITUDE", "LONGITUDE", 'CEP',
    'NUM_ENDERECO', 'NOM_SEGLOGR'
]
address = pd.read_csv(
    "../data/addresses.csv", sep=';', usecols=usecols_address
)
address = address.drop_duplicates(['CEP', 'NOM_SEGLOGR', 'NUM_ENDERECO'])
address['NUM_ENDERECO'] = address['NUM_ENDERECO'].astype(float)
address['CEP'] = address['CEP'].astype(str)
address = address.loc[(address.CEP!="1001000") & (~address.NOM_SEGLOGR.str.contains("SEM DENOMINACAO"))].reset_index(drop=True)
address = address.groupby(['CEP', 'NUM_ENDERECO']).agg({"LATITUDE": "first", "LONGITUDE": "first", 'NOM_SEGLOGR': "first"})
address = address.reset_index()

jobs = jobs.reset_index().rename(columns={"index": "_index"})

merged = jobs.merge(address, on=['CEP', 'NUM_ENDERECO'], how='inner')
print("first attemmpt:", merged.estoque.sum(), 100*merged.estoque.sum()/jobs.estoque.sum())
notFound = jobs.loc[~jobs['_index'].isin(merged['_index'])]
print("CHECANDO SE TEM DUPLICATA 1", notFound.estoque.sum()+merged.estoque.sum()==jobs.estoque.sum())
print("CHECANDO SE TEM DUPLICATA 1", notFound.estoque.sum(), merged.estoque.sum(), jobs.estoque.sum())

#casos em que o número na rais não existe na base do ibge
#consideramos o endereço mais próximo
merged__secondCall = notFound.merge(address, on='CEP', how='inner')
merged__secondCall['DELTA_NUM_ENDERECO'] = abs(merged__secondCall.NUM_ENDERECO_x-merged__secondCall.NUM_ENDERECO_y)
merged__secondCall = merged__secondCall.sort_values(["CEP", "NUM_ENDERECO_x", "DELTA_NUM_ENDERECO"], ascending=True).drop_duplicates(["CEP", "NUM_ENDERECO_x"], keep='first')
print(merged__secondCall.estoque.sum(), 'merged__secondCall sum()....')
print(merged__secondCall.loc[merged__secondCall.CEP=="1039000"])

merged = pd.concat([merged, merged__secondCall])
merged__thirdCall = jobs.loc[~jobs['_index'].isin(merged['_index'])]
print(merged__thirdCall.loc[merged__thirdCall.CEP=="1039000"], 'ficaram para 3a tentaiva merged__thirdCall')
print(merged__thirdCall.estoque.sum(), len(merged__thirdCall), 'STILL NOT FOUND')

del merged__secondCall


merged__thirdCall['PARTIAL_CEP'] = merged__thirdCall.CEP.apply(lambda string: string[:4]).astype(str)
print('now building PARTIAL_CEP')
address['PARTIAL_CEP'] = address.CEP.apply(lambda string: string[:4]).astype(str)
print('DONE building PARTIAL_CEP ---- SHOULD START merged__thirdCall.merge(address')
merged__thirdCall = merged__thirdCall.merge(address, on=['PARTIAL_CEP', 'NUM_ENDERECO'], how='inner')
#merged__thirdCall = merged__thirdCall.merge(address, on='PARTIAL_CEP', how='inner')


#merged__thirdCall['DELTA_NUM_ENDERECO'] = abs(merged__thirdCall.NUM_ENDERECO_x-merged__thirdCall.NUM_ENDERECO_y)
#merged__thirdCall = merged__thirdCall.sort_values(["PARTIAL_CEP", "NUM_ENDERECO_x", "DELTA_NUM_ENDERECO"], ascending=True).drop_duplicates(["PARTIAL_CEP", "NUM_ENDERECO_x"], keep='first')

print('DONE merged__thirdCall.merge(address', merged__thirdCall.estoque.sum())

merged = pd.concat([merged, merged__thirdCall])

del merged__thirdCall

reallyNotFound = jobs.loc[~jobs['_index'].isin(merged['_index'])]
reallyNotFound.to_csv(f"../data/address/reallyNotFound__{YEAR}.csv", index=False, sep=';')

print(merged.estoque.sum(), 'total sum merged / after all attempts')
print('estoque not found', reallyNotFound.estoque.sum(), jobs.estoque.sum())
print('SHOULD BUILD GEOMETRIES NOW::::::')

merged["geometry"] = merged[["LONGITUDE", "LATITUDE"]].apply(Point, axis=1)
print('SHOULD FIND HEXGONS NOW::::::')
print(merged.estoque.sum(), 'total MERGE! vs', 'raw total estoque:', jobs.estoque.sum())
print()
merged = gpd.GeoDataFrame(merged)
merged = merged.h3.geo_to_h3(9).reset_index()

merged = merged.rename(columns={"estoque": "T001", "h3_09": 'id_hex'})

print('now building csv:::: almost done!')
#merged.to_file(f"./data/address/origins__{YEAR}.geojson", driver='GeoJSON')
merged.drop(columns=['geometry']).to_csv(f"../data/address/destinations__{YEAR}.csv", sep=';', index=False)

print(len(merged[merged.CEP=="1422002"]), len(jobs[jobs.CEP=='1422002']))