from flask import Flask

from routes import api
app = Flask(__name__)

app.register_blueprint(api.api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='localhost')