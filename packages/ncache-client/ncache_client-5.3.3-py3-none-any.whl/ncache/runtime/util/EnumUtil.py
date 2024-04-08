from ncache.client.enum.CacheItemPriority import CacheItemPriority
from ncache.client.enum.CacheItemRemovedReason import CacheItemRemovedReason
from ncache.client.enum.CacheStatusNotificationType import CacheStatusNotificationType
from ncache.client.enum.ClientCacheSyncMode import ClientCacheSyncMode
from ncache.client.enum.CmdParamsType import CmdParamsType
from ncache.client.enum.CommandType import CommandType
from ncache.client.enum.DataTypeEventDataFilter import DataTypeEventDataFilter
from ncache.client.enum.DeliveryMode import DeliveryMode
from ncache.client.enum.DeliveryOption import DeliveryOption
from ncache.client.enum.DistributedDataStructure import DistributedDataStructure
from ncache.client.enum.EventDataFilter import EventDataFilter
from ncache.client.enum.EventType import EventType
from ncache.client.enum.ExpirationType import ExpirationType
from ncache.client.enum.IsolationLevel import IsolationLevel
from ncache.client.enum.KeyDependencyType import KeyDependencyType
from ncache.client.enum.LogLevel import LogLevel
from ncache.client.enum.MessgeFailureReason import MessageFailureReason
from ncache.client.enum.OracleCmdParamsType import OracleCmdParamsType
from ncache.client.enum.OracleCommandType import OracleCommandType
from ncache.client.enum.OracleParameterDirection import OracleParameterDirection
from ncache.client.enum.SqlCmpOptions import SqlCmpOptions
from ncache.client.enum.SqlCommandType import SqlCommandType
from ncache.client.enum.SqlDataRowVersion import SqlDataRowVersion
from ncache.client.enum.SqlParamDirection import SqlParamDirection
from ncache.client.enum.SubscriptionPolicy import SubscriptionPolicy
from ncache.client.enum.TagSearchOptions import TagSearchOptions
from ncache.client.enum.TopicPriority import TopicPriority
from ncache.client.enum.TopicSearchOptions import TopicSearchOptions
from ncache.client.enum.WriteBehindOpStatus import WriteBehindOpStatus
from ncache.util.JavaInstancesFactory import *
from ncache.util.TypeCaster import TypeCaster
from ncache.util.ValidateType import ValidateType


