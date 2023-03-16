import web
from asynchronous_database import database

posts_db = database('database/posts.json')
posts_db.start()

web.config.debug = False

urls = (
    '/static/(.+)', 'static',
    '/', 'index',
    '/home', 'home',
    '/about', 'about',
    '/posts/(.+)', 'posts',
    '/contact', 'contact'
    )
app = web.application(urls, locals())
wsgi_app = app.wsgifunc()
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'admin': False})
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
    def GET(self, index):
        return render.posts()
    
class contact:
    def GET(self):
        return render.contact()

if __name__ == "__main__":
    app.run()