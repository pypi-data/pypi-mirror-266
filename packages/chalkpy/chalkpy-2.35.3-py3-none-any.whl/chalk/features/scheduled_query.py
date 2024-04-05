from __future__ import annotations

import inspect
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Collection, Optional, Union

from chalk.utils.duration import CronTab, Duration

if TYPE_CHECKING:
    from chalk.client.models import FeatureReference


class ScheduledQuery:
    def __init__(
        self,
        name: str,
        schedule: CronTab | Duration,
        output: Collection[FeatureReference],
        recompute_features: Union[bool, Collection[FeatureReference]] = True,
        max_samples: Optional[int] = None,
        lower_bound: Optional[datetime] = None,
        upper_bound: Optional[datetime] = None,
        tags: Optional[Collection[str]] = None,
        required_resolver_tags: Optional[Collection[str]] = None,
        store_online: bool = True,
        store_offline: bool = True,
        incremental_resolvers: Optional[Collection[str]] = None,
    ):
        """
        Creates an offline query which runs on a schedule. Scheduled queries do not produce datasets,
        but persists computation results in the feature store.

        By default, scheduled queries use incrementalization to only ingest data which has been updated since the last run.

        Parameters
        ----------
        name
            A unique name for the scheduled query. Scheduled queries with the same name will share status and incrementalization metadata.
        schedule
            A cron schedule or a Duration object representing the interval at which the query should run.
        output
            The features that this query will compute. Namespaces are exploded into all features in the namespace.
        recompute_features
            Whether or not to recompute all features vs. loading from the feature store.
            If True, all features will be recomputed.
            If False, all features will be loaded from the feature store.
            If a list of features, only those features will be recomputed, and the rest will be loaded from the feature store.
        max_samples
            The maximum number of samples to compute.
        lower_bound
            A hard-coded lower bound for the query. If set, the query will not use incrementalization.
        upper_bound
            A hard-coded upper bound for the query. If set, the query will not use incrementalization.
        tags
            Allows selecting resolvers with these tags.
        required_resolver_tags
            Requires that resolvers have these tags.
        store_online
            Whether to store the results of this query in the online store.
        store_offline
            Whether to store the results of this query in the offline store.

        Returns
        -------
        ScheduledQuery
            A scheduled query object.

        Examples
        --------
        >>> from chalk.features import ScheduledQuery
        >>> # this scheduled query will automatically run every 5 minutes after chalk apply
        >>> ScheduledQuery(
        ...     "ingest_users",
        ...     schedule="*/5 * * * *",
        ...     output=[User],
        ... )
        """
        super().__init__()

        if name in CRON_QUERY_REGISTRY:
            raise ValueError(f"Cron query with name {name} already exists. Cron names must be unique.")

        if len(output) == 0:
            raise ValueError(f"Cron query does not require any outputs. Chalk will not run it.")

        if lower_bound is not None:
            lower_bound = lower_bound.astimezone(tz=timezone.utc)
        if upper_bound is not None:
            upper_bound = upper_bound.astimezone(tz=timezone.utc)

        caller_filename = inspect.stack()[1].filename

        if not store_offline and not store_online:
            raise ValueError("Cron query does not store results. This means running it will have no effect.")

        self.name = name
        self.cron = schedule
        self.output = [str(f) for f in output]
        self.max_samples = max_samples
        self.recompute_features = (
            recompute_features
            if recompute_features is True or recompute_features is False
            else [str(f) for f in recompute_features]
        )
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.tags = tags
        self.required_resolver_tags = required_resolver_tags
        self.filename = caller_filename
        self.store_online = store_online
        self.store_offline = store_offline
        self.incremental_resolvers = incremental_resolvers

        CRON_QUERY_REGISTRY[name] = self


CRON_QUERY_REGISTRY: dict[str, ScheduledQuery] = {}
