#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
import secrets


class MasterlistUrls(Enum):
    """This class is used for the masterlist submodule. It provides all urls needed."""

    all_server_stats = "https://api.alt-mp.com/servers/info"
    all_servers = "https://api.alt-mp.com/servers"
    specific_server = "https://api.alt-mp.com/servers/{}"
    specific_server_average = "https://api.alt-mp.com/servers/{}/avg/{}"
    specific_server_maximum = "https://api.alt-mp.com/servers/{}/max/{}"


class Extra(Enum):
    """This class defines extra values."""

    user_agent = "AltPublicAgent"
    default_password = "17241709254077376921"


@dataclass
class Group:
    """This defines the group"""

    id: str
    name: str
    iconUrl: str
    pinned: bool


@dataclass
class RequestHeaders:
    """These are the common request headers used by the request function.
    They are commonly used to emulate an alt:V client.
    """

    host: str = ""
    user_agent: str = Extra.user_agent.value
    accept: str = "*/*"
    alt_debug: str = "false"
    alt_password: str = Extra.default_password.value
    alt_branch: str = ""
    alt_version: str = ""
    alt_player_name: str = secrets.token_urlsafe(10)
    alt_social_id: int = "0"
    alt_hardware_id2: str = secrets.token_hex(19)
    alt_hardware_id: str = secrets.token_hex(19)

    def __init__(self, server):
        self.alt_branch = server.branch
        self.alt_version = server.version
        self.host = server.address

    def to_dict(self):
        return {
            "Host": self.host,
            "Alt-Branch": self.alt_branch,
            "Alt-Debug": self.alt_debug,
            "Alt-Hardware-ID": self.alt_hardware_id,
            "Alt-Hardware-ID2": self.alt_hardware_id2,
            "Alt-Password": self.alt_password,
            "Alt-Player-Name": self.alt_player_name,
            "Alt-Social-ID": self.alt_social_id,
            "Alt-Version": self.alt_version,
            "User-Agent": self.user_agent,
            "Accept": self.accept,
            "Origin": f"http://{self.host}",
            "Connection": "close",
        }


class Permissions:
    """This is the Permission class used by get_permissions.

    Returns:
        Required: The required permissions of an alt:V server. Without them, you can not play on the server.
        Optional: The optional permissions of an alt:V server. You can play without them.
    """

    @dataclass
    class Required:
        """Required Permissions of an alt:V server.

        Attributes:
        ----------
            screen_capture (bool): This allows a screenshot to be taken of the alt:V process (just GTA) and any webview
            webrtc (bool): This allows peer-to-peer RTC inside JS
            clipboard_access (bool): This allows to copy content to users clipboard
        """

        screen_capture: bool = False
        webrtc: bool = False
        clipboard_access: bool = False

    @dataclass
    class Optional:
        """Optional Permissions of an alt:V server.

        Attributes:
        ----------
            screen_capture (bool): This allows a screenshot to be taken of the alt:V process (just GTA) and any webview
            webrtc (bool): This allows peer-to-peer RTC inside JS
            clipboard_access (bool): This allows to copy content to users clipboard
        """

        screen_capture: bool = False
        webrtc: bool = False
        clipboard_access: bool = False