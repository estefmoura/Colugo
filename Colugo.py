import tkinter as tk
from tkinter import ttk  # Para Progressbar
from tkinter import messagebox
from tkinter import ttk, filedialog
import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
import numpy as np
from sklearn.tree import DecisionTreeRegressor
import os
import time
import mysql.connector
from mysql.connector import errorcode

# Consultas SQL
query_treino = """
    SELECT II.DESCRIPTION,
         II.STYLE_SUFFIX,
         II.MERCHANDIZING_GROUP,
         II.MERCHANDIZING_TYPE,
         II.EXT_DHL_CUST_REF1,
         II.EXT_DHL_CUST_REF2,
         II.EXT_DHL_CUST_REF3,
         II.EXT_DHL_CUST_REF4,
         II.EXT_DHL_CUST_REF5,
         II.EXT_DHL_CUST_REF6,
         II.EXT_DHL_CUST_REF7,
         II.EXT_DHL_CUST_REF8,
         II.EXT_DHL_CUST_REF9,
         II.EXT_DHL_CUST_REF10
            FROM default_item_master.ite_item II
        LEFT JOIN default_item_master.ite_item_package IP
        ON II.PK = IP.ITEM_PK
        AND II.PROFILE_ID = IP.PROFILE_ID
        AND IP.STANDARD_QUANTITY_UOM_ID = 'UNIT'
        AND IP.STANDARD = '1'
        LEFT JOIN default_item_master.ite_item_package IP2
    ON II.PK = IP2.ITEM_PK
        AND II.PROFILE_ID = IP2.PROFILE_ID
        AND IP2.STANDARD_QUANTITY_UOM_ID = 'LPN'
        AND IP2.STANDARD = '1'
        WHERE II.PROFILE_ID = 'BR_CID000068'
        AND (II.ITEM_ID IN 
    (SELECT inv.ITEM_ID
    FROM default_dcinventory.dci_inventory inv
    LEFT JOIN default_item_master.ite_item iit
        ON inv.ITEM_ID = iit.ITEM_ID
            AND iit.PROFILE_ID = 'BR_CID000068'
    LEFT JOIN default_item_master.ite_item_package IP
        ON iit.PK = IP.ITEM_PK
            AND IP.PROFILE_ID = 'BR_CID000068'
            AND IP.STANDARD_QUANTITY_UOM_ID = 'LPN'
            AND IP.STANDARD = '1'
    WHERE INV.ORG_ID = 'BR_5078'
            AND iit.MERCHANDIZING_TYPE IN ('01','02','03'))
            OR II.ITEM_ID IN 
        (SELECT ordl.item_id
        FROM default_dcorder.dco_order ord
        LEFT JOIN default_dcorder.dco_order_line ordl
            ON ord.org_id = ordl.org_id
                AND ord.origin_facility_id = ordl.facility_id
                AND ord.business_unit_id = ordl.business_unit_id
                AND ord.order_id = ordl.order_id
        WHERE ord.FACILITY_ID = 'BR_5078')) 
    """
query1_estoque = """
/*itens no manhattan*/
/*itens no manhattan*/
SELECT II.DESCRIPTION,
         II.STYLE_SUFFIX,
         II.MERCHANDIZING_GROUP,
         II.MERCHANDIZING_TYPE,
         II.EXT_DHL_CUST_REF1,
         II.EXT_DHL_CUST_REF2,
         II.EXT_DHL_CUST_REF3,
         II.EXT_DHL_CUST_REF4,
         II.EXT_DHL_CUST_REF5,
         II.EXT_DHL_CUST_REF6,
         II.EXT_DHL_CUST_REF7,
         II.EXT_DHL_CUST_REF8,
         II.EXT_DHL_CUST_REF9,
         II.EXT_DHL_CUST_REF10,
         SUM(inv.ON_HAND)
FROM default_item_master.ite_item II 
/*LEFT JOIN default_item_master.ite_item_package IP ON II.PK = IP.ITEM_PK AND II.PROFILE_ID = IP.PROFILE_ID AND IP.STANDARD_QUANTITY_UOM_ID = 'UNIT' AND IP.STANDARD = '1'*/
JOIN default_dcinventory.dci_inventory inv
    ON II.ITEM_ID = inv.ITEM_ID 
/*LEFT JOIN default_item_master.ite_item_package IP2 ON II.PK = IP2.ITEM_PK AND II.PROFILE_ID = IP2.PROFILE_ID AND IP2.STANDARD_QUANTITY_UOM_ID = 'LPN' AND IP2.STANDARD = '1'*/
WHERE II.PROFILE_ID = 'BR_CID000068'
GROUP BY  II.DESCRIPTION, II.STYLE_SUFFIX, II.MERCHANDIZING_GROUP, II.MERCHANDIZING_TYPE, II.EXT_DHL_CUST_REF1, II.EXT_DHL_CUST_REF2, II.EXT_DHL_CUST_REF3, II.EXT_DHL_CUST_REF4, II.EXT_DHL_CUST_REF5, II.EXT_DHL_CUST_REF6, II.EXT_DHL_CUST_REF7, II.EXT_DHL_CUST_REF8, II.EXT_DHL_CUST_REF9, II.EXT_DHL_CUST_REF10 

"""

