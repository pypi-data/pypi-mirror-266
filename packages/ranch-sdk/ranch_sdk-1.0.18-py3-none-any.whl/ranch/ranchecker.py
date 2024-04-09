"""Module describing a Ranchecker."""

import os
import subprocess


class Ranchecker(object):
    def __init__(self) -> None:
        """_summary_"""
        pass

    def create_c4d_archive(
        self, software_commandline: str, g_licenseUsername: str, g_licensePassword: str, scene_destination: str
    ) -> bool:
        """_summary_



        :param software_commandline: _description_
        :type software_commandline: str
        :param g_licenseUsername: _description_
        :type g_licenseUsername: str
        :param g_licensePassword: _description_
        :type g_licensePassword: str
        :param scene_destination: _description_
        :type scene_destination: str
        :return: _description_
        :rtype: bool
        """
        user = "g_licenseUsername=" + g_licenseUsername
        passw = "g_licensePassword=" + g_licensePassword
        command = f"{software_commandline} {user} {passw} -sdk_scene_path {scene_destination}"
        subprocess.check_output(command, shell=True, text=True)
        vu_path = os.path.splitext(scene_destination)[0] + ".vuc"  # TODO support all vu*
        return vu_path
