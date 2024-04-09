from typing import Dict, Any


def get_key_from_value(obj: Dict, value: Any):
    for i in obj:
        if obj[i] == value:
            return i
    return None


if __name__ == "__main__":
    pass
