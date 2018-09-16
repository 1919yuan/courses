from wiki_config import *
from wiki_database import *
from wiki_util import *
import webapp2
from urlparse import urlparse
from google.appengine.api import memcache
import json
import datetime
import time
import logging

class WikiHandler(webapp2.RequestHandler):
    def jsonrize_page(self, wikipage):
        d={}
        d['content']=wikipage.content
        d['created']=wikipage.created.strftime('%a, %d %b %Y %H:%M:%S')
        d['last_modified']=wikipage.last_modified.strftime('%a, %d %b %Y %H:%M:%S')
        d['path']=wikipage.path
        return json.dumps(d)

    def jsonrize_page_history(self, hists):
        s=[]
        for h in hists:
            d={}
            d['path']=h.page.path
            d['content']=h.content
            d['time']=h.vtime.strftime('%a, %d %b %Y %H:%M:%S')
            d['editor']=h.editor.name
            s.append(d)
        if len(s)==0:
            return ''
        if len(s)==1:
            s=s[0]
        return json.dumps(s)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        params['user']=self.user
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def set_cookie(self, name, val, expires=''):
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; expires=%s; Path=/' %(name, val, expires))

    def read_secure_cookie(self, name, salt):
        h=self.request.cookies.get(name)
        return h and check_hash(salt, h)

    def login(self, user):
        expires = datetime.datetime.now() + datetime.timedelta(days=10)
        self.set_cookie('user_id', 
                               make_hash(user.usalt,user.key().id()),
                               expires.strftime('%a, %d %b %Y %H:%M:%S'))

    def logout(self):
        expires = datetime.datetime.now() + datetime.timedelta(days=-10)
        self.set_cookie('user_id', '', 
                               expires.strftime('%a, %d %b %Y %H:%M:%S'))

    def memcache_get_page(self, path, update=False):
        memcache_key=unicode(path)
        pt=memcache.get(memcache_key)
        if pt is not None and not update:
            return [pt[0], int(time.mktime(time.gmtime())-pt[1])]
        else:
            page=Wikipage.all().filter('path =', path).get()
            ctime=time.mktime(time.gmtime())
            if not page:
                return [None, 0]
            if not memcache.set(memcache_key, [page,ctime]):
                logging.error('Memcache set failed')
            return [page,int(time.mktime(time.gmtime())-ctime)]

    def memcache_get_page_history(self,path,update=False):
        memcache_key=u'_history_'+unicode(path)
        pt=memcache.get(memcache_key)
        if pt is not None and not update:
            return [pt[0], int(time.mktime(time.gmtime())-pt[1])]
        else:
            try:
                page=Wikipage.by_path(path)
                hists=Pagehistory.by_pathkey(page)
            except ValueError:
                hists=None
                return [None, None]
            ctime=time.mktime(time.gmtime())
            if not page or not hists or not hists.get():
                return [None, 0]
            if not memcache.set(memcache_key, [hists,ctime]):
                logging.error('Memcache set failed')
            return [hists, int(time.mktime(time.gmtime())-ctime)]

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        try:
            uid=self.request.cookies.get('user_id').split('|')
        except (RuntimeError, ValueError, TypeError, AttributeError):
            uid=None
        if (not uid or len(uid)>2):
            uid=None
            self.user=None
            return
        try:
            usalt=User.by_id(int(uid[0])).usalt
        except (ValueError, AttributeError):
            self.user=None
            return
        if (self.read_secure_cookie('user_id',usalt)):
            self.user=User.by_id(int(uid[0]))
        else:
            self.user=None
