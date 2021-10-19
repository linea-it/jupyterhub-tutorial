# -*- coding: utf-8 -*-
import collections
import os

import pandas as pd
from sqlalchemy import Date, MetaData, Table, cast, func, inspect
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import select, text

from db_postgresql import DBPostgresql


class DBBase():

    database = None
    engine = None

    # TODO: OS dados de coneção com o banco devem vir de outro lugar!
    available_databases = dict({
        "gavo": {
            "ENGINE": "postgresql_psycopg2",
            "HOST": "desdb4.linea.gov.br",
            "PORT": "5432",
            "USER": "untrustedprod",
            "PASSWORD": "untrusted",
            "DATABASE": "prod_gavo",
            # "HOST": "172.18.0.2",
            # "PORT": "5432",
            # "USER": "postgres",
            # "PASSWORD": "postgres",
            # "DATABASE": "tno_v2"
        }
    })

    def __init__(self, database="gavo"):

        self.__set_database(database)

    def __set_database(self, database):

        if database not in self.available_databases:
            raise Exception("Banco de dados não disponivel ainda")

        db_settings = self.available_databases[database]

        if db_settings["ENGINE"] == "postgresql_psycopg2":
            self.database = DBPostgresql(db_settings)

        # if db["ENGINE"] == "sqlite3":
        #     return DBSqlite(db)

        # if db_settings["ENGINE"] == "oracle":
        #     return DBOracle(db_settings)

    def get_engine(self):
        """Retorna uma instancia de engine para o database solicitado na Instancia da DBBase.
        https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Engine

        Returns:
            sqlalchemy.engine.Engine: uma instancia de Engine
        """

        if self.engine is None:

            self.engine = self.database.get_engine()

        return self.engine

    def get_table(self, tablename, schema=None):
        """Retona uma instancia de sqlalchemy.schema.Table que representa uma tabela no database.
        https://docs.sqlalchemy.org/en/14/core/metadata.html#sqlalchemy.schema.Table

        Args:
            tablename (str): Nome da tabela sem o schema.
            schema (str, optional): Schema onde a tabela se encontra. Defaults to None.

        Returns:
            sqlalchemy.schema.Table: instancia de Table representando a tabela solicitada.
        """
        engine = self.get_engine()
        tbl = Table(
            tablename, MetaData(engine), autoload=True, schema=schema)
        return tbl

    def execute(self, stm):
        """Executa a query usando con.execute, 
        recomendada para query de Delete, Update ou outras querys que não precisem de iteração com o resultado.
        OBS. esta query fecha o conexão logo após ser executada. 

        Args:
            stm (statement): Query a ser executada, pode ser escrita em SqlAlchemy ou string no caso de string ela sera convertida para TextClause.

        Returns:
            CursorResult: [description]
        """
        with self.get_engine().connect() as con:
            return con.execute(stm)

    def fetchall(self, stm):
        """Executa a query e retorna todos os resultados em uma lista.

        Args:
            stm (statement): Query a ser executada, pode ser escrita em SqlAlchemy ou string no caso de string ela sera convertida para TextClause.

        Returns:
            list: Lista com os resultado no formato original do SqlAlchemy LegacyRow.
        """
        # Conver Raw sql to Sql Alchemy TextClause
        stm = self.raw_sql_to_stm(stm)

        with self.get_engine().connect() as con:
            queryset = con.execute(stm).fetchall()
            return queryset

    def fetchall_dict(self, stm):
        """Executa a query e retorna todos os resultados em uma lista de Dicts.

        Args:
            stm (statement): Query a ser executada, pode ser escrita em SqlAlchemy ou string no caso de string ela sera convertida para TextClause.

        Returns:
            list: O resultado da query em uma lista de Dict({'col': 'value', ..., 'coln':'valuen'})
        """
        # Conver Raw sql to Sql Alchemy TextClause
        stm = self.raw_sql_to_stm(stm)

        with self.get_engine().connect() as con:
            queryset = con.execute(stm)

            rows = list()
            for row in queryset:
                rows.append(self.to_dict(row))

            return rows

    def fetchall_df(self, stm):
        """Executa a query usando o pandas e retorna um Dataframe com o resultado.

        Args:
            stm (statement): Query a ser executada, pode ser escrita em SqlAlchemy ou string no caso de string ela sera convertida para TextClause.

        Returns:
            Pandas.Dataframe: Dataframe com o resultado da query.
        """
        df = pd.read_sql(
            stm,
            con=self.get_engine()
        )

        return df

    def fetchone(self, stm):
        """Executa a query retorna a primeira linha do resultado

        Args:
            stm (statement): Query a ser executada, pode ser escrita em SqlAlchemy ou string no caso de string ela sera convertida para TextClause.

        Returns:
            sqlalchemy.engine.row.LegacyRow: Primeira linha do resultado da query.
        """

        # Conver Raw sql to Sql Alchemy TextClause
        stm = self.raw_sql_to_stm(stm)

        with self.get_engine().connect() as con:
            queryset = con.execute(stm).fetchone()
            return queryset

    def fetchone_dict(self, stm):
        """Executa a query retorna a primeira linha do resultado convertida em Dict

        Args:
            stm (statement): Query a ser executada, pode ser escrita em SqlAlchemy ou string no caso de string ela sera convertida para TextClause.

        Returns:
            dict: Primeira linha do resultado da query.
        """
        # Conver Raw sql to Sql Alchemy TextClause
        stm = self.raw_sql_to_stm(stm)

        with self.get_engine().connect() as con:
            queryset = con.execute(stm).fetchone()

            if queryset is not None:
                return self.to_dict(queryset)
            else:
                return None

    def fetch_scalar(self, stm):
        """Retornar o valor da primeira coluna na primeira linha do resultado da query
        util para querys de count por exemplo, ou quando se quer apenas um unico valor.

        Args:
            stm (statement): Query a ser executada, pode ser escrita em SqlAlchemy ou string no caso de string ela sera convertida para TextClause.

        Returns:
            any: Valor da primeira coluna na primeira linha.
        """
        # Conver Raw sql to Sql Alchemy TextClause
        stm = self.raw_sql_to_stm(stm)

        with self.get_engine().connect() as con:
            return con.execute(stm).scalar()

    def to_dict(self, row):
        """Converte uma linha de resultado do SQLAlchemy queryset para Dict

        Args:
            row (sqlalchemy.engine.row.LegacyRow): Row retornada pelo execute.

        Returns:
            dict : Row convertida para Dict {colname: value, colname2: value2 ...}
        """
        return dict(collections.OrderedDict(row))

    def raw_sql_to_stm(self, stm):
        """Converte uma string raw sql para SqlAlchemy TextClause

        Args:
            stm (str): Query SQL em string. ex: Select * from tablename...

        Returns:
            TextClause: TextClause representando uma string SQL.
        """
        if isinstance(stm, str):
            return text(stm)
        return stm

    def get_table_columns(self, tablename, schema=None):
        """Retorna os nomes das colunas de uma tabela.
            Args:
                tablename (string): Nome da tabela sem schema.
                schema (string): Nome do schema ou None quando nao houver.
            Returns:
                columns (list): Colunas disponiveis na tabela
        """
        insp = inspect(self.get_engine())
        return [value['name'] for value in insp.get_columns(tablename, schema)]

    def describe_table(self, tablename, schema=None):
        """Retorna o nome e o tipo das colunas de uma tabela.
            Args:
                tablename (string): Nome da tabela sem schema.
                schema (string): Nome do schema ou None quando nao houver.
            Returns:
                columns (list): Lista de colunas com seu tipo {"name": "", "type": ""}
        """
        cols = list()

        insp = inspect(self.get_engine())
        for c in insp.get_columns(tablename, schema):
            cols.append(dict({
                "name": c["name"],
                "type": c["type"]
            }))

        return cols


