from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import and_, or_, text


class DBPostgresql:
    def __init__(self, db_settings):
        self.db_settings = db_settings

    def get_db_uri(self):
        url = ("postgresql+psycopg2://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s") % {
            'username': self.db_settings['USER'],
            'password': self.db_settings['PASSWORD'],
            'host': self.db_settings['HOST'],
            'port': self.db_settings['PORT'],
            'database': self.db_settings['DATABASE']
        }
        return url

    def get_engine(self):
        return create_engine(
            self.get_db_uri(),
            poolclass=NullPool
        )

    def get_engine_name(self):
        return "postgresql_psycopg2"

    def get_dialect(self):
        return postgresql

    def accept_bulk_insert(self):
        return True

    def get_table_name(self, table):
        return table

    def get_schema_name(self, schema):
        return schema

    def get_condition_square(self, lowerleft, upperright, property_ra, property_dec):

        raul = float(lowerleft[0])
        decul = float(upperright[1])
        ul = "{%s, %s}" % (raul, decul)

        raur = float(upperright[0])
        decur = float(upperright[1])
        ur = "{%s, %s}" % (raur, decur)

        ralr = float(upperright[0])
        declr = float(lowerleft[1])
        lr = "{%s, %s}" % (ralr, declr)

        rall = float(lowerleft[0])
        decll = float(lowerleft[1])
        ll = "{%s, %s}" % (rall, decll)

        # ul, ur, lr, ll
        stm = "q3c_poly_query(ra, dec, '{ %s, %s, %s, %s}')" % (ul, ur, lr, ll)

        return and_(text(stm)).self_group()

    # def get_raw_sql_limit(self, offset, limit):
    #     return "OFFSET %s LIMIT %s" % (offset, limit)

    # def get_create_auto_increment_column(self, table, column_name, schema=None):
    #     raise Exception(
    #         "Method not implemented 'get_create_auto_increment_column'")

    # def get_create_auto_increment_column(self, table, column_name, schema=None):
    #     table_name = table
    #     if schema is not None and schema is not "":
    #         table_name = "%s.%s" % (schema, table)

    #     sql = list()
    #     sql.append("CREATE INDEX %(table)s_%(column)s_idx ON %(table)s USING btree (%(column)s);" % {
    #         "table": table_name,
    #         "column": column_name})

    #     return sql

    # def get_raw_sql_column_properties(self, table, schema=None):
    #     sql = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '%s'" % table
    #     if schema:
    #         sql += " AND table_schema = '%s'" % schema
    #     return sql

    # def get_raw_sql_table_rows(self, table, schema=None):
    #     if schema:
    #         sql = "SELECT reltuples FROM pg_class WHERE oid = '%s.%s'::regclass" % (
    #             schema, table)
    #     else:
    #         sql = "SELECT reltuples FROM pg_class WHERE relname='%s'" % table
    #     return sql

    # def get_raw_sql_size_table_bytes(self, table, schema=None):
    #     sql = "SELECT pg_total_relation_size(relid) as size_in_bytes  FROM pg_catalog.pg_statio_user_tables WHERE relname = '%s'" % table
    #     if schema:
    #         sql += " AND schemaname='%s'" % schema
    #     return sql

    # def get_raw_sql_number_columns(self, table, schema=None):
    #     where = "WHERE table_name = '%s'" % table
    #     if schema:
    #         where += " AND table_schema = '%s'" % schema
    #     sql = "SELECT count(*) as column_count FROM information_schema.columns %s GROUP by table_name order by column_count desc" % where
    #     return sql
