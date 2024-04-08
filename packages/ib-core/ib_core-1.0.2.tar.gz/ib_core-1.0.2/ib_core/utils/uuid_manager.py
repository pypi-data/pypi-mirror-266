from uuid import UUID


def is_valid_uuid(uuid_to_check, version=4):
    """
    Check if uuid_to_check is a valid UUID.

     Parameters
    ----------

    uuid_to_test : str\n
    version : {1, 2, 3, 4}

     Returns
    -------

    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    """

    try:
        uuid_obj = UUID(uuid_to_check, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_check
