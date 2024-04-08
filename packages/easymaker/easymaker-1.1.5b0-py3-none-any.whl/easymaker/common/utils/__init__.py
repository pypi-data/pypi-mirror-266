from easymaker.common.exceptions import EasyMakerError


def from_name_to_id(list: list, name: str) -> str:
    for item in list:
        if item["name"] == name:
            return item["id"]

    raise EasyMakerError(f"Invalid name : {name}")
