import os
import webapp2
import jinja2
from urlparse import urlparse

from google.appengine.ext import db

template_dir=os.path.join(os.path.dirname(__file__), 'html')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

class Meta(db.Model):
    site_title=db.StringProperty(required=True)
    

class Post(db.Model):
    subject=db.StringProperty(required=True)
    content=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)

blogmeta=Meta(site_title='CS 253 Blog')
blogmeta.put()

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        self.write("Ripegraph!")

class BlogNew(Handler):
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
            post=Post(subject=subject,content=content)
            post.put()
            pid=post.key().id()
            self.redirect('/blog/'+str(pid))
        else:
            error = 'subject and content, please!'
            self.render_self(subject, content, error)

class BlogClear(Handler):
    def get(self):
        ps=Post.all()
        db.delete(ps)
        self.write('cleared!')
    

class Blog(Handler):
    def render_self(self, posts):
        site_title=db.GqlQuery('select * from Meta').fetch(1)[0].site_title
        self.render('blog.html', site_title=site_title, posts=posts)
    
    def get(self):
        ups=urlparse(self.request.url).path.split('/')
        for i in range(len(ups)):
            if ups[i]:
                break
        ubl=ups[i]
        if i<len(ups)-1:
            pid=ups[i+1]
        else:
            pid=None
        if (ubl != 'blog'):
            self.redirect('/blog')
        else:
            if pid:
                posts=db.GqlQuery('select * from Post where __key__=KEY(\'Post\','+str(pid)+')')
                if posts:
                    self.render_self(posts)
                else:
                    self.redirect('/blog')
            else:
                posts=db.GqlQuery('select * from Post order by created desc').fetch(10)
                self.render_self(posts)
                


app=webapp2.WSGIApplication([('/', MainPage),
                             ('/blog/newpost', BlogNew),
                             ('/blog/clearall', BlogClear),
                             (r'/blog.*', Blog)],
                            debug=True)

