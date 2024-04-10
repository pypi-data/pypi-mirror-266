from __future__ import annotations

import concurrent.futures
import contextlib
import functools
import os
import queue
import threading
from typing import TYPE_CHECKING, Any, Callable, Mapping, NewType, Optional, Sequence, cast

import orjson
import packaging.version
import pyarrow as pa

from chalk.clogging import chalk_logger
from chalk.features import Feature
from chalk.features._encoding.converter import FeatureConverter
from chalk.integrations.named import load_integration_variable
from chalk.sql._internal.query_execution_parameters import QueryExecutionParameters
from chalk.sql._internal.sql_source import BaseSQLSource, SQLSourceKind, validate_dtypes_for_efficient_execution
from chalk.sql.finalized_query import FinalizedChalkQuery
from chalk.utils.df_utils import is_list_like, pa_array_to_pl_series
from chalk.utils.missing_dependency import missing_dependency_exception
from chalk.utils.threading import DEFAULT_IO_EXECUTOR, MultiSemaphore

if TYPE_CHECKING:
    from snowflake.connector.result_batch import ResultBatch
    from sqlalchemy.engine import Connection
    from sqlalchemy.engine.url import URL
    from sqlalchemy.sql.ddl import CreateTable, DropTable
    from sqlalchemy.sql.schema import Table


try:
    import sqlalchemy as sa
except ImportError:
    sa = None

if sa is None:
    _supported_sqlalchemy_types_for_pa_querying = ()
else:
    _supported_sqlalchemy_types_for_pa_querying = (
        sa.BigInteger,
        sa.Boolean,
        sa.BINARY,
        sa.BLOB,
        sa.LargeBinary,
        sa.Float,
        sa.Integer,
        sa.Time,
        sa.String,
        sa.Text,
        sa.VARBINARY,
        sa.DateTime,
        sa.Date,
        sa.SmallInteger,
        sa.BIGINT,
        sa.BOOLEAN,
        sa.CHAR,
        sa.DATETIME,
        sa.FLOAT,
        sa.INTEGER,
        sa.SMALLINT,
        sa.TEXT,
        sa.TIMESTAMP,
        sa.VARCHAR,
    )


@functools.lru_cache(None)
def _has_new_fetch_arrow_all():
    # The api for fetch arrow all changed in v3.7.0 to include force_return_table
    # See https://github.com/snowflakedb/snowflake-connector-python/blob/3cced62f2d31b84299b544222c836a275a6d45a2/src/snowflake/connector/cursor.py#L1344
    import snowflake.connector

    return packaging.version.parse(snowflake.connector.__version__) >= packaging.version.parse("3.7.0")


_WorkerId = NewType("_WorkerId", int)


