"""Module describing a UploadJob."""

from tusclient import client


class UploadJob(object):
    def __init__(self, endpoint: str, chunk_size: int, file_path: str, metadata: dict) -> None:
        """_summary_



        :param endpoint: _description_
        :type endpoint: str
        :param chunk_size: _description_
        :type chunk_size: int
        :param file_path: _description_
        :type file_path: str
        :param metadata: _description_
        :type metadata: dict
        """
        super().__init__()
        tus_client = client.TusClient(endpoint)
        max_chunk_size = 100000001  # tuspy client will load this in memory
        if chunk_size is None or chunk_size > max_chunk_size:
            chunk_size = max_chunk_size

        self.uploader = tus_client.uploader(
            file_path=file_path,
            log_func="",
            retries=5,
            retry_delay=5,
            metadata=metadata,
            chunk_size=chunk_size,
        )

    def run(self) -> bool:
        """_summary_



        :return: _description_
        :rtype: bool
        """
        if not self.uploader:
            return False
        self.uploader.upload()
        return True
