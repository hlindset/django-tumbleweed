import re
from django.conf import settings
from django import template
from haystack.query import SearchQuerySet

register = template.Library()

TAG_FILTER  = getattr(settings, 'TUMBLEWEED_TAG_FILTER', None)
TAG_DATE_FIELD = getattr(settings, 'TUMBLEWEED_TAG_DATE_FIELD', 'pub_date')

class LatestTumblesNode(template.Node):
    def __init__(self, tumble_count, var_name):
        self.tumble_count = tumble_count
        self.var_name = var_name
    def render(self, context):
        sqs = SearchQuerySet().all()
        if TAG_FILTER is not None:
            sqs = sqs.filter(**TAG_FILTER)
        sqs = sqs.order_by('-%s' % TAG_DATE_FIELD)[:self.tumble_count]
        context[self.var_name] = sqs
        return ''

@register.tag(name='get_latest_tumbles')
def get_latest_tumbles(parser, token):
    """
    Returns a list of the latest tumbles and puts it in a context variable.
    Accepts argument for limiting the number of results returned.
    
    Syntax::
    
        {% get_latest_tumbles <number> as <var> %}
    
    Example::
    
        # Get last 10 tumbles
        {% get_latest_tumbles 10 as latest_tumbles %}
    """
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(\d*?) as (\w+)', arg)
    if not m:
        raise template.TemplateSyntaxError, "%s tag had invalid arguments" % tag_name
    tumble_count, var_name = m.groups()
    try:
        tumble_count = int(tumble_count)
    except ValueError:
        raise template.TemplateSyntaxError, "%s tag's first argument should be an integer" % tag_name
    return LatestTumblesNode(tumble_count, var_name)