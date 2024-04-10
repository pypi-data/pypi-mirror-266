# This test needs to be run by a webhook user. So it doesn't fit the regular unittest.testcase.
from sapiopylib.rest.utils.recorddatasinks import InMemoryRecordDataSink, InMemoryStringDataSink

from sapiopylib.rest.pojo.datatype.FieldDefinition import *

from sapiopylib.rest.utils.FormBuilder import FormBuilder

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import *

from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult

from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext

from sapiopylib.rest.WebhookService import AbstractWebhookHandler, WebhookConfiguration, WebhookServerFactory


class TestDisplayInfo(AbstractWebhookHandler):

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        client_callback.display_info("Info message 1\nInfo message 2")
        client_callback.display_warning("Info message 1\nInfo message 2")
        client_callback.display_error("Info message 1\nInfo message 2")
        client_callback.display_popup(DisplayPopupRequest("Test Title", "Test Message", PopupType.Success))
        return SapioWebhookResult(True)

class TestUserInputDialogs(AbstractWebhookHandler):

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        selected_option: int | None = client_callback.show_option_dialog(OptionDialogRequest("Select Input Dialog Option",
                                                               "Please make a selection in one of these options to test ^_^.",
                                                               ['Abort', 'Field Entry', 'Table Entry', 'List', 'Record IDV', 'Record Selection',
                                                                "Download", "Upload", "Upload Multiple", "Input Selection Search"]))
        if selected_option == 1:
            self.test_field_entry(context)
        elif selected_option == 2:
            self.test_table_entry(context)
        elif selected_option == 3:
            self.test_list(context)
        elif selected_option == 4:
            self.test_record_idv(context)
        elif selected_option == 5:
            self.test_record_selection(context)
        elif selected_option == 6:
            self.test_download_file_to_user(context)
        elif selected_option == 7:
            self.test_upload_file_from_user(context)
        elif selected_option == 8:
            self.test_multi_upload_file_from_user(context)
        elif selected_option == 9:
            self.test_input_selection_search_from_user(context)
        return SapioWebhookResult(True)

    def test_field_entry(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        fb: FormBuilder = FormBuilder()
        fb.add_field(VeloxStringFieldDefinition(fb.get_data_type_name(), "Test1", "Test 1"))
        fb.add_field(VeloxBooleanFieldDefinition(fb.get_data_type_name(), "Test2", "Test 2"))
        temp_dt = fb.get_temporary_data_type()
        user_entry_result: dict[str, Any] | None = client_callback.show_form_entry_dialog(FormEntryDialogRequest(
            "Test Form Entry", "This is a example form entry dialog", temp_dt))
        if not user_entry_result:
            client_callback.display_info("User has cancelled form entry")
        else:
            client_callback.display_info("User has entered: " + str(user_entry_result))

    def test_table_entry(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        fb: FormBuilder = FormBuilder()
        fb.add_field(VeloxStringFieldDefinition(fb.get_data_type_name(), "Test1", "Test 1"))
        fb.add_field(VeloxBooleanFieldDefinition(fb.get_data_type_name(), "Test2", "Test 2"))
        temp_dt = fb.get_temporary_data_type()
        initial_field_map_list: list[dict[str, Any]] = []
        initial_field_map_list.append({"Test1": "aaa", "Test2": True})
        initial_field_map_list.append({"Test1": "bbb", "Test2": False})
        user_entry_result = client_callback.show_table_entry_dialog(TableEntryDialogRequest(
            "Test Table Entry", "This is a example of table entry", temp_dt, initial_field_map_list))
        if not user_entry_result:
            client_callback.display_info("User has cancelled table entry")
        else:
            client_callback.display_info("User has entered: " + str(user_entry_result))

    def test_list(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        response = client_callback.show_list_dialog(ListDialogRequest("List Test", True, ["A", "B", "C", "D", "E"]))
        if response is None:
            client_callback.display_info("User has cancelled list dialog entry.")
        else:
            client_callback.display_info("User has selected: " + str(response))

    def test_record_idv(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        data_record_manager = context.data_record_manager
        root_dir_record = data_record_manager.query_system_for_record("Directory", 1)
        result = client_callback.data_record_form_view_dialog(DataRecordDialogRequest("Root Directory IDV", root_dir_record))
        if result:
            client_callback.display_info("User pressed OK in record IDV dialog.")
        else:
            client_callback.display_info("User has aborted record IDV dialog.")

    def test_record_selection(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        fb: FormBuilder = FormBuilder()
        fb.add_field(VeloxStringFieldDefinition(fb.get_data_type_name(), "Test1", "Test 1"))
        fb.add_field(VeloxBooleanFieldDefinition(fb.get_data_type_name(), "Test2", "Test 2"))
        temp_dt: TemporaryDataType = fb.get_temporary_data_type()
        initial_field_map_list: list[dict[str, Any]] = []
        initial_field_map_list.append({"Test1": "aaa", "Test2": True})
        initial_field_map_list.append({"Test1": "bbb", "Test2": False})
        selection_result = client_callback.show_data_record_selection_dialog(DataRecordSelectionRequest(
            "Test", "Tests", temp_dt.get_field_def_list(), initial_field_map_list, multi_select=True))
        if selection_result is None:
            client_callback.display_info("User has cancelled record selection.")
        else:
            client_callback.display_info("User has selected: " + str(selection_result))

    def test_download_file_to_user(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)

        with open('resources/NAC28735.fa', 'rb') as io:
            client_callback.send_file("downloaded.fa", True, io)

    def test_upload_file_from_user(self, context):
        user = context.user
        sink = InMemoryStringDataSink(user)
        sink.upload_single_file_to_webhook_server(FilePromptRequest("Upload me a text file please...", file_extension=".txt"))
        client_callback = DataMgmtServer.get_client_callback(user)
        client_callback.display_info("Here is what you have uploaded: \n" + sink.text)

    def test_multi_upload_file_from_user(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        fake_file_path_list = client_callback.show_multi_file_dialog(MultiFilePromptRequest("Upload me multiple text files please...", file_extension=".txt"))
        if not fake_file_path_list:
            return
        for fake_file_path in fake_file_path_list:
            sink = InMemoryStringDataSink(user)
            sink.consume_client_callback_file_path_data(fake_file_path)
            client_callback.display_info("Received file content for '" + fake_file_path + "':\n" + sink.text)

    def test_input_selection_search_from_user(self, context):
        user = context.user
        client_callback = DataMgmtServer.get_client_callback(user)
        result = client_callback.show_input_selection_dialog(InputSelectionRequest(data_type_name="Directory", dialog_message="Select One", multi_select=False))
        if result is None:
            client_callback.display_info("User did not select anything.")
        else:
            client_callback.display_info("User has selected: " + str(result))



config: WebhookConfiguration = WebhookConfiguration(verify_sapio_cert=False, debug=True)
config.register('/display_info_test', TestDisplayInfo)
config.register('/dialog_test', TestUserInputDialogs)

app = WebhookServerFactory.configure_flask_app(app=None, config=config)
app.run(host="0.0.0.0", port=8099)