class SnowflakeSourceImpl(BaseSQLSource):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        account_identifier: Optional[str] = None,
        warehouse: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        db: Optional[str] = None,
        schema: Optional[str] = None,
        role: Optional[str] = None,
        engine_args: Optional[dict[str, Any]] = None,
        executor: Optional[concurrent.futures.ThreadPoolExecutor] = None,
    ):
        try:
            import snowflake.connector  # noqa
            import snowflake.sqlalchemy  # noqa
        except ModuleNotFoundError:
            raise missing_dependency_exception("chalkpy[snowflake]")
        del snowflake  # unused
        if engine_args is None:
            engine_args = {}
        engine_args.setdefault("pool_size", 20)
        engine_args.setdefault("max_overflow", 60)
        engine_args.setdefault(
            "connect_args",
            {
                "client_prefetch_threads": min((os.cpu_count() or 1) * 2, 32),
                "client_session_keep_alive": True,
                "application_name": "chalkai_featurepipelines",
                "application": "chalkai_featurepipelines",
            },
        )

        self.account_identifier = account_identifier or load_integration_variable(
            integration_name=name, name="SNOWFLAKE_ACCOUNT_ID"
        )
        self.warehouse = warehouse or load_integration_variable(integration_name=name, name="SNOWFLAKE_WAREHOUSE")
        self.user = user or load_integration_variable(integration_name=name, name="SNOWFLAKE_USER")
        self.password = password or load_integration_variable(integration_name=name, name="SNOWFLAKE_PASSWORD")
        self.db = db or load_integration_variable(integration_name=name, name="SNOWFLAKE_DATABASE")
        self.schema = schema or load_integration_variable(integration_name=name, name="SNOWFLAKE_SCHEMA")
        self.role = role or load_integration_variable(integration_name=name, name="SNOWFLAKE_ROLE")
        self.executor = executor or DEFAULT_IO_EXECUTOR
        BaseSQLSource.__init__(self, name=name, engine_args=engine_args, async_engine_args={})

    kind = SQLSourceKind.snowflake

    def get_sqlglot_dialect(self) -> str | None:
        return "snowflake"

    def local_engine_url(self) -> URL:
        from sqlalchemy.engine.url import URL

        query = {
            k: v
            for k, v in (
                {
                    "database": self.db,
                    "schema": self.schema,
                    "warehouse": self.warehouse,
                    "role": self.role,
                }
            ).items()
            if v is not None
        }
        return URL.create(
            drivername="snowflake",
            username=self.user,
            password=self.password,
            host=self.account_identifier,
            query=query,
        )

    def convert_db_types(self, v: Any, converter: FeatureConverter):
        """
        Overload this if a given DB type needs custom type conversion
        """
        if (is_list_like(converter.pyarrow_dtype) or pa.types.is_struct(converter.pyarrow_dtype)) and isinstance(
            v, (str, bytes)
        ):
            # Need to json-decode these types
            v = orjson.loads(v)
        return converter.from_rich_to_primitive(v, missing_value_strategy="default_or_allow")

    @contextlib.contextmanager
    def _create_temp_table(
        self,
        create_temp_table: CreateTable,
        temp_table: Table,
        drop_temp_table: DropTable,
        connection: Connection,
        temp_value: pa.Table,
    ):
        from snowflake.connector import pandas_tools
        from snowflake.connector.connection import SnowflakeConnection

        snowflake_cnx = cast(SnowflakeConnection, connection.connection.dbapi_connection)
        with snowflake_cnx.cursor() as cursor:
            chalk_logger.info(f"Creating temporary table {temp_table.name} in Snowflake.")
            cursor.execute(create_temp_table.compile(dialect=self.get_sqlalchemy_dialect()).string)
            try:
                pandas_tools.write_pandas(
                    cursor.connection,
                    temp_value.to_pandas(),
                    str(temp_table.name),
                )
                yield
            finally:
                # "temp table", to snowflake, means that it belongs to the session. However, we keep using the same Snowflake session
                chalk_logger.info(f"Dropping temporary table {temp_table.name} in Snowflake.")
                cursor.execute(drop_temp_table.compile(dialect=self.get_sqlalchemy_dialect()).string)

    def _postprocess_table(self, features: Mapping[str, Feature], tbl: pa.Table):
        columns: list[pa.Array] = []
        column_names: list[str] = []

        for col_name, feature in features.items():
            column = tbl[col_name]
            expected_type = feature.converter.pyarrow_dtype
            actual_type = tbl.schema.field(col_name).type
            if pa.types.is_list(expected_type) or pa.types.is_large_list(expected_type):
                if pa.types.is_string(actual_type) or pa.types.is_large_string(actual_type):
                    series = pa_array_to_pl_series(tbl[col_name])
                    column = series.str.json_extract(feature.converter.polars_dtype).to_arrow().cast(expected_type)
            if actual_type != expected_type:
                column = column.cast(expected_type)
            if isinstance(column, pa.ChunkedArray):
                column = column.combine_chunks()
            columns.append(column)
            column_names.append(feature.root_fqn)

        chalk_logger.info(f"Received a PyArrow table from Snowflake with {len(tbl)} rows; {tbl.nbytes=}")
        return pa.RecordBatch.from_arrays(arrays=columns, names=column_names)

    @staticmethod
    def _download_worker(
        result_batches: list[ResultBatch],
        lock: threading.Lock,
        sem: MultiSemaphore | None,
        pa_table_queue: queue.Queue[tuple[pa.Table, int] | _WorkerId],
        worker_idx: _WorkerId,
    ):
        try:
            while True:
                with lock:
                    if len(result_batches) == 0:
                        return
                    x = result_batches.pop()
                weight = x.uncompressed_size
                as_arrow = None
                if weight is None:
                    # This is possible if the chunk is "local", which I think snowflake does for small result batches
                    as_arrow = x.to_arrow()
                    weight = as_arrow.nbytes
                if sem:
                    if weight > sem.initial_value:
                        # If the file is larger than the maximum size, we'll truncate it, so this file will be the only one being downloaded
                        weight = sem.initial_value
                    if weight > 0:
                        # No need to acquire the semaphore for empty tables
                        if not sem.acquire(weight):
                            raise RuntimeError("Failed to acquire semaphore for snowflake download")
                if as_arrow is None:
                    as_arrow = x.to_arrow()
                pa_table_queue.put((as_arrow, weight))
        finally:
            # At the end, putting the worker id to signal that this worker is done
            pa_table_queue.put(worker_idx)

    def _execute_query_efficient(
        self,
        finalized_query: FinalizedChalkQuery,
        columns_to_features: Callable[[Sequence[str]], Mapping[str, Feature]],
        connection: Optional[Connection],
        query_execution_parameters: QueryExecutionParameters,
    ):
        # these imports are safe because the only way we end up here is if we have a valid SnowflakeSource constructed,
        # which already gates this import
        import snowflake.connector
        from sqlalchemy.sql import Select

        if isinstance(finalized_query.query, Select):
            validate_dtypes_for_efficient_execution(finalized_query.query, _supported_sqlalchemy_types_for_pa_querying)

        with (
            self.get_engine().connect() if connection is None else contextlib.nullcontext(connection)
        ) as sqlalchemy_cnx:
            con = cast(snowflake.connector.SnowflakeConnection, sqlalchemy_cnx.connection.dbapi_connection)
            chalk_logger.info("Established connection with Snowflake")
            sql, positional_params, named_params = self.compile_query(finalized_query)
            assert len(positional_params) == 0, "using named param style"
            with contextlib.ExitStack() as exit_stack:
                for (
                    _,
                    temp_value,
                    create_temp_table,
                    temp_table,
                    drop_temp_table,
                ) in finalized_query.temp_tables.values():
                    exit_stack.enter_context(
                        self._create_temp_table(
                            create_temp_table, temp_table, drop_temp_table, sqlalchemy_cnx, temp_value
                        )
                    )
                with con.cursor() as cursor:
                    chalk_logger.info(f"Compiled query: {repr(sql)}")
                    res = cursor.execute(sql, named_params)
                    chalk_logger.info("Executed Snowflake query. Fetching results.")
                    assert res is not None

                    chalk_logger.info("Fetching arrow tables from Snowflake.")
                    result_batches = cursor.get_result_batches()
                    assert result_batches is not None
                    yielded = False
                    max_weight = query_execution_parameters.max_prefetch_size_bytes
                    if max_weight <= 0:
                        max_weight = None
                    lock = threading.Lock()
                    pa_table_queue: queue.Queue[tuple[pa.Table, int] | _WorkerId] = queue.Queue()
                    sem = None if max_weight is None else MultiSemaphore(max_weight)
                    assert query_execution_parameters.num_client_prefetch_threads >= 1
                    futures = {
                        _WorkerId(i): self.executor.submit(
                            self._download_worker, result_batches, lock, sem, pa_table_queue, _WorkerId(i)
                        )
                        for i in range(query_execution_parameters.num_client_prefetch_threads)
                    }
                    schema: pa.Schema | None = None
                    while len(futures) > 0:
                        x = pa_table_queue.get()
                        if isinstance(x, int):
                            # It's a _WorkerId, meaning that this download worker is done
                            # We'll pop this worker from the futures list, and then await the result
                            # This will raise if the download worker crashed, which is what we want, or be a no-op if the download worker succeeded
                            futures.pop(x).result()
                            continue
                        tbl, weight = x
                        if schema is None:
                            schema = tbl.schema
                        try:
                            if len(tbl) == 0:
                                continue
                            assert isinstance(tbl, pa.Table)
                            features = columns_to_features(tbl.schema.names)
                            yield self._postprocess_table(features, tbl)
                            yielded = True
                        finally:
                            # Releasing the semaphore post-yield to better respect the limit
                            if sem is not None and weight > 0:
                                sem.release(weight)
                    if not yielded and query_execution_parameters.yield_empty_batches:
                        if schema is not None:
                            features = columns_to_features(schema.names)
                            yield pa.RecordBatch.from_arrays(
                                arrays=[[] for _ in features], names=[x.root_fqn for x in features.values()]
                            )
                            return
                        else:
                            if _has_new_fetch_arrow_all():
                                tbl = cursor.fetch_arrow_all(True)
                                assert isinstance(tbl, pa.Table)
                                features = columns_to_features(tbl.schema.names)
                                yield self._postprocess_table(features, tbl)

    @classmethod
    def register_sqlalchemy_compiler_overrides(cls):
        try:
            from chalk.sql._internal.integrations.snowflake_compiler_overrides import register_snowflake_compiler_hooks
        except ImportError:
            raise missing_dependency_exception("chalkpy[snowflake]")
        register_snowflake_compiler_hooks()
