# type: ignore
# Library
##############################################################
import hashlib as __hash
import os as __os
from typing import Dict as __Dict
from typing import NewType as __NewType
from typing import TypeVar as __TypeVar
from typing import Union as __Union

# Define type
##############################################################
Password = __NewType("Password", str)
Salt = __NewType("Salt", str)
Key = __NewType("Key", str)
Salt_V = __NewType("Salt_V", bytes)
Key_V = __NewType("Key_V", bytes)
Combo = __Dict[__Union[Salt, Key], __Union[Salt_V, Key_V]]


# Function
##############################################################
def password_hash(password: Password) -> Combo:
    """
    Generate hash for password
    """
    salt = __os.urandom(32)
    key = __hash.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=100000,
    )
    out = {
        "salt": salt,
        "key": key,
    }
    return out


def password_hash_check(
    password: Password,
    combo: Combo,
) -> bool:
    """
    Compare hashes between 2 passwords
    """
    if "salt" in combo and "key" in combo:
        salt = combo["salt"]
        compare_key = combo["key"]
    else:
        return None

    key = __hash.pbkdf2_hmac(
        hash_name="sha256",
        password=password.encode("utf-8"),
        salt=salt,
        iterations=100000,
    )

    if key == compare_key:
        return True
    else:
        return False


def tj():
    import json

    combo = password_hash("lmao")
    for k, v in combo.items():
        combo[k] = str(v)
    j = json.dumps(combo, indent=4)
    return j


if __name__ == "__main__":
    print(tj())
