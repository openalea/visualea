# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright or (C) or Copr. 2006 INRIA - CIRAD - INRA  
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


__doc__="""
Composite Node Widgets
"""

__license__= "CeCILL v2"
__revision__=" $Id$ "



import sys
import math

from PyQt4 import QtCore, QtGui
from openalea.core.node import NodeWidget, RecursionError
from openalea.core.pkgmanager import PackageManager
from openalea.core.observer import lock_notify


class DisplayGraphWidget(NodeWidget, QtGui.QWidget):
    """ Display widgets contained in the graph """
    
    def __init__(self, node, parent=None):

        NodeWidget.__init__(self, node)
        QtGui.QWidget.__init__(self, parent)

        vboxlayout = QtGui.QVBoxLayout(self)
        
        for id in node.get_ids():

            subnode = node.get_node_by_id(id)
            factory = subnode.get_factory()

            if(not factory): continue
            
            widget = factory.instantiate_widget(subnode, self)

            caption = "%s"%(subnode.internal_data['caption'])
            groupbox = QtGui.QGroupBox(caption, self)
            layout = QtGui.QVBoxLayout(groupbox)
            layout.setMargin(3)
            layout.setSpacing(2)

            layout.addWidget(widget)
            
            vboxlayout.addWidget(groupbox)

        

class EditGraphWidget(NodeWidget, QtGui.QGraphicsView):
    """ Graph widget allowing to edit the network """
    
    def __init__(self, node=None, parent=None):

        if(node == None): node = factory.instantiate()
        
        NodeWidget.__init__(self, node)
        QtGui.QGraphicsView.__init__(self, parent)

        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.setScene(scene)
        #self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
            
        self.scale(0.8, 0.8)

        self.newedge = None

        # dictionnary mapping elt_id and graphical items
        self.graph_item = {}
        
        # dictionnary mapping elt_id with tupel (dialog, widget)
        self.node_dialog = {}

        self.rebuild_scene()


    def clear_scene(self):
        """ Remove all items from the scene """
        
        # Close items
        for eltid in self.graph_item.keys():
            self.remove_graphical_node(eltid)

        self.graph_item = {}
        self.node_dialog = {}
        
        scene = self.scene()
        del(scene)
        scene = QtGui.QGraphicsScene(self)
        scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.setScene(scene)


    @lock_notify      
    def rebuild_scene(self):
        """ Build the scene with graphic node and edge"""

        self.clear_scene()
        # create items
        ids= self.node.get_ids()
        #for eltid in self.node.node_id.keys():
        for eltid in ids:
            self.add_graphical_node(eltid)

        # create connections
        dataflow= self.node
        for eid in dataflow.edges():
            src_id, dst_id= dataflow.source( eid ), dataflow.target( eid )
            src_port, dst_port= dataflow._edge_ports[ eid ]
            
            src_item = self.graph_item[src_id]
            dst_item = self.graph_item[dst_id]

            src_connector = src_item.get_output_connector(src_port)
            dst_connector = dst_item.get_input_connector(dst_port)

            self.add_graphical_connection(src_connector, dst_connector)


    # Mouse events

    def mouseMoveEvent(self, event):
        
        # update new edge position
        if(self.newedge) :
            self.newedge.setMousePoint(self.mapToScene(event.pos()))
            event.ignore()
        else:
            QtGui.QGraphicsView.mouseMoveEvent(self, event)


    def mousePressEvent(self, event):

        if (event.buttons() & QtCore.Qt.LeftButton):
            QtGui.QGraphicsView.mousePressEvent(self, event)
            


    @lock_notify
    def mouseReleaseEvent(self, event):
        
        if(self.newedge):
            item = self.itemAt(event.pos())
            if(item and isinstance(item, ConnectorIn)
               and isinstance(self.newedge.connector(), ConnectorOut)
               and not item.is_connected() ):

                self.connect_node( self.newedge.connector(), item)
                self.add_graphical_connection( self.newedge.connector(), item)


            elif(item and isinstance(item, ConnectorOut) and
                 isinstance(self.newedge.connector(), ConnectorIn) ):

                self.connect_node( item, self.newedge.connector())
                self.add_graphical_connection( item, self.newedge.connector())
        
            self.scene().removeItem(self.newedge)
            self.newedge = None

        QtGui.QGraphicsView.mouseReleaseEvent(self, event)


