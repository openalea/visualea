# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Daniel Barbeau <daniel.barbeau@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__license__ = "Cecill-C"
__revision__ = " $Id$ "

import weakref
from PyQt4 import QtGui, QtCore
from openalea.core.observer import Observed
from openalea.grapheditor import qtgraphview

def do_imports():
    import dataflow, layout, color, vertex, port, anno

class GraphOperator(Observed):

    __main__       = None
    vertexType     = None
    annotationType = None
    edgeType       = None

    def __init__(self, graphView=None, graph=None):
        Observed.__init__(self)
        do_imports()
        self.__ops = [ dataflow.DataflowOperators(self), layout.LayoutOperators(self),
                       color.ColorOperators(self), vertex.VertexOperators(self),
                       port.PortOperators(self), anno.AnnotationOperators(self) ]

        self.__availableNames = {}

        for operator in self.__ops:
            for meth in dir(operator):
                self.__availableNames[meth] = getattr(operator, meth)

        self.graphView      = None
        self.graph          = None
        self.__session      = None
        self.__interpreter  = None
        self.__pkgmanager   = None
        self.vertexItem     = None
        self.annotationItem = None
        self.portItem       = None

        if(graphView):
            self.graphView = graphView
        if(graph):
            self.graph     = graph

    ######################################
    # Get Qt Actions for methods in here #
    ######################################
    def get_action(self, actionName=None, parent=None, fName=None, *otherSlots):
        if actionName is None and parent is None and fName is not None:
            return self.__get_wrapped(fName)[0]
        graphView = self.get_graph_view()
        action = QtGui.QAction(actionName, parent)

        return self.bind_action(action, fName, *otherSlots)

    def bind_action(self, action, fName, *otherSlots):
        func, argcount = self.__get_wrapped(fName)
        action.triggered[""].connect(self.identify_focused_graph_view )
        action.triggered[bool].connect(self.identify_focused_graph_view )
        if (argcount) < 2 :
            action.triggered[""].connect(func)
            for f in otherSlots:
                action.triggered[""].connect(f)
        else:
            action.triggered[bool].connect(func)
            for f in otherSlots:
                action.triggered[bool].connect(f)
        return action

    def unbind_action(self, action, fName=None, *otherSlots):
        func, argcount = self.__get_wrapped(fName)
        action.triggered[""].disconnect(self.identify_focused_graph_view )
        action.triggered[bool].disconnect(self.identify_focused_graph_view )
        if (argcount) < 2 :
            action.triggered[""].disconnect(func)
            for f in otherSlots:
                action.triggered[""].disconnect(f)
        else:
            action.triggered[bool].disconnect(func)
            for f in otherSlots:
                action.triggered[bool].disconnect(f)
        return action

    def __add__(self, other):
        self.bind_action(*other)

    def __sub__(self, other):
        self.unbind_action(*other)

    __call__ = get_action

    def __get_wrapped(self, fName):
        func = self.__availableNames.get(fName)
        def wrapped(*args, **kwargs):
            graphView = self.get_graph_view()
            if self.get_graph() is None : return
            return func(*args, **kwargs)
        return wrapped, func.func_code.co_argcount

    ###########
    # setters #
    ###########
    @classmethod
    def set_main(self, main):
        GraphOperator.__main__ = main

    def set_vertex_item(self, vertexItem):
        self.vertexItem = weakref.ref(vertexItem)

    def set_annotation_item(self, annotationItem):
        self.annotationItem = weakref.ref(annotationItem)

    def set_port_item(self, portitem):
        self.portItem = weakref.ref(portitem)

    ###########
    # getters #
    ###########
    @classmethod
    def get_main(self):
        return GraphOperator.__main__

    def get_session(self):
        return self.__main__.session

    def get_interpreter(self):
        return self.__main__.interpreterWidget

    def get_package_manager(self):
        return self.__main__.pkgmanager

    def identify_focused_graph_view(self, *args):
        """Looks in various places to find which graph view
        asked for an operation. Here is the strategy:
        1) Ask the application for the widget in focus.
            If it is a graph view that it becomes the GraphOperator's view.
        2) If this fails, search in the session's list of
            graph views for one that hasFocus() == True.
        3) If this fails, return the current widget from MainWindow's tabwidget.
        The identified view can then be retreived by : operator.get_graph_view()
        This method is bound to every action created or decorated by the operator.

        @note : this method might be better in Session?
        """
        self.graphView = None
        gv = QtGui.QApplication.focusWidget()
        if type(gv)==qtgraphview.View:
            self.graphView = gv
        else:
            widgets = self.get_session().get_graph_views()
            for i in widgets:
                if i.hasFocus() : self.graphView = i
            if not self.graphView:
                self.graphView = self.__main__.tabWorkspace.currentWidget()
        return self.graphView

    def get_graph_view(self):
        return self.graphView

    def get_graph_scene(self):
        return self.graphView.scene()

    def get_graph(self):
        graphView = self.get_graph_view()
        if graphView:
            return graphView.scene().get_graph()
        else:
            return self.graph
