from django import template

register = template.Library()


@register.filter(name="get_dict_value")
def get_dict_value(d, key):
    return d.get(key)


@register.filter(name="get_item_count")
def get_item_count(li, i):
    item = li[i]
    count = li[: i + 1].count(item) - 1
    return count