query2_Pedidos = """
SELECT II.ITEM_ID ,
         II.SIZE_DESCRIPTION,
         II.DESCRIPTION,
         II.WEIGHT WEIGHT_UNIT,
         II.HEIGHT HEIGHT_UNIT,
         II.WIDTH WIDTH_UNIT,
         II.LENGTH LENGTH_UNIT,
         II.VOLUME VOLUME_UNIT,
         II.STYLE,
         II.STYLE_SUFFIX,
         II.COLOR_SUFFIX,
         II.MERCHANDIZING_DEPARTMENT_ID,
         II.MERCHANDIZING_GROUP,
         II.MERCHANDIZING_TYPE,
         II.SECOND_DIMENSION,
         II.PRODUCT_CLASS,
         II.PK ,
         II.CRITICAL_DIMENSION1 ,
         II.CRITICAL_DIMENSION2 ,
         II.CRITICAL_DIMENSION3 ,
         II.EXT_DHL_CUST_REF1,
         II.EXT_DHL_CUST_REF2,
         II.EXT_DHL_CUST_REF3,
         SUM(ordl.ORDERED_QUANTITY)
FROM default_item_master.ite_item II 
/*LEFT JOIN default_item_master.ite_item_package IP ON II.PK = IP.ITEM_PK AND II.PROFILE_ID = IP.PROFILE_ID AND IP.STANDARD_QUANTITY_UOM_ID = 'UNIT' AND IP.STANDARD = '1' LEFT JOIN default_item_master.ite_item_package IP2 ON II.PK = IP2.ITEM_PK AND II.PROFILE_ID = IP2.PROFILE_ID AND IP2.STANDARD_QUANTITY_UOM_ID = 'LPN' AND IP2.STANDARD = '1'*/
JOIN default_dcorder.dco_order_line ordl
    ON II.ITEM_ID = ordl.ITEM_ID
WHERE II.PROFILE_ID = 'BR_CID000068'
        AND ordl.STATUS IN ('READY', 'ALLOCATED', 'ALLOCATING', 'CREATED') 
    /* AND (II.ITEM_ID IN (SELECT inv.ITEM_ID FROM default_dcinventory.dci_inventory inv LEFT JOIN default_item_master.ite_item iit ON inv.ITEM_ID = iit.ITEM_ID AND iit.PROFILE_ID = 'BR_CID000068' LEFT JOIN default_item_master.ite_item_package IP ON iit.PK = IP.ITEM_PK AND IP.PROFILE_ID = 'BR_CID000068' AND IP.STANDARD_QUANTITY_UOM_ID = 'LPN' AND IP.STANDARD = '1' WHERE INV.ORG_ID = 'BR_5078' AND iit.MERCHANDIZING_TYPE IN ('01','02','03
        ')) OR II.ITEM_ID IN (SELECT ordl.item_id FROM default_dcorder.dco_order ord LEFT JOIN default_dcorder.dco_order_line ordl ON ord.org_id = ordl.org_id AND ord.origin_facility_id = ordl.facility_id AND ord.business_unit_id = ordl.business_unit_id AND ord.order_id = ordl.order_id WHERE ord.FACILITY_ID = 'BR_5078'))*/
    
GROUP BY  II.ITEM_ID , II.SIZE_DESCRIPTION, II.DESCRIPTION, II.WEIGHT, II.HEIGHT, II.WIDTH, II.LENGTH, II.VOLUME, II.STYLE, II.STYLE_SUFFIX, II.COLOR_SUFFIX, II.MERCHANDIZING_DEPARTMENT_ID, II.MERCHANDIZING_GROUP, II.MERCHANDIZING_TYPE, II.SECOND_DIMENSION, II.PRODUCT_CLASS, II.PK , II.CRITICAL_DIMENSION1 , II.CRITICAL_DIMENSION2 , II.CRITICAL_DIMENSION3 , II.EXT_DHL_CUST_REF3
"""
# Configuração do MySQL
config = {
    'user': 'SRV_THEVIEW_BREXT01',
    'password': 'Ba6ut72n38ughq!f',
    'host': '10.224.193.68',
    'port': 3306
}

