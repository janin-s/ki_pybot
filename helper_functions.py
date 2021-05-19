import os
import json
from typing import Union

DIR = "data_files"


def reset_file(file: str):
    if file.__contains__("wichtel_list"):
        with open(file, "w") as f:
            json.dump([], f)
        return
    with open(file, "w") as f:
        json.dump({}, f)


def get_file(file: str):
    file_path = os.path.join(DIR, file)
    with open(file_path, "r") as f:
        file_dict = json.load(f)
    return file_dict


async def add_entry(file: str, key: Union[int, str], line: Union[int, str]):
    file_path = os.path.join(DIR, file)
    with open(file_path, "r") as fr:
        file_dict: dict = json.load(fr)

    file_dict[str(key)] = str(line)

    with open(file_path, "w") as fw:
        json.dump(file_dict, fw, separators=(',', ': '), indent=4)

    return f"added line {line} with key {key} to {file}"


def add_entry_unsync(file: str, key: Union[int, str], line: Union[int, str]):
    file_path = os.path.join(DIR, file)
    with open(file_path, "r") as fr:
        file_dict: dict = json.load(fr)

    file_dict[str(key)] = str(line)

    with open(file_path, "w") as fw:
        json.dump(file_dict, fw, separators=(',', ': '), indent=4)

    return f"added line {line} with key {key} to {file}"


def get_entry(file: str, key: Union[int, str]):
    file_path = os.path.join(DIR, file)
    with open(file_path, "r+") as f:
        file_dict: dict = json.load(f)

    try:
        entry = file_dict[str(key)]
    except KeyError:
        entry = "no entry for this key"

    output = (str(key), str(entry))
    return output


async def remove_entry(file: str, key: Union[int, str]):
    file_path = os.path.join(DIR, file)
    with open(file_path, "r") as fr:
        file_dict: dict = json.load(fr)

    try:
        entry = file_dict.pop(str(key))
    except KeyError:
        entry = "not found"

    with open(file_path, "w") as fw:
        json.dump(file_dict, fw, separators=(',', ': '), indent=4)
    return f"removed entry {entry} with key {key} from {file}"


def print_dict(dic: dict) -> str:
    output: str = ""
    for key, value in dic.items():
        output += f"{key} | {value}\n"
    return output