if __name__ == "__main__":

    try:
        print("Instanciando a DAO")
        dao = DBBase(database="gavo")

        print("Executando query de Teste")
        # Instancia sqlalchemy table
        #tbl = dao.get_table('des_ccd')
        tbl = dao.get_table("coadd_objects", schema="des_dr2")        
        # Select simples com limit
        stm = select(tbl.c).limit(10)
        # # Executa a query e retorna uma lista de dicts
        rows = dao.fetchall_dict(stm)
        # rows = dao.fetchall(stm)
        print(rows)
        # # Executa a query e retorna só o primeiro
        # first_row = dao.fetchone_dict(stm)
        # print(first_row)
        # rows = dao.fetchall(stm)
        # first_row = dao.fetchone(stm)
        # print(rows)

        # Executar uma RAW SQL
        # sql = "Select * from des_ccd limit 5"
        # rows = dao.fetchall(sql)
        # print(rows)
        # row = dao.fetchone(sql)
        # print(row)
        # first_column = dao.fetch_scalar(sql)
        # print(first_column)
        # Count com RAW SQL
        # sql = "Select count(*) from des_ccd limit 5"
        # count = dao.fetch_scalar(sql)
        # print(count)

        # # Lista de colunas de uma tabela
        # columns = dao.get_table_columns('des_ccd')
        # print(columns)

        # Lista de colunas com o tipo de uma tabela
        # columns = dao.describe_table('des_ccd')
        # print(columns)

    except Exception as e:
        print(e)