class EnumUtil:
    @staticmethod
    def get_expiration_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getExpirationType(value)

    @staticmethod
    def get_expiration_type_value(optype):
        ValidateType.is_none(optype)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getExpirationTypeValue(optype))
        return ExpirationType(value + 1)

    @staticmethod
    def get_write_operation_type(value):
        pass

    @staticmethod
    def get_write_operation_type_value(optype):
        pass

    @staticmethod
    def get_data_structure_operation_type(value):
        pass

    @staticmethod
    def get_data_structure_operation_type_value(optype):
        pass

    @staticmethod
    def get_data_structure_type(value):
        pass

    @staticmethod
    def get_data_structure_type_value(op_type):
        pass
    
    @staticmethod
    def get_operation_result_status(value):
        pass

    @staticmethod
    def get_operation_result_status_value(status):
        pass

    @staticmethod
    def get_key_dependency_type_value(dependencytype):
        ValidateType.is_none(dependencytype)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getKeyDepenedencyTypeValue(dependencytype))
        return KeyDependencyType(value + 1)

    @staticmethod
    def get_key_dependency_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getKeyDepenedencyType(value)

    @staticmethod
    def get_serialization_format_value(formattype):
        pass

    @staticmethod
    def get_serialization_format(value):
        pass

    @staticmethod
    def get_user_object_type_value(objtype):
        pass
    
    @staticmethod
    def get_user_object_type(value):
        pass

    @staticmethod
    def get_write_mode(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getWriteMode(value)
    
    @staticmethod
    def get_write_mode_value(writemode):
        ValidateType.is_none(writemode)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getWriteModeValue(writemode))
        return KeyDependencyType(value + 1)

    @staticmethod
    def get_read_mode(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getReadMode(value)

    @staticmethod
    def get_read_mode_value(mode):
        ValidateType.is_none(mode)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getReadModeValue(mode))
        return KeyDependencyType(value + 1)
    
    @staticmethod
    def get_topic_priority(value):
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getTopicPriority(value)

    @staticmethod
    def get_topic_priority_value(priority):
        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getTopicPriorityValue(priority))

        if value == 'Low':
            value = 1
        elif value == 'Normal':
            value = 2
        elif value == 'High':
            value = 3

        return TopicPriority(value)

    @staticmethod
    def get_cache_item_priority(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getCacheItemPriority(value)

    @staticmethod
    def get_cache_item_priority_value(priority):
        ValidateType.is_none(priority)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getCacheItemPriorityValue(priority))
        return CacheItemPriority(value + 1)

    @staticmethod
    def get_event_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getEventType(value)

    @staticmethod
    def get_event_type_value(eventtype):
        ValidateType.is_none(eventtype)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getEventTypeValue(eventtype))

        if value == 'ItemAdded':
            value = 1
        elif value == 'ItemUpdated':
            value = 2
        elif value == 'ItemRemoved':
            value = 3

        return EventType(value)

    @staticmethod
    def get_event_data_filter(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getEventDataFilter(value)

    @staticmethod
    def get_event_data_filter_value(datafilter):
        ValidateType.is_none(datafilter)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getEventDataFilterValue(datafilter))

        if value == 'None':
            value = 1
        elif value == 'Metadata':
            value = 2
        elif value == 'DataWithMetadata':
            value = 4

        return EventDataFilter(value)

    @staticmethod
    def get_topic_search_options(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getTopicSearchOptions(value)

    @staticmethod
    def get_topic_search_options_value(options):
        ValidateType.is_none(options)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getTopicSearchOptionsValue(options))

        if value == 'ByName':
            value = 1
        elif value == 'ByPattern':
            value = 2

        return TopicSearchOptions(value)

    @staticmethod
    def enum_set_cache_status(statustype):
        pass

    @staticmethod
    def get_isolation_level(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getIsolationLevel(value)

    @staticmethod
    def get_isolation_level_value(options):
        ValidateType.is_none(options)

        value = int(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getIsolationLevelValue(options))
        return IsolationLevel(value + 1)

    @staticmethod
    def get_log_level(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getLogLevel(value)

    @staticmethod
    def get_log_level_value(options):
        ValidateType.is_none(options)

        value = int(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getLogLevelValue(options))
        return LogLevel(value + 1)

    @staticmethod
    def get_client_cache_sync_mode(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getCacheClientSyncMode(value)

    @staticmethod
    def get_client_cache_sync_mode_value(mode):
        ValidateType.is_none(mode)

        value = int(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getClientCacheSyncModeValue(mode))
        return ClientCacheSyncMode(value + 1)

    @staticmethod
    def get_cache_status_notification_type(value):
        value = value.name

        if value == 'MEMBER_JOINED':
            value = 'MemberJoined'
        elif value == 'MEMBER_LEFT':
            value = 'MemberLeft'
        elif value == 'CACHE_STOPPED':
            value = 'CacheStopped'
        else:
            value = 'ALL'

        value = TypeCaster.to_java_primitive_type(value)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getCacheStatusNotificationType(value)

    @staticmethod
    def get_cache_status_notification_type_value(notificationtype):
        ValidateType.is_none(notificationtype)

        value = str(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getCacheStatusNotificationTypeValue(notificationtype))

        if value == 'MemberJoined':
            value = 1
        elif value == 'MemberLeft':
            value = 2
        elif value == 'CacheStopped':
            value = 3
        elif value == 'ALL':
            value = 4

        return CacheStatusNotificationType(value)

    @staticmethod
    def get_delivery_option(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getDeliveryOption(value)

    @staticmethod
    def get_delivery_option_value(value):
        ValidateType.is_none(value)

        value = str(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getDeliveryOptionValue(value))

        if value == 'All':
            value = 1
        elif value == 'Any':
            value = 2

        return DeliveryOption(value)

    @staticmethod
    def get_subscription_policy(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getSubscriptionPolicy(value)

    @staticmethod
    def get_subscription_policy_value(policy):
        ValidateType.is_none(policy)

        value = str(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getSubscriptionPolicyValue(policy))

        if value == 'Shared':
            value = 1
        elif value == 'Exclusive':
            value = 2

        return SubscriptionPolicy(value)

    @staticmethod
    def get_delivery_mode(value):
        if value == 'ASYNC':
            value = 'Async'
        elif value == 'SYNC':
            value = 'Sync'

        value = TypeCaster.to_java_primitive_type(value)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getDeliveryMode(value)
    
    @staticmethod
    def get_delivery_mode_value(mode):
        ValidateType.is_none(mode)

        value = str(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getDeliveryModeValue(mode))

        if value == 'Async':
            value = 1
        elif value == 'Sync':
            value = 2

        return DeliveryMode(value)

    @staticmethod
    def get_tag_search_options(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getTagSearchOptions(value)

    @staticmethod
    def get_tag_search_options_value(options):
        ValidateType.is_none(options)

        value = int(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getTagSearchOptionsValue(options))
        return TagSearchOptions(value + 1)

    @staticmethod
    def get_write_behind_op_status(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getWriteBehindOpStatus(value)

    @staticmethod
    def get_write_behind_op_status_value(status):
        ValidateType.is_none(status)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getEventDataFilterValue(status))

        if value == 'Failure':
            value = 1
        elif value == 'Success':
            value = 2

        return WriteBehindOpStatus(value)

    @staticmethod
    def get_cache_item_removed_reason(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("ClientEnumUtil").getCacheItemRemovedReason(value)

    @staticmethod
    def get_cache_item_removed_reason_value(reason):
        ValidateType.is_none(reason)

        value = str(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getCacheItemRemovedReasonValue(reason))

        if value == 'DependencyChanged':
            value = 1
        elif value == 'Expired':
            value = 2
        elif value == 'Removed':
            value = 3
        elif value == 'Underused':
            value = 4
        elif value == 'DependencyInvalid':
            value = 5

        return CacheItemRemovedReason(value)

    @staticmethod
    def get_message_failure_reason(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getSubscriptionPolicy(value)

    @staticmethod
    def get_message_failure_reason_value(reason):
        ValidateType.is_none(reason)

        value = str(JavaInstancesFactory.get_java_instance("ClientEnumUtil").getSubscriptionPolicyValue(reason))

        if value == 'Expired':
            value = 1
        elif value == 'Evicted':
            value = 2

        return MessageFailureReason(value)

    @staticmethod
    def get_oracle_command_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getOracleCommandType(value)

    @staticmethod
    def get_oracle_command_type_value(options):
        ValidateType.is_none(options)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getOracleCommandTypeValue(options))
        return OracleCommandType(value + 1)
    
    @staticmethod
    def get_command_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getCommandType(value)

    @staticmethod
    def get_command_type_value(options):
        ValidateType.is_none(options)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getCommandTypeValue(options))

        if value == 'Text':
            value = 1
        elif value == 'StoredProcedure':
            value = 4
        elif value == 'TableDirect':
            value = 512

        return CommandType(value)

    @staticmethod
    def get_oracle_parameter_direction(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getOracleParameterDirection(value)

    @staticmethod
    def get_oracle_parameter_direction_value(options):
        ValidateType.is_none(options)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getOracleParameterDirectionValue(options))
        return OracleParameterDirection(value + 1)

    @staticmethod
    def get_oracle_cmd_params_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getOracleCmdParamsType(value)

    @staticmethod
    def get_oracle_cmd_params_type_value(options):
        ValidateType.is_none(options)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getOracleCmdParamsTypeValue(options))
        return OracleCmdParamsType(value + 1)

    @staticmethod
    def get_cmd_params_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getCmdParamsType(value)

    @staticmethod
    def get_cmd_params_type_value(options):
        ValidateType.is_none(options)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getCmdParamsTypeValue(options))

        value = EnumUtil.get_cmd_params_type_number_for_name(value)

        return CmdParamsType(value)

    @staticmethod
    def get_sql_command_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getSqlCommandType(value)

    @staticmethod
    def get_sql_command_type_value(options):
        ValidateType.is_none(options)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getSqlCommandTypeValue(options))

        if value == 'Text':
            value = 1
        elif value == 'StoredProcedure':
            value = 4

        return SqlCommandType(value)

    @staticmethod
    def get_sql_data_row_version(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getSqlDataRowVersion(value)

    @staticmethod
    def get_sql_data_row_version_value(options):
        ValidateType.is_none(options)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getSqlDataRowVersionValue(options))

        if value == 'Original':
            value = 256
        elif value == 'Current':
            value = 512
        elif value == 'Proposed':
            value = 1024
        elif value == 'Default':
            value = 1536

        return SqlDataRowVersion(value)

    @staticmethod
    def get_sql_cmp_options(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getSqlCmpOptions(value)

    @staticmethod
    def get_sql_cmp_options_value(options):
        ValidateType.is_none(options)

        value = str(JavaInstancesFactory.get_java_instance("EnumUtil").getSqlCmpOptionsValue(options))

        value = EnumUtil.get_sql_cmp_options_number_for_name(value)

        return SqlCmpOptions(value)

    @staticmethod
    def get_sql_param_direction(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getSqlParamDirection(value)

    @staticmethod
    def get_sql_param_direction_value(options):
        ValidateType.is_none(options)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getSqlParamDirectionValue(options))
        return SqlParamDirection(value + 1)

    @staticmethod
    def get_dependency_type_info(value):
        return int(JavaInstancesFactory.get_java_instance("DependencyUtil").getDependencyTypeInfo(value))

    @staticmethod
    def get_data_type_event_data_filter(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value - 1)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getDataTypeEventDataFilter(value)
    
    @staticmethod
    def get_data_type_event_data_filter_value(value):
        ValidateType.is_none(value)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getDataTypeEventDataFilterValue(value))
        return DataTypeEventDataFilter(value + 1)

    @staticmethod
    def get_collection_type(value):
        ValidateType.type_check(value, int)
        value = TypeCaster.to_java_primitive_type(value)

        return JavaInstancesFactory.get_java_instance("EnumUtil").getCollectionType(value)

    @staticmethod
    def get_collection_type_value(value):
        ValidateType.is_none(value)

        value = int(JavaInstancesFactory.get_java_instance("EnumUtil").getCollectionTypeValue(value))
        return DistributedDataStructure(value)

    @staticmethod
    def get_cmd_params_type_number_for_name(name):
        if name == 'BigInt':
            return 1
        elif name == 'Binary':
            return 2
        elif name == 'Bit':
            return 3
        elif name == 'Char':
            return 4
        elif name == 'DateTime':
            return 5
        elif name == 'Decimal':
            return 6
        elif name == 'Float':
            return 7
        elif name == 'Int':
            return 9
        elif name == 'Money':
            return 10
        elif name == 'NChar':
            return 11
        elif name == 'NVarChar':
            return 13
        elif name == 'Real':
            return 14
        elif name == 'UniqueIdentifier':
            return 15
        elif name == 'SmallDateTime':
            return 16
        elif name == 'SmallInt':
            return 17
        elif name == 'SmallMoney':
            return 18
        elif name == 'Timestamp':
            return 20
        elif name == 'TinyInt':
            return 21
        elif name == 'VarBinary':
            return 22
        elif name == 'VarChar':
            return 23
        elif name == 'Variant':
            return 24
        elif name == 'Xml':
            return 26
        elif name == 'Udt':
            return 30
        elif name == 'Structured':
            return 31
        elif name == 'Date':
            return 32
        elif name == 'Time':
            return 33
        elif name == 'DateTime2':
            return 34
        elif name == 'DateTimeOffset':
            return 35

    @staticmethod
    def get_sql_cmp_options_number_for_name(name):
        if name == 'None':
            return 1
        elif name == 'IgnoreCase':
            return 2
        elif name == 'IgnoreNonSpace':
            return 3
        elif name == 'IgnoreKanaType':
            return 9
        elif name == 'IgnoreWidth':
            return 17
        elif name == 'BinarySort2':
            return 16385
        elif name == 'BinarySort':
            return 32769
