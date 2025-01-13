
#!pip install process_spectra

import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pyarrow.parquet as pq

from scipy.signal import find_peaks, savgol_filter
from scipy.interpolate import interp1d
from sklearn.decomposition import PCA
from process_spectra.funcs import get_approximate_valley

def ler_multiplos_txt(diretorio,lambda_min=1400,lambda_max=1650):
    dfs = []  # Lista para armazenar os DataFrames de cada arquivo
    
    for arquivo in os.listdir(diretorio):
        if arquivo.endswith(".txt"):
            caminho_arquivo = os.path.join(diretorio, arquivo)
            df = pd.read_csv(caminho_arquivo, sep=';')  # Lê cada arquivo individualmente
            df = df.rename(columns={df.columns[0]: 'Wavelength', df.columns[1]: 'Level'}) #Nomeia as coluns
            df = df[(df.Wavelength > lambda_min) & (df.Wavelength < lambda_max)]
            dfs.append(df)  # Adiciona o DataFrame à lista
    
    # Combina todos os DataFrames em um único DataFrame
    #resultado = pd.concat(dfs, ignore_index=True)
    
    #return resultado
    return dfs

def plotar_dfs(dataframes):
    # Configurações de plotagem
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Loop para plotar cada DataFrame
    for i, df in enumerate(dataframes):
        ax.plot(df['Wavelength'], df['Level'])
    
    # Configurações do gráfico
    ax.set_xlabel('Wavelength', fontsize=12)
    ax.set_ylabel('Level', fontsize=12)
    ax.set_title('Plot de múltiplos DataFrames', fontsize=14)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    
    # Ajuste do estilo dos eixos
    ax.tick_params(axis='both', which='both', labelsize=10)
    
    # Exibir o gráfico
    plt.tight_layout()
    plt.show()
    
#Analises alterando as franjas de visibilidade
def get_mean(level):
    wind = len(level)/1.1
    wind = int(np.floor(wind))
    wind = wind + wind%2 + 1
    return savgol_filter(level, wind, 2)

def get_fringe(level):
    fringe = level-get_mean(level)
    fringe = savgol_filter(fringe, 11, 2)
    return fringe

def varre_dados_plot(dados_amostra,color='r'):
    Franjas_media = []
    for i, x in enumerate(dados_amostra):
        wl = dados_amostra[i].Wavelength
        level = dados_amostra[i].Level
        x_m = get_fringe(level)
        plt.plot(wl, x_m, color=color)
        Franjas_media.append(x_m)
    Franjas_media = np.array(Franjas_media)
        
def varre_dados(dados_amostra):
    '''
    Realiza a mesma coisa que a função acima, mas não plota
    '''
    Franjas_media = []
    for i, x in enumerate(dados_amostra):
        wl = dados_amostra[i].Wavelength
        level = dados_amostra[i].Level
        x_m = get_fringe(level)
        Franjas_media.append(x_m)
    Franjas_media = np.array(Franjas_media)
    return(Franjas_media)

def save_list_to_json(data, filename):
    '''
    Salva os arquivos processados em arquivos .json
    '''
    if hasattr(data, "to_dict"):
        data_dict = {"data": data.to_dict(orient="records")}
    else:
        data_dict = {"data": data}

    with open(filename, "w") as f:
        json.dump(data_dict, f)
    print(f"Arquivo JSON '{filename}' salvo com sucesso.")
    
def load_json_file(file_path):
    '''
    Carrega o arquivo json processado em forma de dicionário
    '''
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def dict_to_vector(dictionary):
    '''
    Transforma o dicionário para o formato do vetor processado 
    '''
    vector = np.array(list(dictionary.values()))
    vector = np.squeeze(vector)
    return vector

