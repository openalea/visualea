# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       File author(s): Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#                       Christophe Pradal <christophe.prada@cirad.fr>
#                       Frederic Boudon <frederic.boudon@cirad.fr>
#
#       Distributed under the CeCILL v2 License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################
"""Decorator and Utilities"""

from builtins import str
from builtins import object
__license__ = "CeCILL v2"
__revision__ = " $Id$ "

from qtpy import QtCore, QtGui, QtWidgets
from openalea.core.algo.dataflow_evaluation import EvaluationException
import sys
import traceback as tb


def busy_cursor(f):
    """ Decorator to display a busy pointer """

    def wrapped(*args):
        try:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
            arguments = args[0] # not sure
            ret = f(arguments)
            # ret = f(*args)
            QtWidgets.QApplication.restoreOverrideCursor ()
            return ret
        except:
            QtWidgets.QApplication.restoreOverrideCursor ()
            raise

    return wrapped


def processText(txt):
    txt = txt.replace('File','<B>File</B>')
    txt = txt.replace(', in',', <B>in</B>')
    txt = txt.replace(', line',', <B>line</B>')
    txt = txt.replace('\n','<BR>')
    txt = txt.replace('  ','&nbsp;&nbsp;')
    return txt

use_error_box = True

def exception_display(f):
    """ Decorator to display exception if raised """
    def display_error(parent,title,stack):
        global use_error_box
        if not use_error_box:
                QtWidgets.QMessageBox.critical(None,'Exception raised !',title)
        else:
            errorbox = QtWidgets.QErrorMessage(parent)
            errorbox.setModal(True)
            errorbox.resize(700,250)
            errorbox.setWindowTitle(title)
            txt = '<B>Traceback (most recent call last):</B><BR>'
            txt += processText(''.join(stack))
            txt += '<B>'+title+'</B><BR>'
            errorbox.showMessage(txt)
            errorbox.exec_()

    def wrapped(*args):
        try:
            return f(*args)
        except EvaluationException as e:
            self = args[0]
            if not isinstance(self, QtWidgets.QWidget):
                self = None
            txt = e.exception.__class__.__name__+': '+ str(e.exception)
            display_error(self,txt,e.exc_info)
            # raise e.exception

        except Exception as e:
            self = args[0]
            if not isinstance(self,QtWidgets.QWidget):
                self = None
            txt = e.__class__.__name__+': '+ str(e)
            display_error(self,txt,tb.format_tb(sys.exc_info()[2]))
            # raise e

    return wrapped


def open_dialog(parent, widget, title, delete_on_close=True):
    """
    Open a widget in a dialog box
    Return dialog instance
    """

    # Open dialog
    dialog = QtWidgets.QDialog(parent)
    if(delete_on_close):
        dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    widget.setParent(dialog)

    vboxlayout = QtWidgets.QVBoxLayout(dialog)
    vboxlayout.setContentsMargins(3, 3, 3, 3)
    vboxlayout.setSpacing(5)
    vboxlayout.addWidget(widget, 0)#, qt.QtCore.Qt.AlignTop)

    dialog.setWindowTitle(title)
    dialog.show()

    return dialog




class IconGrabber(object):
    """ Display a frame to grab an icon"""

    def __init__(self):
        self.splash = None

    def show(self):
        """ Set the application cursor """

        if(self.splash):
            self.hide()

        pix=QtGui.QPixmap(":/icons/cursor_icon.png")
        self.splash = QtWidgets.QSplashScreen(pix)
        self.splash.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.FramelessWindowHint)
        self.splash.setFixedSize(pix.size())
        self.splash.setMask(pix.mask())
        self.splash.setWindowTitle("Icon Selector")
        self.splash.show()


    def hide(self):

        self.splash.close()
        self.splash = None



def grab_icon(parent):
    """ Return QPixmap under the cursor"""

    HEIGHT = 48
    WIDTH = 48

    grab = IconGrabber()
    grab.show()

    QtWidgets.QMessageBox.information(parent,
                                  "Grab Icon", "Put the image under the icon frame and click ok")

    point = grab.splash.pos()
    pix = QtGui.QPixmap.grabWindow(QtWidgets.QApplication.desktop().winId(),
                                   point.x()+2, point.y()+2, WIDTH, HEIGHT)

    grab.hide()

    return pix
