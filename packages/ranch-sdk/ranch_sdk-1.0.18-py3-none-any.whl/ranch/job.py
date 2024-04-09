"""Module describing a Job."""


class Job(object):
    def __init__(
        self,
        connection,
        archive_path: str,
        job_name: str,
        priority: str,
        renderer_id: int,
    ) -> None:
        """_summary_



        :param connection: The user connection
        :type connection: Connection(:class:`~ranch.connection.Connect)
        :param archive_path: Destination for the archive prepared by Ranchecker.
        :type archive_path: str
        :param job_name: Name of new created job
        :type job_name: str
        :param priority: The priority
        :type priority: str
        :param renderer_id: The renderer ID
        :type renderer_id: int
        """
        self._connection = connection
        self.archive_path = archive_path
        self.job_name = job_name
        self.priority = priority
        self.renderer_id = renderer_id
        self._data = {}

    def set_email(self, email: str) -> str:
        """_summary_



        :param email: _description_
        :type email: str
        :return: _description_
        :rtype: str
        """
        self._data["email"] = email
        return email

    def set_priority(self, priority: str) -> int:
        """_summary_



        :param priority: _description_
        :type priority: str
        :return: _description_
        :rtype: int
        """
        self._data["priority_id"] = priority
        return priority

    def set_renderer_id(self, renderer_id: str) -> int:
        """_summary_
        
        
        
        :param renderer_id: _description_
        :type renderer_id: str
        :return: _description_
        :rtype: int
        """
        self._data["renderer_id"] = renderer_id
        return renderer_id

    def set_specific_frames(self, frames: str) -> dict:
        """_summary_



        :param frames: _description_
        :type frames: str
        :return: _description_
        :rtype: dict
        """
        specific_frames = {"type": "specific", "specific_frames": frames}
        self._data["frames"] = specific_frames
        return specific_frames

    @property
    def get_job_name(self) -> str:
        """_summary_
        
        
        
        :return: _description_
        :rtype: str
        """
        return self.job_name

    @property
    def get_archive_path(self) -> str:
        """_summary_



        :return: _description_
        :rtype: str
        """
        return self.archive_path

    def create(self) -> dict:
        """_summary_



        :return: _description_
        :rtype: dict
        """
        self._data["disclaimer"] = True
        self._data["email"] = self._connection.get_email
        self._data["renderer_id"] = self.renderer_id
        self._data["priority_id"] = self.priority
        return self._connection._post("api/projects", self._data)
