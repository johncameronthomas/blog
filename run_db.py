from simple_database.remote import server

s = server(('localhost', 8080), 'database.json')
s.start()