import os
import webapp2
import jinja2
import re
from urlparse import urlparse
from google.appengine.ext import db
import string
import random
import hmac
import datetime
import json

#templates
template_dir=os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

secret=open('private/private-key').readline().strip()

#Globals
def make_salt():
    return ''.join(random.choice(string.letters) for x in range(5))

def make_hash(salt, val):
    return '%s|%s' % (val,hmac.new(secret+str(salt), str(val)).hexdigest())

def make_pw_hash(salt, val):
    return str(hmac.new(secret+str(salt), str(val)).hexdigest())

def check_pw_hash(salt, pw, h):
    return h==str(hmac.new(secret+str(salt), str(pw)).hexdigest())

def check_hash(salt, phrase):
    val=phrase.split('|')[0]
    if phrase==make_hash(salt,val):
        return val

re_username = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
re_password = re.compile(r"^.{3,20}$")
re_email = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_username(username):
    return re_username.match(username)
def valid_password(password):
    return re_password.match(password)
def valid_email(email):
    return re_email.match(email)

#database
site_title='CS 253 Blog'
def blog_key(name='default'):
    return db.Key.from_path('blogs', name)
def users_key(group='default'):
    return db.Key.from_path('users', group)
class Meta(db.Model):
    site_title=db.StringProperty(required=True)
q=Meta.all()
db.delete(q)
blogmeta=Meta(parent=blog_key(), site_title=site_title)
blogmeta.put()

class Post(db.Model):
    subject=db.StringProperty(required=True)
    content=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)
    last_modified=db.DateTimeProperty(auto_now=True)
    def render_content(self):
        c = self.content.replace('\n', '<br>')
        return c

class User(db.Model):
    username=db.StringProperty(required=True)
    password=db.StringProperty(required=True)
    usalt=db.StringProperty(required=True)
    psalt=db.StringProperty(required=True)
    joined=db.DateTimeProperty(auto_now_add=True)
    email=db.StringProperty(required=False)
    
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_username(cls, name):
        u=User.all().filter('username =',str(name)).get()
        return u

    @classmethod
    def by_email(cls, email):
        u=User.all().filter('email =',str(email)).get()
        return u

    @classmethod
    def register(cls, name, pw, email=''):
        psalt=make_salt()
        usalt=make_salt()
        return User(parent=users_key(),
                    username=name,
                    usalt=usalt,
                    psalt=psalt,
                    password=make_pw_hash(psalt,pw),
                    email=email)
    @classmethod
    def checkin(cls, name, pw):
        u=cls.by_username(name)
        if u and check_pw_hash(u.psalt, pw, u.password):
            return u

    @classmethod
    def checkin_email(cls, email, pw):
        u=cls.by_email(email)
        if u and check_pw_hash(u.psalt, pw, u.password):
            return u

#Handlers

class BlogHandler(webapp2.RequestHandler):
    def jsonrize(self, posts):
        s=[]
        for p in posts:
            d={}
            d['content']=p.content
            d['subject']=p.subject
            d['created']=p.created.strftime('%a, %d %b %Y %H:%M:%S')
            d['last_modified']=p.last_modified.strftime('%a, %d %b %Y %H:%M:%S')
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
                               make_hash(str(user.usalt),str(user.key().id())),
                               expires.strftime('%a, %d %b %Y %H:%M:%S'))

    def logout(self):
        expires = datetime.datetime.now() + datetime.timedelta(days=-10)
        self.set_cookie('user_id', '', 
                               expires.strftime('%a, %d %b %Y %H:%M:%S'))

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
        except ValueError:
            self.user=None
            return
        if (self.read_secure_cookie('user_id',usalt)):
            self.user=User.by_id(int(uid[0]))
        else:
            self.user=None

class MainPage(BlogHandler):
    def get(self):
        self.write("Ripegraph!")

