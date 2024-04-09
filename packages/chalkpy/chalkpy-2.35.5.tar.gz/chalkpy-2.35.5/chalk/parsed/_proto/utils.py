import traceback
from datetime import datetime, timedelta
from typing import Optional, Union

import google.protobuf.duration_pb2 as duration_pb
from google.protobuf import duration_pb2, timestamp_pb2

import chalk._gen.chalk.artifacts.v1.export_pb2 as export_pb
import chalk._gen.chalk.graph.v1.graph_pb2 as graph_pb
import chalk._gen.chalk.graph.v1.sources_pb2 as sources_pb
from chalk.parsed.duplicate_input_gql import FailedImport
from chalk.parsed.utils import MAX_DURATION_NANOS, MAX_DURATION_SECONDS

RESOLVER_ENUM_TO_KIND = {
    graph_pb.ResolverKind.RESOLVER_KIND_UNSPECIFIED: "UNSPECIFIED",
    graph_pb.ResolverKind.RESOLVER_KIND_ONLINE: "online",
    graph_pb.ResolverKind.RESOLVER_KIND_OFFLINE: "offline",
}


def build_failed_import(error: Union[Exception, str], description: str) -> export_pb.FailedImport:
    try:
        formatted_tb = error if isinstance(error, str) else "\n".join(traceback.format_exception(error))
    except:
        formatted_tb = (
            error
            if isinstance(error, str)
            else "\n".join(
                traceback.format_exception(
                    type(error),
                    value=error,
                    tb=None,
                )
            )
        )

    return export_pb.FailedImport(
        file_name="",
        module="",
        traceback=f"EXCEPTION in parsing {description}:\n{formatted_tb}",
    )


def convert_failed_import_to_proto(failed_import: FailedImport) -> export_pb.FailedImport:
    return export_pb.FailedImport(
        file_name=failed_import.filename,
        module=failed_import.module,
        traceback=failed_import.traceback,
    )


def convert_failed_import_to_gql(failed_import: export_pb.FailedImport) -> FailedImport:
    return FailedImport(
        filename=failed_import.file_name,
        module=failed_import.module,
        traceback=failed_import.traceback,
    )


def get_feature_type_attribute_name(feature: graph_pb.FeatureType) -> str:
    if feature.HasField("scalar"):
        return feature.scalar.attribute_name
    elif feature.HasField("has_one"):
        return feature.has_one.attribute_name
    elif feature.HasField("has_many"):
        return feature.has_many.attribute_name
    elif feature.HasField("feature_time"):
        return feature.feature_time.attribute_name
    elif feature.HasField("windowed"):
        return feature.windowed.attribute_name
    else:
        raise ValueError(f"Unknown feature type: {feature}")


def get_feature_type_fqn(feature: graph_pb.FeatureType) -> str:
    if feature.HasField("scalar"):
        return f"{feature.scalar.namespace}.{feature.scalar.name}"
    elif feature.HasField("has_one"):
        return f"{feature.has_one.namespace}.{feature.has_one.name}"
    elif feature.HasField("has_many"):
        return f"{feature.has_many.namespace}.{feature.has_many.name}"
    elif feature.HasField("feature_time"):
        return f"{feature.feature_time.namespace}.{feature.feature_time.name}"
    elif feature.HasField("windowed"):
        return f"{feature.windowed.namespace}.{feature.windowed.name}"
    else:
        raise ValueError(f"Unknown feature type: {feature}")


def get_database_source_name(source: sources_pb.DatabaseSource) -> str:
    source_type = source.WhichOneof("source")
    if hasattr(getattr(source, source_type), "name"):
        return getattr(source, source_type).name
    raise ValueError(f"Unknown database source: {source}")


def get_stream_source_name(source: sources_pb.StreamSource) -> str:
    source_type = source.WhichOneof("source")
    if hasattr(getattr(source, source_type), "name"):
        return getattr(source, source_type).name
    raise ValueError(f"Unknown stream source: {source}")