def salvar_espectros(lista_dataframes, nome_arquivo, pasta_destino):
    '''
    Salva a lista de DataFrames processados em um arquivo JSON.

    Parâmetros:
    - lista_dataframes: Lista de DataFrames a serem salvos.
    - nome_arquivo: Nome do arquivo JSON (com extensão .json).
    - pasta_destino: Caminho da pasta onde o arquivo será salvo.
    '''

    # Cria a pasta de destino caso não exista
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Cria o caminho completo do arquivo
    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

    # Converte a lista de DataFrames em uma lista de dicionários
    lista_dicionarios = [df.to_dict(orient='records') for df in lista_dataframes]

    # Salva a lista de dicionários em um arquivo JSON
    with open(caminho_arquivo, 'w') as outfile:
        json.dump(lista_dicionarios, outfile, indent=4)
    
    print(f"Arquivo JSON salvo com sucesso em: {caminho_arquivo}")
    
def list_dict_to_list_df(list_dict):
    '''
    Transforma uma lista de dicionarios em uma lista de vetores
    Usada para pegar arquivos JSON de multiplos espectros do OSA thorlabs e converter para o formato comum
    '''
    lista_dataframes = []
    for dicionario in list_dict:
        df = pd.DataFrame.from_dict(dicionario)
        lista_dataframes.append(df)
    return(lista_dataframes)

def cria_franjas(specs_experimento):
    '''
    Utiliza a função varre dados para todos os espectros do experimento de uma vez
    É necessario uma lista contendo as listas de DFs de cada amostra
    EX: specs_dia_2 = [spec_1_dia_2,spec_2_dia_2,spec_3_dia_2,spec_4_dia_2,spec_5_dia_2]
    '''
    franjas = []  
    len_franjas = []  
    for spec in specs_experimento:
        franjas_spec = np.array(varre_dados(spec))
        len_spec = (len(franjas_spec))
        len_franjas.append(len_spec)
        franjas.extend(franjas_spec)
    return np.array(franjas), len_franjas

def calcular_wl_res_list(dados_amostra):
    # Salva a saída padrão em uma variável temporária
    stdout_temp = sys.stdout

    # Redireciona a saída padrão para o nulo
    sys.stdout = open(os.devnull, 'w')

    # Loop para processar os DataFrames sem exibir a saída
    wl_res_list = []
    for df in dados_amostra:
        spec = np.array([df['Wavelength'].values, df['Level'].values])
        spec, info = get_approximate_valley(spec.T, {}, prominence=0.5)
        i = info['best_index']
        wl_res = info[f'resonant_wl_{i}']
        wl_res_list.append(wl_res)
    # Restaura a saída padrão
    sys.stdout = stdout_temp

    return wl_res_list

# Encontrar a PDF do vetor
def find_pdf(data):
    unique_values, counts = np.unique(data, return_counts=True)
    pdf = counts / np.sum(counts)
    return unique_values, pdf

# Plotar o histograma
def plot_histogram(data, ax=0):
    plt.hist(data, bins='auto', alpha=0.7, rwidth=0.85, color='r')
    plt.xlabel('Valores')
    plt.ylabel('Frequência')
    plt.title('Histograma')
    plt.grid(True)
    plt.show()

def save_to_parquet(data, dia, sample, rodada, pasta_destino):
    # Cria a pasta de destino caso não exista
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Define o nome do arquivo usando o padrão solicitado
    nome_arquivo = f"dados_{dia}_{sample}_{rodada}.parquet"
    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
    
    # Converte a lista para um DataFrame, caso ainda não seja
    if isinstance(data, list):
        data = pd.DataFrame(data)
    
    try:
        # Salva o DataFrame como arquivo Parquet
        data.to_parquet(caminho_arquivo, engine='pyarrow')
        print(f"Arquivo Parquet salvo com sucesso em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo {caminho_arquivo}: {e}")

def save_to_json(data, nome_arquivo, pasta_destino):
    # Cria a pasta de destino caso não exista
    os.makedirs(pasta_destino, exist_ok=True)
    
    caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
    
    # Converte DataFrame para uma lista de dicionários caso seja um DataFrame
    if isinstance(data, pd.DataFrame):
        data = data.to_dict(orient="records")
    
    try:
        # Salva a estrutura em JSON
        with open(caminho_arquivo, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Arquivo JSON salvo com sucesso em: {caminho_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo {caminho_arquivo}: {e}")