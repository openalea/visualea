# -*- python -*-
#
#       OpenAlea.Visualea: OpenAlea graphical user interface
#
#       Copyright 2006-2010 INRIA - CIRAD - INRA
#
#       File author(s): Daniel Barbeau <daniel.barbeau@sophia.inria.fr>
#
#       File contributor(s):
#
#       Distributed under the CeCILL v2 License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL_V2-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################
"""The QScintilla based code-editor widget for openalea"""

from builtins import str

__license__ = "CeCILL V2"
__revision__ = " $Id$"


import os
# from openalea.vpltk.qt.QtGui import *
from qtpy import QtWidgets, QtGui
from openalea.vpltk.qt import QT_API, PYQT4_API, PYQT5_API, PYSIDE_API, PYSIDE2_API, QtCore

if os.environ[QT_API].lower() in PYQT5_API:
    from PyQt5 import Qsci
    from PyQt5.Qsci import QsciScintilla
if os.environ[QT_API].lower() in PYQT4_API:
    from PyQt4 import Qsci
    from PyQt4.Qsci import QsciScintilla
if os.environ[QT_API].lower() in PYSIDE_API:
    from PySide import QScintilla as Qsci
    from PySide.QScintilla import QSciScintilla
if os.environ[QT_API].lower() in PYSIDE2_API:
    pass

###################################
# LEXERS OVERRIDEN                #
# Some template style programming #
###################################
# style indices (Scintilla reserves up to 39)
styles = {}
styles[40] = "HIGHLIGHT", QtGui.QColor(0, 0, 0), QtGui.QColor(0, 180, 0)

for k, v in list(styles.items()):
    styles[v[0]] = k, v[1], v[2]


def wrapLexerClass(lexerClass):
    class ExtendedLexerWrapper(lexerClass):
        # The lexers will use all 8 bits of style byte

        def styleBitsNeeded(self):
            return 8

    return ExtendedLexerWrapper

    # class ExtendedLexerWrapper(Qsci.QsciLexerCustom):
    #     def __init__(self, parent=None):
    #         Qsci.QsciLexerCustom.__init__(self, parent)
    #         self.baseLexer = lexerClass()
    #         for k, v in styles.iteritems():
    #             if isinstance(k, int):
    #                 setattr(self, v[0], k)

    #     def setEditor(self, editor):
    #         self.baseLexer.setEditor(editor)

    #     def defaultColor(self, style):
    #         st = styles.get(style)
    #         if not st:
    #             return self.baseLexer.defaultColor(style)
    #         return st[1]

    #     def defaultPaper(self, style):
    #         st = styles.get(style)
    #         if not st:
    #             return self.baseLexer.defaultPaper(style)
    #         return st[2]

    #     def description(self, style):
    #         st = styles.get(style)
    #         if not st:
    #             return self.baseLexer.description(style)
    #         return st[3]

    #     def defaultFont(self, style):
    #         return self.baseLexer.defaultFont(style)

    #     def styleText(self, start, end):
    #         return

    #     # The lexers will use all 8 bits of style byte
    #     def styleBitsNeeded(self):
    #         return 8;


lexers = dict((l[9:], wrapLexerClass(getattr(Qsci, l)))
              for l in dir(Qsci) if l.startswith("QsciLexer") and
              "Custom" not in l and l != "QsciLexer")


##########################################
# The Scintilla widgets a bit customized #
##########################################

