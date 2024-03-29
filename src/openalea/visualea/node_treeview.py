# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#
#       Distributed under the CeCILL v2 License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################
"""Tree Item model for package manager.

Only Package and Category objects are view as a tree item.
Others are view as leaves.
"""
from __future__ import print_function

from builtins import str
from builtins import range
from builtins import object
__license__ = "CeCILL v2"
__revision__ = " $Id$ "

import os
from weakref import ref

from qtpy import QtWidgets, QtCore, QtGui

from openalea.core.node import NodeFactory, AbstractFactory
from openalea.core.data import DataFactory
from openalea.core.package import Package, UserPackage
from openalea.core.compositenode import CompositeNodeFactory
from openalea.core.pkgmanager import PackageManager
from openalea.core.pkgmanager import PseudoGroup, PseudoPackage
from openalea.core import cli

from openalea.visualea.dialogs import EditPackage, NewGraph, NewPackage, NewData
from openalea.visualea.util import open_dialog, exception_display, busy_cursor
from openalea.visualea.node_widget import SignalSlotListener
from openalea.visualea.code_editor import get_editor
from openalea.visualea.util import grab_icon

from openalea.visualea import images_rc


# Utilities function

icon_dict = None

# pradal
from functools import cmp_to_key

def cmp(a, b):
    return (a > b) - (a < b) 

def get_icon(item):
    """ Return Icon object depending of the type of item """

    global icon_dict
    if(not icon_dict):
        # dict to do a switch
        icon_dict = {
            PseudoGroup: QtGui.QPixmap(":/icons/category.png"),
            CompositeNodeFactory: QtGui.QPixmap(":/icons/diagram.png"),
            NodeFactory: QtGui.QPixmap(":/icons/node.png"),
            DataFactory: QtGui.QPixmap(":/icons/data.png"),
            UserPackage: QtGui.QPixmap(":/icons/usrpkg.png"),
            Package: QtGui.QPixmap(":/icons/pkg.png"),
        }

    # Get icon from dictionary
    if(type(item) in icon_dict):
        return icon_dict[type(item)]

    elif(isinstance(item, PseudoPackage)):

        if(item.is_real_package()):

            # Try to load package specific icon
            icon = item.item.metainfo.get("icon", None)
            if(icon):
                icon = os.path.join(item.item.path, icon)
                pix = QtGui.QPixmap(icon)
                if(not pix.isNull()):
                    return pix

            # Standard icon
            return icon_dict[type(item.item)]

        return QtGui.QPixmap(":/icons/pseudopkg.png")

    else:
        return None


# Qt4 Models/View classes
type_hierarchy = [(Package, UserPackage, PseudoPackage, PseudoGroup), (CompositeNodeFactory,), (NodeFactory,), (DataFactory,)]
type_order_map = {}
for i, types in enumerate(type_hierarchy):
    for t in types:
        type_order_map[t] = i


def item_compare(x, y):
    if type(x) == type(y):
        return cmp(x.get_id(), y.get_id())
    else:
        tx, ty = type(x), type(y)
        for t in type_order_map:
            if isinstance(x, t):
                tx = t
                break
        for t in type_order_map:
            if isinstance(y, t):
                ty = t
                break
        return cmp(type_order_map[tx], type_order_map[ty])


