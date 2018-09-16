from wiki_config import *
from handler import *
from wiki_util import *

class Wikihistory(WikiHandler):
    def render_self(self, path, hists=None, ages=''):
        self.render('history.html', site_title=site_title, 
                    hists=hists, path=path, ages=ages,
                    breadcrumb=genbreadcrumb(path,self.user,False,True))

    def get(self, path):
        path=strippath(path)
        [hists, ages]=self.memcache_get_page_history(path)
        if not hists:
            self.error(404)
            self.response.write(message404)
            return
        else:
            self.render_self(path=path,hists=hists, ages=agestring(ages))
