import dataclasses
from dataclasses import dataclass
from typing import Set

from chalk.utils.environment_parsing import env_var_bool


@dataclass(frozen=True)
class PostgresQueryExecutionParameters:
    attempt_efficient_postgres_execution: bool
    """
    Overrides QueryExecutionParameters.attempt_efficient_parameters if True
    """

    polars_read_csv: bool
    """
    When `attempt_postgres_efficient_execution` is True, this flag decides whether to use polars'
    read_csv or pyarrow's read_csv.
    """

    skip_datetime_timezone_cast: bool
    """
    skip datetime timezone casting, only under efficient execution. This happens BEFORE the sql query.
    """

    csv_read_then_cast: bool = True
    """DEPRECATED"""


@dataclass(frozen=True)
class QueryExecutionParameters:
    attempt_efficient_execution: bool
    """
    This will be overriden at query time if the source is a postgres source and
    PostgresQueryExecutionParameters.attempt_efficient_postgres_execution is True in the invoker
    """

    postgres: PostgresQueryExecutionParameters

    yield_empty_batches: bool = False
    """Whether to yield empty batches. This can be useful to capture the schema of an otherwise-empty results set"""

    fallback_to_inefficient_execution: bool = True
    """Whether to fallback to inefficient execution if efficient execution fails for an unexpected error"""

    max_prefetch_size_bytes: int = 1024 * 1024 * 1024
    """If nonnegative, the maximum number of bytes to prefetched when executing a query. If zero or negative,
    then there is no limit to the number of bytes that can be prefetched."""

    num_client_prefetch_threads: int = 4
    """Number of threads to use when downloading query results."""

    tags: Set[str] = dataclasses.field(default_factory=set)
    """Tags that can be used to select a source. These tags are proxied from the overlying Chalk query context."""


def query_execution_parameters_from_env_vars():
    """
    For when called in user resolver code.
    If you do not want to do efficient execution, set CHALK_FORCE_SQLALCHEMY_QUERY_EXECUTION_WITHOUT_EXCEPTION to True
    """
    return QueryExecutionParameters(
        attempt_efficient_execution=not env_var_bool("CHALK_FORCE_SQLALCHEMY_QUERY_EXECUTION"),
        postgres=PostgresQueryExecutionParameters(
            attempt_efficient_postgres_execution=True,
            polars_read_csv=env_var_bool("CHALK_FORCE_POLARS_READ_CSV"),
            skip_datetime_timezone_cast=env_var_bool("CHALK_SKIP_PG_DATETIME_ZONE_CAST"),
        ),
    )