class PkgModel (QtCore.QAbstractItemModel):

    """ QT4 data model (model/view pattern) to support pkgmanager """

    def __init__(self, pkgmanager, parent=None):

        QtCore.QAbstractItemModel.__init__(self, parent)
        self.pman = pkgmanager
        self.rootItem = self.pman.get_pseudo_pkg()

        self.parent_map = {}
        self.row_map = {}
        self.index_map = {} # map between name and Index object

    def reset(self):

        self.rootItem = self.pman.get_pseudo_pkg()
        QtCore.QAbstractItemModel.beginResetModel(self)
        QtCore.QAbstractItemModel.endResetModel(self)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):

        if not index.isValid():
            return None

        item = index.internalPointer()

        # Text
        if (role == QtCore.Qt.DisplayRole):

            # Add size info
            lenstr = ''
            try:
                l = item.nb_public_values()
                if(l):
                    lenstr = " ( %i )" % (l,)
            except:
                pass

            return str(item.get_id()) + lenstr

        # Tool Tip
        elif(role == QtCore.Qt.ToolTipRole):
            return str(item.get_tip())

        # Icon
        elif(role == QtCore.Qt.DecorationRole):
            return get_icon(item)

        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | \
            QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsDragEnabled

    def headerData(self, section, orientation, role):
        return None

    def get_full_name(self, item):
        """construct a full unique name from item
        using parent.parent.item syntax
        """
        if item is None:
            return None
        try:
            if item.item is not None:
                return item.item.name
        except AttributeError:
            pass
        return item.name

    def index(self, row, column, parent):

        if (not parent.isValid()):
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        l = list(parentItem.iter_public_values())
     # F. Bauget 2023-01-18    
        l.sort(key=cmp_to_key(item_compare)) 
        childItem = l[row]

        # save parent and row
        self.parent_map[id(childItem)] = parentItem
        self.row_map[id(childItem)] = row

        i = self.createIndex(row, column, childItem)

        name = self.get_full_name(childItem)
        #self.index_map[childItem.name] = i
        self.index_map[name] = i

        return i

    def parent(self, index):

        if (not index.isValid()):
            return QtCore.QModelIndex()

        childItem = index.internalPointer()

        parentItem = self.parent_map[id(childItem)]

        # Test if it is the root
        if (id(parentItem) not in self.parent_map):
            return QtCore.QModelIndex()

        else:
            row = self.row_map[id(parentItem)]
            return self.createIndex(row, 0, parentItem)

    def rowCount(self, parent):

        if (not parent.isValid()):
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        if isinstance(parentItem, AbstractFactory):
            return 0

        # Return the number of DIFFERENT OBJECTS
        l = parentItem.nb_public_values()

        return l


class CategoryModel (PkgModel):

    """ QT4 data model (model/view pattern) to view category """

    def __init__(self, pkgmanager, parent=None):

        QtCore.QAbstractItemModel.__init__(self, parent)
        self.pman = pkgmanager
        self.rootItem = self.pman.get_pseudo_cat()

        self.parent_map = {}
        self.row_map = {}
        self.index_map = {}

    def reset(self):
        self.rootItem = self.pman.get_pseudo_cat()
        # self.parent_map = {}
        # self.row_map = {}
        QtCore.QAbstractItemModel.beginResetModel(self)
        QtCore.QAbstractItemModel.endResetModel(self)


class DataPoolModel (QtCore.QAbstractListModel):

    """ QT4 data model (model/view pattern) to support Data Pool """

    def __init__(self, datapool, parent=None):

        QtCore.QAbstractListModel.__init__(self, parent)
        self.datapool = datapool

    def reset(self):
        QtCore.QAbstractItemModel.beginResetModel(self)
        QtCore.QAbstractItemModel.endResetModel(self)

    def data(self, index, role):

        if (not index.isValid()):
            return None

        if (index.row() >= len(list(self.datapool.keys()))):
            return None

        if (role == QtCore.Qt.DisplayRole):
            l = list(self.datapool.keys())
            l.sort()
            name = l[index.row()]
            #classname = self.datapool[name].__class__
            value = repr(self.datapool[name])
            if(len(value) > 30):
                value = value[:30] + "..."
            return "%s ( %s )" % (name, value)

        # Icon
        elif(role == QtCore.Qt.DecorationRole):
            return QtGui.QPixmap(":/icons/ccmime.png")

        # Tool Tip
        elif(role == QtCore.Qt.ToolTipRole):
            l = list(self.datapool.keys())
            l.sort()
            name = l[index.row()]

            tips = [name]

            tips.append("%s\n" % (str(self.datapool[name]),))
            tips.append("Dir :")

            temp = ""
            for i, n in enumerate(dir(self.datapool[name])):
                s = str(n)
                if(len(s) > 20):
                    s = s[:20]
                temp += s + "\t\t"
                # 2 column view
                if(i % 2):
                    tips.append(temp)
                    temp = ""

            if(temp):
                tips.append(temp)
            tipstr = '\n'.join(tips)

            return str(tipstr)

        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | \
            QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsDragEnabled

    def headerData(self, section, orientation, role):
        return None

    def rowCount(self, parent):
        return len(list(self.datapool.keys()))


