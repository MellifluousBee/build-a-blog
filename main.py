import os
import cgi#imports autoescaping
import webapp2 #imports handlers
import jinja2#imports the template communicator

from google.appengine.ext import db

template_dir= os.path.join(os.path.dirname(__file__), 'templates')
jinja_env= jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                              autoescape = True) #autoescape includes anything defined as a variable
#above code sets up jinja to use the html templates I create in the "templates" directory


class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw): #makes it easy to write without typing entire code
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):#renders the template as a string
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):#calls write on the returned string
         self.write(self.render_str(template, **kw))

class Post (db.Model): #creates database, identifies types allowed by googleappengine datastore such as int, float, str, date, time, datetime, email, length, postal address, etc.
    title=db.StringProperty(required=True) #defines datatype for the title, makes it required
    post= db.TextProperty(required=True)
    created= db.DateTimeProperty(auto_now_add=True) #automatically adds current time
    last_modified= db.DateTimeProperty(auto_now = True)

    # def render(self):#this function replaces next lines with linebreaks so all the info doesn't appear on one line
    #     self._render_text = self.content.replace('\n', '<br>')
    #     return render_str("post.html", p = self)

    # def render_post(self, title="", post=""):
    #     self.render("post.html", title=title, post=post)

    # def get(self)
    #     self.render_post()

class MainPage(BlogHandler):
    def render_front(self, title="", post="",error=""): #want to render error message while keeping subject OR content
        posts= db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5") #looks up and lists 5 most recent of the posts
        self.render("front.html", title=title, post=post, error=error, posts= posts)#values of subject and content are passed into the html via {{}} from this function

    def get(self):
        self.render_front()


class NewPost(BlogHandler):
    def render_newpost(self, title="",post="", error=""):
        self.render("newpost.html", title=title, post=post, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title= self.request.get("title")
        post= self.request.get("post")

        if title and post:
            a=Post(title=title, post=post)
            a.put() #stores new post in database


            self.redirect('/blog/%s' % str(a.key().id())) #stores data and redirects to newpost page
        else:
            error= "We need both a title and a post, please."
            self.render_newpost(title, post, error) #renders form with error message while retaining subject OR content

class ViewPostHandler(BlogHandler):


    def get(self, id):
        int_id= int(id) #browser interprets numbers as strings, so must cast to an int
        idnum= Post.get_by_id(int_id)

        if idnum:
            self.render("post.html", idnum=idnum)
        else:
            error= "<h1>There is no post by the id </h1>"
            self.response.out.write(error)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
