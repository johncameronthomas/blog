import web
import time

from simple_database.local import database

web.db = database('database.json')
web.db.start()
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
    '/edit_post/(.+)', 'edit_post',
    '/delete_post/(.+)', 'delete_post'
    )
app = web.application(urls, globals())
wsgi_app = app.wsgifunc()
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'logged_in': False})
render = web.template.render('templates/')

class static:
    def GET(self, path):
        try:
            f = open('static/' + path, 'r')
        except:
            return web.notfound()
        else:
            data = f.read()
            return data

class index:
    def GET(self):
        raise web.seeother('/home')

class home:
    def GET(self):
        return render.layout(render.home(), session.logged_in)

class about:
    def GET(self):
        return render.layout(render.about(), session.logged_in)

class posts:
    def GET(self):
        posts = web.db.read('posts')
        if len(posts) == 0:
            return render.layout(render.error('<p>No posts found.</p>'), session.logged_in)
        else:
            return render.layout(render.posts(posts), session.logged_in)

class contact:
    def GET(self):
        return render.layout(render.contact(), session.logged_in)

class login:
    def GET(self):
        if session.logged_in:
            return render.layout(render.error('<p>You are already logged in.</p>'), session.logged_in)
        else:
            return render.layout(render.login(False), session.logged_in)

    def POST(self):
        if session.logged_in:
            return render.layout(render.error('<p>You are already logged in.</p>'), session.logged_in)
        else:
            data = web.input()
            username = data['username']
            password = data['password']
            users = web.db.read('users')
            if (username in users) and (users[username] == password):
                session.logged_in = True
                return render.layout(render.success('<p>You have been logged in.</p>'), session.logged_in)
            else:
                return render.layout(render.login(True), session.logged_in)

class logout:
    def GET(self):
        if session.logged_in:
            session.logged_in = False
            return render.layout(render.success('<p>You have been logged out.</p>'), session.logged_in)
        else:
            return render.layout(render.error("<p>You must be logged in to log out.</p>"), session.logged_in)

class post:
    def GET(self, id):
        posts = web.db.read('posts')
        if id in posts:
            post = posts[id]
            return render.layout(render.post(post, session.logged_in, id), session.logged_in)
        else:
            return web.notfound()

class create_post:
    def GET(self):
        if session.logged_in:
            return render.layout(render.create_post(), session.logged_in)
        else:
            return render.layout(render.error("<p>You must be logged in to create a post.</p>"), session.logged_in)

    def POST(self):
        if session.logged_in:
            data = web.input()
            id = data['id']
            posts = web.db.read('posts')
            if id in posts:
                return render.layout(render.error('<p>This id is already in use.</p>'), session.logged_in)
            else:
                title = data['title']
                content = data['content']
                date = time.strftime('%X %x %Z')
                web.db.write({'title': title, 'content': content, 'date': date}, 'posts', id)
                return render.layout(render.success('<p>Post created!</p><a href="/post/{}">Link</a>'.format(id)), session.logged_in)
        else:
            return render.layout(render.error("<p>You must be logged in to create a post.</p>"), session.logged_in)

class edit_post:
    def GET(self, id):
        if session.logged_in:
            try:
                post = web.db.read('posts', id)
            except:
                return web.notfound()
            else:
                title = post['title']
                content = post['content']
                return render.layout(render.edit_post(title, content), session.logged_in)
        else:
            return render.layout(render.error("<p>You must be logged in to edit a post.</p>"), session.logged_in)

    def POST(self, id):
        if session.logged_in:
            try:
                post = web.db.read('posts', id)
            except:
                return web.notfound()
            else:
                data = web.input()
                title = data['title']
                content = data['content']
                date = time.strftime('%X %x %Z')
                web.db.write({'title': title, 'content': content, 'date': date}, 'posts', id)
                return render.layout(render.success('<p>Post edited!</p><a href="/post/{}">Link</a>'.format(id)), session.logged_in)
        else:
            return render.layout(render.error("<p>You must be logged in to edit a post.</p>"), session.logged_in)

class delete_post:
    def GET(self, id):
        if session.logged_in:
            posts = web.db.read('posts')
            if id in posts:
                web.db.remove('posts', id)
                return render.layout(render.success('<p>Post deleted.</p>'), session.logged_in)
            else:
                return render.layout(render.error("<p>This post doesn't exist.</p>"), session.logged_in)
        else:
            return render.layout(render.error('<p>You must be logged in to delete a post.</p>'), session.logged_in)

if __name__ == "__main__":
    app.run()