class BlogNew(BlogHandler):
    def render_self(self, subject='', content='', error=''):
        site_title=db.GqlQuery('select * from Meta').fetch(1)[0].site_title
        self.render('newpost.html', site_title=site_title,
                    subject=subject, content=content, error=error)
        
    def get(self):
        self.render_self()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            post=Post(subject=subject,content=content,parent=blog_key())
            post.put()
            pid=post.key().id()
            self.redirect('/blog/'+str(pid))
        else:
            error = 'subject and content, please!'
            self.render_self(subject, content, error)

class BlogClear(BlogHandler):
    def get(self):
        ps=Post.all()
        us=User.all()
        db.delete(us)
        db.delete(ps)
        self.write('cleared!')

class Blog(BlogHandler):
    def render_self(self, posts):
        site_title=db.GqlQuery('select * from Meta').fetch(1)[0].site_title
        self.render('blog.html', site_title=site_title, posts=posts)
    
    def get(self):
        posts=Post.all().order('-created').fetch(limit=10)
        self.render_self(posts)

class BlogPage(BlogHandler):
    def render_self(self, posts):
        site_title=db.GqlQuery('select * from Meta').fetch(1)[0].site_title
        self.render('blog.html', site_title=site_title, posts=posts)
    
    def get(self, pid):
        try:
            #posts=db.GqlQuery('select * from Post where __key__=KEY(\'Post\','+str(pid)+')', parent=blog_key())
            #posts=list(posts)
            key=db.Key.from_path('Post', int(pid), parent=blog_key());
            posts=[db.get(key)]
        except ValueError:
            posts=None
        if not posts:
            self.error(404)
            return
        else:
            self.render_self(posts)

class BlogJson(BlogHandler):
    
    def get(self):
        posts=Post.all().order('-created').fetch(limit=10)
        self.response.headers['Content-Type'] = 'application/json'
        self.write(self.jsonrize(posts))

class BlogPageJson(BlogHandler):
    def get(self, pid):
        pid=pid.strip('.json')
        key=db.Key.from_path('Post', int(pid), parent=blog_key());
        post=[db.get(key)]
        if not post:
            self.error(404)
            return
        else:
            self.response.headers['Content-Type'] = 'application/json'
            self.write(self.jsonrize(post))

class Welcome(BlogHandler):
    def render_self(self, username=''):
        site_title=db.GqlQuery('select * from Meta').fetch(1)[0].site_title
        self.render('welcome.html', site_title=site_title, username=username)
    def get(self):
        if self.user:
            self.render_self(username=self.user.username)
        else:
            #self.render_self(username='')
            self.redirect('/blog/signup')

class Signup(BlogHandler):
    def render_self(self, username='', username_e='', 
                    password='', password_e='',
                    vpassword='', vpassword_e='',
                    email='', email_e=''):
        site_title=db.GqlQuery('select * from Meta').fetch(1)[0].site_title
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
            user=db.GqlQuery('select * from User where username=\''+str(input_un)+'\'').get()
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
            self.redirect('/blog/welcome')
        else:
            self.render_self(username=input_un,password=input_pw,
                             vpassword=input_vf,email=input_em,
                             username_e=une,password_e=pwe,vpassword_e=vpwe,
                             email_e=eme)


class Login(BlogHandler):
    def render_self(self, username='', username_e='', 
                    password='', password_e=''):
        site_title=db.GqlQuery('select * from Meta').fetch(1)[0].site_title
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
                self.redirect('/blog/welcome')
                return
        une='Invalid login or password'
        self.render_self(username=input_un,password='',username_e=une,password_e=pwe)
        
class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

app=webapp2.WSGIApplication([('/', MainPage),
                             ('/blog/newpost', BlogNew),
                             ('/blog/clearall', BlogClear),
                             ('/blog/signup', Signup),
                             ('/blog/welcome', Welcome),
                             ('/blog/login', Login),
                             ('/blog/logout',Logout),
                             (r'/blog/([0-9]+)', BlogPage),
                             (r'/blog/([0-9]+)[/]?.json', BlogPageJson),
                             (r'/blog[/]?.json', BlogJson),
                             (r'/blog.*', Blog)
                             ],
                            debug=True)

