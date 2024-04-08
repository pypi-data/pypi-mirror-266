from __future__ import absolute_import
from __future__ import unicode_literals
from sqlalchemy import exc, pool, types
from sqlalchemy.engine import default
from sqlalchemy.sql import compiler
from sqlalchemy import inspect
import re
import logging
from sqlalchemy.sql import text

try:
    from sqlalchemy.sql.compiler import SQLCompiler
except ImportError:
    from sqlalchemy.sql.compiler import DefaultCompiler as SQLCompiler

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.ERROR)

_type_map = {
    'bit': types.BOOLEAN,
    'bigint': types.BIGINT,
    'binary': types.LargeBinary,
    'boolean': types.BOOLEAN,
    'date': types.DATE,
    'decimal': types.DECIMAL,
    'double': types.FLOAT,
    'int': types.INTEGER,
    'integer': types.INTEGER,
    'int64': types.INTEGER,
    'interval': types.Interval,
    'smallint': types.SMALLINT,
    'timestamp': types.TIMESTAMP,
    'time': types.TIME,
    'varchar': types.String,
    'character varying': types.String,
    'any': types.String,
    'map': types.UserDefinedType,
    'list': types.UserDefinedType,
    'float8': types.FLOAT,
    'float64': types.FLOAT,
    'json': types.JSON,
    'datetime': types.DateTime,
    'datetime64[ns]': types.DateTime,
    'datetime64[ms]': types.DateTime,
    'object': types.JSON
}


class ChipmunkDbCompiler_jdbc(compiler.SQLCompiler):

    def default_from(self):
        """Called when a ``SELECT`` statement has no froms,
        and no ``FROM`` clause is to be appended.
       Drill uses FROM values(1)
        """
        return " FROM (values(1))"

    def visit_char_length_func(self, fn, **kw):
        return 'length{}'.format(self.function_argspec(fn, **kw))

    def visit_table(self, table, asfrom=False, **kwargs):

        if asfrom:
            try:
                fixed_schema = ""
                if table.schema != "":
                    fixed_schema = ".".join(
                        ["`{i}`".format(i=i.replace('`', '')) for i in table.schema.split(".")])
                fixed_table = "{fixed_schema}.`{table_name}`".format(
                    fixed_schema=fixed_schema, table_name=table.name.replace(
                        "`", "")
                )
                return fixed_table
            except Exception as ex:
                logging.error(
                    "Error in DrillCompiler_sadrill.visit_table :: " + str(ex))

        else:
            return ""

    def visit_tablesample(self, tablesample, asfrom=False, **kw):
        logging.debug(tablesample)


class ChipmunkdbTypeCompiler_jdbc(compiler.GenericTypeCompiler):

    def visit_JSON(self, type_, **kwargs):
        # TODO might need to do more to fully enable json support
        # see https://gist.github.com/slitayem/c7b87d3f329caaa9794a408ad83ef0e5
        #
        # adding this class+method (plus adding json to `_type_map` above)
        # seems to be enough to avoid exceptions when trying to use tables
        # with json columns like these bugs in other sqlalchemy extensions/dialects:
        # - https://bitbucket.org/estin/sadisplay/issues/17/cannot-render-json-column-type
        #   (fixed by https://bitbucket.org/estin/sadisplay/commits/a49203105e8f4f1048cb28a64f21a2e789f04594)
        # - https://github.com/insightindustry/sqlathanor/issues/63
        #   (fixed by https://github.com/insightindustry/sqlathanor/commit/697bd455d4c38aa8a0888e118106dea429f06f9e)
        # - https://github.com/sqlalchemy-bot/test_sqlalchemy/issues/3549
        # - https://stackoverflow.com/questions/13484900/generate-sql-string-using-schema-createtable-fails-with-postgresql-array
        return 'JSON'


class ChipmunkIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = compiler.RESERVED_WORDS.copy()
    reserved_words.update(
        [
            'abs', 'all', 'allocate', 'allow', 'alter', 'and', 'any', 'are', 'array', 'as', 'asensitive',
            'asymmetric', 'at', 'atomic', 'authorization', 'avg', 'begin', 'between', 'bigint', 'binary',
            'bit', 'blob', 'boolean', 'both', 'by', 'call', 'called', 'cardinality', 'cascaded', 'case',
            'cast', 'ceil', 'ceiling', 'char', 'character', 'character_length', 'char_length', 'check',
            'clob', 'close', 'coalesce', 'collate', 'collect', 'column', 'commit', 'condition', 'connect',
            'constraint', 'convert', 'corr', 'corresponding', 'count', 'covar_pop', 'covar_samp', 'create',
            'cross', 'cube', 'cume_dist', 'current', 'current_catalog', 'current_date',
            'current_default_transform_group', 'current_path', 'current_role', 'current_schema', 'current_time',
            'current_timestamp', 'current_transform_group_for_type', 'current_user', 'cursor', 'cycle',
            'databases', 'date', 'day', 'deallocate', 'dec', 'decimal', 'declare', 'default', 'default_kw',
            'delete', 'dense_rank', 'deref', 'describe', 'deterministic', 'disallow', 'disconnect', 'distinct',
            'double', 'drop', 'dynamic', 'each', 'element', 'else', 'end', 'end_exec', 'escape', 'every', 'except',
            'exec', 'execute', 'exists', 'exp', 'explain', 'external', 'extract', 'false', 'fetch', 'files', 'filter',
            'first_value', 'float', 'floor', 'for', 'foreign', 'free', 'from', 'full', 'function', 'fusion', 'get',
            'global', 'grant', 'group', 'grouping', 'having', 'hold', 'hour', 'identity', 'if', 'import', 'in',
            'indicator', 'inner', 'inout', 'insensitive', 'insert', 'int', 'integer', 'intersect', 'intersection',
            'interval', 'into', 'is', 'jar', 'join', 'language', 'large', 'last_value', 'lateral', 'leading', 'left',
            'like', 'limit', 'ln', 'local', 'localtime', 'localtimestamp', 'lower', 'match', 'max', 'member', 'merge',
            'method', 'min', 'minute', 'mod', 'modifies', 'module', 'month', 'multiset', 'national', 'natural',
            'nchar', 'nclob', 'new', 'no', 'none', 'normalize', 'not', 'null', 'nullif', 'numeric', 'octet_length',
            'of', 'offset', 'old', 'on', 'only', 'open', 'or', 'order', 'out', 'outer', 'over', 'overlaps', 'overlay',
            'parameter', 'partition', 'percentile_cont', 'percentile_disc', 'percent_rank', 'position', 'power',
            'precision', 'prepare', 'primary', 'procedure', 'properties', 'range', 'rank', 'reads', 'real', 'recursive',
            'ref', 'references', 'referencing', 'regr_avgx', 'regr_avgy', 'regr_count', 'regr_intercept', 'regr_r2',
            'regr_slope', 'regr_sxx', 'regr_sxy', 'release', 'replace', 'result', 'return', 'returns', 'revoke',
            'right', 'rollback', 'rollup', 'row', 'rows', 'row_number', 'savepoint', 'schemas', 'scope', 'scroll',
            'search', 'second', 'select', 'sensitive', 'session_user', 'set', 'show', 'similar', 'smallint', 'some',
            'specific', 'specifictype', 'sql', 'sqlexception', 'sqlstate', 'sqlwarning', 'sqrt', 'start', 'static',
            'stddev_pop', 'stddev_samp', 'submultiset', 'substring', 'sum', 'symmetric', 'system', 'system_user',
            'table', 'tables', 'tablesample', 'then', 'time', 'timestamp', 'timezone_hour', 'timezone_minute',
            'tinyint', 'to', 'trailing', 'translate', 'translation', 'treat', 'trigger', 'trim', 'true', 'uescape',
            'union', 'unique', 'unknown', 'unnest', 'update', 'upper', 'use', 'user', 'using', 'value', 'values',
            'varbinary', 'varchar', 'varying', 'var_pop', 'var_samp', 'when', 'whenever', 'where', 'width_bucket',
            'window', 'with', 'within', 'without', 'year'
        ]
    )

    def __init__(self, dialect):
        super(ChipmunkIdentifierPreparer, self).__init__(
            dialect, initial_quote='`', final_quote='`')

    def format_drill_table(self, schema, isFile=True):
        formatted_schema = ""

        num_dots = schema.count(".")
        schema = schema.replace('`', '')

        # For a file, the last section will be the file extension
        schema_parts = schema.split('.')

        if isFile and num_dots == 3:
            # Case for File + Workspace
            plugin = schema_parts[0]
            workspace = schema_parts[1]
            table = schema_parts[2] + "." + schema_parts[3]
            formatted_schema = plugin + ".`" + workspace + "`.`" + table + "`"
        elif isFile and num_dots == 2:
            # Case for file and no workspace
            plugin = schema_parts[0]
            formatted_schema = plugin + "." + \
                schema_parts[1] + ".`" + schema_parts[2] + "`"
        else:
            # Case for non-file plugins or incomplete schema parts
            for part in schema_parts:
                quoted_part = "`" + part + "`"
                if len(formatted_schema) > 0:
                    formatted_schema += "." + quoted_part
                else:
                    formatted_schema = quoted_part

        return formatted_schema


