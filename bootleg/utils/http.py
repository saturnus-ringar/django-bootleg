
def cast_param(request_data, param):
    value = request_data.get(param, None)
    ret_value = None
    if value:
        if value == "on" or value == "true":
            ret_value = True
        elif value == "unknown":
            ret_value = None
        elif value == "false":
            ret_value = False

    return ret_value
