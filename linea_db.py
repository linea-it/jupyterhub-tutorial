import sqlalchemy
import pandas as pd
from astropy.table import Table

import collections
import os

import pandas as pd
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text


def get_table(query, pandas=True, user="untrustedprod", password="untrusted"):

    """ 
    Get data from database and return Pandas DataFrame. 
    
    Parameters
    ----------
    query: `string`
        SQL statement
    pandas: `boolean`
        if True, return Pandas DataFrame
        if False, return Astropy Table     
        
    Returns
    -------
    table : `pandas.DataFrame` or Astropy Table 

    """   
    address = f'postgresql://{user}:{password}@desdb4.linea.gov.br:5432/prod_gavo'
    engine = sqlalchemy.create_engine(address)
    conn = engine.connect()
    stm = sqlalchemy.sql.text(query)
    result = conn.execute(stm).fetchall() 
    #---------
    #print(type(result))
    column_names = [col.strip(',') for col in query.upper().split("FROM")[0].split()[1:]] 
    table = Table(rows=result, names=column_names)
    if pandas:
        table = table.to_pandas()
    
    return table



class MissingDBURIException(Exception):
    pass


class DBBase():

    engine = None

    def get_db_uri(self):

        # TODO: Pegar usuario e senha de uma forma segura.
        db_uri="postgresql+psycopg2://USER:PASS@HOST:PORT/DB_NAME"

        return db_uri

    def get_db_engine(self):

        if self.engine is None:

            self.engine = create_engine(
                self.get_db_uri(),
                poolclass=NullPool
            )

        return self.engine

    def get_table(self, tablename, schema=None):
        engine = self.get_db_engine()
        tbl = Table(
            tablename, MetaData(engine), autoload=True, schema=schema)
        return tbl

    def execute(self, stm):
        with self.engine.connect() as con:
            return con.execute(stm)

    def fetch_all_dict(self, stm, log=True):
        with self.engine.connect() as con:
            queryset = con.execute(stm)

            rows = list()
            for row in queryset:
                rows.append(self.to_dict(row))

            return rows

    def fetch_one_dict(self, stm):
        with self.engine.connect() as con:
            queryset = con.execute(stm).fetchone()

            if queryset is not None:
                return self.to_dict(queryset)
            else:
                return None

    def fetch_scalar(self, stm):
        with self.engine.connect() as con:
            return con.execute(stm).scalar()
        

    def to_dict(self, row):
        return dict(collections.OrderedDict(row))