# Função para salvar DataFrame em um arquivo CSV
def save_to_csv(df, filename):
    # Obtém o diretório de Downloads do usuário
    base_path = os.path.expanduser("~")
    # Define o caminho da pasta Downloads
    downloads_path = os.path.join(base_path, "Downloads")
    # Define o caminho completo do arquivo CSV
    file_path = os.path.join(downloads_path, filename)
    # Salva o DataFrame em um arquivo CSV
    df.to_csv(file_path, index=False)
    print(f"Arquivo salvo em: {file_path}")

# Nome do arquivo CSV
#filename1 = 'consulta_query.csv'

def rodar_query(query, arquivo):
    while True:
        try:
            # Conecta ao banco de dados
            conn = mysql.connector.connect(**config)
            print("Conexão estabelecida com sucesso!")
            print("Realizando consulta no banco de dados!.......")
            status_label.config(text="Consultando itens em pedido no MHT")
            progress_var.set(9)  # Define o progresso como completo (100%)
            root.update_idletasks()  # Atualiza a GUI
            # Executa a primeira consulta e armazena o resultado em um DataFrame
            df1 = pd.read_sql(query, conn)
            print("Consulta executada com sucesso!")
            progress_var.set(13)  # Define o progresso como completo (100%)
            root.update_idletasks()  # Atualiza a GUI            
            # Salva o DataFrame da primeira consulta em um arquivo CSV
            df1.to_csv(arquivo, index=False)
            progress_var.set(14)  # Define o progresso como completo (100%)
            root.update_idletasks()  # Atualiza a GUI
            #save_to_csv(df1, "itens2.csv")
                        # Fecha a conexão com o banco de dados

            conn.close()
            #Retornar DataFrame
    
            return df1

            print("Conexão encerrada com sucesso!")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Erro de acesso: Nome de usuário ou senha incorretos")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Erro: Banco de dados não existe")
            else:
                print(f"Erro ao conectar ao MySQL: {err}")

        except Exception as e:
            print(f"Ocorreu um erro: {e}")

        # Espera 10 segundos antes de repetir
        time.sleep(500)

def iniciar_consulta():
    progress_var.set(0)  # Resetar a barra de progresso
    root.update_idletasks()  # Atualiza a GUI

    # Simulação de progresso para demonstrar
    for i in range(1, 101):
        progress_var.set(i)
        time.sleep(0.05)  # Simula uma espera para cada atualização
        root.update_idletasks()  # Atualiza a GUI

