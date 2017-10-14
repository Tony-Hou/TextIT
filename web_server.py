#! /usr/bin/python

import requests
import subprocess
from flask import Flask, jsonify, request
from recognize import get_img_from_url, recognize, parse_response

app = Flask(__name__)
app.debug = True


TOKEN = 'Bearer oauth2:a5c57ac69c0ff3d278ff36621e6693591dede092'


@app.route('/textit', methods=['POST'])
def textit():
    content = request.json['content']
    thread_id = request.json['thread_id']
    if content.startswith('/textit '):
        url = content[8:]
        body, im_bytes = get_img_from_url(url)
        response = recognize('application/json', body)

        buff = parse_response(response)

        f = open('test.txt', 'w')
        f.write(buff)
        f.close()

        out = subprocess.check_output('curl -X POST https://api.twistapp.com/api/v2/comments/add \
                                       -d thread_id=' + str(thread_id) + ' \
                                       -d attachments="[$(curl -X POST https://api.twistapp.com/api/v2/attachments/upload -F attachment_id=ac2fd489-9eab-4956-9d9d-c9b590258328 -F file_name=@test.txt -H "Authorization: ' + TOKEN + '")]" \
                                       -d content="Testing on hackupc" \
                                       -H "Authorization: ' + TOKEN + '"', shell=True)
        print out

    return '{}'


if __name__ == '__main__':
    app.run()
