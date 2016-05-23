#!/Users/azymuth/www/virtualenv/fest/bin/python
# -*- coding: utf-8 -*-
### Mirrors data.glasgow.gov.uk datasets and catalogues the metadata. 

## Init
import sys
import os
import urllib2
import urllib
import json
import pprint
import re
import csv 
import time

site = Config::ckan_site_api_url
auth = Config::auth_key
local_dir = Config::storage_dir

### HTTP Request for CKAN
def ckan_request(url, *args):
   
   hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
          'Accept-Encoding': 'none',
          'Accept-Language': 'en-US,en;q=0.8',
          'Connection': 'keep-alive'}
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

#### Get package list

def get_packages():
  package_list = ckan_request(site+"package_list")
  
  return package_list
  
### Write row of metadata for catalogue 
  
def write_row(resource, package):
  # tags_string = get_tags(package["tags"])
  # revisions = ckan_request(site+"package_revision_list?id=%s" % package["name"])

  row = {
  "set_name":resource["name"], 
  "package_id":package["name"],
  "last_package_revision":package["revision_timestamp"],
  # "last_set_revision":resource["revision_timestamp"],
  "created":resource["created"],
  "format":resource["format"],
  "url":resource["url"],
  "organisation":package["organization"]["name"],
  "description":unicode(resource["description"]).strip(),
  # "last_revised_by":revisions[0]["author"],
  # "first_revised_by":revisions[-1]["author"],
  "total_downloads":unicode(resource["tracking_summary"]["total"]),
  "recent_downloads":unicode(resource["tracking_summary"]["recent"]),
  "total_package_views":unicode(package["tracking_summary"]["total"]),
  "recent_package_views":unicode(package["tracking_summary"]["recent"]),
  "tags":", ".join([tag["name"] for tag in package["tags"]]),
  "groups":", ".join([group["name"] for group in package["groups"]])
  }
  
  return row

  
### Get a package

def get_package(package_id):
 
  package_id = json.dumps({'id':package_id})
  url = site+"package_show"
 
  response = ckan_request(url, package_id)
  return response

#Build catalogue dictionary or read from JSON

filename = local_dir+"/catalogue.json"

if os.path.isfile(filename):
  catalogue = json.load(open(filename))
else:
  catalogue = {}

## Build error file

errors = []

#Get packages

packages = get_packages()

## Create Folder if one doesn't already exist

if not os.path.exists(local_dir+"Datasets"):
  os.makedirs(local_dir+"Datasets")

### Dataset downloader

def download_set(resource, local_dir):

  downloader = urllib.URLopener()

  ## get filename unless its an HTML link
  if resource["format"] == "HTML":
    filename = resource["name"]+".html"
  else:
    filename = re.findall(r'[^/]*$', resource["url"])[0]

  target = local_dir+"/"+filename

  try: 
    # Downloader disabled for live CKAN Server
    # downloader.retrieve(resource["url"], target)
    print "\t downloading set %s" % resource["name"]
  except (urllib2.HTTPError, IOError) as e:
    error_message = str(e)
    print "skipping %s, problem..." % resource["name"]
    errors.append({"type":"dataset", "name":resource["name"], "error message":error_message})
    return

#iterate through all the packages         

for package in packages:
    try:
      response = get_package(package)
      print "successfully requested %s" % package
      
    except (urllib2.HTTPError, IOError) as e:
      error_message = str(e)
      print error_message
      print "skipping %s, problem..." % package
      errors.append({"type":"package", "name":package, "error message":error_message})
      pass
      
       
    ## Create directory if its not already there
    package_dir = local_dir + "Datasets/" + response["name"]
    
    if not os.path.exists(package_dir):
      os.makedirs(package_dir)
    
    
    ## Write a row for each resource to the catalogue
    for resource in response["resources"]:
      

      try: 
        catalogue[resource["id"]]

        ## Check if the package has been updated and download resource and update catalogue if it has
        ### TODO - check resource revision date and update, not just based on the package. 
        
        if resource["revision_timestamp"] != catalogue[resource["id"]]["last_set_revision"]:
          print "package has been updated, so"
          
          # Downloader disabled for live CKAN Server    
          # download_set(resource, package_dir)
          row = write_row(resource, response)
          catalogue[resource["id"]] = row  
        else:   
          print "\tno change - skipping %s" % resource["name"]

      except KeyError:
        print "\tNot found in the catalogue, so adding %s to the catalogue and downloading" % resource["name"]
        row = write_row(resource, response)
        catalogue[resource["id"]] = row
        
        # Downloader disabled for live CKAN Server    
        # download_set(resource, package_dir)                           
        
 

### Write catalogue and errors to files

encoded_catalogue = catalogue

## JSON

with open(local_dir+"/catalogue.json", "w") as outfile:
  json.dump(encoded_catalogue, outfile, encoding="utf-8") 
  
with open(local_dir+"/errors.json", "w") as outfile:
  json.dump(errors, outfile, encoding="utf-8")  

  
## CSV

def csv_dict_writer(path, fieldnames, data):
  f = open(path, 'wb')
  with open(path, "wb") as out_file:    
    writer = csv.DictWriter(out_file, delimiter=',', fieldnames=fieldnames, dialect='excel')
    writer.writeheader()   
    for row in data:
      writer.writerow(dict((k, v.encode('utf-8')) for k, v in row.iteritems()))


## CSV Write catalogue

data = []
fieldnames = ["set_name", "package_id", "last_set_revision", "last_package_revision", "created", "format", "url", "organisation", "description", "last_revised_by", "first_revised_by", "total_downloads", "recent_downloads", "total_package_views", "recent_package_views", "tags", "groups"]
                            
for k, v in encoded_catalogue.items():
  data.append(v)

timestamp = time.strftime("[%d-%m-%Y--%I_%M_%S]")  
path = local_dir+"/%s-catalogue.csv" % timestamp 

csv_dict_writer(path, fieldnames, data)

### CSV Write errors

path = local_dir+"/%s-errors.csv" % timestamp         
fieldnames = ["type", "name", "error message"]

csv_dict_writer(path, fieldnames, errors)

