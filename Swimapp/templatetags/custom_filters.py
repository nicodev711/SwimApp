from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def url_with_query(view_name, **kwargs):
    url = reverse(view_name)
    querystring = '&'.join([f"{key}={value}" for key, value in kwargs.items()])
    return f"{url}?{querystring}"
