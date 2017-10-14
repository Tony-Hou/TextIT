#! /usr/bin/python
from __future__ import division
import httplib
import io
import json
import urllib

import numpy as np
from PIL import Image, ImageDraw

subscription_key = 'be9dac277ac44c0589f0974c547680d2'
uri_base = 'westcentralus.api.cognitive.microsoft.com'

headers = {
    # Request headers.
    # Another valid content type is "application/octet-stream".
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': subscription_key,
}

# The URL of a JPEG image containing handwritten text.
#url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Cursive_Writing_on_Notebook_paper.jpg/800px-Cursive_Writing_on_Notebook_paper.jpg'
#body = "{'url':'%s'}" % url
#fd = urllib.urlopen(url)
#im_bytes = io.BytesIO(fd.read())

# The file name of a JPEG image containing handwritten text.
im_bytes = open('IMG_06241.jpg', 'rb')
body = im_bytes

# For printed text, set "handwriting" to false.
params = urllib.urlencode({'handwriting': 'true'})

# This operation requrires two REST API calls. One to submit the image for processing,
# the other to retrieve the text found in the image.
#
# This executes the first REST API call and gets the response.
conn = httplib.HTTPSConnection(uri_base)
conn.request("POST", "/vision/v1.0/RecognizeText?%s" % params, body, headers)
response = conn.getresponse()

# Success is indicated by a status of 202.
if response.status != 202:
    # Display JSON data and exit if the first REST API call was not successful.
    parsed = json.loads(response.read())
    print ("Error:")
    print (json.dumps(parsed, sort_keys=True, indent=2))
    conn.close()
    exit()

# The 'Operation-Location' in the response contains the URI to retrieve the recognized text.
operationLocation = response.getheader('Operation-Location')
parsedLocation = operationLocation.split(uri_base)
answerURL = parsedLocation[1]

# NOTE: The response may not be immediately available. Handwriting recognition is an
# async operation that can take a variable amount of time depending on the length
# of the text you want to recognize. You may need to wait or retry this GET operation.

print('\nHandwritten text submitted.')

# Execute the second REST API call and get the response.
conn = httplib.HTTPSConnection(uri_base)
while True:
    conn.request("GET", answerURL, '', headers)
    response = conn.getresponse()
    data = response.read()
    parsed = json.loads(data)
    if parsed['status'] != 'Running':
        break

print ("Response:")
print (json.dumps(parsed, sort_keys=False, indent=2))
conn.close()


im = Image.open(im_bytes)
draw = ImageDraw.Draw(im)

xmax = 0
ymax = 0
widhts = []
heights = []
for line in parsed['recognitionResult']['lines']:
    text = line['text']
    bb = line['boundingBox']
    draw.rectangle([bb[0], bb[1], bb[4], bb[5]], outline=(0, 255, 0))

    if bb[4] > xmax:
        xmax = bb[4]
    if bb[5] > ymax:
        ymax = bb[5]

    wbb = bb[2] - bb[0]
    hbb = bb[7] - bb[1]

    widhts.append(wbb / len(text))
    heights.append(hbb)

del draw

wcell = np.mean(widhts)
hcell = np.mean(heights)
#hcell = np.min(heights)

print 'w:', widhts
print 'h:', heights
print xmax, ymax, wcell, hcell

n = np.ceil(ymax / hcell)
#m = np.ceil(xmax / wcell)
m = 120

print n, m

grid = np.full([n, m], ord(' '), dtype=np.uint8)
for line in parsed['recognitionResult']['lines']:
    bb = line['boundingBox']
    i = np.rint(bb[1] / hcell)
    j = np.rint(bb[0] / wcell)

    text = line['text']
    print text
    print '(%d,%d) (%d,%d)' % (bb[0], bb[1], j, i)
    for e, c in enumerate(text):
        grid[i, j + e] = ord(c)

buff = ''
for line in grid:
    buff += ''.join(map(lambda x: chr(x), line)) + '\n'

f = open('test.txt', 'w')
f.write(buff)
f.close()

im.show()
