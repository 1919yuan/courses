import os
#import webapp2
import jinja2
import re
#from urlparse import urlparse
#from google.appengine.ext import db
#from google.appengine.api import memcache
#import string
#import random
#import hmac
#import datetime
#import json
#import time
#import logging

#templates
template_dir=os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

#variables
site_title='CS 253 Final wiki'
message404=r'<h1>404 Not Found</h1>The resource could not be found.'
allow_anon_edit=True
