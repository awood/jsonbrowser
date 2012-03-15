#!/usr/bin/python

import urwid
import sys
import simplejson as json
from collections import OrderedDict

class JsonTreeWidget(urwid.TreeWidget):
    """ Display widget for leaf nodes """
    def get_display_text(self):
        return self.get_node().get_value()['name']


class JsonNode(urwid.TreeNode):
    """ Data storage object for leaf nodes """
    def load_widget(self):
        return JsonTreeWidget(self)


class JsonParentNode(urwid.ParentNode):
    """ Data storage object for interior/parent nodes """
    def load_widget(self):
        return JsonTreeWidget(self)

    def load_child_keys(self):
        data = self.get_value()
        return range(len(data['children']))

    def load_child_node(self, key):
        """Return either an JsonNode or JsonParentNode"""
        childdata = self.get_value()['children'][key]
        childdepth = self.get_depth() + 1
        if 'children' in childdata:
            childclass = JsonParentNode
        else:
            childclass = JsonNode
        return childclass(childdata, parent=self, key=key, depth=childdepth)


class JsonTreeBrowser:
    palette = [
        ('body', 'black', 'light gray'),
        ('focus', 'light gray', 'dark blue', 'standout'),
        ('head', 'yellow', 'black', 'standout'),
        ('foot', 'light gray', 'black'),
        ('key', 'light cyan', 'black','underline'),
        ('title', 'white', 'black', 'bold'),
        ('flag', 'dark gray', 'light gray'),
        ('error', 'dark red', 'light gray'),
        ]

    footer_text = [
        ('title', "Json Data Browser"), "    ",
        ('key', "UP"), ",", ('key', "DOWN"), ",",
        ('key', "PAGE UP"), ",", ('key', "PAGE DOWN"),
        "  ",
        ('key', "+"), ",",
        ('key', "-"), "  ",
        ('key', "LEFT"), "  ",
        ('key', "HOME"), "  ",
        ('key', "END"), "  ",
        ('key', "Q"),
        ]

    def __init__(self, data=None):
        self.topnode = JsonParentNode(data)
        self.listbox = urwid.TreeListBox(urwid.TreeWalker(self.topnode))
        self.listbox.offset_rows = 1
        self.header = urwid.Text( "" )
        self.footer = urwid.AttrWrap( urwid.Text( self.footer_text ),
            'foot')
        self.view = urwid.Frame(
            urwid.AttrWrap( self.listbox, 'body' ),
            header=urwid.AttrWrap(self.header, 'head' ),
            footer=self.footer )

    def main(self):
        """Run the program."""
        self.loop = urwid.MainLoop(self.view, self.palette,
            unhandled_input=self.unhandled_input)
        self.loop.run()

    def unhandled_input(self, k):
        if k in ('q','Q'):
            raise urwid.ExitMainLoop()


def build_tree(data, tree):
    if type(data) is OrderedDict:
        for k, v in data.iteritems():
            if type(v) is OrderedDict:
                tree.append({"name" : "%s {}" % k, "children" : []})
                build_tree(v, tree[-1]["children"])
            elif type(v) is list:
                tree.append({"name" : "%s []" % k, "children" : []})
                build_tree(v, tree[-1]["children"])
            else:
                tree.append({"name" : "%s : %s" % (k, v)})
    elif type(data) is list:
        for i, v in enumerate(data):
            if type(v) is OrderedDict:
                tree.append({"name" : "%s {}" % i, "children" : []})
                build_tree(v, tree[-1]["children"])
            elif type(v) is list:
                tree.append({"name" : "%s []" % i, "children" : []})
                build_tree(v, tree[-1]["children"])

    return tree

def load_json(json_file):
    fp = open(json_file)
    return json.load(fp, object_pairs_hook=OrderedDict)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Please provide a single JSON file to browse.\n")
        sys.exit(-1)

    json = load_json(sys.argv[1])
    root = {"name" : "{}"}
    root["children"] = build_tree(json, [])
    JsonTreeBrowser(root).main()

if __name__=="__main__":
    main()

