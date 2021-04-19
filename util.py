from datetime import datetime


def generate_list(parameter):
    return [line for line in parameter]


def pack_variables(elem_to_add, *args) -> dict:
    for item in args:
        elem_to_add.insert(0, item)
    return dict(elem_to_add)


def add_initial_attributes(dbase_len, elem_to_add):
    new_id = ('id', len(dbase_len) + 1)
    submission_time = ('submission_time', round(datetime.timestamp(datetime.now())))
    view_number = ('view_number', 0)
    vote_number = ('vote_number', 0)
    return pack_variables(elem_to_add, new_id, submission_time,
                          view_number, vote_number)