class ChipmunkDialect(default.DefaultDialect):
    name = 'chipmunkdbapi'
    driver = 'rest'
    dbapi = ""
    preparer = ChipmunkIdentifierPreparer
    statement_compiler = ChipmunkDbCompiler_jdbc
    type_compiler = ChipmunkdbTypeCompiler_jdbc
    poolclass = pool.SingletonThreadPool
    supports_alter = False
    supports_pk_autoincrement = False
    supports_default_values = False
    supports_empty_insert = False
    supports_unicode_statements = True
    supports_unicode_binds = True
    returns_unicode_strings = True
    description_encoding = None
    supports_native_boolean = True

    def __init__(self, **kw):
        default.DefaultDialect.__init__(self, **kw)
        self.supported_extensions = []

    @classmethod
    def dbapi(cls):
        import chipmunkdb.chipmunkdbapi as module
        return module

    def create_connect_args(self, url, **kwargs):
        url_port = url.port or 8091
        qargs = {'host': url.host, 'port': url_port}

        try:
            db_parts = (url.database or 'chipmunkdb').split('/')
            db = ".".join(db_parts)

            # Save this for later use.
            self.host = url.host
            self.port = url_port
            self.username = url.username
            self.password = url.password
            self.db = db

            # Get Storage Plugin Info:
            if db_parts[0]:
                self.storage_plugin = db_parts[0]

            if len(db_parts) > 1:
                self.workspace = db_parts[1]

            qargs.update(url.query)
            qargs['db'] = db
            if url.username:
                qargs['drilluser'] = url.username
                qargs['drillpass'] = ""
                if url.password:
                    qargs['drillpass'] = url.password
        except Exception as ex:
            logging.error(
                "Error in DrillDialect_sadrill.create_connect_args :: " + str(ex))

        return [], qargs

    def do_rollback(self, dbapi_connection):
        # No transactions for Drill
        pass

    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        """Drill has no support for foreign keys.  Returns an empty list."""
        return []

    def get_indexes(self, connection, table_name, schema=None, **kw):
        """Drill has no support for indexes.  Returns an empty list. """
        return []

    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        """Drill has no support for primary keys.  Retunrs an empty list."""
        return []

    def get_schema_names(self, connection, **kw):

        # Get table information
        query = "SHOW DATABASES"

        curs = connection.execute(text(query))
        result = []
        try:
            for row in curs:
                #if row.SCHEMA_NAME != "cp.default" and row.SCHEMA_NAME != "INFORMATION_SCHEMA" and row.SCHEMA_NAME != "dfs.default":
                #    result.append(row.SCHEMA_NAME)
                result.append(row[0])
        except Exception as ex:
            logging.error(
                ("Error in DrillDialect_sadrill.get_schema_names :: ", str(ex)))

        return tuple(result)

    def get_selected_workspace(self):
        return self.workspace

    def get_selected_storage_plugin(self):
        return self.storage_plugin

    def get_table_names(self, connection, schema=None, **kw):
        if schema is None:
            schema = connection.engine.url.database
        # Clean up schema


        self.plugin_type = None
        self.quoted_schema = schema


        # Get table information
        query = "SHOW TABLES"

        curs = connection.execute(text(query))
        result = []
        try:
            for row in curs:
                #if row.SCHEMA_NAME != "cp.default" and row.SCHEMA_NAME != "INFORMATION_SCHEMA" and row.SCHEMA_NAME != "dfs.default":
                #    result.append(row.SCHEMA_NAME)
                result.append(row[0])
        except Exception as ex:
            logging.error(
                ("Error in Chipmunkdb_jdbc.get_schema_names :: ", str(ex)))

        return tuple(result)

    def get_view_names(self, connection, schema=None, **kw):

        return tuple([])

    def has_table(self, connection, table_name, schema=None):
        try:
            self.get_columns(connection, table_name, schema)
            return True
        except exc.NoSuchTableError:
            logging.error(
                "Error in DrillDialect_sadrill.has_table :: " + exc.NoSuchTableError)
            return False

    def _check_unicode_returns(self, connection, additional_tests=None):
        # requests gives back Unicode strings
        return True

    def _check_unicode_description(self, connection):
        # requests gives back Unicode strings
        return True

    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    def get_data_type(self, data_type):
        try:
            dt = _type_map[data_type]
        except:
            dt = types.UserDefinedType
        return dt

    def get_columns(self, connection, table_name, schema=None, **kw):
        result = []

        g = text("DESCRIBE " + schema+"."+table_name)

        column_metadata = connection.execute(g)

        # check if the column_metadata is empty
        if column_metadata.rowcount == 0:
            return result
        for row in column_metadata:
            result.append({
                'name': row[0],
                'type': self.get_data_type(row[1]),
                'nullable': row[2] == 'YES',
                'default': row[4],
                'extra': row[5]
            })
        return result

    def get_plugin_type(self, connection, plugin=None):
        if plugin is None:
            return

        return False