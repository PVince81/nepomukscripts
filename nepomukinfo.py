#!/usr/bin/python

import optparse
import sys
from PyQt4 import QtCore
from PyKDE4 import kdecore
from PyKDE4 import kdeui
from PyKDE4.nepomuk import Nepomuk

def formatPropertyName(propName, expand = False):
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
                text = '"' + resource.label().toUtf8().__str__() + '"'
        if value.isResourceList():
            labels = []
            for resource in value.toResourceList():
                labels.append(resource.label().toUtf8().__str__())
            text = '"' + '", "'.join(labels) + '"'

    return text

def getTags(resource):
    tags = []
    for tag in resource.tags():
        tags.append(tag.label().toUtf8().__str__())

    return tags

def getResourceFromFile(filename):
    file_info = QtCore.QFileInfo(filename)
    absolute_path = file_info.absoluteFilePath()
    return Nepomuk.Resource(kdecore.KUrl(absolute_path))


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
        tags = [t.label().toUtf8().__str__() for t in Nepomuk.Tag.allTags()]
        tags.sort()
        
        for tag in tags:
            print tag
        return

    tagToAdd = None
    if args.setTag:
        tagToAdd = Nepomuk.Tag(args.setTag)
        if tagToAdd.label() == '':
            tagToAdd.setLabel(args.setTag)

    for filename in filenames:
        resource = getResourceFromFile(filename)

        if tagToAdd:
            resource.addTag(tagToAdd)

        #resource.setDescription("This is an example comment.")
        print "========", filename

        for key, value in resource.properties().iteritems():
            print "%-20s: %s" % (formatPropertyName(key.toString().__str__(), args.expand), formatValue(value, not args.noResolve))

    
if __name__ == '__main__':
    main()