#     def itemMoved(self, item, newvalue):
#         """ function called when a node item has moved """


    def wheelEvent(self, event):
        #self.centerOn(self.mapToScene(event.globalPos()))
        self.scaleView(-event.delta() / 1200.0)
        QtGui.QGraphicsView.wheelEvent(self, event)
        
    def scaleView(self, scaleFactor):

        scaleFactor += 1
        self.scale(scaleFactor, scaleFactor)

    
    def notify(self, sender, event):
        """ Function called by observed objects """

        if(not event): return

        if( event[0] == "connection_modified"):
            self.rebuild_scene()
        elif( event[0] == "graph_modified"):
            self.rebuild_scene()


    def start_edge(self, connector):
        """ Start to create an edge """

        self.newedge= SemiEdge(self, connector, None, self.scene())

  
    # graph edition

    def add_graphical_node(self, eltid):
        """
        Add the node graphical representation in the widget
        @param eltid : element id 
        """

        subnode = self.node.get_node_by_id(eltid)
        
        nin = subnode.get_nb_input()
        nout = subnode.get_nb_output()

        gnode = GraphicalNode(self, eltid, nin, nout)

        self.graph_item[eltid] = gnode
        
        return gnode


    def add_graphical_connection(self, connector_src, connector_dst):
        """ Return the new edge """
        
        edge = Edge(self, connector_src.parentItem(), connector_src.index(),
                    connector_dst.parentItem(), connector_dst.index(),
                    None, self.scene())

        return edge
        
    
    def connect_node(self, connector_src, connector_dst):
        """
        Convenience function
        Connect the node in the graph
        """
        
        if(connector_dst.is_connected()):
            return None

        self.node.connect(connector_src.parentItem().get_id(), connector_src.index(),
                                connector_dst.parentItem().get_id(), connector_dst.index())


    def open_item(self, elt_id):
        """ Open the widget of the item elt_id """

        # Test if the node is already opened
        if(self.node_dialog.has_key(elt_id)):
            (d,w) = self.node_dialog[elt_id]

            if w.is_empty():
                d.hide()
            else:
                d.show()

            d.raise_()
            d.activateWindow ()
            return

        # We Create a new Dialog
        node = self.node.get_node_by_id(elt_id)
        factory = node.get_factory()
        if(not factory) : 
            return
        
        container = QtGui.QDialog(self)
        #container.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            
        widget = factory.instantiate_widget(node, container)
        
        vboxlayout = QtGui.QVBoxLayout(container)
        vboxlayout.setMargin(3)
        vboxlayout.setSpacing(5)

        vboxlayout.addWidget(widget)

        container.setWindowTitle(factory.get_id())

        self.node_dialog[elt_id] = (container, widget)
        if widget.is_empty():
            container.hide()
        else:
            container.show()


    def get_selected_item(self):
        """ Return the list id of the selected item """

        # get the selected id
        s = []
        for id in self.graph_item.keys():
            item = self.graph_item[id]
            if(item.isSelected()):
                s.append(id)

        return s


    def remove_selection(self):
        """ Remove selected nodes """

        s = self.get_selected_item()
        
        # remove the nodes
        map(self.remove_node, s)

        # Remove other item
        items = self.scene().selectedItems()
        for i in items :
            self.scene().removeItem(i)


    def export_selection(self):
        """
        Export selected node in a new composite node
        Return the created factory or None if canceled
        """

        s = self.get_selected_item()

        # Get a composite node factory
        from dialogs import FactorySelector

        dialog = FactorySelector(self.node.factory, self)
        ret = dialog.exec_()
        if(ret == 0): return None
        
        factory = dialog.get_factory()
        self.node.to_factory(factory, s)
        self.remove_selection()

        return factory


    def remove_graphical_node(self, elt_id):
        """ Remove the graphical node item identified by elt_id """

        # close dialog
        try:
            (dialog, widget) = self.node_dialog[elt_id]
            dialog.close()
            dialog.destroy()
            
            del(self.node_dialog[elt_id])
        except KeyError:
            pass
        
        item = self.graph_item[elt_id]
        item.remove_connections()
        self.scene().removeItem(item)
        del(self.graph_item[elt_id])
                

    @lock_notify      
    def remove_node(self, elt_id):
        """ Remove node identified by elt_id """

        self.remove_graphical_node(elt_id)
        self.node.remove_node(elt_id)


    def remove_graphical_connection(self, src_connector, dst_connector):
        """ Remove a graphical edge """

        item = dst_connector.edge
        dst_connector.set_edge(None)
        src_connector.edge_list.remove(item)
        self.scene().removeItem(item)


    @lock_notify
    def remove_connection(self, connector_src, connector_dst):
        """ Remove a connection """

        self.remove_graphical_connection(connector_src, connector_dst)
        self.node.disconnect(connector_src.parentItem().get_id(), connector_src.index(),
                               connector_dst.parentItem().get_id(), connector_dst.index()) 
    

    # Drag and Drop from TreeView support
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("openalea/nodefactory"):
            event.accept()
        else:
            QtGui.QGraphicsView.dragEnterEvent(self, event)


    def dragMoveEvent(self, event):
        if ( event.mimeData().hasFormat("openalea/nodefactory") ):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            QtGui.QGraphicsView.dragMoveEvent(self, event)


    @lock_notify
    def add_new_node(self, package_id, factory_id, position):
        """ convenience function """

        # Add new node
        pkgmanager = PackageManager()
        pkg = pkgmanager[str(package_id)]
        factory = pkg.get_factory(str(factory_id))
        
        position = self.mapToScene(position)
            
        try:
            newnode = factory.instantiate([self.node.factory.get_id()])
            newnode.set_data('posx', position.x())
            newnode.set_data('posy', position.y())
        
            newid = self.node.add_node(newnode)
            self.add_graphical_node(newid)

        except RecursionError:
            mess = QtGui.QMessageBox.warning(self, "Error",
                                                 "A graph cannot be contained in itself.")


    def add_graphical_annotation(self):
        """ Add text annotation """

        version = QtCore.PYQT_VERSION
        if(version <= 262401):
            mess = QtGui.QMessageBox.warning(None, "Error",
                                             "This function need PyQT >= 4.2")
            return 

        item = Annotation(self.scene(), self.mapToScene(
            self.mapFromGlobal(self.cursor().pos())))

                

    def dropEvent(self, event):

        if (event.mimeData().hasFormat("openalea/nodefactory")):
            pieceData = event.mimeData().data("openalea/nodefactory")
            dataStream = QtCore.QDataStream(pieceData, QtCore.QIODevice.ReadOnly)
            
            package_id = QtCore.QString()
            factory_id = QtCore.QString()
            
            dataStream >> package_id >> factory_id

            self.add_new_node(package_id, factory_id, event.pos())

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()

        else:
            QtGui.QGraphicsView.dropEvent(self, event)

    # Keybord Event
    def keyPressEvent(self, e):

        QtGui.QGraphicsView.keyPressEvent(self, e)
        
        key   = e.key()
        if( key == QtCore.Qt.Key_Delete):
            self.remove_selection()

        elif(key == QtCore.Qt.Key_Space):
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)


    def keyReleaseEvent(self, e):
        """ Key """
        QtGui.QGraphicsView.keyReleaseEvent(self, e)
        key   = e.key()
        if(key == QtCore.Qt.Key_Space):
            self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)


    def event(self, event):
        """ Main event handler """
        
        if (event.type() == QtCore.QEvent.ToolTip):
            item = self.itemAt(event.pos())
            if(item and isinstance(item, Connector)):
                txt = item.update_tooltip()

        return QtGui.QGraphicsView.event(self, event)
 

    def contextMenuEvent(self, event):
        """ Context menu event : Display the menu"""

        if(self.itemAt(event.pos())):
           QtGui.QGraphicsView.contextMenuEvent(self, event)
           return

        menu = QtGui.QMenu(self)
        action = menu.addAction("Add Annotation")
        self.scene().connect(action, QtCore.SIGNAL("activated()"), self.add_graphical_annotation)
        
        menu.move(event.globalPos())
        menu.show()
        event.accept()



        

