#/usr/bin/python

## Initialize ckan api functions
from ckan_api_utils import *

## Set up list of available packages on ckan

packages = ckan_request(site+"package_list")

# packages = json.loads(open('dead_packages.json').read())

## Function for rewriting metadata
def rewrite_meta(packages):

  for package in packages:

    response = ckan_request(site+"package_show?id="+package)
    resources = response['resources']
    
    package = response
    try: 
      license_url = package['license_url']
      
    except Exception as e:
      error_message = str(e)
      print error_message + ": license URL not in the response"
      license_url = ""
    try: 
      license_url = package['license_id']
      
    except Exception as e:
      error_message = str(e)
      print error_message + ": license URL not in the response"
      license_id = ""
    
    if "http://dashboard.glasgow.gov.uk" in license_id:
      try:
          ## Update the license information if necessary
          license_id_updated = license_id.replace("http://dashboard.glasgow.gov.uk/", "http://open.glasgow.gov.uk/")
          
          print "changing license from -- " + license_id + " to: " + license_id_updated
          package['license_id'] = license_id_updated
          # print package['license_url']
          # Send the updated data to CKAN
          response = ckan_post("http://data.glasgow.gov.uk/api/3/action/package_update", package)
          # print response
          if "data.glasgow.gov.uk" in response['license_id']:
            print "\t ** license id successfully updated **"
      except Exception as e:
        error_message = str(e)
        print "skipping %s, problem..." % package["name"]
        print error_message
        continue
    elif "http://dashboard.glasgow.gov.uk" in license_url:
          ## Update the license information if necessary
          license_url_updated = license_url.replace("http://dashboard.glasgow.gov.uk/", "http://open.glasgow.gov.uk/")
          
          print "changing license from -- " + license_url + " to: " + license_url_updated
          package['license_url'] = license_url_updated
          # print package['license_url']
          # Send the updated data to CKAN
          response = ckan_post("http://data.glasgow.gov.uk/api/3/action/package_update", package)
          # print response
          if "data.glasgow.gov.uk" in response['license_url']:
            print "\t ** license url successfully updated **"
      except Exception as e:
        error_message = str(e)
        print "skipping %s, problem..." % package["name"]
        print error_message
        continue
    else:
      print "no need to replace license URL for " + package['name']


# Run loop
rewrite_meta(packages)

