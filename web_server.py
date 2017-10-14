# -*- coding: utf-8 -*-

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route('/textit', methods=['POST'])
def textit():
    event_type = request.form['event_type']
    print dir(request)

    if event_type == 'ping':
        return jsonify({'content': 'pong'})
    else:
        content = request.form['content']
        command = request.form['command']
        command_argument = request.form['command_argument']

        url = command_argument
        thred_id = request.form['thread_id']

        return jsonify({
            'content': content,
        })


if __name__ == '__main__':
    app.run()