def get_feature_reference_fqn(feature: graph_pb.FeatureReference) -> str:
    return f"{feature.namespace}.{feature.name}"


def get_feature_type_name(feature: graph_pb.FeatureType) -> str:
    if feature.HasField("scalar"):
        return feature.scalar.name
    elif feature.HasField("has_one"):
        return feature.has_one.name
    elif feature.HasField("has_many"):
        return feature.has_many.name
    elif feature.HasField("feature_time"):
        return feature.feature_time.name
    elif feature.HasField("windowed"):
        return feature.windowed.name
    else:
        raise ValueError(f"Unknown feature type: {feature}")


def get_feature_type_namespace(feature: graph_pb.FeatureType) -> str:
    if feature.HasField("scalar"):
        return feature.scalar.namespace
    elif feature.HasField("has_one"):
        return feature.has_one.namespace
    elif feature.HasField("has_many"):
        return feature.has_many.namespace
    elif feature.HasField("feature_time"):
        return feature.feature_time.namespace
    elif feature.HasField("windowed"):
        return feature.windowed.namespace
    else:
        raise ValueError(f"Unknown feature type: {feature}")


def get_feature_type_etl_offline_to_online(feature: graph_pb.FeatureType) -> Optional[bool]:
    if feature.HasField("scalar"):
        return feature.scalar.etl_offline_to_online if feature.scalar.HasField("etl_offline_to_online") else None
    elif feature.HasField("has_one"):
        return None
    elif feature.HasField("has_many"):
        return None
    elif feature.HasField("feature_time"):
        return None
    elif feature.HasField("windowed"):
        return None
    else:
        raise ValueError(f"Unknown feature type: {feature}")


def get_feature_type_max_staleness(feature: graph_pb.FeatureType) -> Optional[duration_pb.Duration]:
    if feature.HasField("scalar"):
        return feature.scalar.max_staleness_duration if feature.scalar.HasField("max_staleness_duration") else None
    elif feature.HasField("has_one"):
        return None
    elif feature.HasField("has_many"):
        return feature.has_many.max_staleness_duration if feature.has_many.HasField("max_staleness_duration") else None
    elif feature.HasField("feature_time"):
        return None
    elif feature.HasField("windowed"):
        return None
    else:
        raise ValueError(f"Unknown feature type: {feature}")


def get_feature_type_is_autogenerated(feature: graph_pb.FeatureType) -> bool:
    if feature.HasField("scalar"):
        return feature.scalar.is_autogenerated
    elif feature.HasField("has_one"):
        return feature.has_one.is_autogenerated
    elif feature.HasField("has_many"):
        return feature.has_many.is_autogenerated
    elif feature.HasField("feature_time"):
        return feature.feature_time.is_autogenerated
    elif feature.HasField("windowed"):
        return feature.windowed.is_autogenerated
    else:
        raise ValueError(f"Unknown feature type: {feature}")


def seconds_to_proto_duration(seconds: int) -> duration_pb2.Duration:
    if seconds == timedelta.max.total_seconds():
        resolved_timedelta = timedelta.max
    else:
        resolved_timedelta = timedelta(seconds=seconds)

    return timedelta_to_proto_duration(resolved_timedelta)


def timedelta_to_proto_duration(duration: timedelta) -> duration_pb2.Duration:
    pb_duration = duration_pb2.Duration()
    if duration == timedelta.max:
        pb_duration.seconds = MAX_DURATION_SECONDS
        pb_duration.nanos = MAX_DURATION_NANOS
    else:
        try:
            pb_duration.FromTimedelta(duration)
        except Exception as e:
            raise ValueError(f"Invalid duration: {e}")

    return pb_duration


def datetime_to_proto_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    pb_timestamp = timestamp_pb2.Timestamp()
    pb_timestamp.FromDatetime(dt)
    return pb_timestamp