class Annotation(QtGui.QGraphicsTextItem):
    """ Text annotation on the data flow """
    
    def __init__(self, scene, pos):

        QtGui.QGraphicsTextItem.__init__(self)

        self.setPlainText("Comments...")

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setPos(pos)

        font = self.font()
        font.setBold(True)
        font.setPointSize(12)

        self.setFont(font)
        scene.addItem(self)
        
        
        
    def mouseDoubleClickEvent(self, event):

        self.setTextInteractionFlags(QtCore.Qt.TextEditable)
        self.setSelected(True)
        self.setFocus()
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.Document)
        self.setTextCursor(cursor)
        

    def focusOutEvent(self, event):
        
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        QtGui.QGraphicsTextItem.focusOutEvent(self, event)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, False)
        


from openalea.core.observer import AbstractListener


def port_name( name, interface ):
    """ Return the port name str """
    iname = 'Any'
    if(interface):
        try:
            iname = interface.__name__
        except AttributeError:
            try:
                iname = interface.__class__.__name__
            except AttributeError:
                iname = str(interface)
    return '%s(%s)'%(name,iname)

    

class GraphicalNode(QtGui.QGraphicsItem, AbstractListener):
    """ Represent a node in the graphwidget """

    def __init__(self, graphview, elt_id, ninput, noutput):
        """
        @param graphview : EditGraphWidget container
        @param elt_id : id in the graph
        @param ninput : number of input
        @param noutput : number of output
        @param caption : box text
        """

        scene = graphview.scene()

        QtGui.QGraphicsItem.__init__(self)

        # members
        self.elt_id = elt_id
        self.graphview = graphview
        self.subnode = self.graphview.node.get_node_by_id(elt_id)
        self.connector_in = []
        self.connector_out = []
        self.sizey = 32
        self.sizex = 20


        # Record item as a listener for the subnode
        self.ismodified = True
        self.initialise(self.subnode)

        self.setFlag(QtGui.QGraphicsItem.GraphicsItemFlag(
            QtGui.QGraphicsItem.ItemIsMovable +
            QtGui.QGraphicsItem.ItemIsSelectable))
        self.setZValue(1)

        
        # Set ToolTip
        doc= self.subnode.__doc__
        if doc:
            doc = doc.split('\n')
            doc = [x.strip() for x in doc] 
            doc = '\n'.join(doc)
            self.setToolTip( "Class : %s\n"%(self.subnode.__class__.__name__) +
                             "Instance : %s\n"%(elt_id,) +
                             "Documentation : \n%s"%(doc,))
        else:
            self.setToolTip( "Class : %s\n"%(self.subnode.__class__.__name__) +
                             "Instance : %s\n"%(elt_id,) )

        # Font and box size
        self.font = self.graphview.font()
        self.font.setBold(True)
        self.font.setPointSize(10)


        # Add to scene
        scene.addItem(self)

        # Connectors
        for i,desc in enumerate(self.subnode.input_desc):
            name = desc['name']
            interface = desc.get('interface', None)
            
            tip= port_name(name,interface)
            self.connector_in.append(ConnectorIn(self.graphview, self, scene, i, ninput, tip))
            
        for i,desc in enumerate(self.subnode.output_desc):
            name = desc['name']
            interface = desc.get('interface', None)

            tip= port_name(name,interface)
            self.connector_out.append(ConnectorOut(self.graphview, self, scene, i, noutput, tip))

        # Set Position
        try:
            x = self.subnode.internal_data['posx']
            y = self.subnode.internal_data['posy']
        except:
            (x,y) = (10,10)
        self.setPos(QtCore.QPointF(x,y))

        self.adjust_size()


    def adjust_size(self):
        """ Compute the box size """

        fm = QtGui.QFontMetrics(self.font);
        newsizex = fm.width(self.get_caption()) + 20;
        # when the text is small but there are lots of ports, 
        # add more space.
        nb_ports= max(len(self.connector_in),len(self.connector_out))
        newsizex= max( nb_ports * Connector.WIDTH * 2, newsizex)
        
        if(newsizex > self.sizex):

            self.sizex = newsizex
            for i in range(len(self.connector_in)):
                c = self.connector_in[i]
                c.adjust_position(self, i, len(self.connector_in))
            for i in range(len(self.connector_out)):
                c = self.connector_out[i]
                c.adjust_position(self, i, len(self.connector_out))


    def get_caption(self):
        """ Return the node caption (convenience)"""
        
        return self.subnode.internal_data['caption']


    def notify(self, sender, event):
        """ Notification sended by the node associated to the item """

        if(event and event[0] == "caption_modified"):
            self.adjust_size()
            self.update()
            QtGui.QApplication.processEvents()
           
        elif(self.ismodified != sender.modified):
            self.ismodified = sender.modified or not sender.lazy
            
            self.update()
            QtGui.QApplication.processEvents()


    def get_id(self):
        return self.elt_id
    

    def get_input_connector(self, index):
        try:
            return self.connector_in[index]
        except:
            return None


    def get_output_connector(self, index):
        try:
            return self.connector_out[index]
        except:
            return None


    def remove_connections(self):
        """ Remove edge connected to this item """ 

        for cin in self.connector_in:
            if(cin.edge) :
                cin.edge.remove_edge()
                cin.edge = None
                
        for cout in self.connector_out:
            for e in cout.edge_list[:]:
                e.remove_edge()
            cout.edge_list = []
                

    def boundingRect(self):
        adjust = 4.0
        return QtCore.QRectF(0 , 0,
                             self.sizex + adjust, self.sizey + adjust)


    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(0, 0, self.sizex, self.sizey)
        return path


    def paint(self, painter, option, widget):
        
        # Shadow
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(100, 100, 100, 50))
        painter.drawRoundRect(3, 3, self.sizex, self.sizey)

        # Draw Box
        if(self.isSelected()):
            color = QtGui.QColor(180, 180, 180, 180)
        else:
            color = QtGui.QColor(255, 255, 255, 100)

        if(self.ismodified):
            secondcolor = QtGui.QColor(255, 0, 0, 200)
        else:
            secondcolor = QtGui.QColor(0, 0, 255, 200)
            
        
        gradient = QtGui.QLinearGradient(0, 0, 0, 100)
        gradient.setColorAt(0.0, color)
        gradient.setColorAt(1.0, secondcolor)
        painter.setBrush(QtGui.QBrush(gradient))
        
        painter.setPen(QtGui.QPen(QtCore.Qt.black, 1))
        painter.drawRoundRect(0, 0, self.sizex, self.sizey)
        
        # Draw Text
        textRect = QtCore.QRectF(0, 0, self.sizex, self.sizey)
        painter.setFont(self.font)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(textRect, QtCore.Qt.AlignCenter,
                         self.get_caption())


    def itemChange(self, change, value):
        """ Callback when item has been modified (move...) """

        if (change == QtGui.QGraphicsItem.ItemPositionChange):
            
            [ c.adjust() for c in self.connector_in ]
            [ c.adjust() for c in self.connector_out ]

            point = value.toPointF()
        
            self.subnode.set_data('posx', point.x())
            self.subnode.set_data('posy', point.y())
         
            #self.graphview.itemMoved(self, value)

        return QtGui.QGraphicsItem.itemChange(self, change, value)


    def mousePressEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.update()
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        self.graphview.open_item(self.elt_id)
        self.run_node()

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)


    def contextMenuEvent(self, event):
        """ Context menu event : Display the menu"""

        menu = QtGui.QMenu(self.graphview)

        action = menu.addAction("Run")
        self.scene().connect(action, QtCore.SIGNAL("activated()"), self.run_node)
        
        action = menu.addAction("Open Widget")
        self.scene().connect(action, QtCore.SIGNAL("activated()"), self.open_widget)

        action = menu.addAction("Delete")
        self.scene().connect(action, QtCore.SIGNAL("activated()"), self.delete_node)
        
