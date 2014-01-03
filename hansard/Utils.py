import collections


def unique(list):
    known = set()
    newlist = []
    for item in list:
        if item is None:
            continue
        id = item.id
        if id in known:
            continue
        newlist.append(item)
        known.add(id)
    return newlist


def top(list, number):
    counter = collections.Counter(list)
    return [i[0] for i in counter.most_common(number)]


def serialize_list(list_obj):
    return [l.serialize for l in list_obj]