class SearchModel (QtCore.QAbstractListModel):

    """ QT4 data model (model/view pattern) to support Search result"""

    def __init__(self, parent=None):

        QtCore.QAbstractListModel.__init__(self, parent)
        self.searchresult = []

    def reset(self):
        QtCore.QAbstractListModel.beginResetModel(self)
        QtCore.QAbstractListModel.endResetModel(self)

    def set_results(self, results):
        """ Set the search results : results is a list of factory """
        self.searchresult = results
        self.beginResetModel()
        # self.searchresult = None
        self.endResetModel()
        # self.reset() # deprecated

    def index(self, row, column, parent):

        if (row < len(self.searchresult)):
            factory = self.searchresult[row]
            return self.createIndex(row, column, factory)

        else:
            return QtCore.QModelIndex()

    def data(self, index, role):

        if (not index.isValid()):
            return None

        if (index.row() >= len(self.searchresult)):
            return None

        item = self.searchresult[index.row()]

        if (role == QtCore.Qt.DisplayRole):
            if(index.column() == 1):
                return str(item.package.get_id())
            return str(item.name + " (" + item.package.name + ")")

        # Icon
        elif(role == QtCore.Qt.DecorationRole):
            if(index.column() > 0):
                return None
            return get_icon(item)

        # Tool Tip
        elif(role == QtCore.Qt.ToolTipRole):
            return str(item.get_tip())

        else:
            return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        return QtCore.Qt.ItemIsEnabled | \
            QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsDragEnabled

    def headerData(self, section, orientation, role):
        return None

    def rowCount(self, parent):

        if (not parent.isValid()):
            return len(self.searchresult)
        else:
            return 0

    def columnCount(self, index):
        return 2


################################################################################
# Views