#         action = menu.addAction("Enable in Widget")
#         self.scene().connect(action, QtCore.SIGNAL("activated()"), self.enable_in_widget)
        
        action = menu.addAction("Edit Caption")
        self.scene().connect(action, QtCore.SIGNAL("activated()"), self.set_caption)

        menu.move(event.screenPos())
        menu.show()

        event.accept()
        

    def run_node(self):
        """ Run the current node """
        self.graphview.node.eval_as_expression(self.elt_id)


    def open_widget(self):
        """ Open widget in dialog """
        self.graphview.open_item(self.elt_id)


    def delete_node(self):
        """ Remove current node """
        self.graphview.remove_node(self.elt_id)
        

    def enable_in_widget(self):
        pass


    def set_caption(self):
        """ Open a input dialog to set node caption """

        n = self.subnode
        (result, ok) = QtGui.QInputDialog.getText(self.graphview, "Node caption", "",
                                   QtGui.QLineEdit.Normal, n.internal_data['caption'])
        if(ok):
            n.set_caption(str(result))


################################################################################

class Connector(QtGui.QGraphicsEllipseItem):
    """ A node connector """
    WIDTH = 12
    HEIGHT = 8

    def __init__(self, graphview, parent, scene, index, tooltip=""):
        """
        @param graphview : EditGraphWidget container
        @param parent : QGraphicsItem parent
        @param scene : QGraphicsScene container
        @param index : connector index
        """
        
        QtGui.QGraphicsItem.__init__(self, parent, scene)

        self.mindex = index
        self.graphview = graphview

        self.base_tooltip = tooltip
        self.update_tooltip()
        self.setRect(0, 0, self.WIDTH, self.HEIGHT)

        gradient = QtGui.QRadialGradient(-3, -3, 10)
        gradient.setCenter(3, 3)
        gradient.setFocalPoint(3, 3)
        gradient.setColorAt(1, QtGui.QColor(QtCore.Qt.yellow).light(120))
        gradient.setColorAt(0, QtGui.QColor(QtCore.Qt.darkYellow).light(120))
        
        self.setBrush(QtGui.QBrush(gradient))
        self.setPen(QtGui.QPen(QtCore.Qt.black, 0))


    def index(self):
        return self.mindex

    def update_tooltip(self):
        self.setToolTip(self.base_tooltip)

    def mouseMoveEvent(self, event):
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)



