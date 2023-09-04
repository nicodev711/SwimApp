from django import template
from Swimapp.forms import SubscriberForm

register = template.Library()


@register.inclusion_tag('Swimapp/subscriber.html')  # Replace with your template path
def footer_newsletter_form():
    form = SubscriberForm()
    return {'form': form}
