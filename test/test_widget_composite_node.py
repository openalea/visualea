from openalea.core import logger, CompositeNodeFactory
from openalea.visualea.mainwindow import MainWindow
from openalea.core.pkgmanager import PackageManager
from qtpy import QtWidgets, QtCore
from openalea.core.alea import *

def open_window(factory):

    dialog = QtWidgets.QDialog()
    widget = factory.instantiate_widget(autonomous=True)

    dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    widget.setParent(dialog)

    vboxlayout = QtWidgets.QVBoxLayout(dialog)
    vboxlayout.setContentsMargins(3,3,3,3)
    vboxlayout.setSpacing(5)
    vboxlayout.addWidget(widget)

    dialog.setWindowTitle(factory.name)

    return dialog

def test_addition_composite_node():
    # Allow to test DisplayGraphWidget from openalea.visualea.compositenode_widget
    app = QtWidgets.QApplication(sys.argv)

    p = PackageManager()
    p.init(verbose=False)

    # factory = addition_composite_node
    factory, node = get_node(('dataflow_test', 'addition'), {}, pm=p)
    widget = factory.instantiate_widget(autonomous = True)
    win = open_window(factory)

    # get the button 'Run', there is only one for the node 7 which is user marked
    for ch in win.findChildren(QtWidgets.QPushButton):
        if ch.text() == 'Run':
            ch.click()
            break
    # get the new caption of node 7, originally set to '0'
    output = win.children()[0].node.node(7).caption
    win.close()

    res = run(('dataflow_test', 'addition'), {}, pm = p, vtx_id = 4)


    assert output == str(res[0])

def test_call_mainwindow():
    # test the basic call to openalea.visualea.mainwindow
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow(None)

# def test_remove_one_edge():
