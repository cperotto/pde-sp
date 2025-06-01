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

def FirstTrial(jobs, address):
    merged = jobs.merge(address, on=['CEP', 'NUM_ENDERECO'], how='inner')
    merged['merged_at'] = 1
    print("first attemmpt:", merged.estoque.sum(), 100*merged.estoque.sum()/jobs.estoque.sum())

    return merged.reset_index()

def SecondTrial(jobs, address):
    merged = jobs.merge(address, on='CEP', how='inner')
    merged['DELTA_NUM_ENDERECO'] = abs(merged.NUM_ENDERECO_x-merged.NUM_ENDERECO_y)
    merged = merged.sort_values(["_index", 'DELTA_NUM_ENDERECO'], ascending=True).drop_duplicates("_index", keep='first')
    merged['merged_at'] = 2
    print("second attemmpt:", merged.estoque.sum(), 100*merged.estoque.sum()/jobs.estoque.sum())
    return merged.reset_index()

def trimCEP(cep):
    return str(str(cep)[:-2])

def ThirdTrial(_jobs, _address):
    #print(jobs, 'VERIFICAR JOBS DF')
    #print('JOBS COLUMNS', jobs.columns)
    
    _jobs['PARTIAL_CEP'] = _jobs.CEP.apply(trimCEP).astype(str).apply(lambda x: x.strip())
    _address['PARTIAL_CEP'] = _address.CEP.apply(trimCEP).astype(str).apply(lambda x: x.strip())
    _merged = _jobs.merge(_address, on='PARTIAL_CEP', how='inner')
    _merged['DELTA_NUM_ENDERECO'] = abs(_merged.NUM_ENDERECO_x-_merged.NUM_ENDERECO_y)
    print()
    print(_merged["_index"].nunique(), 'before drop')
    _merged = _merged.sort_values(["_index", 'DELTA_NUM_ENDERECO'], ascending=True).drop_duplicates("_index", keep='first')
    _merged = _merged.rename(columns={'CEP_x': 'CEP'})
    print(_merged["_index"].nunique(), 'after drop')
    _merged['merged_at'] = 3
    print("third attemmpt:", _merged.estoque.sum(), 100*_merged.estoque.sum()/_jobs.estoque.sum())
    return _merged

"""
def ThirdTrial(jobs, address):
    #print(jobs, 'VERIFICAR JOBS DF')
    #print('JOBS COLUMNS', jobs.columns)
    jobs['PARTIAL_CEP'] = jobs.CEP.apply(trimCEP).astype(str)
    address['PARTIAL_CEP'] = address.CEP.apply(trimCEP).astype(str)
    merged = jobs.merge(address, on='PARTIAL_CEP', how='inner')
    merged['DELTA_NUM_ENDERECO'] = abs(merged.NUM_ENDERECO_x-merged.NUM_ENDERECO_y)
    merged = merged.sort_values(["_index", 'DELTA_NUM_ENDERECO'], ascending=True).drop_duplicates(["_index"], keep='first')
    merged = merged.rename(columns={'CEP_x': 'CEP'})
    merged['merged_at'] = 3
    print(merged.estoque.sum(), jobs.estoque.sum(), 'verificar match em 3a trial')
    return merged
"""

merged1 = FirstTrial(jobs, address)
merged2 = SecondTrial(jobs.loc[~jobs._index.isin(merged1._index)], address)
merged = pd.concat([merged1, merged2])
del merged1
del merged2

# for now: should test if 2 trials is enough
merged3 = ThirdTrial(jobs.loc[(~jobs._index.isin(merged._index))], address)
merged = pd.concat([merged, merged3])

merged = merged.sort_values(["_index", 'merged_at']).drop_duplicates("_index", keep='first')

reallyNotFound = jobs.loc[~jobs['_index'].isin(merged['_index'])]
reallyNotFound.to_csv(f"../data/address/reallyNotFound__{YEAR}.csv", index=False, sep=';')

merged['geometry'] = merged.apply(lambda _row: Point(_row.LONGITUDE, _row.LATITUDE), axis=1)
merged = gpd.GeoDataFrame(merged)
merged = merged.h3.geo_to_h3(9).reset_index()

merged = merged.rename(columns={"estoque": "T001", "h3_09": 'id_hex'})
print(merged.T001.sum(), jobs.estoque.sum())
print('now building csv:::: almost done!')
#merged.to_file(f"./data/address/origins__{YEAR}.geojson", driver='GeoJSON')
merged.drop(columns=['geometry']).to_csv(f"../data/address/_destinations__{YEAR}.csv", sep=';', index=False)


print(len(merged[merged.CEP=="1422002"]), len(jobs[jobs.CEP=='1422002']))