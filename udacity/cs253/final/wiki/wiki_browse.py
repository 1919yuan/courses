import wiki_config
from handler import *
import wiki_util

class Wikibrowse(WikiHandler):    
    def render_self(self, path, content='None yet', ages='', version=0):
        self.render('wiki.html', site_title=site_title, content=content, 
                    path=path, ages=ages,
                    breadcrumb=genbreadcrumb(path,self.user,False,False,version))
    
    def get(self, path):
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
            self.render_self(content=page.render(), path=page.path, ages=agestring(ages), version=version)
        else:
            if path=='/':
                self.render_self(path=path)
            else:
                self.redirect('/_edit'+path)
