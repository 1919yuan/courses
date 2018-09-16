from handler import *
from wiki_util import *
from wiki_edit import *
from wiki_history import *
from wiki_browse import *
from urlparse import urlparse

class Clearall(WikiHandler):
    def get(self):
        ps=Wikipage.all()
        us=User.all()
        hs=Pagehistory.all()
        db.delete(us)
        db.delete(ps)
        db.delete(hs)
        self.write('cleared!')

class CacheFlush(WikiHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/')

class WikipageJson(WikiHandler):
    def get(self,path):
        path=strippath(path)
        [page, ages]=self.memcache_get_page(path)
        self.response.headers['Content-Type'] = 'application/json'
        if (page):
            self.write(self.jsonrize_page(page))

class WikihistJson(WikiHandler):
    def get(self, path):
        path=strippath(path)
        [hists, ages]=self.memcache_get_page_history(path)
        if not hists:
            self.error(404)
            return
        else:
            self.response.headers['Content-Type'] = 'application/json'
            self.write(self.jsonrize_page_history(hists))

class Signup(WikiHandler):
    def render_self(self, username='', username_e='', 
                    password='', password_e='',
                    vpassword='', vpassword_e='',
                    email='', email_e=''):
        self.render('signup.html', site_title=site_title,
                    username=username, username_e=username_e,
                    password=password, password_e=password_e,
                    vpassword=vpassword, vpassword_e=vpassword_e,
                    email=email, email_e=email_e)
    def get(self):
        self.render_self()

    def post(self):
        input_un=self.request.get('username')
        input_pw=self.request.get('password')
        input_vf=self.request.get('verify')
        input_em=self.request.get('email')
        une=''
        pwe=''
        vpwe=''
        eme=''
        if (not valid_username(input_un)):
            une='That\'s not a valid username.'
        else:
            user=db.GqlQuery('select * from User where name=\''+str(input_un)+'\'').get()
            if (user):
                une='That user already exists.'
        if (not valid_password(input_pw)):
            pwe='That wasn\'t a valid password.'
        else:
            if (input_pw != input_vf):
                vpwe='Your passwords didn\'t match.'
        if (input_em and not valid_email(input_em)):
            eme='That\'s not a valid email.'
        if ((not une) and (not pwe) and (not vpwe) and (not eme)):
            udb=User.register(input_un, input_pw,input_em)
            udb.put()
            self.login(udb)
            self.redirect('/')
        else:
            self.render_self(username=input_un,password=input_pw,
                             vpassword=input_vf,email=input_em,
                             username_e=une,password_e=pwe,vpassword_e=vpwe,
                             email_e=eme)


class Login(WikiHandler):
    def render_self(self, username='', username_e='', 
                    password='', password_e=''):
        self.render('login.html', site_title=site_title,
                    username=username, username_e=username_e,
                    password=password, password_e=password_e)
    def get(self):
        self.render_self()

    def post(self):
        input_un=self.request.get('username')
        input_pw=self.request.get('password')
        une=''
        pwe=''
        login_un=False
        login_em=False
        u=None
        if (not valid_username(input_un)):
            login_un=False
            if (not valid_email(input_un)):
                login_em=False
            else:
                login_em=True
                u=User.checkin_email(input_un, input_pw)
        else:
            login_un=True
            u=User.checkin(input_un, input_pw)

        if (login_un or login_em):
            if u:
                self.login(u)
                self.redirect('/')
                return
        une='Invalid login or password'
        self.render_self(username=input_un,password='',username_e=une,password_e=pwe)
        
class Logout(WikiHandler):
    def get(self):
        self.logout()
        self.redirect('/')

class Urlprocess(WikiHandler):
    def get(self, *a):
        if self.request.path=='/_history' or self.request.path=='/_edit':
            self.redirect(self.request.path+'/')
        elif self.request.path=='/_history.json':
            path='/_history/.json'
            self.redirect(path)
        elif self.request.path[1]=='_':
            self.error(404)
            self.response.write(message404)
        else:
            self.redirect(url_trim(self.request.path))

PAGE_RE=r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app=webapp2.WSGIApplication([('.*/{2,}.*', Urlprocess),
                             ('/signup/?', Signup),
                             ('/login/?', Login),
                             ('/logout/?', Logout),
                             ('/flushall/?', CacheFlush),
                             ('/clearall/?', Clearall),
                             ('/_edit'+PAGE_RE, Wikiedit),
                             ('/_history'+PAGE_RE, Wikihistory),
                             ('/_history'+PAGE_RE+'[/]?\.json', WikihistJson),
                             ('/(_edit|_history).*$', Urlprocess),
                             (PAGE_RE+'[/]?\.json', WikipageJson),
                             (PAGE_RE, Wikibrowse)
                             ],
                            debug=True)

