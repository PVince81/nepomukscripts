#!/usr/bin/python

import signal, os
import optparse
import sys
from PyQt4 import QtCore,QtGui
from PyKDE4 import kdecore
from PyKDE4 import kdeui
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.kio import KIO
from PyKDE4.soprano import Soprano

app = None
job = None
q = None

class NepomukQuery(QtCore.QObject):
 
    def __init__(self, parent=None, options={}):
        super(NepomukQuery, self).__init__(parent)
        self.options = options
        self.count = 0

    def query_string(self, url):
        search_job = KIO.listDir(kdecore.KUrl('nepomuksearch:/?query=' + url), KIO.HideProgressInfo)
        search_job.entries.connect(self.search_slot)
        search_job.result.connect(self.result)
        search_job.start()
        return search_job

    def query_tag(self, tagNames):
        soprano_term_uri = Soprano.Vocabulary.NAO.hasTag()
        nepomuk_property = Nepomuk.Types.Property(soprano_term_uri)

        tag = Nepomuk.Tag(tagNames[0])

        if tag.uri() == "":
            print "Tag \"%s\" does not exist" % tagNames[0]
            return False

        comparison_term = Nepomuk.Query.ComparisonTerm(nepomuk_property, Nepomuk.Query.ResourceTerm(tag))
        if self.options.filesOnly:
            query = Nepomuk.Query.FileQuery(comparison_term)
        else:
            query = Nepomuk.Query.Query(comparison_term)

        search_url = query.toSearchUrl()

        search_job = KIO.listDir(kdecore.KUrl(search_url), KIO.HideProgressInfo)
        search_job.entries.connect(self.search_slot)
        search_job.result.connect(self.result)
        search_job.start()
        return search_job

    def search_slot(self, job, data):
        global app
        for item in data:
            print item.stringValue(KIO.UDSEntry.UDS_URL),
            print "\t",
            print (item.stringValue(KIO.UDSEntry.UDS_LOCAL_PATH).__str__() or item.stringValue(KIO.UDSEntry.UDS_NAME).__str__())

            self.count = self.count + 1

    def result(self, job):
        print >> sys.stderr, "Retrieved %i result(s)" % self.count
        job.entries.disconnect()
        app.exit()

def term_handler(signum, frame):
    job.kill()
    app.exit()
    print >> sys.stderr, "Interrupted"

def main():
    global app
    global job

    parser = optparse.OptionParser(description='Nepomuk Search')
    parser.add_option('-t', '--tags', action="store",
                        dest='useTags',
                        default=False, help='comma separated list of tags to search for')
    parser.add_option('-q', '--query', action="store",
                        dest='useQuery',
                        default=False, help='specify Nepomuk query')
    parser.add_option('-f', '--files', action="store_true",
                        dest='filesOnly',
                        default=False, help='limit results to files')
    (args, rest) = parser.parse_args()

    result = Nepomuk.ResourceManager.instance().init()
    if result != 0:
        print("Error initializing nepomuk: result code %i" % result)
        sys.exit(2) 

    app = QtGui.QApplication(sys.argv)

    signal.signal(signal.SIGTERM, term_handler)
    signal.signal(signal.SIGINT, term_handler)

    if args.useQuery:
        q = NepomukQuery(None, args)
        job = q.query_string(args.useQuery)
        
    elif args.useTags:
        q = NepomukQuery(None, args)
        job = q.query_tag(args.useTags.split(','))

    if job:
       app.exec_()
    
if __name__ == '__main__':
    main()
