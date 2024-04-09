"""Module connection"""

import os
from ranch.exceptions import RanchException
from ranch.uploadJob import UploadJob
from ranch.job import Job
from ._retry import retry

import requests
import boto3
from requests.adapters import HTTPAdapter


SWEB_URL = "https://www.ranchcomputing.com/"
TIME_OUT = 5  # TODO add time out to the env variable

endpoint_url = "http://10.0.0.1:80"  # TODO replace with DNS server
# endpoint_url = "https://storage.ranchcomputing.com"


class Connect(object):
    def __init__(self, api_key: str) -> None:
        """Connect with the user authentication token (API Key) found in your user
        dashboard under the settings tab. It is recommended to store this
        token in environment variables or a configuration file.
        Your API token is personal and should be securely kept.


        :param api_key:  Personal API Key.
        :type api_key: str
        """
        self.api_key = api_key.strip()
        self._session = requests.session()
        s3_session = boto3.session.Session()
        self._email = self.get_email
        self._s3_client = s3_session.client(
            "s3",
            aws_access_key_id=self._email,
            aws_secret_access_key=self.api_key,
            endpoint_url=endpoint_url,
            verify=False,
        )

    @property
    def _api_key(self) -> str:
        """Get personal API Key


        :return: API Key
        :rtype: str
        """
        return self.api_key

    def get_prioritys(self, farm: str = "cpu") -> dict:
        """Retrieve the list of priorities utilized in the farm.
        The farm type may vary, depending on whether the renderer
        used in the scene is CPU-base or GPU-base.


        :param farm: The name of the farm, defaults to "cpu"
        :type farm: str, optional
        :return: List of priorities within the specified farm
        :rtype: dict
        """
        url = f"api/ranchtools/farms/{farm}.json"
        return self._get(url=url).json()

    @property
    def get_cpu_rendering_occupation(self) -> int:
        """Retrieve the number of jobs currently running on the CPU-based farm.


        :return: Number of jobs in the rendering state
        :rtype: int
        """
        response = self.get_prioritys("cpu")
        return response.get("occupation")["rendering"]

    @property
    def get_cpu_queued_occupation(self) -> int:
        """Retrieve the number of jobs currently in the queued
        
        
        :return: number of jobs
        :rtype: int
        """
        response = self.get_prioritys("cpu")
        return response.get("occupation")["queued"]

    def get_priority(self, priority: str = "cpu-low") -> int:
        """Retrieve the ID associated with the given priority.
        
        
        :param priority: The name of priority, defaults to "cpu-low"
        :type priority: str, optional
        :return: The ID
        :rtype: int
        """
        # TODO add check for priority string if farm existes
        priority_lower = priority.split("-")[1].lower()
        farm = priority.split("-")[0].lower()
        prioritys = self.get_prioritys(farm)
        for prio in prioritys.get("priorities"):
            if priority_lower == prio["name"].split("-")[1].lower():
                return prio["id"]
        return 1  # TODO handle priorty error

    def get_renderer_id(self, software: str, software_version: str, renderer_name: str) -> int:
        """Retrieve the ID of the renderer used with a given software version.
        
        
        :param software: The name of the software used
        :type software: str
        :param software_version: The version of the software
        :type software_version: str
        :param renderer_name: The name of the renderer
        :type renderer_name: str
        :return: The renderer ID
        :rtype: int
        """
        url = f"api/ranchtools/ranchecker/{software}.json"
        releases = self._get(url=url).json()
        for release in releases["application"]["releases"]:
            if release["version"] == software_version:
                renderers = release["renderers"]
                for rendere in renderers:
                    if rendere["name"] == renderer_name:
                        return rendere["id"]
        # TODO check exception
        return 0

    @property
    def get_email(self) -> str:
        """Retrieve the email address of the user currently logged in with the provided API key.
        
        
        :return: Email address
        :rtype: str
        """
        url = "api/projects/downloadable?secure"  # TODO get url from endpoint
        response = self._get(url=url)
        try:
            email = response.json().get("account")["email"]
            return email
        except:
            return ""

    @_api_key.setter
    def _api_key(self, api_key: str) -> None:
        """Set the user API key in the connection
        
        
        :param api_key: User API key
        :type api_key: str
        """
        self.api_key = api_key.strip()

    def _set_header(self, api_key: str) -> dict:
        """Set header


        :param api_key: User API key
        :type api_key: str
        :return: header
        :rtype: dict
        """
        headers = {"x-auth-token": api_key, "Content-type": "application/json", "Accept": "application/json"}
        return headers

    def create_job(
        self,
        archive_path: str,
        job_name: str,
        priority: str,
        software: str,
        software_version: str,
        renderer_name: str,
    ):
        """Create a new job in the user account
        

        :param archive_path: Destination for the archive prepared by Ranchecker.
        :type archive_path: str
        :param job_name: Name of new created job
        :type job_name: str
        :param priority: The priority name
        :type priority: str
        :param software: Software name
        :type software: str
        :param software_version: Software version
        :type software_version: str
        :param renderer_name: Renderer name
        :type renderer_name: str
        :return: Job
        :rtype: job(:class:`~ranch.job.Job`)
        """
        job_renderer_id = self.get_renderer_id(software, software_version, renderer_name)
        job_priority = self.get_priority(priority)
        return Job(self, archive_path, job_name, job_priority, job_renderer_id)

    # @retry
    def _post(self, url: str, data: dict = {}) -> dict:
        """_summary_

        :param url: _description_
        :type url: str
        :param data: _description_
        :type data: dict
        """
        _url = SWEB_URL + url
        # self._session.mount(SWEB_URL, HTTPAdapter(max_retries=50))
        headers = self._set_header(self._api_key)
        self._session.headers.update(headers)
        try:
            return self._session.post(_url, headers=headers, json=data, timeout=TIME_OUT)
        except requests.ConnectionError as e:
            raise RanchException("Internet connection check failed")

    def _get(self, url: str, data: dict = {}) -> dict:
        """_summary_

        :param url: _description_
        :type url: str
        :param data: _description_
        :type data: dict
        """
        _url = SWEB_URL + url
        # self._session.mount(SWEB_URL, HTTPAdapter(max_retries=50))
        headers = self._set_header(self._api_key)
        self._session.headers.update(headers)
        try:
            return self._session.get(_url, headers=headers, data=data, timeout=TIME_OUT)
        except requests.ConnectionError as e:
            raise RanchException("Internet connection check failed")

    def submit(self, job: Job) -> bool:
        """Submit the job created by the user to the Ranch Render Farm, along with the associated
        data generated by the job and specifying the destination for the archive.
        
        
        :param job: The job created by the user
        :type job: job(:class:`~ranch.job.Job`)
        :return: True if the job was successfully uploaded to the server.
        :rtype: bool
        """
        if not os.path.exists(job.get_archive_path):
            return False
        job_name_extension = os.path.splitext(os.path.basename(job.get_archive_path))[1]
        job_name_ext = job.get_job_name + job_name_extension

        response = job.create()

        if not response.json().get("success"):
            # TODO
            return False
        else:
            metadata = response.json().get("metadata")
            metadata["uploader_name"] = "racnhcomputing python SDK"
            metadata["uploader_version"] = "2.0.0"
            metadata["filename"] = job_name_ext

            tuspload = response.json().get("tuspload")
            upload = UploadJob(
                endpoint=tuspload["endpoint"],
                chunk_size=tuspload.get("chunkSize", None),
                file_path=job.get_archive_path,
                metadata=metadata,
            )
            if upload.run():
                return True
        return False

    def buckets(self) -> list:
        """Get the list of buckets.
        
        :return: list bucket
        :rtype: list(:class:`~ranch.bucket.Bucket`). # TODO
        :raise: RanchException("") # TODO
        """
        if self._s3_client is None:
            raise RanchException("") # TODO

        return self._s3_client.list_buckets()

    def _call_api(self, url: str, request) -> dict:
        pass
