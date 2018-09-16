
import webapp2
import cgi
import re

wel_msg='''
<!DOCTYPE html>

<html>
  <head>
    <title>Unit 2 Signup</title>
  </head>

  <body>
    <h2>Welcome, %(username)s!</h2>
  </body>
</html>
'''

form='''
<!DOCTYPE html>

<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(username)s">
          </td>
          <td class="error">
            %(username_e)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="%(password)s">
          </td>
          <td class="error">
            %(password_e)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="%(vpassword)s">
          </td>
          <td class="error">
            %(vpassword_e)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">
            %(email_e)s
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
'''

UN_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PW_RE = re.compile(r"^.{3,20}$")
EM_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_username(username):
    return UN_RE.match(username)

def valid_password(password):
    return PW_RE.match(password)

def valid_email(email):
    if email:
        return EM_RE.match(email)
    else:
        return True

class MainPage(webapp2.RequestHandler):
    def render(self, un='',pw='',vpw='',em='',une='',pwe='',vpwe='',eme=''):
        return form%{'username': un, 
                     'password': pw,
                     'vpassword': vpw,
                     'email': em,
                     'username_e': une,
                     'password_e': pwe,
                     'vpassword_e': vpwe,
                     'email_e': eme}

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(self.render())

    def post(self):
        input_un=self.request.get('username')
        input_pw=self.request.get('password')
        input_vf=self.request.get('verify')
        input_em=self.request.get('email')
        un=cgi.escape(input_un,quote=True)
        pw=cgi.escape(input_pw,quote=True)
        vpw=cgi.escape(input_vf,quote=True)
        em=cgi.escape(input_em,quote=True)
        une=''
        pwe=''
        vpwe=''
        eme=''
        self.response.headers['Content-Type'] = 'text/html'
        if (not valid_username(input_un)):
            une='That\'s not a valid username.'
        if (not valid_password(input_pw)):
            pwe='That wasn\'t a valid password.'
        else:
            if (input_pw != input_vf):
                vpwe='Your passwords didn\'t match.'
        if (not valid_email(input_em)):
            eme='That\'s not a valid email.'
        if ((not une) and (not pwe) and (not vpwe) and (not eme)):
            self.redirect(str('welcome.html?username=%s'%input_un))
        else:
            self.response.out.write(self.render(un,pw,vpw,em,une,pwe,vpwe,eme))

class Welcome(webapp2.RequestHandler):
    def render(self,s):
        return wel_msg%{'username':s}
    def get(self):
        un=self.request.get('username')
        if un:
            self.response.out.write(self.render(un))
        else:
            self.redirect("/signup")
        

app = webapp2.WSGIApplication([('/signup', MainPage),
                              ('/welcome.html', Welcome)],
                              debug=True)

