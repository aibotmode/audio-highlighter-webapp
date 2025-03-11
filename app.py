from flask import Flask

app = Flask(__name__)  # THIS is what gunicorn is looking for

@app.route('/')
def home():
    return "Hello, world!"