class NodeFactoryView(object):

    """
    Base class for all view which display node factories.
    Implements Drag and Drop facilities.
    """

    def __init__(self, main_win=None, parent=None):
        """
        @param main_win : main window
        @param parent : parent widget
        """
        if main_win:
            self.set_main_win(main_win)
        else:
            self.main_win = None

        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)
        try:
            h = self.header().hide()
        except:
            pass

    def set_main_win(self, main_win):
        self.main_win = ref(main_win)

    def dragEnterEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasFormat(NodeFactory.mimetype) or mimedata.hasFormat(CompositeNodeFactory.mimetype):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        mimedata = event.mimeData()
        if mimedata.hasFormat(NodeFactory.mimetype) or mimedata.hasFormat(CompositeNodeFactory.mimetype):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        event.ignore()

    def startDrag(self, supportedActions):

        item = self.currentIndex()

        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        pixmap = QtGui.QPixmap(item.data(QtCore.Qt.DecorationRole))

        (pkg_id, factory_id, mimetype) = self.get_item_info(item)

        dataStream.writeQString(pkg_id) # otherwise unexpected str type, 2 other lines modified
        dataStream.writeQString(factory_id)
        mimeData = QtCore.QMimeData()

        mimeData.setData(mimetype, itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QtCore.QPoint(pixmap.width() // 2, pixmap.height() // 2))
        drag.setPixmap(pixmap)

        drag.exec_(QtCore.Qt.MoveAction)

    @staticmethod
    def get_item_info(item):
        """
        Return (package_id, factory_id, mimetype) corresponding to item.
        """

        # put in the Mime Data pkg id and factory id
        obj = item.internalPointer()

        if obj.mimetype in [NodeFactory.mimetype, CompositeNodeFactory.mimetype]:

            factory_id = obj.get_id()
            pkg_id = obj.package.get_id()

            return (pkg_id, factory_id, obj.mimetype)

        return ("0", "0", "openalea/notype")

    def contextMenuEvent(self, event):
        """ Context menu event : Display the menu"""

        item = self.currentIndex()
        obj = item.internalPointer()
        menu = None

        if(isinstance(obj, AbstractFactory)): # Factory
            menu = QtWidgets.QMenu(self)
            action = menu.addAction("Open")
            action.triggered.connect(self.open_node)

            action = menu.addAction("Edit")
            action.triggered.connect(self.edit_node)

            action = menu.addAction("Properties")
            action.triggered.connect(self.edit_properties)

            menu.addSeparator()

            action = menu.addAction("Remove")
            action.triggered.connect(self.remove_node)

        elif(isinstance(obj, PseudoPackage)): # Package

            enabled = obj.is_real_package()
            pkg = obj.item

            menu = QtWidgets.QMenu(self)

            action = menu.addAction("Open URL")
            action.setEnabled(enabled)
            action.triggered.connect(self.open_node)

            action = menu.addAction("Meta informations")
            action.setEnabled(enabled)
            action.triggered.connect(self.edit_package)

            action = menu.addAction("Edit Code")
            action.setEnabled(enabled and pkg.is_editable())
            action.triggered.connect(self.edit_pkg_code)

            menu.addSeparator()

            action = menu.addAction("Add Python Node")
            action.setEnabled(enabled and pkg.is_editable())
            action.triggered.connect(self.add_python_node)

            action = menu.addAction("Add Composite Node")
            action.setEnabled(enabled and pkg.is_editable())
            action.triggered.connect(self.add_composite_node)

            action = menu.addAction("Add Data File")
            action.setEnabled(enabled and pkg.is_editable())
            action.triggered.connect(self.add_data)

            menu.addSeparator()

            action = menu.addAction("Grab Icon")
            action.setEnabled(enabled)
            action.triggered.connect(self.grab_icon)

            menu.addSeparator()

            action = menu.addAction("Move/Rename Package")
            action.setEnabled(enabled and pkg.is_editable())
            action.triggered.connect(self.move_package)

            action = menu.addAction("Copy Package")
            action.setEnabled(enabled)
            action.triggered.connect(self.duplicate_package)

            action = menu.addAction("Remove Package")
            action.setEnabled(enabled and pkg.is_editable())
            action.triggered.connect(self.remove_package)

            menu.addSeparator()

            action = menu.addAction("Reload Package")
            action.setEnabled(enabled)
            action.triggered.connect(self.reload_package)

        if(menu):
            menu.move(event.globalPos())
            menu.show()

    def get_current_pkg(self):
        """ Return the current package """
        item = self.currentIndex()
        obj = item.internalPointer()
        # obj is necessary a pseudo package (menu disbled in other case)
        obj = obj.item

        return obj

    def add_python_node(self):
        """ """
        pman = self.model().pman # pkgmanager
        pkg = self.get_current_pkg()

        dialog = NewGraph("New Python Node", pman, self, pkg_id=pkg.name)
        ret = dialog.exec_()

        if(ret > 0):
            dialog.create_nodefactory(pman)
            self.reinit_treeview()

    def add_composite_node(self):
        """ """
        pman = self.model().pman # pkgmanager
        pkg = self.get_current_pkg()

        dialog = NewGraph("New Composite Node", pman, self, pkg_id=pkg.name)
        ret = dialog.exec_()

        if(ret > 0):
            newfactory = dialog.create_cnfactory(pman)
            self.reinit_treeview()

    def add_data(self):
        """ """
        pman = self.model().pman # pkgmanager
        pkg = self.get_current_pkg()

        dialog = NewData("Import Data", pman, self, pkg_id=pkg.name)
        ret = dialog.exec_()

        if(ret > 0):
            newfactory = dialog.create_datafactory(pman)
            self.reinit_treeview()

    def remove_package(self):
        """ Remove selected package """

        pkg = self.get_current_pkg()
        pman = self.model().pman # pkgmanager

        if(not pkg.is_directory()):
            QtWidgets.QMessageBox.warning(self, "Error",
                                         "Cannot Remove old style package\n")
            return

        if(not pkg.is_editable()):
            return

        ret = QtWidgets.QMessageBox.question(self, "Remove package",
                                            "Remove %s?\n" % (pkg.name,),
                                            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No,)

        if(ret == QtWidgets.QMessageBox.No):
            return

        try:
            pkg.remove_files()
        except AssertionError:
            return

        del pman[pkg.get_id()]
        self.reinit_treeview()

    def grab_icon(self):
        """ Set the package icon """

        pkg = self.get_current_pkg()
        if self.main_win is None:
            parent = self
        else:
            parent = self.main_win()
        pix = grab_icon(parent)

        fname = os.path.join(pkg.path, "icon.png")
        pix.save(fname)
        pkg.set_icon(fname)

        self.reinit_treeview()

    def edit_pkg_code(self):
        """ Edit __wralea__ """

        pkg = self.get_current_pkg()
        pman = self.model().pman # pkgmanager

        if(not pkg.is_directory()):
            QtWidgets.QMessageBox.warning(self, "Error",
                                         "Cannot edit code of old style package\n")
            return

        filename = pkg.get_wralea_path()
        widget = get_editor()(self)
        widget.edit_file(filename)

        if self.main_win is None:
            parent = self
        else:
            parent = self.main_win()

        if(widget.is_widget()):
            open_dialog(parent, widget, pkg.name)

    def reload_package(self):
        """ Reload package """

        pkg = self.get_current_pkg()
        pman = self.model().pman # pkgmanager

        if(not pkg.is_directory()):
            QtWidgets.QMessageBox.warning(self, "Error",
                                         "Cannot reload old style package\n")
            return

        pman.reload(pkg)
        self.reinit_treeview()

    def duplicate_package(self):
        """ Duplicate a package """

        pkg = self.get_current_pkg()
        pman = self.model().pman # pkgmanager

        if(not pkg.is_directory()):
            QtWidgets.QMessageBox.warning(self, "Error",
                                         "Cannot duplicate old style package\n")
            return

        dialog = NewPackage(list(pman.keys()), parent=self, metainfo=pkg.metainfo)
        ret = dialog.exec_()

        if(ret > 0):
            (name, metainfo, path) = dialog.get_data()

            newpkg = pman.create_user_package(name, metainfo, path)
            newpkg.clone_from_package(pkg)
            pman.add_package(newpkg)
            self.reinit_treeview()

    def move_package(self):
        """ Move a package """

        pkg = self.get_current_pkg()
        pman = self.model().pman # pkgmanager

        if(not pkg.is_directory()):
            QtWidgets.QMessageBox.warning(self, "Error",
                                         "Cannot move old style package\n")
            return

        (result, ok) = QtWidgets.QInputDialog.getText(self, "Move/Rename Package",
                                                     "Full new name (ex: openalea.data)",
                                                     QtWidgets.QLineEdit.Normal, )

        if(ok):
            new_name = str(result)
            old_name = pkg.name
            pman.rename_package(old_name, new_name)
            self.reinit_treeview()

    def edit_package(self):
        """ Edit package Metadata """

        obj = self.get_current_pkg()

        dialog = EditPackage(obj, parent=self)
        ret = dialog.exec_()

    def mouseDoubleClickEvent(self, event):
        # TODO: emit signal to make widget totally independent
        if self.main_win is None:
            return

        item = self.currentIndex()
        obj = item.internalPointer()

        if(isinstance(obj, CompositeNodeFactory)):
            session = self.main_win().session
            for ws in session.workspaces:
                if obj == ws.factory:
                    res = QtWidgets.QMessageBox.warning(self.main_win(), "Other instances are already opened!",
                                                       """You are trying to open a composite node that has already been opened.
Doing this might cause confusion later on.
Do you want to continue?""",
                                                       QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                    if res == QtWidgets.QMessageBox.Cancel:
                        return
                    else:
                        break

            self.edit_node()
        elif (not isinstance(obj, Package)):
            self.open_node()

    @busy_cursor
    @exception_display
    def open_node(self):
        """ Instantiate Node : open a dialog """

        item = self.currentIndex()
        obj = item.internalPointer()

        if self.main_win is None:
            parent = self
        else:
            parent = self.main_win()

        if(isinstance(obj, AbstractFactory)):
            widget = obj.instantiate_widget(autonomous=True)
            open_dialog(parent, widget, obj.get_id())

        elif(isinstance(obj, PseudoPackage)):
            # Display URL
            urlstr = obj.get_metainfo('url')
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(urlstr))

    @busy_cursor
    @exception_display
    def edit_node(self):
        """ Edit Node in tab workspace"""

        if self.main_win is None:
            return

        item = self.currentIndex()
        obj = item.internalPointer()

        if(isinstance(obj, CompositeNodeFactory)):
            self.main_win().open_compositenode(obj)

        elif(isinstance(obj, NodeFactory)
             or isinstance(obj, DataFactory)
             ):
            widget = obj.instantiate_widget(edit=True)
            if(widget.is_widget()):
                open_dialog(self.main_win(), widget, obj.get_id())

    def edit_properties(self):
        """ Edit Node info"""

        item = self.currentIndex()
        obj = item.internalPointer()

        if(isinstance(obj, DataFactory)):
            QtWidgets.QMessageBox.information(self, "Properties", "Data : %s" % (obj.name))
            return

        d = NewGraph("Node Properties", PackageManager(), self, obj)
        ret = d.exec_()
        if(ret):
            d.update_factory()

    def remove_node(self):
        """ Remove the node from the package """

        item = self.currentIndex()
        obj = item.internalPointer()

        ret = QtWidgets.QMessageBox.question(self, "Remove Model",
                                            "Remove %s?\n" % (obj.name,),
                                            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No,)

        if(ret == QtWidgets.QMessageBox.Yes):

            try:
                obj.package[obj.name].clean_files()
            except Exception as e:
                print(e)

            del(obj.package[obj.name])
            obj.package.write()
            self.reinit_treeview()

    def reinit_treeview(self):
        if self.main_win:
            self.main_win().reinit_treeview()


class NodeFactoryTreeView(QtWidgets.QTreeView, NodeFactoryView):

    """ Specialized TreeView to display node factory in a tree with Drag and Drop support  """

    def __init__(self, main_win, parent=None):
        """
        @param main_win : main window
        @param parent : parent widget
        """

        QtWidgets.QTreeView.__init__(self, parent)
        NodeFactoryView.__init__(self, main_win, parent)

        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        #self.setAnimated(True)

        # F. Bauget 2023-01-18
        # self.connect(self, qt.QtCore.SIGNAL("expanded (const QModelIndex &)"), self.expanded)
        # self.connect(self, qt.QtCore.SIGNAL("collapsed (const QModelIndex &)"), self.collapsed)
        self.expanded.connect(self.on_expanded)
        self.collapsed.connect(self.on_collapsed)

        
        self.expanded_items = set()
    
    def on_collapsed(self, index):
        name = self.model().get_full_name(index.internalPointer())
        #self.expanded_items.remove(index.internalPointer().name)
        self.expanded_items.remove(name)

    def on_expanded(self, index):
        name = self.model().get_full_name(index.internalPointer())
        #self.expanded_items.add(index.internalPointer().name)
        self.expanded_items.add(name)

    def reset(self):
        QtWidgets.QTreeView.reset(self)

        for n in list(self.expanded_items):
            i = self.model().index_map[n]
            self.setExpanded(i, True)


class SearchListView(QtWidgets.QTreeView, NodeFactoryView):

    """ Specialized QListView to display search results with Drag and Drop support """

    def __init__(self, main_win, parent=None):
        """
        @param main_win : main window
        @param parent : parent widget
        """

        QtWidgets.QTreeView.__init__(self, parent)
        NodeFactoryView.__init__(self, main_win, parent)
        self.setRootIsDecorated(False)

    def reset(self):
        QtWidgets.QTreeView.reset(self)
        for i in range(self.model().columnCount(None)):
            self.resizeColumnToContents(i)


class DataPoolListView(QtWidgets.QListView, SignalSlotListener):

    """ Specialized QListView to display data pool contents """

    def __init__(self, main_win, datapool, parent=None):
        """
        @param main_win : main window
        @param datapool : datapool instance
        @param parent : parent widget
        """

        QtWidgets.QListView.__init__(self, parent)
        SignalSlotListener.__init__(self)

        self.main_win = ref(main_win)

        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setAcceptDrops(True)

        self.initialise(datapool)

    def notify(self, sender, event):
        """ Notification by observed """

        self.reset()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("openalea/data_instance"):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("openalea/data_instance"):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):

        event.ignore()

    def startDrag(self, supportedActions):

        item = self.currentIndex()

        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        pixmap = QtGui.QPixmap(":/icons/ccmime.png")

        l = list(self.model().datapool.keys())
        l.sort()
        name = l[item.row()]

        dataStream.writeQString(name)

        mimeData = QtCore.QMimeData()
        mimeData.setData("openalea/data_instance", itemData)

        linecode = cli.get_datapool_code(name)
        mimeData.setText(linecode)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QtCore.QPoint(pixmap.width() // 2, pixmap.height() // 2))
        drag.setPixmap(pixmap)

        drag.exec(QtCore.Qt.MoveAction)

    def contextMenuEvent(self, event):
        """ Context menu event : Display the menu"""

        menu = QtWidgets.QMenu(self)
        action = menu.addAction("Remove")
        action.triggered.connect(self.remove_element)
        menu.move(event.globalPos())
        menu.show()

    def remove_element(self):
        """ Remove an element from the datapool"""

        item = self.currentIndex()

        model = item.model()
        if(not model):
            return

        datapool = model.datapool

        l = list(self.model().datapool.keys())
        l.sort()
        name = l[item.row()]

        del(datapool[name])

if __name__ == '__main__':

    import sys
    from qtpy import QtGui

    instance = QtWidgets.QApplication.instance()
    if instance is None:
        qapp = QtWidgets.QApplication(sys.argv)
    else:
        qapp = instance

    widget = NodeFactoryTreeView(main_win=None)
    widget.show()
    widget.raise_()

    if instance is None:
        qapp.exec_()
