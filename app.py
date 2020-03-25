from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request

app = Flask(__name__)

bootstrap = Bootstrap(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('base.html')

@app.route('/explore', methods=['GET', 'POST'])
def explore():
    return render_template('explore.html')

@app.route('/playground', methods=['GET', 'POST'])
def playground():
    return render_template('playground.html')

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)