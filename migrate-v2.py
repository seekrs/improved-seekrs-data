#!/usr/bin/env python3

import os
import sys
import json
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from dc_schema import get_schema


# @dataclass_json
@dataclass
class UserLoginOverrideData:
    prefix: str = None
    suffix: str = None
    login: str = None
    separator: str = None
    full: str = None


# @dataclass_json
@dataclass
class UserImageOverrideData:
    profile: str = None
    banner: str = None


# @dataclass_json
@dataclass
class UserBadgeBackgroundData:
    type: str = field(default="color")
    value: str = field(default="#000000")


# @dataclass_json
@dataclass
class UserBadgeOverrideData:
    text: str
    background: UserBadgeBackgroundData = field(default_factory=UserBadgeBackgroundData)


# @dataclass_json
@dataclass
class UserOverrideData:
    login: UserLoginOverrideData = field(default_factory=UserLoginOverrideData)
    images: UserImageOverrideData = field(default_factory=UserImageOverrideData)
    badges: list[UserBadgeOverrideData] = field(default_factory=list)


# @dataclass_json
@dataclass
class UserData:
    override: UserOverrideData = field(default_factory=UserOverrideData)


def clean_nones(value):
    """
    Recursively remove all None values from dictionaries and lists, and returns
    the result as a new dictionary or list.
    """
    if isinstance(value, list):
        return [clean_nones(x) for x in value if x is not None]
    elif isinstance(value, dict):
        return {
            key: clean_nones(val)
            for key, val in value.items()
            if val is not None and len(clean_nones(val)) > 0
        }
    return value


if __name__ == '__main__':
    data = "v2-ext-data"
    if not os.path.exists(data):
        os.system(f"git clone https://github.com/seekrs/improved-seekrs.git {data}")

    data = data + "/data"
    user_data = defaultdict(UserData)

    # gather v2 data
    badges = json.load(open(data + "/badges.json"))
    for badge in badges:
        user, tag, color = badge["user"], badge["tag"], badge["color"]
        user_data[user].override.badges.append(
            UserBadgeOverrideData(
                text=tag,
                background=UserBadgeBackgroundData(type="color", value=color)
            )
        )
    logins = json.load(open(data + "/titles.json"))
    for login in logins:
        user = login["user"]
        if "format" in login:
            if "%" in login["format"]:
                user_data[user].override.login.full = login["format"] \
                    .replace("%prefix%", login.get("prefix", "")) \
                    .replace("%suffix%", login.get("suffix", "")) \
                    .replace("%user%", user)
            else:
                user_data[user].override.login.login = login["format"]
        else:
            user_data[user].override.login = UserLoginOverrideData(
                prefix=login.get("prefix"),
                suffix=login.get("suffix"),
                login=None,
                separator=None,
                full=None,
            )
    requests_overrides = json.load(open(data + "/requests-overrides.json"))
    for request in requests_overrides:
        target = request["target"]
        target_type = target.get("type")
        if target_type is None or target_type != "userProfile":
            print(f"Skipping request override '{target_type}' value={target['value']}")
            continue
        user = target["value"]
        url = request["replaceBy"]
        user_data[user].override.images.profile = url


    # write v3 data
    os.makedirs("data/users", exist_ok=True)
    for user, user_data in user_data.items():
        if " " in user: # old compat for titles, disregard
            continue
        json.dump(clean_nones(asdict(user_data)), open(f"data/users/{user}.json", "w"), indent=4)

    json.dump(get_schema(UserData), open("data/schemas/user.json", "w"), indent=4)
