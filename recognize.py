#! /usr/bin/python
from __future__ import division

import httplib
import json
import urllib

import numpy as np

subscription_key = 'be9dac277ac44c0589f0974c547680d2'
uri_base = 'westcentralus.api.cognitive.microsoft.com'


def recognize(content_type, body):
    headers = {
        # Request headers.
        # Another valid content type is "application/octet-stream".
        'Content-Type': content_type,
        'Ocp-Apim-Subscription-Key': subscription_key,
    }

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
    operation_location = response.getheader('Operation-Location')
    parsed_location = operation_location.split(uri_base)
    answer_url = parsed_location[1]

    # NOTE: The response may not be immediately available. Handwriting recognition is an
    # async operation that can take a variable amount of time depending on the length
    # of the text you want to recognize. You may need to wait or retry this GET operation.

    print('\nHandwritten text submitted.')

    # Execute the second REST API call and get the response.
    conn = httplib.HTTPSConnection(uri_base)
    while True:
        conn.request("GET", answer_url, '', headers)
        response = conn.getresponse()
        data = response.read()
        parsed = json.loads(data)
        if parsed['status'] in ['Failed', 'Succeeded']:
            break

    print ("Response:")
    print (json.dumps(parsed, sort_keys=False, indent=2))
    conn.close()

    return parsed


def parse_response(parsed, tight=True):
    xmax = 0
    ymax = 0
    lmax = 0
    widhts = []
    heights = []
    for line in parsed['recognitionResult']['lines']:
        text = line['text']
        bb = line['boundingBox']

        if bb[4] > xmax:
            xmax = bb[4]
        if bb[5] > ymax:
            ymax = bb[5]
        if len(text) > lmax:
            lmax = len(text)

        wbb = bb[2] - bb[0]
        hbb = bb[7] - bb[1]

        widhts.append(wbb / len(text))
        heights.append(hbb)

    wcell = np.mean(widhts)
    if tight:
        hcell = (np.min(heights) + np.mean(heights)) / 2
    else:
        hcell = np.min(heights)

    print xmax, ymax, lmax, wcell, hcell

    n = np.ceil(ymax / hcell)
    m = np.ceil(xmax / wcell) + lmax
    # m = 120

    print n, m

    grid = np.full([n, m], ord(' '), dtype=np.uint8)
    for line in parsed['recognitionResult']['lines']:
        bb = line['boundingBox']
        i = np.rint(bb[1] / hcell)
        j = np.rint(bb[0] / wcell)

        text = line['text']
        for e, c in enumerate(text):
            grid[i, j + e] = ord(c)

    buff = ''
    for line in grid[:-1]:
        buff += ''.join(map(lambda x: chr(x), line)).rstrip() + '\n'
    buff += ''.join(map(lambda x: chr(x), grid[-1])).rstrip()

    return buff
