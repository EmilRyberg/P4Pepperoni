# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 20:24:55 2019

@author: Emil
"""

import shutil
import requests
url = "http://image-net.org/api/text/imagenet.synset.geturls?wnid=n04451818"
name = "tool"
r = requests.get(url);
contents = r.text
lines = contents.splitlines()
successfulDownloads = 0;
for i in range(len(lines)):
    line = lines[i]
    print(str(i) + " - trying to DL - " + str(len(lines) - i) + " left")
    try:
        imageRequest = requests.get(line, stream=True, timeout=0.5)
        if imageRequest.status_code == requests.codes.ok:
            successfulDownloads += 1
            with open(name + str(successfulDownloads) + '.jpg', 'wb') as out_file:
                shutil.copyfileobj(imageRequest.raw, out_file)
        
        del imageRequest
    except:
        print("Image with URL " + line + " failed.")