class ConnectorIn(Connector):
    """ Input node connector """

    def __init__(self, graphview, parent, scene, index, ntotal, tooltip):

        Connector.__init__(self, graphview, parent, scene, index, tooltip)

        self.edge = None

        self.adjust_position(parent, index, ntotal)
        self.setAcceptDrops(True)

    def set_edge(self, edge):
        self.edge = edge

    def is_connected(self):
        return bool(self.edge)

    def adjust(self):
        if(self.edge): self.edge.adjust()


    def update_tooltip(self):
        node = self.parentItem().subnode
        data = node.get_input(self.mindex)
        self.setToolTip("%s %s"%(self.base_tooltip, str(data)))

    
    def adjust_position(self, parentitem, index, ntotal):
        width= parentitem.sizex / float(ntotal+1)
        self.setPos((index+1) * width - self.WIDTH/2., - self.HEIGHT/2)


    def mousePressEvent(self, event):
        QtGui.QGraphicsItem.mousePressEvent(self, event)

        if(not self.edge and (event.buttons() & QtCore.Qt.LeftButton)):
            self.graphview.start_edge(self)
            

    # Drag and Drop from TreeView support
    def dragEnterEvent(self, event):
        event.setAccepted(event.mimeData().hasFormat("openalea/data_instance"))


    def dragMoveEvent(self, event):
        if ( event.mimeData().hasFormat("openalea/data_instance") ):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

            
    def dropEvent(self, event):

        if (event.mimeData().hasFormat("openalea/data_instance")):
            pieceData = event.mimeData().data("openalea/data_instance")
            dataStream = QtCore.QDataStream(pieceData, QtCore.QIODevice.ReadOnly)
            
            data_key = QtCore.QString()
            
            dataStream >> data_key
            data_key = str(data_key)

            from openalea.core.session import DataPool
            datapool = DataPool()  # Singleton

            node = self.parentItem().subnode
            data = node.set_input(self.mindex, datapool[data_key])

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()

        else:
            event.ignore()

            


