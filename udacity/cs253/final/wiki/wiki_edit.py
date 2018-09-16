from wiki_config import *
from handler import *
from wiki_util import *
import datetime
import logging

class Wikiedit(WikiHandler):
    def render_self(self, path, content=u'', content_error=u''):
        self.render('edit.html', site_title=site_title, content=content, 
                    content_error=content_error, path=path, 
                    breadcrumb=genbreadcrumb(path,self.user,True,False))

    def get(self, path):
        if (self.user == None and not allow_anon_edit):
            self.write('You need to login first to edit any page!')
            return
        path=strippath(path)
        try:
            version = int(self.request.get('v'))
        except (ValueError, TypeError):
            version = 0
        page = None
        if (version):
            [hists, ages]=self.memcache_get_page_history(path)
            if (hists):
                hists=hists.order('-version')
                if (version==0):
                    page=hists.get().page
                else:
                    page=hists.filter('version =', int(version)).get().page
            else:
                page=None
        else:
            [page, ages]=self.memcache_get_page(path)
        if (page is not None):
            self.render_self(content=page.content, path=page.path)
        else:
            self.render_self(path=path)
        
    def post(self,path):
        if (self.user == None and not allow_anon_edit):
            self.write('You need to login first to edit any page!')
            return
        path=strippath(path)
        content = self.request.get('content')
        if (not content):
            self.render_self(path=path, content_error=u'Please enter some content')
            return
        page = Wikipage.by_path(path)
        if page is not None:
            page.content=content
            page.put()
        else:
            page=Wikipage(content=content, path=path, parent=wikis_key())
            page.put()
        
        [hists, ages]=self.memcache_get_page_history(path)
        if (hists and hists.get()):
            version=hists.order('-version').get().version+1
        else:
            version=1
        hist=Pagehistory(page=page, content=page.content, editor=self.user, version = version, vtime=datetime.datetime.now(), parent=hists_key())
        hist.put()
        self.memcache_get_page(path, update=True)
        self.memcache_get_page_history(path, update=True)
        self.redirect(path)
