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
"""Python code editor"""
from __future__ import print_function

from builtins import str
from builtins import object
__license__ = "CeCILL V2"
__revision__ = " $Id$"

from qtpy import QtWidgets, QtGui, QtCore
import os
from subprocess import Popen
from openalea.core.settings import Settings
from openalea.visualea.util import open_dialog
from openalea.core.path import path


def get_editor():
    """ Return the editor class """
    
    editor = PythonCodeEditor

    s = Settings()
    try:
        str = s.get('editor', 'use_external')
        l = eval(str)
        if(l): editor = ExternalCodeEditor
        
    except:
        pass

    return editor


class AbstractCodeEditor(object):
    """ External code editor """

    def __init__(self, *args):
        pass


    def is_widget(self):
        raise NotImplementedError()


    def is_empty(self):
        return False


    def edit_file(self, filename):
        """ Open file in the editor """
        
    def edit_module(self, module, class_name=None):
        """ Edit the source file of a python module """

        import inspect
        filename =  inspect.getsourcefile(module)
        self.edit_file(filename)



class ExternalCodeEditor(AbstractCodeEditor):
    """ External code editor """

    def __init__(self, *args):
        AbstractCodeEditor.__init__(self)


    def is_widget(self):
        return False


    def get_command(self):
        """ Return command to execute """
        s = Settings()
        cmd = ""
        try:
            cmd = s.get('editor', 'command')
            
        except:
            cmd = ""
            
        if(not cmd):
            if('posix' in os.name):
                return "/usr/bin/vim"
            else:
                return "C:\\windows\\notepad.exe"

        return cmd


    def edit_file(self, filename):
        """ Open file in the editor """
        
        if(not filename):
            ret = QtWidgets.QMessageBox.warning(None, "Error", "Cannot find the file to edit.")
            return

        c = self.get_command()
        try:
            Popen([c, filename])
        except:
            print("Cannot execute %s"%(c,))




class PythonCodeEditor(QtWidgets.QWidget, AbstractCodeEditor):
    """ Simple Python code editor """

    def __init__(self, parent=None):
        
        QtWidgets.QWidget.__init__(self, parent)
        AbstractCodeEditor.__init__(self)

        self.textedit = self.get_editor()

        vboxlayout = QtWidgets.QVBoxLayout(self)
        vboxlayout.setContentsMargins(1, 1, 1, 1)
        vboxlayout.setSpacing(1)
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.hboxlayout.setContentsMargins(1, 1, 1, 1)
        self.hboxlayout.setSpacing(1)
        self.applybut = QtWidgets.QPushButton("Apply changes", self)
        self.hboxlayout.addWidget(self.applybut)

        self.savbut = QtWidgets.QPushButton("Save changes", self)
        self.hboxlayout.addWidget(self.savbut)
        vboxlayout.addLayout(self.hboxlayout)
        vboxlayout.addWidget(self.textedit)


        self.label = QtWidgets.QLabel("")
        vboxlayout.addWidget(self.label)

        self.savescut = QtWidgets.QShortcut( QtGui.QKeySequence(QtGui.QKeySequence.Save), self)
        self.savescut.activated.connect(self.save_changes)
        self.savbut.clicked.connect(self.save_changes)
        self.applybut.clicked.connect(self.apply_changes)
        
    
    def is_widget(self):
        return True


    def on_file_changed(self, path):
        ret = QtWidgets.QMessageBox.question(self, "File has changed on the disk.",
                                         "Reload ?\n",
                                         QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No,)

        if(ret == QtWidgets.QMessageBox.No): return
        self.edit_file(self.filename)
        

    def get_editor(self):
        """
        Return an editor object based on QScintilla if available.
        Else, return a standard editor.
        """

        try:
            from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciAPIs
            
            textedit = QsciScintilla(self)
            textedit.setAutoIndent(True)
            textedit.setAutoCompletionThreshold(2)
            textedit.setAutoCompletionSource(QsciScintilla.AcsDocument)

            # API
            lex = QsciLexerPython(textedit)
            textedit.setLexer(lex)

