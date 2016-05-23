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
    license = package['license_url']
    
    if "http://dashboard.glasgow.gov.uk" in license:
      try:
          ## Update the license information if necessary
          license_updated = license.replace("http://dashboard.glasgow.gov.uk/", "http://data.glasgow.gov.uk/")
          print "changing license from -- " + license + " to: " + license_updated
          package['license_url'] = license_updated
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
     
# DONE - Step 4 - Iterate through the resources
  print str(len(response['resources'])) + " resources for " + response['name']
  for resource in resources:

    url = resource['url']
    if "http://dashboard.glasgow.gov.uk" in url:
      try:
        print "\t " + resource['name'] + " has the url: " + url
        replaced_url = url.replace("http://dashboard.glasgow.gov.uk/", "http://data.glasgow.gov.uk/")
        resource['url'] = replaced_url
        print "\t changing it to: " + replaced_url

        # Send the updated data to CKAN
        response = ckan_post("http://data.glasgow.gov.uk/api/3/action/resource_update", resource)
        if "data.glasgow.gov.uk" in response['url']:
          print "\t ** data url successfully updated **"
      except Exception as e:
        error_message = str(e)
        print "skipping %s, problem..." % resource
        print error_message
        continue

    else:
      print "\t no need to replace for " + resource['name']

# Run loop
rewrite_meta(packages)

