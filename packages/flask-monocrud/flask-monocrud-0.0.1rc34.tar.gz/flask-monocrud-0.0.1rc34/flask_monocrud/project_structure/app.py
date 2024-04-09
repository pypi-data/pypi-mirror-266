from flask import Flask
from flask_monocrud import FlaskMonoCrud

app = Flask(__name__)
FlaskMonoCrud(app)

if __name__ == '__main__':
    app.run()
