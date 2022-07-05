from flask import Flask, render_template
from flask_restful import Resource, Api
from label_api.api import init_api as init_user

app = Flask(__name__)
api = Api(app)

init_user(api)

@app.route('/', methods=['GET'])
def index():  # put application's code here
    return render_template('index.html')


if __name__ == '__main__':
    app.run()