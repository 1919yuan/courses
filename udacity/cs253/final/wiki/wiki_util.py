import random
import hmac
import re
import string
from wiki_config import *

secret=open('private/private-key').readline().strip()

#Globals
def make_salt():
    return str(''.join(random.choice(string.letters) for x in range(5)))

def make_hash(salt, val):
    return '%s|%s' % (val,hmac.new(str(secret)+str(salt), str(val)).hexdigest())

def make_pw_hash(salt, val):
    return str(hmac.new(str(secret)+str(salt), str(val)).hexdigest())

def check_pw_hash(salt, pw, h):
    return str(h)==str(hmac.new(str(secret)+str(salt), str(pw)).hexdigest())

def check_hash(salt, phrase):
    val=phrase.split('|')[0]
    if phrase==make_hash(salt,val):
        return val

def url_trim(path):
    firstslash=False
    s=[]
    for i in path:
        if i=='/' and firstslash==False:
            s.append(i)
            firstslash=True
        elif i!='/':
            s.append(i)
            firstslash=False
    return ''.join(s)

def agestring(ages):
    if ages==1:
        ages=u'Queried '+unicode(ages)+u' second ago.'
    else:
        ages=u'Queried '+unicode(ages)+u' seconds ago.'
    return ages


def genbreadcrumb(path, user, bEdit, bHistory, version=0):
    sUser=u''
    if user:
        sUser = sUser+user.name+r' (<a class="login-link" href="/logout">logout</a>)'
    else:
        sUser = sUser+r'<a class="login-link" href="/login">login</a> | <a class="login-link" href="/signup">signup</a>'
    
    sEdit=r'<a class="login-link" href="'+'/_edit'+path
    if (version):
        sEdit=sEdit+r'?v='+unicode(version)
    sEdit=sEdit+'">edit</a>'
    sHist=r'<a class="login-link" href="'+'/_history'+path
    sHist=sHist+'">history</a>'
    sBreadcrumb=''
    if bEdit:
        sBreadcrumb=sHist
    elif bHistory:
        if user or allow_anon_edit:
            sBreadcrumb=sEdit
    else:
        if (user or allow_anon_edit):
            sBreadcrumb=sEdit + ' | '+sHist
        else:
            sBreadcrumb=sHist
    sBreadcrumb=sBreadcrumb+'&emsp;&emsp;'+sUser
    return sBreadcrumb

def strippath(path):
    if (len(path)>1):
        return path.rstrip('/')
    else:
        return path

re_username = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
re_password = re.compile(r'^.{3,20}$')
re_email = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_username(username):
    return re_username.match(username)
def valid_password(password):
    return re_password.match(password)
def valid_email(email):
    return re_email.match(email)
