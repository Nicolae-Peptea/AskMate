import connection


def generate_list(parameter):
    return [line for line in parameter]


def add_id(dbase_len, elem_to_add):
    new_id = ('id', len(dbase_len) + 1)
    elem_to_add.insert(0, new_id)
    return dict(elem_to_add)


list_to_test = ['gg','nn','ii']

def add_first_elem(lista):
    for times in range(3):
        lista.insert(0, 'gigel')

    return  lista

print (add_first_elem(list_to_test))