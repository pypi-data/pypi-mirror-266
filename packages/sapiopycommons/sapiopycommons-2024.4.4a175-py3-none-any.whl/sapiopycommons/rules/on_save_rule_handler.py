from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.general.exceptions import SapioException


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class OnSaveRuleHandler:
    """
    A class which helps with the parsing and navigation of the on save rule result map of a webhook context.
    TODO: Add functionality around the VeloxRuleType of the rule results.
    """
    __context: SapioWebhookContext
    """The context that this handler is working from."""

    __inst_man: RecordModelInstanceManager
    """The record model instance manager, used for wrapping the data records as record models."""

    # Reformatted and cached version of the Velox on save rule result map for easier handling.
    __records: dict[str, set[DataRecord]]
    """A mapping of data type to the set of data records from the context that match that data type."""
    __base_id_to_records: dict[int, dict[str, set[DataRecord]]]
    """A mapping of record IDs of records in the context.data_record_list to the sets of data records related to that
    record, each set of records being mapped by its data type."""

    def __init__(self, context: SapioWebhookContext):
        if context.velox_on_save_result_map is None:
            raise SapioException("No Velox on save rule result map in context for OnSaveRuleHandler to parse.")
        self.__context = context
        self.__inst_man = RecordModelManager(context.user).instance_manager
        self.__cache_records()

    def __cache_records(self) -> None:
        """
        Cache the records from the context into dictionaries. Two caches are created. One cache maps the data type of
        each record to a set of all records of that data type. The other cache maps the record ID that the records relate
        to with another dict that maps the data types to the records of that type. Doesn't cache any relationship info.
        """
        self.__records = {}
        self.__base_id_to_records = {}
        # Each record ID in the context has a list of results for that record.
        for record_id, rule_results in self.__context.velox_on_save_result_map.items():
            # TODO: Record IDs are currently being stored in the map as strings instead of ints. This can be removed
            #  once sapiopylib is fixed.
            record_id = int(record_id)
            # Keep track of the records for this specific record ID.
            id_dict: dict[str, set[DataRecord]] = {}
            # The list of results for a record consist of a list of data records and a VeloxType that specifies
            # how the records in the list relate to the main record.
            for record_result in rule_results:
                # For the purposes of caching, we don't care about the VeloxType.
                for record in record_result.data_records:
                    # Get the data type of this record. If this is an ELN type, ignore the digits.
                    data_type: str = record.data_type_name
                    # PR-46331: Ensure that all ELN types are converted to their base data type name.
                    if data_type.startswith("ELNExperiment_"):
                        data_type = "ELNExperiment"
                    elif data_type.startswith("ELNExperimentDetail_"):
                        data_type = "ELNExperimentDetail"
                    elif data_type.startswith("ELNSampleDetail_"):
                        data_type = "ELNSampleDetail"
                    # Update the list of records of this type that exist so far globally.
                    self.__records.setdefault(data_type, set()).add(record)
                    # Do the same for the list of records of this type that relate to this record ID.
                    id_dict.setdefault(data_type, set()).add(record)
            # Update the related records for this record ID.
            self.__base_id_to_records.update({record_id: id_dict})

    def get_records(self, data_type: str, record_id: int | None = None) -> list[DataRecord]:
        """
        Get records from the cached context with the given data type. Capable of being filtered to searching within
        the context of a record ID. If the given data type or record ID does not exist in the context,
        returns an empty list.

        :param data_type: The data type of the records to return.
        :param record_id: The record ID of the base record to search from. If None, returns the records that match the
            data type from ID. If an ID is provided, but it does not exist in the context, returns an empty list.
        :return: The records from the context that match the input parameters.
        """
        records: dict[str, set[DataRecord]] = self.__base_id_to_records.get(record_id, {}) if record_id else self.__records
        return list(records.get(data_type, []))

    def get_models(self, wrapper_type: type[WrappedType], record_id: int | None = None) -> list[WrappedType]:
        """
        Get records from the cached context with the given data type. Capable of being filtered to searching within
        the context of a record ID. If the given data type or record ID does not exist in the context,
        returns an empty list.

        :param wrapper_type: The record model wrapper to use.
        :param record_id: The record ID of the base record to search from. If None, returns the records that match the
            data type from ID. If an ID is provided, but it does not exist in the context, returns an empty list.
        :return: The record models from the context that match the input parameters.
        """
        dt: str = wrapper_type.get_wrapper_data_type_name()
        return self.__inst_man.add_existing_records_of_type(self.get_records(dt, record_id), wrapper_type)
