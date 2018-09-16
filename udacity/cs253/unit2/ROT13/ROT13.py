
import webapp2
import cgi
from string import maketrans

form="""
<head>
    <title>Unit 2 Rot 13</title>
</head>
<body>
    <h2>Enter some text to ROT13:</h2>
    <form method="post">
        <textarea name="text" style="height: 100px; width: 400px;">%(txt)s</textarea>
        <br>
        <input type="submit">
    </form>
</body>
"""

reps={}
for char in range(ord('a'),ord('z')+1):
    mapc=char+13
    if mapc > ord('z'):
        mapc = mapc-26
    reps[chr(char)]=chr(mapc)
for char in range(ord('A'),ord('Z')+1):
    mapc=char+13
    if mapc > ord('Z'):
        mapc = mapc-26
    reps[chr(char)]=chr(mapc)

class MainPage(webapp2.RequestHandler):
    def write_form(self, s):
        return form%{'txt': s}

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(self.write_form(''))

    def post(self):
        user_txt=self.request.get('text')
        txt=user_txt
        intab=''.join(reps.keys())
        outtab=''.join(reps.values())
        #self.response.out.write(intab)
        #self.response.out.write(outtab)
        trantab=maketrans(intab,outtab)
        txt=str(txt).translate(trantab)
        txt=cgi.escape(txt, quote=True)
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(self.write_form(txt))

app = webapp2.WSGIApplication([('/', MainPage)], 
                              debug=True)

