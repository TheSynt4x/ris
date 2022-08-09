def find_in_sql_tuple(result_set, field_to_find):
    to_find = [s[1] for s in result_set if s[0] == field_to_find]

    if to_find:
        return to_find[0]
