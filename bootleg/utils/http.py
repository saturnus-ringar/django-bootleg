
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
    field_names = model.get_all_field_names()
    for param in request.GET:
        if param in field_names:
            value = cast_param(request.GET, param)
            if value or value is None or value is False:
                args[param] = value

    for m2m_field in model._meta.many_to_many:
        param = request.GET.get(m2m_field.name)
        if param:
            args[m2m_field.name + "__id"] = param

    return args
