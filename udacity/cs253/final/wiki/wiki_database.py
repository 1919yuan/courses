from google.appengine.ext import db
from wiki_util import *
import logging

def wikis_key(name='default'):
    return db.Key.from_path('wikis', name)
def hists_key(name='default'):
    return db.Key.from_path('hists', name)
def users_key(group='default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name=db.StringProperty(required=True)
    password=db.StringProperty(required=True)
    usalt=db.StringProperty(required=True)
    psalt=db.StringProperty(required=True)
    joined=db.DateTimeProperty(auto_now_add=True)
    email=db.StringProperty(required=False)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u=User.all().filter('name =',unicode(name)).get()
        return u

    @classmethod
    def by_email(cls, email):
        u=User.all().filter('email =',email).get()
        return u

    @classmethod
    def register(cls, name, pw, email=''):
        psalt=make_salt()
        usalt=make_salt()
        return User(parent=users_key(),
                    name=unicode(name),
                    usalt=usalt,
                    psalt=psalt,
                    password=make_pw_hash(psalt,pw),
                    email=email)

    @classmethod
    def checkin(cls, name, pw):
        u=cls.by_name(name)
        if u and check_pw_hash(u.psalt, pw, u.password):
            return u

    @classmethod
    def checkin_email(cls, email, pw):
        u=cls.by_email(email)
        if u and check_pw_hash(u.psalt, pw, u.password):
            return u

class Wikipage(db.Model):
    path=db.StringProperty(required=True)
    content=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)
    last_modified=db.DateTimeProperty(auto_now=True)
    
    def render(self):
        c=self.content.replace('\n', '<br/>')
        return c

    @classmethod
    def by_path(cls, path):
        p=Wikipage.all().filter('path =', path).get()
        if p:
            return Wikipage.get_by_id(p.key().id(), parent=wikis_key())
        else:
            return None

class Pagehistory(db.Model):
    page=db.ReferenceProperty(Wikipage, required=True)
    content=db.TextProperty(required=True)
    vtime=db.DateTimeProperty(required=True)
    editor=db.ReferenceProperty(User, required=False)
    version=db.IntegerProperty(required=True)
    def render1(self):
        shtml='<tr'
        if ((self.version %2) ==0):
            shtml=shtml+r' class="history-alternative"'
        shtml=shtml+'>'
        #shtml=shtml+'<td>'+self.by_id(self.key().id()).vtime.strftime('%a, %d %b %Y %H:%M:%S')+'</td>'
        shtml=shtml+'<td>'+self.vtime.strftime('%a, %d %b %Y %H:%M:%S')+'</td>'
        shtml=shtml+r'<td class="history-content">'
        return shtml

    def render2(self):
        c = self.content.replace('\n', '<br/>')
        return c
    
    def render3(self):
        shtml='</td>'
        shtml=shtml+'<td>'+r'<a href="'+self.page.path+r'?v='+unicode(self.version)
        shtml=shtml+r'" class="login-link">view</a>&emsp;'
        shtml=shtml+r'<a href="/_edit'+self.page.path+r'?v='+unicode(self.version)
        shtml=shtml+r'" class="login-link">edit</a></td></tr>'
        return shtml
    
    @classmethod
    def by_pathkey(cls, pathkey):
        hists=Pagehistory.all().filter('page =', pathkey)
        return hists

    @classmethod
    def by_id(cls, hid):
        return Pagehistory.get_by_id(hid, parent=hists_key())