#             apis = QsciAPIs(lex)
#             apis.prepare()
            
            textedit.setMinimumWidth(250)
            textedit.setMinimumHeight(250)
            
        except ImportError:
            textedit = QtWidgets.QTextEdit(self)
            textedit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
            textedit.setMinimumWidth(200)
            textedit.setMinimumHeight(200)

        return textedit


    def goToLine(self, linenb):
        """ Go to line nb """
        try:
            self.ensureLineVisible(linenb)
        except:
            pass

    def setText(self, str):
        """ Set the text of the editor """

        try:
            self.textedit.setText(str)
        except:
            self.textedit.setPlainText(str)


    def getText(self):
        """ Return editor text """
        try:
            return self.textedit.text()
        except:
            return self.textedit.toPlainText()
        

    def edit_file(self, filename):
        """ Open file in the editor """
        
        if(filename):
            filename = os.path.abspath(filename)

        self.filename = filename

        try:
            f = open(filename, 'r')
            self.textedit.setText(f.read())
            self.label.setText("File : " + filename)
            self.file_stat = os.stat(filename)
            f.close()
            self.savbut.setEnabled(True)
            self.applybut.setEnabled(False)

            self.filewatcher = QtCore.QFileSystemWatcher(self)
            self.filewatcher.addPath(self.filename)
            self.filewatcher.fileChanged.connect(self.on_file_changed)
        

        except Exception as e:
            print(e)
            self.src = None
            self.applybut.setEnabled(False)
            self.savbut.setEnabled(False)
            self.textedit.setText(" Sources are not available...")


    def edit_module(self, module, class_name=None):
        """ Edit the source file of a python module """

        self.module = module
        if(not module):  
            self.applybut.setEnabled(False)
            return
            
        import inspect
        filename =  inspect.getsourcefile(module)
        self.edit_file(filename)

        self.savbut.setEnabled(True)
        self.applybut.setEnabled(True)


    def apply_changes(self):
        """ Reload file """

        if(self.module):
            newsrc = str(self.getText())
            exec(newsrc, self.module.__dict__)


    def save_changes(self):
        """ Save module """
        if(not os.access(self.filename, os.W_OK)):
            ret = QtWidgets.QMessageBox.warning(self, "Cannot write file %s", self.filename)
            return
            
        self.filewatcher.removePath(self.filename)

        try:
            f = open(self.filename, 'w')
            f.write(str(self.getText()))
            self.label.setText("Write file : " + self.filename)
        finally:
            f.close()
        
        self.filewatcher.addPath(self.filename)
            
            



class NodeCodeEditor(PythonCodeEditor):
    """ Default node editor """

    def __init__(self, factory, parent=None):
        
        PythonCodeEditor.__init__(self, parent)

        self.factory = factory
        self.src = None

        self.edit_class(factory)
        


    def edit_class(self, nodefactory):
        """ Open class source in editor """
        
        try:
            self.src = nodefactory.get_node_src()
            self.textedit.setText(self.src)
            self.label.setText("Module : " + self.factory.nodemodule_path)
        except Exception as e:
            print(e)
            self.src = None
            self.applybut.setEnabled(False)
            self.savbut.setEnabled(False)
            self.textedit.setText(" Sources are not available...")
            

    def apply_changes(self):
        """ Apply """
        self.src = str(self.getText())
        if(self.src != self.factory.get_node_src()):
            self.factory.apply_new_src(self.src)


    def save_changes(self):
        """ Save module """

        ret = QtWidgets.QMessageBox.question(self, "Save",
                                         "Modification will be written in the module\n"+
                                         "Continue ?\n",
                                         QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No,)

        if(ret == QtWidgets.QMessageBox.No): return

        module_name = self.factory.nodemodule_name
        newsrc = str(self.getText())

        self.factory.save_new_src(newsrc)



class Command(object):
    """
    Execute a command depending on a filename.
    Create a process and execute the command locally.
    """
    def __init__(self, command):
        self.p = None
        self.command = command

    def __del__(self):
        if self.p and (self.p.poll() is None):
            try:
                os.kill(self.p.pid,1)
            except:
                pass
        self.p = None

    def __call__(self, filename):
        fn = path(filename)
        cwd = fn.dirname()
        name = str(fn.basename())
        if self.p and (self.p.poll() is None):
            os.kill(self.p.pid, 1)

        cmd = self.command.split('%')[0]
        cmd = cmd.split('-')[0]

        try:
            import win32api
            cmd1 = win32api.GetShortPathName(cmd)
            command  = self.command.replace(cmd, cmd1)
        except ImportError:
            command = self.command

        self.p = Popen(command%name, shell = True, cwd = cwd)


class EditorSelector(AbstractCodeEditor, QtWidgets.QWidget):
    """
    Dialog to select an editor
    """

    def __init__(self, parent, editors, params):
        """
        @param editors : dictionnary name:command
        @param params : strings to replace command param (%s)
        """

        QtWidgets.QWidget.__init__(self, parent)

        vboxlayout = QtWidgets.QVBoxLayout(self)
        vboxlayout.setContentsMargins(3, 3, 3, 3)
        vboxlayout.setSpacing(5)

        self.editors = editors
        self.params = params

        # put the edit button in the first place
        keys = list(editors.keys())
        if 'edit' in keys:
            keys.remove('edit')
            keys.insert(0, 'edit')

        for k in keys:
            but = QtWidgets.QPushButton(self)
            but.setText(k)
            vboxlayout.addWidget(but)

            but.clicked.connect(self.on_button_clicked)

    
    def is_widget(self):
        return True

            
    def __del__(self):
        """ Destroy widget """
        for e in list(self.editors.values()):
            try:
                e.close()
            except:
                del e
        
        
    def on_button_clicked(self):

        name = str(self.sender().text())
        command = self.editors[name]
        fn = str(self.params[0])
        
        if(not command):
            widget = get_editor()(self.parent())
            
            if(widget.is_widget()):
                open_dialog(self.parent(), widget, fn, 
                            delete_on_close=True)

            widget.edit_file(fn)

        else:
            c = Command(command)
            c(fn)



