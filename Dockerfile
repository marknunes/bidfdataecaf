FROM postgres:latest
ENV POSTGRES_USER=seu_usuario
ENV POSTGRES_PASSWORD=senha
ENV POSTGRES_DB=seu_banco_de_dados
EXPOSE 5432