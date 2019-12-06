from flask import Flask, render_template
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret?'


socketio = SocketIO(app)

@socketio.on('message')
def handleMessage(msg):
    print("\n\nMessage:", msg, "\n\n")
    send(msg, broadcast=True)
    
@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