class CodeWidget(QsciScintilla):

    def __init__(self, *args, **kwargs):
        QsciScintilla.__init__(self)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)

        self.highlit = None
        # self.SendScintilla(QsciScintilla.SCI_STYLESETFORE,
        #                    styles["HIGHLIGHT"][0],
        #                    styles["HIGHLIGHT"][1] )

        # self.SendScintilla(QsciScintilla.SCI_STYLESETBACK,
        #                    styles["HIGHLIGHT"][0],
        #                    styles["HIGHLIGHT"][2] )

    def setLanguage(self, language):
        if language is not None:
            lexer = lexers[str(language)]()
            self.setLexer(lexer)

    def showLineNumber(self, checked):
        self.setMarginType(1, QsciScintilla.NumberMargin)
        self.setMarginWidth(1, "10000" if checked else 0)
        self.setMarginLineNumbers(1, checked)

    def showFolding(self, checked):
        if checked:
            self.setMarginType(2, QsciScintilla.SymbolMargin)
            self.setFolding(QsciScintilla.CircledTreeFoldStyle, 2)
        else:
            self.setFolding(QsciScintilla.NoFoldStyle, 2)

    def findTextOccurences(self, text):
        """Return byte positions of start and end of all 'text' occurences in the document"""
        textLen = len(text)
        endPos = self.SendScintilla(QsciScintilla.SCI_GETLENGTH)
        self.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, 0)
        self.SendScintilla(QsciScintilla.SCI_SETTARGETEND, endPos)

        occurences = []

        match = self.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, textLen, text)
        while(match != -1):
            matchEnd = self.SendScintilla(QsciScintilla.SCI_GETTARGETEND)
            occurences.append((match, matchEnd))
            # -- if there's a match, the target is modified so we shift its start
            # -- and restore its end --
            self.SendScintilla(QsciScintilla.SCI_SETTARGETSTART, matchEnd)
            self.SendScintilla(QsciScintilla.SCI_SETTARGETEND, endPos)
            # -- find it again in the new (reduced) target --
            match = self.SendScintilla(QsciScintilla.SCI_SEARCHINTARGET, textLen, text)
        return occurences

    def highlightOccurences(self, text):
        occurences = self.findTextOccurences(text)
        textLen = len(text)
        self.SendScintilla(QsciScintilla.SCI_SETSTYLEBITS, 8)
        for occs in occurences:
            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
            self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE,
                               occs[0], textLen)

            # -- this is somewhat buggy : it was meant to change the color
            # -- but somewhy the colouring suddenly changes colour.

            # self.SendScintilla(QsciScintilla.SCI_STARTSTYLING, occs[0], 0xFF)
            # self.SendScintilla(QsciScintilla.SCI_SETSTYLING,
            #                    textLen,
            #                    styles["HIGHLIGHT"][0])
        self.highlit = occurences

    def clearHighlights(self):
        if self.highlit is None:
            return

        for occs in self.highlit:
            self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
            self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE,
                               occs[0], occs[1] - occs[0])
        self.highlit = None

    def textSearch(self, text, fromStart, highlightAll, re=False,
                   cs=True, wo=False, wrap=True, forward=True,
                   line=-1, index=-1, show=True):
        if text is not None:
            if highlightAll:
                self.clearHighlights()
                self.highlightOccurences(text)
            if fromStart:
                self.setCursorPosition(0)

            match = self.findFirst(text, re, cs, wo, wrap, forward, line, index, show)

    def textReplace(self, text, sub, fromStart, re=False,
                    cs=True, wo=False, wrap=True, forward=True,
                    line=-1, index=-1, show=True):
        if text is not None and sub is not None:
            self.clearHighlights()
            self.highlightOccurences(text)
            if fromStart:
                self.setCursorPosition(0)

            match = self.findFirst(text, re, cs, wo, wrap, forward, line, index, show)
            if match:
                self.replace(sub)


#####################################
# Code editor controls and settings #
#####################################

class CodeWidgetFindReplace(QtWidgets.QWidget):

    # -- signals forwarded from internal widget --
    textSearchRequest = QtCore.Signal(str, bool, bool)
    textReplaceRequest = QtCore.Signal(str, str, bool)
    resultClearRequest = QtCore.Signal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # - Find text -
        findLabel = QtWidgets.QLabel("Find:")
        findLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.findLineEdit = QtWidgets.QLineEdit()
        self.highlightResultsCheckBox = QtWidgets.QCheckBox("Highlight all matches")
        self.clearResultsPushButton = QtWidgets.QPushButton("Clear results")

        # - Replace text -
        replaceLabel = QtWidgets.QLabel("Replace with:")
        replaceLabel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.replaceLineEdit = QtWidgets.QLineEdit()

        # --- signal bindings ---
        self.findLineEdit.returnPressed.connect(self._searchRequest)
        self.highlightResultsCheckBox.released.connect(self._searchRequest)
        self.clearResultsPushButton.released.connect(self.resultClearRequest)
        self.replaceLineEdit.returnPressed.connect(self._replaceRequest)

        # --- general layout ---
        layout = QtWidgets.QGridLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        layout.addWidget(findLabel, 0, 0)
        layout.addWidget(self.findLineEdit, 0, 1)
        layout.addWidget(self.highlightResultsCheckBox, 0, 2)
        layout.addWidget(self.clearResultsPushButton, 0, 3)
        layout.addWidget(replaceLabel, 1, 0)
        layout.addWidget(self.replaceLineEdit, 1, 1)
        self.setLayout(layout)

    def initialise(self):
        # --- initialise everybody ---
        pass

    def _searchRequest(self):
        text = self.findLineEdit.text()
        highlightAll = self.highlightResultsCheckBox.isChecked()
        fromStart = False
        if text != "":
            self.textSearchRequest.emit(text, fromStart, highlightAll)

    def _replaceRequest(self):
        findText = self.findLineEdit.text()
        replaceText = self.replaceLineEdit.text()
        fromStart = False
        if findText != "" and replaceText != "":
            self.textReplaceRequest.emit(findText, replaceText, fromStart)


