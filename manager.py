import os

from flask import render_template

from src import create_app

config_name = os.environ.get('FLASK_CONFIG') or 'Dev'
app = create_app(config_name)

@app.route('/')
def hello_world():
    return render_template('index.html',name="World")

if __name__ == '__main__':
    app.run(debug=True)