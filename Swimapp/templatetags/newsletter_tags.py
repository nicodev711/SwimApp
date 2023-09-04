from django import template
from mysite.forms import SubscriberForm

register = template.Library()


@register.inclusion_tag('mysite/subscriber.html')  # Replace with your template path
def footer_newsletter_form():
    form = SubscriberForm()
    return {'form': form}
