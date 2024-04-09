"""
This module contains the set of ranchcomputing exceptions.
"""


class RanchException(Exception):
    """ranchcomputing Exception"""


class InvalidKeyException(RanchException):
    """ranchcomputing InvalidKeyException Exception"""


class EmptySafeException(RanchException):
    """ranchcomputing EmptySafeException Exception



    :param RanchException: _description_
    :type RanchException: _type_
    """

    def __init__(self, message: str, data: dict):
        """_summary_



        :param message: _description_
        :type message: str
        :param data: _description_
        :type data: dict
        """
        super().__init__(f"Error: {message}")
        self.data = data
