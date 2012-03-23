#! /usr/bin/python

import sys
import pygtk
pygtk.require('2.0')
import gtk
import simplejson as json
from collections import OrderedDict

class JsonTreeView(object):
    def __init__(self, json):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("JSON Browser")
        self.window.set_size_request(400, 600)
        self.window.connect("delete_event", self.delete_event)

        treestore = gtk.TreeStore(str)
        treestore = self.buildTreeStore(json, treestore, None)
        treeview = self.buildTreeView(treestore)
        self.window.add(treeview)
        self.window.show_all()

    def buildTreeView(self, treestore):
        treeview = gtk.TreeView(treestore)
        tvcolumn = gtk.TreeViewColumn('JSON')
        treeview.append_column(tvcolumn)

        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)

        return treeview

    def buildTreeStore(self, data, treestore, parent):
        if type(data) is OrderedDict:
            for k, v in data.iteritems():
                if type(v) is OrderedDict:
                    parent = treestore.append(parent, ["%s {}" % k])
                    self.buildTreeStore(v, treestore, parent)
                elif type(v) is list:
                    parent = treestore.append(parent, ["%s []" % k])
                    self.buildTreeStore(v, treestore, parent)
                else:
                    treestore.append(parent, ["%s : %s" % (k, v)])
        elif type(data) is list:
            for i, v in enumerate(data):
                if type(v) is OrderedDict:
                    parent = treestore.append(parent, ["%s {}" % i])
                    self.buildTreeStore(v, treestore, parent)
                elif type(v) is list:
                    parent = treestore.append(parent, ["%s []" % i])
                    self.buildTreeStore(v, treestore, parent)
                else:
                    treestore.append(parent, ["%s : %s" % (i, v)])

        return treestore

    def main(self):
        gtk.main()

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

def load_json(json_file):
    fp = open(json_file)
    return json.load(fp, object_pairs_hook=OrderedDict)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Please provide a single JSON file to browse.\n")
        sys.exit(-1)

    json = load_json(sys.argv[1])

    tree = JsonTreeView(json)
    tree.main()

if __name__ == '__main__':
    main()