def arvore_decisão(df_teste, df_treino,sText):
    def mean_absolute_percentage_error(y_true, y_pred):
        y_true, y_pred = np.array(y_true), np.array(y_pred)
        non_zero_mask = y_true != 0
        if not np.all(non_zero_mask):
            print("Encontrado valor zero ou nulo em y_true:")
            print(y_true[~non_zero_mask])
        return np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100
        status_label.config(text="Iniciando modelo de IA")
        progress_var.set(20)  # Define o progresso como completo (100%)
        root.update_idletasks()  # Atualiza a GUI
    def clean_text(text):
        # Remove tudo após "/"
        text = re.sub(r'/.*', '', text)
        # Remove "-" e outros caracteres especiais
        text = re.sub(r'[\W_]+', '', text)
        return text

  
    # Filtrar linhas onde HEIGHT_UNIT é maior que 0.1
    df_teste = df_teste[df_teste['HEIGHT_UNIT'] > 0.1]
    df_treino = df_treino[df_treino['HEIGHT_UNIT'] > 0.1]

    
    # Substituir valores nulos por uma string vazia ou uma string padrão
    df_teste = df_teste.dropna(subset=['DESCRIPTION'])
    df_treino = df_treino.dropna(subset=['DESCRIPTION'])

     # Converter todos os valores para string
    df_teste['DESCRIPTION'] = df_teste['DESCRIPTION'].astype(str)
    df_teste['MERCHANDIZING_TYPE'] = df_teste['MERCHANDIZING_TYPE'].astype(str)
    df_teste['EXT_DHL_CUST_REF1'] = df_teste['EXT_DHL_CUST_REF1'].astype(str)
    df_teste['EXT_DHL_CUST_REF2'] = df_teste['EXT_DHL_CUST_REF2'].astype(str)
    df_teste['EXT_DHL_CUST_REF3'] = df_teste['EXT_DHL_CUST_REF3'].astype(str)
    df_teste['MERCHANDIZING_GROUP'] = df_teste['MERCHANDIZING_GROUP'].astype(str)

    # Converter todos os valores para string
    df_treino['DESCRIPTION'] = df_treino['DESCRIPTION'].astype(str)
    df_treino['MERCHANDIZING_TYPE'] = df_treino['MERCHANDIZING_TYPE'].astype(str)
    df_treino['EXT_DHL_CUST_REF1'] = df_treino['EXT_DHL_CUST_REF1'].astype(str)
    df_treino['EXT_DHL_CUST_REF2'] = df_treino['EXT_DHL_CUST_REF2'].astype(str)
    df_treino['EXT_DHL_CUST_REF3'] = df_treino['EXT_DHL_CUST_REF3'].astype(str)
    df_treino['MERCHANDIZING_GROUP'] = df_treino['MERCHANDIZING_GROUP'].astype(str)

    # Criar uma nova coluna para a primeira palavra da descrição
    df_teste['Primeira_Palavra_Descricao'] = df_teste['DESCRIPTION'].apply(lambda x: x.split()[0])
    df_treino['Primeira_Palavra_Descricao'] = df_treino['DESCRIPTION'].apply(lambda x: x.split()[0])

    df_teste['Duas_Palavras_Apos_Primeira'] = df_teste['DESCRIPTION'].apply(
        lambda x: ' '.join(x.split()[1:3]) if len(x.split()) > 2 else '')

    df_treino['Duas_Palavras_Apos_Primeira'] = df_treino['DESCRIPTION'].apply(
        lambda x: ' '.join(x.split()[1:3]) if len(x.split()) > 2 else '')
    

    # Adicionar uma nova coluna com os três últimos dígitos de ITEM_ID
    df_teste['Tamanho'] = df_teste['ITEM_ID'].astype(str).str[-3:]
    df_teste['Volume'] = df_teste['VOLUME_UNIT']

    df_treino['Tamanho'] = df_treino['ITEM_ID'].astype(str).str[-3:]
    df_treino['Volume'] = df_treino['VOLUME_UNIT']

    # Definir features e alvo
    X_train = df_treino[['EXT_DHL_CUST_REF3', 'Tamanho','MERCHANDIZING_GROUP','MERCHANDIZING_TYPE','EXT_DHL_CUST_REF1','EXT_DHL_CUST_REF2']]
    y_train = df_treino['Volume']

    X_test = df_teste[['EXT_DHL_CUST_REF3', 'Tamanho','MERCHANDIZING_GROUP','MERCHANDIZING_TYPE','EXT_DHL_CUST_REF1','EXT_DHL_CUST_REF2']]
    y_test = df_teste['Volume']

    status_label.config(text="Treinando e testando o modelo")
    progress_var.set(25)  # Define o progresso como completo (100%)
    root.update_idletasks()  # Atualiza a GUI
 

    # Preprocessamento
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), ['EXT_DHL_CUST_REF3', 'Tamanho','MERCHANDIZING_GROUP','MERCHANDIZING_TYPE','EXT_DHL_CUST_REF1','EXT_DHL_CUST_REF2'])
        ])

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', DecisionTreeRegressor(random_state=42))
    ])
    progress_var.set(50)  # Define o progresso como completo (100%)
    root.update_idletasks()  # Atualiza a GUI

    print("Iniciando o treinamento...")
    # Treinamento do modelo
    pipeline.fit(X_train, y_train)
    print("Treinamento concluído!")
    
    progress_var.set(70)  # Define o progresso como completo (100%)
    root.update_idletasks()  # Atualiza a GUI
    # Previsões
    print("Iniciando predição...")
    y_pred = pipeline.predict(X_test)
    print("Predições concluídas!")
    status_label.config(text="Montando arquivo de resultados")
    progress_var.set(90)  # Define o progresso como completo (100%)
    root.update_idletasks()  # Atualiza a GUI
    # Avaliação do modelo
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')
    mape = mean_absolute_percentage_error(y_test, y_pred)
    print(f'MAPE: {mape:.2f}%')

    # Adicionar previsões e valores reais ao DataFrame de teste
    X_test_with_preds = X_test.copy()
    X_test_with_preds['Volume_Real'] = y_test.values
    X_test_with_preds['Volume_Predito'] = y_pred

    # Adicionar coluna 'index' para referência
    X_test_with_preds = X_test_with_preds.reset_index(drop=True)

    # Adicionar as colunas de informações adicionais
    df_with_info = df_teste[['ITEM_ID', sText, 'DESCRIPTION', 'HEIGHT_UNIT', 'WIDTH_UNIT', 'LENGTH_UNIT']]
    df_with_info = df_with_info.reset_index(drop=True)

    # Mesclar as informações adicionais com o DataFrame de previsões
    final_df = pd.concat([X_test_with_preds, df_with_info], axis=1)

    # Adicionar coluna com diferença percentual
    final_df['Diferenca_Percentual'] = ((final_df['Volume_Real'] - final_df['Volume_Predito']) / final_df['Volume_Predito']) 
    progress_var.set(100)  # Define o progresso como completo (100%)
    root.update_idletasks()  # Atualiza a GUI
    # Exportar para CSV com a nova coluna
    final_df.to_csv('c:/Colugo/resultados_completos.csv', index=False)

    if final_df is not None:
        status_label.config(text="Processo finalizado com sucesso!")
        root.withdraw() 
        mostrar_resultados(final_df)  # Mostra os resultados na nova tela
    else:
        status_label.config(text="Ocorreu um erro durante o processo.")

    print(f'Arquivo CSV com resultados exportado como "resultados_completos.csv" com coluna de diferença percentual adicionada.')


