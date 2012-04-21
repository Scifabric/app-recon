#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import datetime
from optparse import OptionParser

def delete_app(api_url, api_key, id):
    """
    Deletes the application.

    :arg integer id: The ID of the application
    :returns: True if the application has been deleted
    :rtype: boolean
    """
    request = urllib2.Request(api_url + '/api/app/' + str(id) + '?api_key=' + api_key)
    request.get_method = lambda: 'DELETE'

    if (urllib2.urlopen(request).getcode() == 204):
        return True
    else:
        return False

def update_app(api_url, api_key, id, name = None):
    """
    Updates the name of the application

    :arg integer id: The ID of the application
    :arg string name: The new name for the application
    :returns: True if the application has been updated
    :rtype: boolean
    """
    data = dict(id = id, name = name)
    data = json.dumps(data)
    request = urllib2.Request(api_url + '/api/app/' + str(id) + '?api_key=' + api_key)
    request.add_data(data)
    request.add_header('Content-type', 'application/json')
    request.get_method = lambda: 'PUT'

    if (urllib2.urlopen(request).getcode() == 200):
        return True
    else:
        return False

def create_app(api_url , api_key, template="template.html"):
    """
    Creates the application.

    :arg string name: The application name.
    :arg string short_name: The slug application name.
    :arg string description: A short description of the application.

    :returns: Application ID or 0 in case of error.
    :rtype: integer
    """
    print('Creating app')

    # JSON Blob to present the tasks for this app to the users
    # First we read the template:
    name = u'Identify'
    short_name = u'identify'
    info = {'task_presenter': open(template).read()}
    data = {
        'name':        name,
        'short_name':  short_name,
        'description': u'Help clean up messy datasets by grouping names to the entities they represent',
        'hidden':      0,
        'info':        info
    }
    data = json.dumps(data)

    # Checking which apps have been already registered in the DB
    apps = json.loads(urllib2.urlopen(api_url + '/api/app' + '?api_key=' + api_key).read())
    for app in apps:
        if app['short_name'] == short_name:
            print('{app_name} app is already registered in the DB'.format(app_name=name))
            print('Deleting it!')
            if (delete_app(api_url, api_key, app['id'])): print "Application deleted!"

    print("The application is not registered in PyBOSSA. Creating it...")
    # Setting the POST action
    request = urllib2.Request(api_url + '/api/app?api_key=' + api_key )
    request.add_data(data)
    request.add_header('content-type', 'application/json')

    # Create the app in PyBOSSA
    output = json.loads(urllib2.urlopen(request).read())
    if (output['id'] != None):
        print("Done!")
        return output['id']
    else:
        print("Error creating the application")
        return 0

def create_task(api_url, api_key, app_id, name):
    """
    Creates tasks for the application

    :arg integer app_id: Application ID in PyBossa.
    :returns: Task ID in PyBossa.
    :rtype: integer
    """
    # Data for the tasks
    info = {'name': name}
    data = {'app_id': app_id, 'state': 0, 'info': info, 'calibration': 0, 'priority_0': 0}
    data = json.dumps(data)

    # print data

    # Setting the POST action
    request = urllib2.Request(api_url + '/api/task' + '?api_key=' + api_key)
    request.add_data(data)
    request.add_header('Content-type', 'application/json')

    # Create the task
    output = json.loads(urllib2.urlopen(request).read())
    if (output['id'] != None):
        return True
    else:
        return False

import sys
if __name__ == "__main__":
    # Arguments for the application
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)

    parser.add_option("-u", "--url", dest="api_url", help="PyBossa URL http://domain.com/", metavar="URL")
    parser.add_option("-k", "--api-key", dest="api_key", help="PyBossa User API-KEY to interact with PyBossa", metavar="API-KEY")
    parser.add_option("-t", "--template", dest="template", help="PyBossa HTML+JS template for application presenter", metavar="TEMPLATE")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")

    (options, args) = parser.parse_args()

    if not options.api_url:
        options.api_url = 'http://localhost:5000'

    if not options.api_key:
        parser.error("You must supply an API-KEY to create an applicationa and tasks in PyBossa")

    if not options.template:
        print("Using default template: template.html")
        options.template = "template.html"

    if (options.verbose):
       print('Running against PyBossa instance at: %s' % options.api_url)
       print('Using API-KEY: %s' % options.api_key)

    app_id = create_app(options.api_url, options.api_key, template = options.template)

    for city in sys.stdin:
        create_task(options.api_url, options.api_key, app_id, city[:-1])

