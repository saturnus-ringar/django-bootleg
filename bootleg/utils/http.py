
def cast_param(request_data, param):
    value = request_data.get(param, None)
    ret_value = value
    if value:
        if value == "on" or value == "true":
            ret_value = True
        elif value == "unknown":
            ret_value = None
        elif value == "false":
            ret_value = False

    return ret_value


def get_model_args_from_request(model, request):
    args = {}
    # TODO: handle "created__gte" and "created__lte"
    for param in request.GET:
        value = cast_param(request.GET, param)
        if model.is_valid_search_field(param):
            if value or value is None or value is False:
                args[param] = value

    for m2m_field in model._meta.many_to_many:
        param = request.GET.get(m2m_field.name)
        if param:
            args[m2m_field.name + "__id"] = param

    return args