class ConnectorOut(Connector):
    """ Output node connector """

    def __init__(self, graphview, parent, scene, index, ntotal, tooltip):
        Connector.__init__(self, graphview, parent, scene, index, tooltip)
        
        self.adjust_position(parent, index, ntotal)
        self.edge_list = []
        
    def update_tooltip(self):
        node = self.parentItem().subnode
        data = node.get_output(self.mindex)
        self.setToolTip("%s %s"%(self.base_tooltip, str(data)))


    def add_edge(self, edge):
        self.edge_list.append(edge)
        

    def adjust(self):
        for e in self.edge_list:
            e.adjust()

    def adjust_position(self, parentitem, index, ntotal):
            
        width= parentitem.sizex / float(ntotal+1)
        self.setPos((index+1) * width - self.WIDTH/2., parentitem.sizey - self.HEIGHT/2)


    def mousePressEvent(self, event):

        if (event.buttons() & QtCore.Qt.LeftButton):
            self.graphview.start_edge(self)
        
        QtGui.QGraphicsItem.mousePressEvent(self, event)


    def contextMenuEvent(self, event):
        """ Context menu event : Display the menu"""

        menu = QtGui.QMenu(self.graphview)

        action = menu.addAction("Send to Pool")
        self.scene().connect(action, QtCore.SIGNAL("activated()"), self.send_to_pool)
        
        menu.move(event.screenPos())
        menu.show()

        event.accept()
        

    def send_to_pool(self):

        (result, ok) = QtGui.QInputDialog.getText(self.graphview, "Data Pool", "Instance name",
                                                      QtGui.QLineEdit.Normal, )
        if(ok):
            from openalea.core.session import DataPool
            datapool = DataPool()  # Singleton

            self.parentItem().run_node()
            node = self.parentItem().subnode
            data = node.get_output(self.mindex)
            datapool[str(result)] = data