# Funções para os botões
def carregar_itens_pedidos():
    # Lógica para carregar a base de itens com pedidos
    # Exemplo de código que pode carregar e mostrar dados
    try:
        df_treino = pd.read_csv('c:/Colugo/itens.csv')
        #df_treino = rodar_query(query_treino, "itens_treino.csv")
        progress_var.set(5)  # Define o progresso como completo (100%)
        status_label.config(text="Base de treino lida")
        root.update_idletasks()  # Atualiza a GUI
        # MUDAR DEPOISSS
        df_teste = rodar_query(query2_Pedidos, "C:\Colugo\itens_teste.csv")

        progress_var.set(14)  # Define o progresso como completo (100%)
        status_label.config(text="Carregando base de treino")
        root.update_idletasks()  # Atualiza a GUI
        df_teste = pd.read_csv('c:/Colugo/itens_teste.csv')
        #df_teste = rodar_query(query2_Pedidos, "itens_teste.csv")
        progress_var.set(15)  # Define o progresso como completo (100%)
        status_label.config(text="Consulta do MHT finalizada")
        root.update_idletasks()  # Atualiza a GUI
        #df_teste = pd.read_csv('itens2.csv')
        arvore_decisão(df_teste,df_treino,'SUM(ordl.ORDERED_QUANTITY)')
        messagebox.showinfo("Carregado", "Itens com Pedidos carregados com sucesso!")
        # Aqui você pode atualizar a base de dados que está sendo usada
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")

def carregar_itens_estoque():
    # Lógica para carregar a base de itens do estoque
    try:
        df = pd.read_csv('c:/itens.csv')
        df_treino = pd.read_csv('itens.csv')
        df_teste = rodar_query(query1_estoque)
        arvore_decisão(df_teste,df_treino)
        messagebox.showinfo("Carregado", "Itens do Estoque carregados com sucesso!")
        # Aqui você pode atualizar a base de dados que está sendo usada
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")

def carregar_itens_sem_cadastro():
    # Lógica para carregar a base de itens sem cadastro
    try:
        df = pd.read_csv('itens.csv')
        arvore_decisão(df,df)
        messagebox.showinfo("Carregado", "Itens sem Cadastro carregados com sucesso!")
        # Aqui você pode atualizar a base de dados que está sendo usada
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")

        # Função para baixar o relatório
def baixar_relatorio(df):
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Sucesso", f"Relatório salvo em: {file_path}")

# Função para mostrar os resultados em uma nova tela
def mostrar_resultados(df):
     # Cria uma nova janela
    results_window = tk.Toplevel()
    results_window.title("Resultados da Consulta")

    # Cria uma tabela para exibir os resultados
    tree = ttk.Treeview(results_window, columns=list(df.columns), show='headings')
    tree.pack(expand=True, fill='both')

    # Configura as colunas
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')

    # Insere os dados na tabela
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Botão para baixar o relatório
    download_button = tk.Button(results_window, text="Baixar Relatório", command=lambda: baixar_relatorio(df))
    download_button.pack(pady=10)


# Criar a janela principal
root = tk.Tk()
root.title("Colugo")
root.geometry("400x200")

# Variável da barra de progresso
progress_var = tk.DoubleVar()

# Adiciona a barra de progresso à janela
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(pady=20)

status_label = tk.Label(root, text="Status: Aguardando...", wraplength=300)
status_label.pack(pady=10)

# Criar os botões
btn_itens_pedidos = tk.Button(root, text="Rodar Machine Learning", command=carregar_itens_pedidos)
btn_itens_pedidos.pack(pady=10)

# Iniciar o loop principal da interface
root.mainloop()
