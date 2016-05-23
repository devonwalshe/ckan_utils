## /usr/bin/python
## CKAN API data utilities

import sys
import os
import urllib2
import urllib
import json
import pprint as pp
import re
import csv 
import time
from dateutil.parser import parse
from mimetypes import guess_extension


## Intialize script wide variables
site = 'http://[ckan_site]/api/3/action/'
auth = 'API_KEY'
# auth = '5684b795-d228-49f1-b21a-ffa8857299d8'


def ckan_request(url, *args):
   
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive',
          'Authorization': auth
      
      }
    req = urllib2.Request(url, headers=hdr)

    if len(args) >= 1:
     response = urllib2.urlopen(req, args[0])
    else:
     response = urllib2.urlopen(req)
  
    assert response.code == 200
                        
    response_dict = json.loads(response.read()) 

    assert response_dict['success'] is True

    result = response_dict['result']      

    return result
    
    
## CKAN Post

def ckan_post(url, data):
   
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive',
          'Authorization': auth
      
      }
    req = urllib2.Request(url, headers=hdr)
  
    json_data = json.dumps(data)
  
    response = urllib2.urlopen(req, json_data)
    assert response.code == 200
                        
    response_dict = json.loads(response.read()) 

    assert response_dict['success'] is True

    result = response_dict['result']      

    return result
    
    
## Dataset file downloader
def download_set(resource, local_dir):

  downloader = urllib.URLopener()

  ## get filename unless its an HTML link
  if resource["format"] == "HTML":
    filename = resource["name"]+".html"
  else:
    filename = re.findall(r'[^/]*$', resource["url"])[0]

  source = urllib.urlopen(resource['url'])
  extension = guess_extension(source.info()['Content-Type'])
  
  target = local_dir+"/"+"content"

  if len(re.findall(r'glasgow\.gov\.uk', resource['url'])) >= 1:
      try: 
    
        downloader.retrieve(resource["url"], target)
        print "\t downloading set %s" % resource["name"]
      except (urllib2.HTTPError, IOError, KeyError) as e:
        error_message = str(e)
        print "skipping %s, problem..." % resource["name"]
        # error_.append({"type":"dataset", "name":resource["name"], "error message":error_message})
        return
  else:
    return
       

## API search for specific organisation
def get_api_object(object_type, object_id):

  url = site+ object_type + "_show?id="+object_id
 
  response = ckan_request(url)
  return response
