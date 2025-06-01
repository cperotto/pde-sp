import pandas as pd
import geopandas as gpd
import h3pandas

from unidecode import unidecode

from shapely.geometry import Point

def checkNames(row):
    return unidecode(row.NOM_SEGLOGR.lower()) in unidecode(row.NOME_LOG.lower())

import sys

YEAR = str(sys.argv[1])

iptu = pd.read_csv(f"./data/iptu/01_addresses___{YEAR}.csv")
iptu = iptu.groupby(['CEP', 'NOME_LOG', 'NUMERO_LOG']).agg({'N_HOUSING': 'sum', 'ADDRESS': 'first'}).reset_index()
iptu['NUMERO_LOG'] = iptu['NUMERO_LOG'].astype(float)
iptu = iptu.rename(columns={'NUMERO_LOG': 'NUM_ENDERECO'})
iptu['CEP'] = iptu['CEP'].astype(str).str.replace("-", "").str[1:]
print(iptu.N_HOUSING.sum(), 'TOTAL IPTU')

usecols_address = [
    "LATITUDE", "LONGITUDE", 'CEP',
    'NUM_ENDERECO', 'NOM_SEGLOGR'
]
address = pd.read_csv(
    "/Users/camillaperotto/Downloads/3550308_SAO_PAULO.csv", sep=';', usecols=usecols_address
)
print('before drop', len(address))
address = address.drop_duplicates(['CEP', 'NOM_SEGLOGR', 'NUM_ENDERECO'])
print('after drop', len(address))
address['NUM_ENDERECO'] = address['NUM_ENDERECO'].astype(float)
address['CEP'] = address['CEP'].astype(str)

iptu = iptu.reset_index()

merged = iptu.merge(address, on=['CEP', 'NUM_ENDERECO'], how='inner')
notFound = iptu.loc[~iptu['index'].isin(merged['index'])]

#casos em que o número no iptu não existe na base do ibge
#consideramos o endereço mais próximo
merged__secondCall = notFound.merge(address, on=['CEP'], how='inner')
merged__secondCall['DELTA_NUM_ENDERECO'] = abs(merged__secondCall.NUM_ENDERECO_x-merged__secondCall.NUM_ENDERECO_y)
merged__secondCall = merged__secondCall.sort_values(["CEP", "NUM_ENDERECO_x", "DELTA_NUM_ENDERECO"], ascending=True).drop_duplicates(["CEP", "NUM_ENDERECO_x"], keep='first')
merged = pd.concat([merged, merged__secondCall])
merged__thirdCall = notFound.loc[~iptu['index'].isin(merged__secondCall['index'])]
del merged__secondCall

merged__thirdCall['PARTIAL_CEP'] = merged__thirdCall.CEP.apply(lambda string: string[:4]).astype(str)
print('now building PARTIAL_CEP')
address['PARTIAL_CEP'] = address.CEP.apply(lambda string: string[:4]).astype(str)
print('DONE building PARTIAL_CEP ---- SHOULD START merged__thirdCall.merge(address')
merged__thirdCall = merged__thirdCall.merge(address, on='PARTIAL_CEP', how='inner')
print('DONE merged__thirdCall.merge(address')

merged__thirdCall['NOME_LOG_MATCH'] = merged__thirdCall.apply(checkNames, axis=1)
merged__thirdCall = merged__thirdCall.loc[merged__thirdCall.NOME_LOG_MATCH==True]

merged__thirdCall['DELTA_NUM_ENDERECO'] = abs(merged__thirdCall.NUM_ENDERECO_x-merged__thirdCall.NUM_ENDERECO_y)
merged__thirdCall = merged__thirdCall.sort_values(["PARTIAL_CEP", "NUM_ENDERECO_x", "DELTA_NUM_ENDERECO"], ascending=True).drop_duplicates(["CEP_x", "NUM_ENDERECO_x"], keep='first')
print(len(merged__thirdCall), 'checando 3a rodada')
print(merged__thirdCall.loc[merged__thirdCall.NOM_SEGLOGR=='HIGIENOPOLIS'], 'HIGIENOPOLIS AFTER 3 TRIALS')
### TO DO: CORRIGIR LOCAIS EM QUE O CEP DO IPTU ESTÁ CADASTRADO COMO 0
# que são os registros no df reallyNotFound

merged = pd.concat([merged, merged__thirdCall])

del merged__thirdCall

#reallyNotFound = iptu.loc[~iptu['index'].isin(merged['index'])]
#reallyNotFound.to_csv(f"./data/address/reallyNotFound__{YEAR}.csv", index=False, sep=';')

#print(reallyNotFound.N_HOUSING.sum())
print(merged.N_HOUSING.sum(), 'total sum merged')
print('SHOULD BUILD GEOMETRIES NOW::::::')
merged = merged.groupby(['LATITUDE', 'LONGITUDE']).agg(
    {'N_HOUSING': 'sum', 'CEP': 'first'}
).reset_index()
merged["geometry"] = merged[["LONGITUDE", "LATITUDE"]].apply(Point, axis=1)
print('SHOULD FIND HEXGONS NOW::::::')
print(merged.N_HOUSING.sum(), 'total MERGE!')
merged = gpd.GeoDataFrame(merged)
merged = merged.h3.geo_to_h3(9).reset_index()

print('now building csv:::: almost done!')
#merged.to_file(f"./data/address/origins__{YEAR}.geojson", driver='GeoJSON')
merged.drop(columns=['geometry']).to_csv(f"./data/address/origins__{YEAR}.csv", sep=';', index=False)


### deprecated

"""
enderecos = iptu[['ADDRESS']].to_records()
# Cria uma instância do geocodificador Nominatim
geolocator = Nominatim(user_agent="IPTU_ADDRESS")

# Função para obter a latitude e longitude de um endereço
def obter_lat_lng(endereco, idx):
    try:
        # Geocodificando o endereço
        location = geolocator.geocode(endereco)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Erro ao geocodificar o endereço {endereco}: {e} no índice: ", idx)
        return None, None

# Nome do arquivo CSV onde os resultados serão armazenados
filepath = f'./data/iptu/02_addressesCoordinates___{YEAR}.csv'

if os.path.exists(filepath):
    mode = 'a+'
    currentFile = pd.read_csv(filepath)
    currentidx = currentFile.iloc[-1].idx+1
    
else:
    currentidx = 0
    mode = 'w+'

print('should process from:', currentidx)


with open(filepath, mode=mode, newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    if mode=='w+': writer.writerow(['idx', 'address', 'latitude', 'longitude'])  # Cabeçalho do CSV

    # Para cada endereço, obtemos as coordenadas e escrevemos no CSV
    for idx, endereco in enderecos[currentidx:]:
        lat, lng = obter_lat_lng(endereco, idx)
        
        # Escreve uma nova linha no CSV com o endereço e as coordenadas
        writer.writerow([idx, endereco, lat, lng])
        
        # Aguarda um pouco para não sobrecarregar a API
        time.sleep(1.02)

print(f"Processamento concluído. Resultados salvos em '{filepath}'.")
"""
