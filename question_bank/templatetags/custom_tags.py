from django import template
from django.utils.text import slugify

register = template.Library()

@register.filter
def to_range(start, end=None):
    """
    Generates a range for use in Django templates.
    - Usage: {% for i in 1|to_range:6 %} → outputs 1 to 6
    """
    if end is None:
        return range(1, int(start) + 1)
    return range(int(start), int(end) + 1)

@register.filter
def get_user_data(data_list, email):
    """
    Retrieves a user's count of idioms or input suggestions from a list of dicts.
    - Usage: data_list|get_user_data:email
    """
    for data in data_list:
        if data.get('created_by__email') == email:
            return data.get('total_idioms') or data.get('total_suggestions', 0)
    return 0

@register.filter(name='get_dynamic_field')
def get_dynamic_field(instance, field_name):
    """
    Gets dynamic field value from a model instance.
    - Usage: instance|get_dynamic_field:"field_name"
    """
    return getattr(instance, field_name, '')

@register.filter(name='get_dynamic_attr')
def get_dynamic_attr(instance, field_name):
    """
    Alias for get_dynamic_field.
    - Usage: instance|get_dynamic_attr:"list_1_row1"
    """
    return getattr(instance, field_name, '')

@register.filter
def get_list_items(question, list_type):
    """
    Extracts non-empty list items for List-I or List-II (English).
    - Usage: question|get_list_items:"list_1"
    """
    items = []
    for i in range(1, 9):
        field_name = f"{list_type}_row{i}"
        item = getattr(question, field_name, None)
        if item:
            items.append(item.strip())
    return items

@register.filter
def get_list_items_hi(question, list_type):
    """
    Extracts non-empty Hindi list items for List-I or List-II.
    - Usage: question|get_list_items_hi:"list_1"
    """
    items = []
    for i in range(1, 9):
        field_name = f"{list_type}_row{i}_hi"
        item = getattr(question, field_name, None)
        if item and item.strip() and item.strip().lower() != "_hi":
            items.append(item.strip())
    return items

@register.filter
def slugify_filter(value):
    """
    Slugifies a string for safe URL usage.
    - Usage: {{ value|slugify_filter }}
    """
    return slugify(value)


# ✅ Enhanced Split Filter (supports comma, semicolon, or pipe)
@register.filter
def split(value, delimiter=None):
    """
    Splits a string into a list by the given delimiter.
    Automatically detects common separators (',', ';', '|') if none provided.
    Removes empty strings and trims spaces.
    Example:
        {{ "A, B; C|D"|split }}
        → ['A', 'B', 'C', 'D']
    """
    if not value:
        return []
    text = str(value).strip()
    if delimiter:
        parts = text.split(delimiter)
    else:
        # Auto-detect common delimiters
        for sep in [",", ";", "|"]:
            if sep in text:
                parts = text.split(sep)
                break
        else:
            parts = [text]
    return [p.strip() for p in parts if p.strip()]


@register.filter
def get_item(dictionary, key):
    """
    Safely get a value from a dictionary in Django templates.
    Usage: {{ my_dict|get_item:"key_name" }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []

@register.filter
def to_letter(value):
    """
    Converts 1 -> A, 2 -> B, 3 -> C, etc.
    Usage: {{ forloop.counter|to_letter }}
    """
    try:
        value = int(value)
        return chr(64 + value)  # A=65 in ASCII
    except Exception:
        return ''

@register.filter
def index(sequence, position):
    """
    Returns element at the given index from a list or tuple.
    Usage: {{ my_list|index:0 }}
    """
    try:
        return sequence[int(position)]
    except Exception:
        return ''

@register.filter
def trim(value):
    """
    Safely trims whitespace from both ends of a string.
    Usage: {{ value|trim }}
    """
    if isinstance(value, str):
        return value.strip()
    return value

@register.filter
def get_area_color(area_color_map, keyword):
    """Return area color for a keyword by checking area match."""
    if not area_color_map:
        return '#1fa83b'
    keyword_lower = keyword.strip().lower()
    for area, color in area_color_map.items():
        if area in keyword_lower:
            return color
    return '#1fa83b'
