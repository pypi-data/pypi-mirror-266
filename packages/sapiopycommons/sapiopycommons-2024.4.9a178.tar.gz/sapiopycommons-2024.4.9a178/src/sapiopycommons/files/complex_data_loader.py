import io

from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext


class CDL:
    @staticmethod
    def load_cdl(context: SapioWebhookContext, config_name: str, file_name: str, file_data: bytes | str) \
            -> list[int]:
        """
        Create data records from a file using one of the complex data loader (CDL) configurations in the system.

        :param context: The current webhook context.
        :param config_name: The name of the CDL configuration to run.
        :param file_name: The name of the file being read by the CDL.
        :param file_data: A string or bytes of the file to be read by the CDL.
        :return: A list of the record IDs of the data records created by the CDL.
        """
        sub_path = "/ext/cdl/load"
        params = {
            "configName": config_name,
            "fileName": file_name
        }
        with io.StringIO(file_data) if isinstance(file_data, str) else io.BytesIO(file_data) as data_stream:
            response = context.user.post_data_stream(sub_path, params=params, data_stream=data_stream)
        context.user.raise_for_status(response)
        # The response content is returned as bytes for a comma separated string of record IDs.
        return [int(x) for x in bytes.decode(response.content).split(",")]
