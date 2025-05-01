import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def get_db_connection():
    return create_engine(os.getenv("DATABASE_URL"))

def create_table(engine, df):
    df.to_sql('temperature_logs', engine, if_exists='replace', index=False)

st.title("Upload de Arquivo CSV")
uploaded_file = st.file_uploader("Escolha o arquivo iot.csv", type="csv")

if uploaded_file is not None:
    # Ler o CSV
    df = pd.read_csv(uploaded_file)
    st.write("Estrutura do Dataset:")
    st.write(df.head())

    # Conectar ao banco de dados
    engine = get_db_connection()

    # Criar tabela no PostgreSQL
    create_table(engine, df)
    st.success("Dados enviados para o banco de dados.")

    # Ler dados do banco de dados
    query = "SELECT * FROM temperature_logs"
    data = pd.read_sql(query, engine)

    # Visualização dos dados com Plotly
    st.title("Visualização dos Dados")
    fig = px.line(data, x='noted_date', y='temp', title='Série Temporal de Temperaturas')
    st.plotly_chart(fig)
