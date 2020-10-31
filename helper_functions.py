import fileinput
from datetime import datetime


async def persistent_counter(caller="all"):
    # premium function
    # hilfsfunktion für shotcounter, wenn ohne argument globaler shared counter
    # evtl in Zukunft für persönliche Counter nutzbar: user-ID als parameter String

    # data stored like this: 'userid:shotcount'
    # shared counter with id 'all'

    if caller == "resetAll":
        for line in fileinput.input(r"data", inplace=True):
            if line.__contains__("all"):
                newline = "all:0"
                print(newline.strip())
            else:
                print(line.strip())
        fileinput.close()
        return 0
    else:
        found = False
        number: int = 0
        for line in fileinput.input(r"data", inplace=True):
            if line.__contains__(caller):
                found = True
                try:
                    number = int(line.split(':').__getitem__(1))
                except ValueError:
                    number = 0
                number = number + 1
                newline = caller + ":" + str(number)
                print(newline.strip())
            else:
                print(line.strip())
        fileinput.close()
        if not found:
            data = open(r"data", "a")
            data.write(caller + ":0")
            return 0
        return number


async def are_characters_unique(s):
    # hilfsfunktion dreist von g4g geklaut und wild hässlich gemacht
    # https://www.geeksforgeeks.org/efficiently-check-string-duplicates-without-using-additional-data-structure/
    # An integer to store presence/absence
    # of 26 characters using its 32 bits
    checker = 0
    # 0 to 9, ?, !, +, -
    numbers_and_special = list(map(lambda x: False, range(0, 15)))
    s = s.lower()
    for i in range(len(s)):
        ascii_value = ord(s[i])
        if ascii_value < 97 or ascii_value > 122:
            if 48 <= ascii_value <= 57:
                if numbers_and_special[ascii_value - 48]:
                    return False
                else:
                    numbers_and_special[ascii_value - 48] = True
            elif ascii_value == 63:
                if numbers_and_special[10]:
                    return False
                else:
                    numbers_and_special[10] = True
            elif ascii_value == 33:
                if numbers_and_special[11]:
                    return False
                else:
                    numbers_and_special[11] = True
            elif ascii_value == 43:
                if numbers_and_special[12]:
                    return False
                else:
                    numbers_and_special[12] = True
            elif ascii_value == 45:
                if numbers_and_special[13]:
                    return False
                else:
                    numbers_and_special[13] = True
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


async def set_punish_time(member_id: int, t: datetime):
    found = False
    for line in fileinput.input(r"punish_times", inplace=True):
        if line.__contains__(str(member_id)):
            found = True
            newline = str(member_id) + ";" + t.isoformat().strip()
            print(newline.strip())
        else:
            print(line.strip())
    fileinput.close()
    if not found:
        data = open(r"punish_times", "a")
        data.write(str(member_id) + ";" + t.isoformat().strip())


async def get_punish_time(member_id: int):
    with open(r"punish_times", "r") as file:
        lines = file.readlines()
        t = datetime.min
        for line in lines:
            if line.__contains__(str(member_id)):
                try:
                    t = datetime.fromisoformat(line.split(';').__getitem__(1).strip())
                except ValueError:
                    t = datetime.min
        return t
