import os
import json
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt  # Para visualização, se necessário


pasta_base = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/ARQUIVOS'
pasta_json = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/JSONS'
pasta_destino = 'D:/DOUTORADO_RENATO/DADOS/QUEIJO/ARQUIVOS/PARQUET'
dias = ["08_01_2025"]
rodadas_por_dia = {
    "08_01_2025": ["RODADA_1", "RODADA_2"]
}
samples = ["21104_A1", "21104_A2", "21104_A3", "21104_A4", "21104_A5"]


franjas = {}

for dia in dias:
    franjas[dia] = {}
    for sample in samples:
        franjas[dia][sample] = {}
        for rodada in rodadas_por_dia[dia]:
            nome_arquivo_json = f"franjas_{dia}_{sample}_{rodada}.json"
            caminho_json = os.path.join(pasta_json, nome_arquivo_json)
            # Carrega o arquivo JSON
            with open(caminho_json, 'r') as infile:
                dados_completos = json.load(infile)
                
                franjas[dia][sample][rodada] = [vetor[1000:] for vetor in dados_completos]



pca = PCA(n_components=2)

PC = {}
for dia in dias:
    PC[dia] = {}
    for sample in samples:
        PC[dia][sample] = {}
        for rodada in rodadas_por_dia[dia]: 
            PC[dia][sample][rodada] = pca.fit_transform(franjas[dia][sample][rodada])


tamanhos_por_dia = {"05_09_2024": 50, "06_09_2024": 100}  # Tamanho dos pontos para cada dia
formatos_por_rodada = {"RODADA_1": 'o', "RODADA_2": 's', "RODADA_3": 'D', "RODADA_4": '^'}  # Formatos dos pontos para cada rodada
cores_por_amostra = ["red", "blue", "green", "purple", "orange", "cyan"]  # Cores para diferenciar amostras

# Inicia a figura para a plotagem
plt.figure(figsize=(12, 10))

for dia, samples_data in PC.items():
    tamanho = tamanhos_por_dia.get(dia, 30)

    for sample_idx, (sample, rodadas_data) in enumerate(samples_data.items()):
        cor = cores_por_amostra[sample_idx % len(cores_por_amostra)] 
        
        for rodada, pc_values in rodadas_data.items():
            if pc_values.size > 0:
                formato = formatos_por_rodada.get(rodada, 'o')
                plt.scatter(
                    pc_values[:, 0], 
                    pc_values[:, 1], 
                    label=f"{dia} - {sample} - {rodada}", 
                    color=cor,
                    marker=formato, 
                    s=tamanho
                )

# Configurações do gráfico
plt.title("Componentes Principais (PCA) das Franjas - Todos os Dias e Rodadas")
plt.xlabel("Componente Principal 1")
plt.ylabel("Componente Principal 2")
plt.legend(loc="best", bbox_to_anchor=(1.05, 1), borderaxespad=0.)
plt.grid(True)
plt.tight_layout()
plt.show()