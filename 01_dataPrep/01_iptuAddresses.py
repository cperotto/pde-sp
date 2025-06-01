import pandas as pd
import sys

YEAR = str(sys.argv[1])
print(YEAR)

usecols = [
    'BAIRRO DO IMOVEL', 'NOME DE LOGRADOURO DO IMOVEL', 'NUMERO DO IMOVEL', 
    'CODLOG DO IMOVEL', 'CEP DO IMOVEL', 'TIPO DE USO DO IMOVEL', 'TIPO DE PADRAO DA CONSTRUCAO'
]
encodingByYear = {
    '2022': 'latin-1', '2013': 'utf-8'
}

iptu = pd.read_csv(f"../data/iptu/raw/IPTU{YEAR}.csv", sep=';', on_bad_lines='skip', encoding=encodingByYear[str(YEAR)], usecols=usecols)
print(iptu.columns)
print(len(iptu.loc[iptu['TIPO DE USO DO IMOVEL'].isna()]), 'IPTU IS NA VS ALL', len(iptu))

iptu = iptu.loc[~iptu['TIPO DE USO DO IMOVEL'].isna()]

"""
def getHousing(string):
    if 'garagem' in string.lower(): return False
    if 'residencial' in string.lower(): return True
    return False
"""

def getHousing(string):

    if 'residência' in string.lower(): return True
    if 'residencial' in string.lower(): return True

    return False


iptu['residencial'] = iptu['TIPO DE PADRAO DA CONSTRUCAO'].apply(getHousing)
print(len(iptu.loc[iptu['residencial']==True]), 'COMPARAR: LEN RESIDENCIAL VS ALL', len(iptu))
iptu = iptu.loc[iptu['residencial']==True]
print(len(iptu), 'len iptu')

def checkName(string):
    if 'SEM DENOMINACAO' in string: return 1
    return 0

iptu['SEM_DENOM'] = iptu['NOME DE LOGRADOURO DO IMOVEL'].apply(checkName)
print(iptu[iptu['SEM_DENOM']==1]['CEP DO IMOVEL'], 'SEM DENOMINACAO')

iptu['NO_CEP'] = 0
iptu.loc[iptu['CEP DO IMOVEL']=="00000-000", 'SEM_DENOM'] = 1

iptu['POOR_RECORDS'] = iptu['NO_CEP']*iptu.SEM_DENOM

print(len(iptu.loc[iptu.POOR_RECORDS==1]), 'LEN POOR RECORDS')

iptu = iptu.loc[iptu.POOR_RECORDS!=1]

def formatLog(string):
    string = string.replace("AC    ", "")
    string = string.replace("PRSA ", "Princesa")
    string = string.replace("AV ", "Avenida ")
    string = string.replace(" STA ", " Santa ")
    string = string.replace(" STO ", " Santo ")
    string = string.replace("SARG ", " Sargento ")
    string = string.replace(" S   ", " São ")
    string = string.replace(" CAP ", " Capitão ")
    string = string.replace(" GAL ", " General ")
    string = string.replace(" BR ", " Barão ")
    string = string.replace(" SEN ", " Senador ")
    string = string.replace(" PROF ", " Professor ")
    string = string.replace(" CONS ", " Conselheiro ")
    string = string.replace(" COMEN ", " Comendador ")
    string = string.replace(" CEL ", " Coronel ")
    string = string.replace(" CD ", " Conde ")
    string = string.replace(" CDSSADE ", " Condessa ")
    string = string.replace("PC ", "Praça ")
    string = string.replace("LG  ", "Largo ")
    string = string.replace("LD  ", "Ladeira ")
    string = string.replace("TV  ", "Travessa ")
    string = string.replace("VL  ", "Vila ")
    string = string.replace("DR ", "Doutor ")
    string = string.replace("MARQ ", "Marquês ")
    string = string.replace("VD  ", "Viaduto ")
    string = string.replace("VP ", "Via de Pedestre ")
    string = string.replace("AL ", "Alameda ")
    string = string.replace("MONS ", "Monsenhor ")
    string = string.replace("ESQ A ", "")
    if string[0:2]=='R ': string = "Rua "+" ".join(string.split(' ')[1:])
    return " ".join(string.split())

grouped = iptu.groupby(['NOME DE LOGRADOURO DO IMOVEL', 'NUMERO DO IMOVEL']).agg({'CODLOG DO IMOVEL': 'count', 'CEP DO IMOVEL': 'first', 'TIPO DE USO DO IMOVEL': 'count'}).reset_index()
grouped['NOME DE LOGRADOURO DO IMOVEL'] = grouped['NOME DE LOGRADOURO DO IMOVEL'].apply(formatLog)
grouped['NUMERO DO IMOVEL'] = grouped['NUMERO DO IMOVEL'].astype(int, errors="ignore").astype(str)
grouped['CEP DO IMOVEL'] = grouped['CEP DO IMOVEL'].astype(str)
grouped['ADDRESS'] = grouped['NOME DE LOGRADOURO DO IMOVEL'] + ", " + grouped['NUMERO DO IMOVEL'] + ", São Paulo - SP, " + grouped['CEP DO IMOVEL']
grouped = grouped.rename(columns={'CEP DO IMOVEL': 'CEP', 'NUMERO DO IMOVEL': 'NUMERO_LOG', 'NOME DE LOGRADOURO DO IMOVEL': 'NOME_LOG', 'CODLOG DO IMOVEL': 'CODLOG', 'TIPO DE USO DO IMOVEL': 'N_HOUSING'})
print(len(grouped), 'LEN GROUPED! SAVE NOW', grouped.N_HOUSING.sum(), len(iptu))

grouped.to_csv(f"../data/iptu/01_addresses___{YEAR}.csv", sep=',', index=False)
