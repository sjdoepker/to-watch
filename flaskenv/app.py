from flask import Flask

app = Flask(__name__)

@app.route("/")
def base():
    return "<h1>heya world!</h1>"