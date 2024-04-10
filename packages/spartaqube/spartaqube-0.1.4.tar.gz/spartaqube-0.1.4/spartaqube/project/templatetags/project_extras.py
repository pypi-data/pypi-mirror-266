import json
from django import template
from django.utils.safestring import mark_safe
register=template.Library()
@register.filter(is_safe=True)
def replaceFilter(value,replaceStr):A=replaceStr.split('=>');B=A[0];C=A[1];return value
@register.filter(name='range')
def filter_range(start,end):return range(start,end)
@register.filter
def addstr(arg1,arg2):return str(arg1)+str(arg2)
@register.filter
def is_false(arg):return arg is False
@register.filter
def get_type(value):return type(value)
@register.simple_tag
def call_method(obj,method_name,*A):B=getattr(obj,method_name);return B(*A)
@register.filter(is_safe=True)
def js(obj):return mark_safe(json.dumps(obj))
@register.filter(name='json_loads')
def json_loads(value):return json.loads(value)
@register.filter
def replaceSpaceUnderscore(value):return value.replace(' ','_')
@register.filter
def replaceUnderscoreSeparator(value):return value.replace('_','-')
@register.filter
def hash(h,key):return h[key]
@register.simple_tag
def define(val=None):return val
@register.filter
def list_item(lst,i):
	try:return lst[i]
	except:return
@register.filter
def to_str(value):return str(value)
@register.filter
def get_item(dictionary,key):return dictionary.get(key).replace('/','\\')