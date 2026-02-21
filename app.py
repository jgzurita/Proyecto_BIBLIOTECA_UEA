import os
from flask import Flask, render_template


app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/libro/<titulo>')
def libro(titulo):
    return render_template('libro.html', titulo=titulo)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)