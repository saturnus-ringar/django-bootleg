

def add_unique(li1, li2):
    for value in li2:
        if value not in li1:
            li1.append(value)

    return li1


def remove_duplicates(li):
    my_set = set()
    res = []
    for e in li:
        if e not in my_set:
            res.append(e)
            my_set.add(e)
    return list(res)


def remove_empty(li):
    return [x for x in li if x]


def remove_short(li, length=1):
    cleaned = []
    for string in li:
        if len(string) > length:
            cleaned.append(string)

    return cleaned


def to_lowercase(li):
    lowercase = []
    for string in li:
        lowercase.append(string.lower())
    return lowercase


def querysets_to_list(queryset1, queryset2):
    objects = []
    for obj in queryset1:
        objects.append(obj)
    for obj in queryset2:
        objects.append(obj)

    return objects
