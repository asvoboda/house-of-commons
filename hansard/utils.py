import collections


def unique(old_list):
    known = set()
    new_list = []
    for item in old_list:
        if item is None:
            continue
        m_id = item.id
        if m_id in known:
            continue
        new_list.append(item)
        known.add(m_id)
    return new_list


def top(m_list, number):
    counter = collections.Counter(m_list)
    return [i[0] for i in counter.most_common(number)]


def serialize_list(list_obj):
    return [l.serialize for l in list_obj]
