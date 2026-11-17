from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='rupiah')
def rupiah(val):
    if val is None or val == '':
        return 'Rp 0'
    try:
        val = Decimal(str(val))
        formatted = f"{val:,.0f}".replace(',', '.')
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return f"Rp {val}"

@register.filter(name='angka_id')
def angka_id(val):
    if val is None or val == '':
        return '0'
    try:
        val = Decimal(str(val))
        return f"{val:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return str(val)

@register.filter(name='get_item')
def get_item(dictionary, key):
    if dictionary and hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None
