import fileinput
import os
import json
from datetime import datetime
from typing import Union

DIR = "data_files"


async def are_characters_unique(s):
    # hilfsfunktion dreist von g4g geklaut und wild hässlich gemacht
    # https://www.geeksforgeeks.org/efficiently-check-string-duplicates-without-using-additional-data-structure/
    # An integer to store presence/absence
    # of 26 characters using its 32 bits
    checker = 0
    num_checker = 0
    # ?, !, +, -
    special = list(map(lambda x: False, range(0, 4)))
    s = s.lower()
    for c in s:
        ascii_value = ord(c)
        if ascii_value < 97 or ascii_value > 122:
            if 48 <= ascii_value <= 57:
                val1 = ascii_value - ord('0')
                # If bit corresponding to current
                # character is already set
                if (num_checker & (1 << val1)) > 0:
                    return False
                # set bit in checker
                num_checker |= (1 << val1)

            elif ascii_value == 63:
                if special[0]:
                    return False
                else:
                    special[0] = True
            elif ascii_value == 33:
                if special[1]:
                    return False
                else:
                    special[1] = True
            elif ascii_value == 43:
                if special[2]:
                    return False
                else:
                    special[2] = True
            elif ascii_value == 45:
                if special[3]:
                    return False
                else:
                    special[3] = True
            else:
                return False

        else:
            val = ascii_value - ord('a')

            # If bit corresponding to current
            # character is already set
            if (checker & (1 << val)) > 0:
                return False

            # set bit in checker
            checker |= (1 << val)

    return True


def get_unicode_id(c):
    c = c.lower()
    o = ord(c)
    if 97 <= o <= 122:
        return chr(127462 + (o - 97))
    if 48 <= o <= 57:
        return c + chr(65039) + chr(8419)
    if o == 63:
        return '\U00002753'
    if o == 33:
        return '\U00002757'
    if o == 43:
        return '\U00002795'
    if o == 45:
        return '\U00002796'
    return '\U00002753'


def reset_file(file: str):
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
