import os

BYTES_IN_MEGABYTE = 1024**2
BYTES_IN_GIGABYTE = 1024**3

UNIX_OS_NAME = "posix"
WINDOWS_OS_NAME = "nt"


class Util:
    @staticmethod
    def convert_bytes_to_megabytes(file_size_bytes):
        return file_size_bytes / BYTES_IN_MEGABYTE

    @staticmethod
    def convert_bytes_to_gigabytes(file_size_bytes):
        return file_size_bytes / BYTES_IN_GIGABYTE

    @staticmethod
    def is_unix():
        return os.name == UNIX_OS_NAME

    @staticmethod
    def is_windows():
        return os.name == WINDOWS_OS_NAME

    @staticmethod
    def keep_prioritized_key_value_in_dict(dictionary, prioritized_key, fallback_key):
        if not dictionary.get(prioritized_key):
            dictionary[prioritized_key] = dictionary[fallback_key]
        del dictionary[fallback_key]

    @staticmethod
    def get_message_from_list(item_list, wrap_in="'"):
        if len(item_list) == 1:
            return f"{wrap_in}{item_list[0]}{wrap_in}"
        if len(item_list) == 2:
            return f"{wrap_in}{item_list[0]}{wrap_in} and {wrap_in}{item_list[1]}{wrap_in}"
        return (
            ", ".join([f"{wrap_in}{item}{wrap_in}" for item in item_list[:-1]])
            + f", and {wrap_in}{item_list[-1]}{wrap_in}"
        )
