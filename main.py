import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Conexão com o banco de dados
def get_db_connection():
    return create_engine(os.getenv("DATABASE_URL"))

# Função para criar a tabela no banco de dados
def create_table(engine, df):
    df.to_sql('temperature_logs', engine, if_exists='replace', index=False)

# Função para criar as views no banco de dados
def create_sql_views(engine):
    with engine.connect() as conn:
        # View 1: Média de temperatura por dispositivo
        conn.execute("""
            CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
            SELECT device_id, AVG(temperature) as avg_temp
            FROM temperature_logs
            GROUP BY device_id;
        """)
        # View 2: Leituras por hora
        conn.execute("""
            CREATE OR REPLACE VIEW leituras_por_hora AS
            SELECT EXTRACT(HOUR FROM noted_date) AS hora, COUNT(*) AS contagem
            FROM temperature_logs
            GROUP BY EXTRACT(HOUR FROM noted_date);
        """)
        # View 3: Temperaturas máximas e mínimas por dia
        conn.execute("""
            CREATE OR REPLACE VIEW temp_max_min_por_dia AS
            SELECT DATE(noted_date) AS data, MAX(temperature) AS temp_max, MIN(temperature) AS temp_min
            FROM temperature_logs
            GROUP BY DATE(noted_date);
        """)

# Título do app
st.title("Upload de Arquivo CSV")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Escolha o arquivo iot.csv", type="csv")

if uploaded_file is not None:
    # Ler o CSV
    df = pd.read_csv(uploaded_file)

    # Verificar a estrutura do dataset
    if 'device_id' not in df.columns or 'temperature' not in df.columns or 'noted_date' not in df.columns:
        st.error("Arquivo CSV inválido. As colunas 'device_id', 'temperature' e 'noted_date' são obrigatórias.")
    else:
        st.write("Estrutura do Dataset:")
        st.write(df.head())

        # Conectar ao banco de dados
        engine = get_db_connection()

        # Criar tabela no PostgreSQL
        create_table(engine, df)
        st.success("Dados enviados para o banco de dados.")

        # Criar as views SQL
        create_sql_views(engine)

        # Ler dados do banco de dados e gerar gráficos
        st.title("Visualização dos Dados")

        # Gráfico 1: Média de temperatura por dispositivo
        df_avg_temp = pd.read_sql('SELECT * FROM avg_temp_por_dispositivo', engine)
        fig1 = px.bar(df_avg_temp, x='device_id', y='avg_temp', title='Média de Temperatura por Dispositivo')
        st.plotly_chart(fig1)

        # Gráfico 2: Leituras por hora do dia
        df_leituras_hora = pd.read_sql('SELECT * FROM leituras_por_hora', engine)
        fig2 = px.line(df_leituras_hora, x='hora', y='contagem', title='Leituras por Hora do Dia')
        st.plotly_chart(fig2)

        # Gráfico 3: Temperaturas máximas e mínimas por dia
        df_temp_max_min = pd.read_sql('SELECT * FROM temp_max_min_por_dia', engine)
        fig3 = px.line(df_temp_max_min, x='data', y=['temp_max', 'temp_min'], title='Temperaturas Máximas e Mínimas por Dia')
        st.plotly_chart(fig3)
