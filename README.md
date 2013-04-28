nepomukscripts
==============

Command line tools for Nepomuk written in Python

Requirements
============

You will need the python bindings for Soprano and Nepomuk.

On openSUSE, these can be installed using the following command:
    sudo zypper install python-kde4-soprano python-kde4-nepomuk


Running
=======

Getting the list of known tags
------------------------------

    ./nepomukinfo.py -l


Displaying the properties of files
----------------------------------

    ./nepomukinfo.py /home/vincent/Pictures/PictureOfMyself.jpg

will show

    ======== /home/vincent/Pictures/PictureOfMyself.jpg
    hasTag              : "Vincent", "Travel"
    description         : A picture of myself while travelling in the mountain
    created             : 2013-01-20T11:40:17.872Z
    url                 : /home/vincent/Pictures/PictureOfMyself.jpg
    lastModified        : 2013-01-20T11:40:17.895Z


Getting a list of all files with a given tag
--------------------------------------------

    ./nepomuksearch.py -t Travel


Getting a list of files matching a nepomuk query
------------------------------------------------

    ./nepomuksearch.py -q "hasTag:Vincent AND hasTag:Travel"



