import base64
import io
import urllib.parse

from requests import Response
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class FileBridge:
    @staticmethod
    def read_file(context: SapioWebhookContext, bridge_name: str, file_path: str, base64_decode: bool = True) -> bytes:
        """
        Read a file from FileBridge.

        :param context: The current webhook context.
        :param bridge_name: The name of the bridge to use.
        :param file_path: The path to read the file from.
        :param base64_decode: If true, base64 decode the file. Files are by default base64 encoded when retrieved from
            FileBridge.
        :return: The bytes of the file.
        """
        sub_path = '/ext/filebridge/readFile'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        response = context.user.get(sub_path, params)
        context.user.raise_for_status(response)

        ret_val = response.content
        if base64_decode:
            ret_val = base64.b64decode(response.content)
        return ret_val

    @staticmethod
    def write_file(context: SapioWebhookContext, bridge_name: str, file_path: str, file_data: bytes | str) -> None:
        """
        Write a file to FileBridge.

        :param context: The current webhook context.
        :param bridge_name: The name of the bridge to use.
        :param file_path: The path to write the file to. If a file already exists at the given path then the file is
            overwritten.
        :param file_data: A string or bytes of the file to be written.
        """
        sub_path = '/ext/filebridge/writeFile'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        with io.StringIO(file_data) if isinstance(file_data, str) else io.BytesIO(file_data) as data_stream:
            # noinspection PyTypeChecker
            response = context.user.post_data_stream(sub_path, params=params, data_stream=data_stream)
        context.user.raise_for_status(response)

    @staticmethod
    def list_directory(context: SapioWebhookContext, bridge_name: str, file_path: str | None = "") -> list[str]:
        """
        List the contents of a FileBridge directory.

        :param context: The current webhook context.
        :param bridge_name: The name of the bridge to use.
        :param file_path: The path to read the directory from.
        :return: A list of name of files and folders in the directory.
        """
        sub_path = '/ext/filebridge/listDirectory'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        response: Response = context.user.get(sub_path, params=params)
        context.user.raise_for_status(response)

        response_body: list[str] = response.json()
        path_length = len(f"bridge://{bridge_name}/")
        return [urllib.parse.unquote(value[path_length:]) for value in response_body]

    @staticmethod
    def create_directory(context: SapioWebhookContext, bridge_name: str, file_path: str) -> None:
        """
        Create a new directory in FileBridge.

        :param context: The current webhook context.
        :param bridge_name: The name of the bridge to use.
        :param file_path: The path to create the directory at. If a directory already exists at the given path then an
            exception is raised.
        """
        sub_path = '/ext/filebridge/createDirectory'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        response = context.user.post(sub_path, params=params)
        context.user.raise_for_status(response)