class CodeWidgetPreferences(QtWidgets.QWidget):

    # -- signals forwarded from internal widgets --
    languageChanged = QtCore.Signal(str)
    lineNumberToggled = QtCore.Signal(bool)
    foldingToggled = QtCore.Signal(bool)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        # - language chooser -
        label = QtWidgets.QLabel("Language:")
        self.languageCombo = QtWidgets.QComboBox()
        self.languageCombo.addItems(sorted(list(lexers.keys())))
        langLayout = QtWidgets.QHBoxLayout()
        langLayout.addWidget(label, 0, QtCore.Qt.AlignLeft)
        langLayout.addWidget(self.languageCombo, 0, QtCore.Qt.AlignLeft)
        # - show line no -
        self.showLineCheckBox = QtWidgets.QCheckBox("Show line numbers")
        # - show folding -
        self.showFoldingCheckBox = QtWidgets.QCheckBox("Show folding")

        # --- signal bindings ---
        self.languageCombo.currentIndexChanged[str].connect(self.languageChanged)
        self.showLineCheckBox.toggled.connect(self.lineNumberToggled)
        self.showFoldingCheckBox.toggled.connect(self.foldingToggled)

        # --- general layout ---
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        layout.addLayout(langLayout)
        layout.addWidget(self.showLineCheckBox, 0, QtCore.Qt.AlignLeft)
        layout.addWidget(self.showFoldingCheckBox, 1, QtCore.Qt.AlignLeft)
        self.setLayout(layout)

    def initialise(self, language="Python", showLineNo=False, showFolding=False):
        # --- initialise everybody ---
        if language is not None:
            self.languageCombo.setCurrentIndex(self.languageCombo.findText(language))
        self.showLineCheckBox.setChecked(showLineNo)
        self.showFoldingCheckBox.setChecked(showFolding)


######################################################
# The final top widgets aggregating everything above #
######################################################

class SmallTabWidget(QtWidgets.QTabWidget):

    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        tabbar = self.tabBar()
        tabbar.setStyleSheet("QTabBar::tab {" +
                             "height :18px;" +
                             "font-size :10px;" +
                             "}"
                             )


class ScintillaCodeEditor(QtWidgets.QWidget):

    # -- this signal makes us compatible with Openalea's NodeWidgets --
    textChanged = QtCore.Signal()

    def __init__(self, language="Python", *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        # --- the scintilla widget ---
        self.editor = CodeWidget()

        # --- the controls ---
        findReplaceWidget = CodeWidgetFindReplace()
        preferencesWidget = CodeWidgetPreferences()
        # -- controls are organised into a tabwidget --
        # tabWidget = QTabWidget()
        tabWidget = SmallTabWidget()
        # - fill the tabwidget -
        tabWidget.addTab(findReplaceWidget, "Find & Replace")
        tabWidget.addTab(preferencesWidget, "Preferences")

        # --- signal bindings ---
        findReplaceWidget.textSearchRequest.connect(self.editor.textSearch)
        findReplaceWidget.textReplaceRequest.connect(self.editor.textReplace)
        findReplaceWidget.resultClearRequest.connect(self.editor.clearHighlights)
        preferencesWidget.languageChanged.connect(self.editor.setLanguage)
        preferencesWidget.lineNumberToggled.connect(self.editor.showLineNumber)
        preferencesWidget.foldingToggled.connect(self.editor.showFolding)
        self.editor.textChanged.connect(self.textChanged)

        # --- general layout ---
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(0)
        layout.addWidget(self.editor)
        layout.addWidget(tabWidget)
        self.setLayout(layout)

        # --- initialise everybody ---showLineNo showFolding
        preferencesWidget.initialise(language, showLineNo=False, showFolding=False)

    # -- for compatibility with Openalea --
    def setText(self, text):
        self.editor.setText(text)

    # -- for compatibility with Openalea --
    def text(self):
        # do not remove this line! Reference counting will otherwise make
        # this function return None (if you do "return self.editor.text()")
        txt = self.editor.text()
        return txt

    def document(self):
        return self.editor.document()

    def setDocument(self, doc):
        self.editor.setDocument(doc)


if __name__ == "__main__":
    s = """
class CodeEditor(QsciScintilla):
    def __init__(self, *args, **kwargs):
        QsciScintilla.__init__(self)
        self.setLexer(Qsci.QsciLexerPython())
        self.setMarginLineNumbers(1, True)
        self.setMarginType(1,QsciScintilla.SymbolMargin|QsciScintilla.NumberMargin)
        self.setMarginWidth(1,"10000")
        self.setIndentationsUseTabs(False)
    """
    app = QtWidgets.QApplication([])
    w = ScintillaCodeEditor(parent=None)
    w.show()
    w.setText(s)
    app.exec_()
