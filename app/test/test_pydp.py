from flask import Flask
from pydap.wsgi.app import DapServer

application = DapServer('./test/')
app = Flask(__name__)
app.wsgi_app = application
app.run('0.0.0.0', 8006)