################################################################################

class AbstractEdge(QtGui.QGraphicsLineItem):
    """
    Base classe for edges
    """

    def __init__(self, graphview, parent=None, scene=None):
        QtGui.QGraphicsLineItem.__init__(self, parent, scene)

        self.graph = graphview
        self.sourcePoint = QtCore.QPointF()
        self.destPoint = QtCore.QPointF()

        line = QtCore.QLineF(self.sourcePoint, self.destPoint)
        self.setLine(line)

        self.setPen(QtGui.QPen(QtCore.Qt.black, 3,
                                  QtCore.Qt.SolidLine,
                                  QtCore.Qt.RoundCap,
                                  QtCore.Qt.RoundJoin))

    def shape(self):

        path = QtGui.QPainterPath()
        

        dp = QtCore.QPointF(20,0)
        p1 = QtCore.QPointF(self.sourcePoint) - dp
        p2 = QtCore.QPointF(self.sourcePoint) + dp
        p3 = QtCore.QPointF(self.destPoint) + dp
        p4 = QtCore.QPointF(self.destPoint) - dp
        poly = QtGui.QPolygonF([p1,p2,p3,p4])
        
        path.addPolygon(poly)
        return path
        

    def update_line(self):
        line = QtCore.QLineF(self.sourcePoint, self.destPoint)
        self.setLine(line)

    
class SemiEdge(AbstractEdge):
    """
    Represents an edge during its creation
    It is connected to one connector only
    """

    def __init__(self, graphview, connector, parent=None, scene=None):
        AbstractEdge.__init__(self, graphview, parent, scene)

        self.connect = connector
        self.sourcePoint = self.mapFromItem(connector, connector.rect().center())


    def connector(self):
        return self.connect


    def setMousePoint(self, scene_point):
        self.destPoint = scene_point
        self.update_line()
        self.update()
    


class Edge(AbstractEdge):
    """ An edge between two graphical nodes """
        
    def __init__(self, graphview, sourceNode, out_index, destNode, in_index,
                 parent=None, scene=None):
        """
        @param sourceNode : source GraphicalNode
        @param out_index : output connector index
        @param destNode : destination GraphicalNode
        @param in_index : input connector index
        """
        AbstractEdge.__init__(self, graphview, parent, scene)

        self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

        src = sourceNode.get_output_connector(out_index)
        if( src ) : src.add_edge(self)

        dst = destNode.get_input_connector(in_index)
        if( dst ) : dst.set_edge(self)

        self.source = src
        self.dest = dst
        self.adjust()


    def adjust(self):
        if not self.source or not self.dest:
            return

        line = QtCore.QLineF(self.mapFromItem(self.source, self.source.rect().center() ),
                              self.mapFromItem(self.dest, self.dest.rect().center() ))
       
        length = line.length()
        if length == 0.0:
            return
        self.prepareGeometryChange()
        self.sourcePoint = line.p1() 
        self.destPoint = line.p2()
        self.update_line()


    def contextMenuEvent(self, event):
        """ Context menu event : Display the menu"""

        menu = QtGui.QMenu(self.graph)

        action = menu.addAction("Delete connection")
        self.scene().connect(action, QtCore.SIGNAL("activated()"), self.remove_edge)
        
        menu.move(event.screenPos())
        menu.show()

        event.accept()


    def remove_edge(self):
        self.graph.remove_connection(self.source, self.dest)
    