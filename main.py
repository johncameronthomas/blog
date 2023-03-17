import web
import time
from asynchronous_database import database

db = database('database.json')
db.start()

web.config.debug = False

urls = (
    '/static/(.+)', 'static',
    '/', 'index',
    '/home', 'home',
    '/about', 'about',
    '/posts', 'posts',
    '/contact', 'contact',
    '/login', 'login',
    '/logout', 'logout',
    '/post/(.+)', 'post',
    '/create_post', 'create_post',
    '/edit_post', 'edit_post',
    '/delete_post/(.+)', 'delete_post'
    )
app = web.application(urls, globals())
wsgi_app = app.wsgifunc()
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'user': None})
render = web.template.render('templates/', base='layout')

class static:
    def GET(self, path):
        try:
            f = open('static/' + path, 'r')
            data = f.read()
            return data
        except:
            return web.notfound()

class index:
    def GET(self):
        raise web.seeother('/home')

class home:
    def GET(self):
        return render.home()
    
class about:
    def GET(self):
        return render.about()
    
class posts:
    def GET(self):
        posts = db.read('posts')
        if len(posts) == 0:
            return render.error('<p>No posts found.</p>')
        return render.posts(posts)
    
class contact:
    def GET(self):
        return render.contact()
    
class login:
    def GET(self):
        if session.user == None:
            return render.login(False)
        return render.error('<p>You are already logged in.</p>')
    
    def POST(self):
        if session.user == None:
            users = db.read('users')
            data = web.input()
            username = data['username']
            password = data['password']
            if (username in users) and (users[username] == password):
                session.user = username
                return render.success('<p>You have been logged in.</p>')
            return render.login(True)
        return render.error('<p>You are already logged in.</p>')
        
class logout:
    def GET(self):
        if session.user == None:
            return render.error("<p>You must be logged in to log out.</p>")
        session.user = None
        return render.success('<p>You have been logged out.</p>')
        
class post:
    def GET(self, id):
        posts = db.read('posts')
        if id in posts:
            post = posts[id]
            if session.user != None:
                return render.post(post, id, True)
            return render.post(post, id, False)
        return web.notfound()
        
class create_post:
    def GET(self):
        if session.user == None:
            return render.error("<p>You must be logged in to create a post.</p>")
        return render.create_post()
    def POST(self):
        if session.user == None:
            return render.error("<p>You must be logged in to create a post.</p>")
        data = web.input()
        posts = db.read('posts')
        id = data['id']
        if id in posts:
            return render.error('<p>This id is already in use.</p>')
        title = data['title']
        content = data['content']
        date = time.strftime('%X %x %Z')
        posts = db.read('posts')
        posts[id] = (title, content, date)
        db.update('posts', posts)
        return render.success('<p>Post created!</p><a href="/post/{}">Link</a>'.format(id))
    
class delete_post:
    def GET(self, id):
        if session.user == None:
            return render.error('<p>You must be logged in to create a post.</p>')
        posts = db.read('posts')
        if id not in posts:
            return render.error("<p>This post doesn't exist.</p>")
        posts.pop(id)
        db.update('posts', posts)
        return render.success('<p>Post deleted.</p>')
    
if __name__ == "__main__":
    app.run()