from __future__ import annotations

import re
from enum import Enum
from typing import Any, Callable, IO, cast
from weakref import WeakValueDictionary

from sapiopylib.rest.pojo.DataRecord import DataRecord

from sapiopylib.rest.pojo.webhook.ClientCallbackResult import InputSelectionResult, ClientCallbackResultParser

from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import FilePromptRequest, DisplayPopupRequest, \
    MultiFilePromptRequest, DataRecordSelectionRequest, TableEntryDialogRequest, DataRecordDialogRequest, \
    FormEntryDialogRequest, ListDialogRequest, OptionDialogRequest, InputSelectionRequest

from sapiopylib.rest.User import SapioUser

class ClientCallback:
    user: SapioUser

    __instances: WeakValueDictionary[SapioUser, ClientCallback] = WeakValueDictionary()
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
        if self.__initialized:
            return
        self.user = user
        self.__initialized = True

    def display_info(self, msg: str) -> None:
        """
        Displays the provided method to the current user in a dialog.  This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param msg: The message to be displayed.
        """
        url = '/clientcallback/display/info'
        response = self.user.post(url, payload=msg, is_payload_plain_text=True)
        self.user.raise_for_status(response)

    def display_warning(self, msg: str) -> None:
        """
        Displays the provided warning message to the current user in a dialog. This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param msg: The warning message to be displayed.
        """
        url = '/clientcallback/display/warning'
        response = self.user.post(url, payload=msg, is_payload_plain_text=True)
        self.user.raise_for_status(response)

    def display_error(self, msg: str) -> None:
        """
        Displays the provided error message to the current user in a dialog. This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param msg: The error message to be displayed.
        """
        url = '/clientcallback/display/error'
        response = self.user.post(url, payload=msg, is_payload_plain_text=True)
        self.user.raise_for_status(response)

    def display_popup(self, request: DisplayPopupRequest) -> None:
        """
        Display a toastr popup message in user's log in session screen.
        :param request: The request to be displayed.
        """
        url = '/clientcallback/display/popup'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)

    def show_file_dialog(self, request: FilePromptRequest, data_sink: Callable[[bytes], None]) -> str | None:
        """
        Displays a file prompt dialog to the current user. This method is only available when using the credentials provided in the context of a webhook endpoint.
        The file dialog will be displayed with the options provided in the request. User's browser will upload this file which will be consumed by the data sink.
        :param request: The request for the file prompt dialog.
        :param data_sink: The data sink the process the incoming data chunks in sequence.
        """
        url = '/clientcallback/filedialog'
        response = self.user.consume_octet_stream_post(url, data_sink, payload=request.to_json())
        self.user.raise_for_status(response)
        header: str | None = response.headers.get("Content-Disposition")
        if not header:
            return None
        match = re.search("attachment; filename=\"(.+)\"", header)
        if not match:
            return None
        return match.group(1)

    def get_file(self, fake_file_path: str, data_sink: Callable[[bytes], None]) -> None:
        """
        Retrieve a file provided by a fake file path that is only valid in this session.
        :param fake_file_path: The fake file path that points to the file content in this session.
        :param data_sink: The data sink the process the incoming data chunks in sequence.
        """
        url = '/clientcallback/file'
        params = {'filePath': fake_file_path}
        response = self.user.consume_octet_stream_get(url, data_sink, params=params)
        self.user.raise_for_status(response)

    def show_multi_file_dialog(self, request: MultiFilePromptRequest) -> list[str] | None:
        """
        Prompt the user (client) for a file path or list of file paths with a file dialog that allows multiple
        selection.  This method is only available when using the credentials provided in the context of a webhook endpoint.
        The file dialog will be displayed with the options provided in the request.

        :param request:  the options for the file dialog
        :return: the list of file names (full paths) if the user selected something, or null if they hit cancel
        """
        url = '/clientcallback/multifiledialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        return self.user.get_json_data_or_none(response)

    def send_file(self, default_file_name: str, request_file_name: bool, data: IO) -> None:
        """
        Send a file to the user in the system that invoked the webhook.
        This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param default_file_name: The default name of the file being sent.
        :param request_file_name: Whether the callback should ask the user to provide a file name for the sent file.
        :param data: The file stream to send to the user. The mode of IO MUST BE 'rb' (read-binary), even if it is a text file.
        """
        mode: str = data.mode
        if mode != 'rb':
            raise IOError("When sending file through sapiopylib, the open mode must be of rb (read-binary) even for text files.")
        url = '/clientcallback/sendfile'
        params = {
            "defaultFileName": default_file_name,
            "requestFileName": request_file_name
        }
        response = self.user.post_data_stream(url, data, params)
        self.user.raise_for_status(response)

    def show_data_record_selection_dialog(self, request: DataRecordSelectionRequest) -> list[dict[str, Any]] | None:
        """
        Shows an input-selection dialog with a row for each of the given records.  Allows the user to select records
        using the dialog and returns their selection to the user. This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param request: The request containing the available records to select.
        :return: A list of the selected records.  If no records are selected, an empty list is returned.  If the user cancels the dialog, then None will be returned.
        """
        url = '/clientcallback/datarecordselectiondialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        return self.user.get_json_data_or_none(response)

    def show_table_entry_dialog(self, request: TableEntryDialogRequest) -> list[dict[str, Any]] | None:
        """
        Show a table dialog with the specified title, optional message and a table populated with default values
        that returns value entered by the user for each cell on the table.  The table is defined through attributes
        specified on the request provided to the method.
        The request defines the structure of the table and the request's field map list defines the data that will be displayed in the table when it is first displayed to the user.
        This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param request: the criteria object defining how the table should appear and function.
        :return: map of data entered by user keyed by data field name
        """
        url = '/clientcallback/tableentrydialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        return self.user.get_json_data_or_none(response)

    def data_record_form_view_dialog(self, request: DataRecordDialogRequest) -> bool:
        """
        Show a dialog with the specified title.  The dialog will display the given dataRecord using the provided
        DataTypeLayout.  This dialog can display all normal record toolbar buttons including save and cancel.  Use this
        when it is safe for the user transaction to be committed or rolled back. This method is only available when using the
        credentials provided in the context of a webhook endpoint.
        :param request: The criteria object that defines how this dialog will be displayed.  This criteria
        includes options to enable or disable core features, specify plugins that should be displayed, set the layout that should be used, set the title of the dialog, etc.
        :return: true if the OK button was pressed. false if the Cancel button was pressed by user.
        """
        url = '/clientcallback/dataRecordFormViewDialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        return self.user.get_json_data_or_none(response)

    def show_form_entry_dialog(self, request: FormEntryDialogRequest) -> dict[str, Any] | None:
        """
        Show a dialog with the specified title, optional message and list of controls that returns value entered by the
        user for each control.  The controls are built off of the TemporaryDataType that is created by the developer or
        that mirrors actual an actual type in the system, but the type does not have actual data record mappings.
        This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param request: options to use when displaying the dialog
        :return: map of data entered by user keyed by data field name. If user did not respond by existing the dialog, None is returned.
        """
        url = '/clientcallback/formentrydialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        return self.user.get_json_data_or_none(response)

    def show_list_dialog(self, request: ListDialogRequest) -> list[str] | None:
        """
        Show a list box to the user to make a selection from a list of choices.
        This method is only available when using the credentials provided in the context of a webhook endpoint.
        :param request: the details about how the dialog should be displayed
        :return: the list of selected strings, or None if they hit cancel
        """
        url = '/clientcallback/selectionlistdialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        return self.user.get_json_data_or_none(response)

    def show_option_dialog(self, request: OptionDialogRequest) -> int | None:
        """
        Show a dialog with the specified title, message and list of buttons that returns index of selected button.
        This method is only available when using the credentials provided in the context of a webhook endpoint.

        :param request: options to use when displaying the dialog
        :return: the index of the button that the user choose or {@code null} if the user cancelled the dialog.
        """
        url = '/clientcallback/custombuttondialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        return self.user.get_json_data_or_none(response)

    def show_input_selection_dialog(self, request: InputSelectionRequest) -> list[DataRecord] | None:
        """
        Shows an input-selection dialog with configurations for enabling tabs for tree navigation, reports, and quick search.
        Allows the user to select records using the dialog and returns their selection to the user.
        :param request: The request defining the options for the dialog
        :return: A list of the selected data records.  If no records are selected, an empty list is returned.  If the user cancels the dialog, then None will be returned.
        """
        url = '/clientcallback/inputselectiondialog'
        response = self.user.post(url, payload=request.to_json())
        self.user.raise_for_status(response)
        json = self.user.get_json_data_or_none(response)
        if not json:
            return None
        result = cast(InputSelectionResult, ClientCallbackResultParser.parse_client_callback_result(json))
        if result.user_cancelled:
            return None
        return result.selected_record_list
