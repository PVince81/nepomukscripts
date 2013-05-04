#!/usr/bin/python

import optparse
import sys
from PyQt4 import QtCore
from PyKDE4 import kdecore
from PyKDE4 import kdeui
from PyKDE4.nepomuk import Nepomuk

def formatPropertyName(propName, expand = False):
    if not type(propName) == str and not type(propName) == unicode:
        propName = propName.toString().__str__()

    if not expand:
        return propName[propName.index('#') + 1:]
    else:
        return propName

def formatValue(value, resolve = True):
    text = value.toString().__str__()
    if resolve:
        if value.isResource():
            resource = value.toResource()
            if not resource.isFile():
                text = u'"' + resource.label().__str__() + u'"'
        if value.isResourceList():
            labels = []
            for resource in value.toResourceList():
                labels.append(resource.label().__str__())
            text = u'"' + u'", "'.join(labels) + u'"'

    return text

def formatResult(key, value, expand = False, resolve = True):
    return "%-20s: %s" % (formatPropertyName(key, expand), formatValue(value, resolve))

def getTags(resource):
    tags = []
    for tag in resource.tags():
        tags.append(tag.label().__str__())

    return tags

def getResourceFromFile(filename):
    file_info = QtCore.QFileInfo(filename)
    absolute_path = file_info.absoluteFilePath()
    return Nepomuk.Resource(kdecore.KUrl(absolute_path))

def getResourceFromUrl(url):
    return Nepomuk.Resource(kdecore.KUrl(url))

def main():
    parser = optparse.OptionParser(description='Nepomuk File Info')
    parser.add_option('-l', '--listtags', action="store_true",
                        dest='listTags',
                        default=False, help='list all knownt tags')
    parser.add_option('-t', '--tag', action="store",
                        dest='setTag',
                        default=False, help='set tag')
    parser.add_option('-e', '--expand', action="store_true",
                        dest='expand',
                        default=False, help='expand URL names')
    parser.add_option('-n', '--noresolve', action="store_true",
                        dest='noResolve',
                        default=False, help='do not resolve resource URLs')
    parser.add_option('-u', '--url', action="store_true",
                        dest='isUrl',
                        default=False, help='Assume all arguments are URLs, not files. Default is to autodetect.')
    parser.add_option('-p', '--properties', action="store",
                        dest='properties',
                        default=False, help='Comma separated list of shortened property names')
    parser.add_option('-P', '--propertyurls', action="store",
                        dest='urlProperties',
                        default=False, help='Comma separated list of property name URLs')
    (args, rest) = parser.parse_args()
    if len(rest) == 0 and not args.listTags:
        print("Filename argument missing")
        parser.print_usage()
        sys.exit(1)

    filenames = rest

    result = Nepomuk.ResourceManager.instance().init()
    if result != 0:
        print("Error initializing nepomuk: result code %i" % result)
        sys.exit(2) 

    if args.listTags:
        tags = [t.label().__str__() for t in Nepomuk.Tag.allTags()]
        tags.sort()
        
        for tag in tags:
            print tag
        return

    properties = None
    if args.properties:
        properties = set(args.properties.split(','))

    urlProperties = None
    if args.urlProperties:
        urlProperties = set(args.urlProperties.split(','))

    tagToAdd = None
    if args.setTag:
        tagToAdd = Nepomuk.Tag(args.setTag)
        if tagToAdd.label() == '':
            tagToAdd.setLabel(args.setTag)

    for filename in filenames:
        url = kdecore.KUrl(filename)
        if url.scheme() == "" and not args.isUrl:
            file_info = QtCore.QFileInfo(filename)
            absolute_path = file_info.absoluteFilePath()
            url = kdecore.KUrl(absolute_path)

        resource = Nepomuk.Resource(url)

        if tagToAdd:
            resource.addTag(tagToAdd)

        if resource.isFile():
            print "========", filename
        else:
            print "======== (%s) %s" % (resource.className(), filename)

        if args.urlProperties:
            for propUrl in urlProperties:
                value = resource.property(propUrl)
                print formatResult(propUrl, value, args.expand, not args.noResolve)
        else:
            for key, value in resource.properties().iteritems():
                propName = formatPropertyName(key.toString().__str__(), False)
                if not properties or propName in properties:
                    print formatResult(key, value, args.expand, not args.noResolve)

    
if __name__ == '__main__':
    main()
