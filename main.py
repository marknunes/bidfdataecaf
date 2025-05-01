import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def get_db_connection():
    return create_engine(os.getenv("DATABASE_URL"))


def create_table(engine, df):
    df.to_sql('temperature_logs', engine, if_exists='replace', index=False)


def execute_views(engine):
    with engine.connect() as conn:
        conn.execute(
            text("""
            CREATE OR REPLACE VIEW avg_temp_por_dia AS
            SELECT
                DATE(noted_date) AS dia,
                AVG(temp) AS temperatura_media    
            FROM
                temperature_logs
            GROUP BY
                DATE(noted_date);
        """))

        conn.execute(
            text("""
            CREATE OR REPLACE VIEW max_temp_por_device AS
            SELECT
                device_id,
                MAX(temp) AS temperatura_maxima
            FROM
                temperature_logs
            GROUP BY
                device_id;
        """))

        conn.execute(
            text("""
            CREATE OR REPLACE VIEW leitura_por_hora AS
            SELECT
                EXTRACT(HOUR FROM noted_date) AS hora,
                COUNT(*) AS numero_leituras
            FROM
                temperature_logs
            GROUP BY
                EXTRACT(HOUR FROM noted_date)
            ORDER BY
                hora;
        """))
    st.success("Views SQL criadas com sucesso.")


# Início da interface Streamlit
st.title("Análise de Temperaturas")

file_path = 'iot.csv'

# Verificar se o arquivo existe
if os.path.exists(file_path):
    st.info(f"Arquivo '{file_path}' encontrado. Carregando dados...")
    try:
        df = pd.read_csv(file_path)
        st.write("Dados carregados do arquivo:")
        st.write(df.head())

        # Conectar ao banco de dados
        engine = get_db_connection()

        # Criar tabela no PostgreSQL
        create_table(engine, df)
        st.success("Dados enviados para o banco de dados.")

        # Executar as views SQL
        execute_views(engine)

        # Ler dados do banco de dados (exemplo de uma view)
        query_avg_temp = "SELECT * FROM avg_temp_por_dia"
        df_avg_temp = pd.read_sql(query_avg_temp, engine)
        st.subheader("Média de Temperatura por Dia")
        st.write(df_avg_temp)
        fig_avg_temp = px.line(df_avg_temp,
                               x='dia',
                               y='temperatura_media',
                               title='Média de Temperatura Diária')
        st.plotly_chart(fig_avg_temp)

        # Você pode adicionar leituras e visualizações para as outras views aqui

    except Exception as e:
        st.error(f"Erro ao processar o arquivo '{file_path}': {e}")

else:
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
    if uploaded_file is not None:
        try:
            # Leitura do arquivo CSV carregado
            df = pd.read_csv(uploaded_file)
            st.write("Estrutura do Dataset Carregado:")
            st.write(df.head())

            # Conectar ao banco de dados
            engine = get_db_connection()

            # Criar tabela no PostgreSQL
            create_table(engine, df)
            st.success("Dados enviados para o banco de dados.")

            # Executar as views SQL
            execute_views(engine)

            # Ler dados do banco de dados (exemplo de uma view)
            query_avg_temp = "SELECT * FROM avg_temp_por_dia"
            df_avg_temp = pd.read_sql(query_avg_temp, engine)
            st.subheader("Média de Temperatura por Dia")
            st.write(df_avg_temp)
            fig_avg_temp = px.line(df_avg_temp,
                                   x='dia',
                                   y='temperatura_media',
                                   title='Média de Temperatura Diária')
            st.plotly_chart(fig_avg_temp)

            # Salvar o arquivo carregado para futuras execuções
            df.to_csv(file_path, index=False)
            st.info(f"Arquivo carregado e salvo como '{file_path}'.")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo CSV carregado: {e}")
