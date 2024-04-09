from __future__ import annotations

from weakref import WeakValueDictionary

from sapiopylib.rest.pojo.eln.ElnEntryPosition import ElnEntryPosition

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.DataRecordPaging import DataRecordPojoPageCriteria, DataRecordPojoListPageResult
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldDefinitionParser, AbstractVeloxFieldDefinition
from sapiopylib.rest.pojo.eln.ElnExperiment import *
from sapiopylib.rest.pojo.eln.ExperimentEntry import ExperimentEntryParser, ExperimentEntry
from sapiopylib.rest.pojo.eln.ExperimentEntryCriteria import ElnEntryCriteria, AbstractElnEntryUpdateCriteria
from sapiopylib.rest.pojo.eln.SapioELNEnums import ExperimentEntryStatus, ElnBaseDataType
from sapiopylib.rest.pojo.eln.field_set import ElnFieldSetInfo
from sapiopylib.rest.pojo.eln.protocol_template import ProtocolTemplateQuery, ProtocolTemplateInfo


class ElnManager:
    """
    Manages ELN notebook experiments in the system.
    """
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, ElnManager] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, user: SapioUser):
        """
        Observes singleton pattern per record model manager object.

        :param user: The user that will make the webservice request to the application.
        """
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, user: SapioUser):
        """
        Obtain an ELN manager to perform ELN operations.

        :param user: The user that will make the webservice request to the application.
        """
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def create_notebook_experiment(self, pojo: InitializeNotebookExperimentPojo) -> ElnExperiment:
        """
        Use the provided criteria to create a new notebook experiment.

        :param pojo: The criteria for the creation of the new experiment.
        :return: An object representing the new experiment that was created in the system.
        """
        sub_path = '/eln/notebookexperiment/'
        response = self.user.post(sub_path, payload=pojo.to_json())
        self.user.raise_for_status(response)
        json_dict = response.json()
        return ELNExperimentParser.parse_eln_experiment(json_dict)

    def delete_notebook_experiment(self, notebook_experiment_id: int) -> None:
        """
        Delete a notebook experiment when providing a notebook experiment ID.

        :param notebook_experiment_id: The notebook experiment ID of the experiment to delete.
        """
        subpath = self.user.build_url(['eln', 'experiment', str(notebook_experiment_id)])
        response = self.user.delete(subpath)
        self.user.raise_for_status(response)

    def get_template_experiment_list(self, query: TemplateExperimentQueryPojo) -> List[ElnTemplate]:
        """
        Get a list of experiment template from the system that match the provided query criteria.

        :param query: Search criteria for finding experiment templates.
        :return: A list of templates matching the provided criteria in the system.
        """
        sub_path = "/eln/templateexperiment/"
        response = self.user.post(sub_path, payload=query.to_json())
        self.user.raise_for_status(response)
        json_list: List[Dict[str, Any]] = response.json()
        return [ELNExperimentParser.parse_template_experiment(x) for x in json_list]

    def get_experiment_entry_list(self, eln_experiment_id: int, to_retrieve_field_definitions: bool = False) \
            -> List[ExperimentEntry]:
        """
        Get all the experiment entries for an ELN experiment.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param to_retrieve_field_definitions: If true, the returned experiment entry objects will contain field
            definitions for the fields that are present in the entry (e.g. the columns of a table entry or fields of a
            form entry).
        :return: A list of experiment entries from the given experiment.
        """
        sub_path = self.user.build_url(['eln', 'getExperimentEntryList', str(eln_experiment_id)])
        params = {
            'retrieveDataDefinitions': to_retrieve_field_definitions
        }
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_list: List[Dict[str, Any]] = response.json()
        return [ExperimentEntryParser.parse_experiment_entry(x) for x in json_list]

    def get_experiment_entry(self, eln_experiment_id: int, entry_id: int,
                             to_retrieve_field_definitions: bool = False) -> Optional[ExperimentEntry]:
        """
        Get a specific entry from an ELN experiment given its entry ID.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry.
        :param to_retrieve_field_definitions: If true, the returned experiment entry objects will contain field
            definitions for the fields that are present in the entry (e.g. the columns of a table entry or fields of a
            form entry).
        :return: The experiment entry that matches the input if it exists, or None if it does not.
        """
        sub_path = self.user.build_url(['eln', 'getExperimentEntry', str(eln_experiment_id), str(entry_id)])
        params = {
            'retrieveDataDefinitions': to_retrieve_field_definitions
        }
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dct: Optional[Dict[str, Any]] = response.json()
        if json_dct is None:
            return None
        return ExperimentEntryParser.parse_experiment_entry(json_dct)

    def get_eln_experiment_by_record_id(self, record_id: int) -> ElnExperiment:
        """
        Given the record ID of the experiment data record for a notebook, find the ELN experiment.
        This can be useful when trying to retrieve ELN experiments from the global data type hierarchy.

        :param record_id: The record ID of the experiment record.
        :return: The ELN experiment for the matching experiment record.
        """
        sub_path = '/eln/queryExperimentByRecordId'
        params = {
            'recordId': record_id
        }
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        return ELNExperimentParser.parse_eln_experiment(response.json())

    def get_eln_experiment_list(self, owner_username: Optional[str] = None,
                                status_types: Optional[List[ExperimentEntryStatus]] = None) \
            -> List[ElnExperiment]:
        """
        Get the ELN experiments from the system that match the basic input parameters.

        :param owner_username: If specified, filter to only those experiments that are owned by the user with this name.
        :param status_types: If specified, filter to only those experiments with the matching status.
        :return: A list of ELN experiments that match the input search criteria.
        """
        sub_path = '/eln/getExperimentInfoList'
        params = dict()
        if owner_username is not None:
            params['ownerUsername'] = owner_username
        if status_types is not None:
            params['statusTypes'] = [x.name for x in status_types]
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_list: List[Dict[str, Any]] = response.json()
        return [ELNExperimentParser.parse_eln_experiment(x) for x in json_list]

    def get_eln_experiment_by_criteria(self, criteria: ElnExperimentQueryCriteria) -> List[ElnExperiment]:
        """
        Get the ELN experiments from the system that match the complex search criteria.

        :param criteria: The complex search criteria for the experiments.
        :return: A list of ELN experiments that match the input search criteria.
        """
        sub_path = '/eln/queryExperimentByCriteria'
        response = self.user.post(sub_path, payload=criteria.to_json())
        self.user.raise_for_status(response)
        json_list: List[Dict[str, Any]] = response.json()
        return [ELNExperimentParser.parse_eln_experiment(x) for x in json_list]

    def get_eln_experiment_by_id(self, eln_experiment_id: int) -> Optional[ElnExperiment]:
        """
        Get an ELN experiment by its notebook experiment ID.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :return: The ELN experiment object. Returns None if it does not exist, or the current user does not have access.
        """
        criteria = ElnExperimentQueryCriteria(notebook_experiment_id_white_list=[eln_experiment_id])
        results = self.get_eln_experiment_by_criteria(criteria)
        if results:
            return results[0]
        return None

    def add_experiment_entry(self, eln_experiment_id: int, entry_criteria: ElnEntryCriteria) -> ExperimentEntry:
        """
        Create a new entry under in an ELN experiment.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_criteria: The creation criteria for the new experiment entry.
        :return: The experiment entry that was created. This entry object will not contain field definitions.
        """
        sub_path = self.user.build_url(['eln', 'addExperimentEntry', str(eln_experiment_id)])
        response = self.user.post(sub_path, payload=entry_criteria.to_json())
        self.user.raise_for_status(response)
        json_dct: Dict[str, Any] = response.json()
        return ExperimentEntryParser.parse_experiment_entry(json_dct)

    def add_predefined_entry_fields(self, eln_experiment_id: int, entry_id: int,
                                    predefined_field_name_list: List[str]) -> ExperimentEntry:
        """
        Add additional predefined fields to an ELN experiment entry.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry.
        :param predefined_field_name_list: A list of the predefined fields to be added to the experiment entry.
        :return: The entry that the fields were added to with updated field definitions.
        """
        sub_path = self.user.build_url(['eln', 'addPredefinedEntryFields', str(eln_experiment_id), str(entry_id)])
        response = self.user.post(sub_path, payload=predefined_field_name_list)
        self.user.raise_for_status(response)
        json_dct: Dict[str, Any] = response.json()
        return ExperimentEntryParser.parse_experiment_entry(json_dct)

    def get_predefined_fields(self, eln_base_data_type: ElnBaseDataType) -> List[AbstractVeloxFieldDefinition]:
        """
        Determine what the available predefined fields in the system are for an entry given its base ELN data type.

        :param eln_base_data_type: The base data type of the ELN entry. This includes ELNExperiment,
            ELNExperimentDetail, and ELNSampleDetail entries.
        :return: All predefined field definitions for this ELN data type.
        """
        sub_path = self.user.build_url(['eln', 'getPredefinedFields', eln_base_data_type.data_type_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        json_list: List[Dict[str, Any]] = response.json()
        return [FieldDefinitionParser.to_field_definition(x) for x in json_list]

    def get_predefined_field_by_id(self, field_id: int) -> AbstractVeloxFieldDefinition:
        """
        Given a predefined field ID, retrieve its full field definition.

        :param field_id: The system generated ID for the predefined field.
        :return: The field definition for the matching predefined field.
        """
        sub_path = self.user.build_url(['eln', 'getPredefinedFieldById', str(field_id)])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        json_dct: Dict[str, Any] = response.json()
        return FieldDefinitionParser.to_field_definition(json_dct)

    def get_predefined_field_by_name(self, eln_base_data_type: ElnBaseDataType, field_name: str) \
            -> AbstractVeloxFieldDefinition:
        """
        Given the base ELN data type and data field name of a predefined field, retrieve its full field definition.

        :param eln_base_data_type: The base data type of the entry type that the predefined field is for. This includes
            ELNExperiment, ELNExperimentDetail, and ELNSampleDetail entries.
        :param field_name: The data field name of the predefined field.
        :return: The field definition for the matching predefined field.
        """
        sub_path = self.user.build_url(['eln', 'getPredefinedFieldByName', eln_base_data_type.data_type_name,
                                        field_name])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        json_dct: Dict[str, Any] = response.json()
        return FieldDefinitionParser.to_field_definition(json_dct)

    def get_data_records_for_entry(self, eln_experiment_id: int, entry_id: int,
                                   paging_criteria: DataRecordPojoPageCriteria = None) -> DataRecordPojoListPageResult:
        """
        Get the data records that are associated with the given entry.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry.
        :param paging_criteria: Optional paging criteria info for the current page. Note the maximum page size may be
            enforced by the system. If it is, a page size must be given that is less than or equal to the maximum.
            If not provided, returns the first page of results.
        :return: The query results from the current page, containing a list of the data records from the query,
            the current page information, and whether more pages exist after it.
        """
        sub_path = self.user.build_url(['eln', 'getDataRecordsForEntry', str(eln_experiment_id), str(entry_id)])
        params = dict()
        if paging_criteria is not None:
            params['lastRetrievedRecordId'] = paging_criteria.last_retrieved_record_id
            params['pageSize'] = paging_criteria.page_size
        response = self.user.get(sub_path, params)
        self.user.raise_for_status(response)
        json_dct: Dict[str, Any] = response.json()
        return DataRecordPojoListPageResult.from_json(json_dct)

    def submit_experiment_entry(self, eln_experiment_id: int, entry_id: int) -> None:
        """
        Submit the given experiment entry. This locks down the entry and will cause any entries that are dependent
        upon this one to become enabled.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry.
        """
        sub_path = self.user.build_url(['eln', 'submitExperimentEntry', str(eln_experiment_id), str(entry_id)])
        response = self.user.post(sub_path)
        self.user.raise_for_status(response)

    def add_records_to_table_entry(self, eln_experiment_id: int, entry_id: int,
                                   records_to_add: List[DataRecord]) -> None:
        """
        Add data records to an experiment table entry.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry. This ID must correspond to a table entry.
        :param records_to_add: A list of data records to add to the corresponding experiment table entry. These data
            records do not need to already exist in the system. If the data record objects lack record IDs, then
            the system will create the data records alongside adding them to the experiment entry. If the data records
            do already exist, then the records are only added to the entry; no field updates will be performed.
        """
        sub_path = self.user.build_url(['eln', 'addRecordsToTableEntry', str(eln_experiment_id), str(entry_id)])
        record_pojo_list = [x.to_json() for x in records_to_add]
        response = self.user.post(sub_path, payload=record_pojo_list)
        self.user.raise_for_status(response)

    def remove_records_from_table_entry(self, eln_experiment_id: int, entry_id: int,
                                        record_id_remove_list: List[int]) -> None:
        """
        Remove data records from an experiment table entry.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry. This ID must correspond to a table entry.
        :param record_id_remove_list: A list of record IDs corresponding to the records that should be removed from the
            entry.
        """
        sub_path = self.user.build_url(['eln', 'removeRecordsFromTableEntry', str(eln_experiment_id), str(entry_id)])
        response = self.user.post(sub_path, payload=record_id_remove_list)
        self.user.raise_for_status(response)

    def update_experiment_entry(self, eln_experiment_id: int, entry_id: int,
                                entry_update_criteria: AbstractElnEntryUpdateCriteria) -> None:
        """
        Update the metadata of an experiment entry. Possible metadata changes include the entry's name, status,
        entry options, and more.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry.
        :param entry_update_criteria: The update criteria for the experiment entry.
        """
        sub_path = self.user.build_url(['eln', 'updateExperimentEntry', str(eln_experiment_id), str(entry_id)])
        response = self.user.post(sub_path, payload=entry_update_criteria.to_json())
        self.user.raise_for_status(response)

    def update_notebook_experiment(self, eln_experiment_id: int,
                                   experiment_update_criteria: ElnExperimentUpdateCriteria) -> None:
        """
        Update the metadata of a notebook experiment. Possible metadata changes include the experiment's name, status,
        and experiment options.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param experiment_update_criteria: The update criteria for the ELN experiment.
        """
        sub_path = self.user.build_url(['eln', 'updateNotebookExperiment', str(eln_experiment_id)])
        response = self.user.post(sub_path, payload=experiment_update_criteria.to_json())
        self.user.raise_for_status(response)

    def get_experiment_entry_options(self, eln_experiment_id: int, entry_id: int) -> Dict[str, str]:
        """
        Get the entry options from an experiment entry. These may be used to store plugin or configuration data.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param entry_id: The entry ID of the entry.
        :return: A dictionary of the experiment entry options.
        """
        sub_path = self.user.build_url(['eln', 'getExperimentEntryOptions', str(eln_experiment_id), str(entry_id)])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        return response.json()

    def get_notebook_experiment_options(self, eln_experiment_id: int) -> Dict[str, str]:
        """
        Get the experiment options from an ELN experiment. These may be used to store plugin or configuration data.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :return: A dictionary of the experiment entry options.
        """
        sub_path = self.user.build_url(['eln', 'getNotebookExperimentOptions', str(eln_experiment_id)])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        return response.json()

    # FR-51551 Added method
    def transfer_ownership(self, eln_experiment_id: int, new_owner_username: str) -> None:
        """
        Transfer ownership of an experiment to a new user.

        :param eln_experiment_id: The notebook experiment ID of the experiment.
        :param new_owner_username: The new owner's username.
        """
        sub_path: str = self.user.build_url(['eln', 'changeOwner', str(eln_experiment_id), new_owner_username])
        response = self.user.post(sub_path)
        self.user.raise_for_status(response)

    def get_protocol_template_info_list(self, query: ProtocolTemplateQuery) -> list[ProtocolTemplateInfo]:
        """
        Get a list of protocol templates using the provided criteria to search for templates in the app.

        :param query: The search criteria for the protocol templates.
        :return: A list of protocol templates matching the search criteria.
        """
        sub_path: str = self.user.build_url(['eln', 'protocoltemplate'])
        response = self.user.post(sub_path, payload=query.to_json())
        self.user.raise_for_status(response)
        json_list: list[dict[str, Any]] = response.json()
        return [ProtocolTemplateInfo.from_json(x) for x in json_list]

    def add_protocol_template(self, exp_id: int, protocol_template: int, position: ElnEntryPosition) -> list[ExperimentEntry]:
        """
        Adds the entries from a protocol template to the given ELN experiment at the given position.

        :param exp_id: The notebook experiment ID of the experiment.
        :param protocol_template: The ID of the protocol template to add to the experiment.
        :param position: The position in the experiment where the protocol template should be added to the experiment.
            The first entry from the template will be added in this position and all subsequent entries will be added
            after it.
        :return: A list of the newly added experiment entries in the ELN experiment.
        """
        sub_path = self.user.build_url(['eln', 'addProtocolTemplate', str(exp_id), str(protocol_template)])
        response = self.user.post(sub_path, payload=position.to_json())
        self.user.raise_for_status(response)
        json_list: list[dict[str, Any]] = response.json()
        return [ExperimentEntryParser.parse_experiment_entry(x) for x in json_list]

    def get_field_set_info_list(self) -> List[ElnFieldSetInfo]:
        """
        Get a list of field set info from the system.

        :return: A list of all field set info in the system.
        """
        sub_path = self.user.build_url(['eln', 'enbFieldSet', 'infolist'])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        json_list: list[dict[str, Any]] = response.json()
        return [ElnFieldSetInfo.from_json(x) for x in json_list]

    def get_predefined_fields_from_field_set_id(self, field_set_id: int) -> list[AbstractVeloxFieldDefinition]:
        """
        Get a list of field definitions for the fields that are present in a field set.

        :param field_set_id: The system generated ID for the field set.
        :return: A list of field definitions for the fields in the matching field set.
        """
        sub_path = self.user.build_url(['eln', 'enbFieldSet', 'fields', str(field_set_id)])
        response = self.user.get(sub_path)
        self.user.raise_for_status(response)
        json_list: list[dict[str, Any]] = response.json()
        return [FieldDefinitionParser.to_field_definition(x) for x in json_list]
