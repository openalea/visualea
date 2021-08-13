# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newpackage.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_NewPackageDialog(object):
    def setupUi(self, NewPackageDialog):
        NewPackageDialog.setObjectName("NewPackageDialog")
        NewPackageDialog.resize(479, 435)
        self.vboxlayout = QtWidgets.QVBoxLayout(NewPackageDialog)
        self.vboxlayout.setContentsMargins(9, 9, 9, 9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")
        self.gridlayout = QtWidgets.QGridLayout()
        self.gridlayout.setContentsMargins(0, 0, 0, 0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        self.authorsEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.authorsEdit.setObjectName("authorsEdit")
        self.gridlayout.addWidget(self.authorsEdit, 4, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(NewPackageDialog)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.pathButton = QtWidgets.QPushButton(NewPackageDialog)
        self.pathButton.setObjectName("pathButton")
        self.gridlayout.addWidget(self.pathButton, 7, 2, 1, 1)
        self.label = QtWidgets.QLabel(NewPackageDialog)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label, 0, 0, 1, 1)
        self.versionEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.versionEdit.setObjectName("versionEdit")
        self.gridlayout.addWidget(self.versionEdit, 2, 1, 1, 1)
        self.label_7 = QtWidgets.QLabel(NewPackageDialog)
        self.label_7.setObjectName("label_7")
        self.gridlayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.label_8 = QtWidgets.QLabel(NewPackageDialog)
        self.label_8.setObjectName("label_8")
        self.gridlayout.addWidget(self.label_8, 7, 0, 1, 1)
        self.pathEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.pathEdit.setObjectName("pathEdit")
        self.gridlayout.addWidget(self.pathEdit, 7, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(NewPackageDialog)
        self.label_6.setObjectName("label_6")
        self.gridlayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.descriptionEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.descriptionEdit.setObjectName("descriptionEdit")
        self.gridlayout.addWidget(self.descriptionEdit, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(NewPackageDialog)
        self.label_3.setObjectName("label_3")
        self.gridlayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.institutesEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.institutesEdit.setObjectName("institutesEdit")
        self.gridlayout.addWidget(self.institutesEdit, 5, 1, 1, 1)
        self.urlEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.urlEdit.setObjectName("urlEdit")
        self.gridlayout.addWidget(self.urlEdit, 6, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(NewPackageDialog)
        self.label_4.setObjectName("label_4")
        self.gridlayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.nameEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.nameEdit.setObjectName("nameEdit")
        self.gridlayout.addWidget(self.nameEdit, 0, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(NewPackageDialog)
        self.label_5.setObjectName("label_5")
        self.gridlayout.addWidget(self.label_5, 4, 0, 1, 1)
        self.licenseEdit = QtWidgets.QLineEdit(NewPackageDialog)
        self.licenseEdit.setObjectName("licenseEdit")
        self.gridlayout.addWidget(self.licenseEdit, 3, 1, 1, 1)
        self.vboxlayout.addLayout(self.gridlayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(NewPackageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.NoButton|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout.addWidget(self.buttonBox)

        self.retranslateUi(NewPackageDialog)
        self.buttonBox.accepted.connect(NewPackageDialog.accept)
        self.buttonBox.rejected.connect(NewPackageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewPackageDialog)
        NewPackageDialog.setTabOrder(self.nameEdit, self.descriptionEdit)
        NewPackageDialog.setTabOrder(self.descriptionEdit, self.versionEdit)
        NewPackageDialog.setTabOrder(self.versionEdit, self.licenseEdit)
        NewPackageDialog.setTabOrder(self.licenseEdit, self.authorsEdit)
        NewPackageDialog.setTabOrder(self.authorsEdit, self.institutesEdit)
        NewPackageDialog.setTabOrder(self.institutesEdit, self.urlEdit)
        NewPackageDialog.setTabOrder(self.urlEdit, self.pathEdit)
        NewPackageDialog.setTabOrder(self.pathEdit, self.pathButton)
        NewPackageDialog.setTabOrder(self.pathButton, self.buttonBox)

    def retranslateUi(self, NewPackageDialog):
        _translate = QtCore.QCoreApplication.translate
        NewPackageDialog.setWindowTitle(_translate("NewPackageDialog", "Package"))
        self.label_2.setText(_translate("NewPackageDialog", "Description"))
        self.pathButton.setText(_translate("NewPackageDialog", "..."))
        self.label.setText(_translate("NewPackageDialog", "Name"))
        self.label_7.setText(_translate("NewPackageDialog", "URL"))
        self.label_8.setText(_translate("NewPackageDialog", "Path"))
        self.label_6.setText(_translate("NewPackageDialog", "Institutes"))
        self.label_3.setText(_translate("NewPackageDialog", "Version"))
        self.label_4.setText(_translate("NewPackageDialog", "License"))
        self.label_5.setText(_translate("NewPackageDialog", "Authors"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    NewPackageDialog = QtWidgets.QDialog()
    ui = Ui_NewPackageDialog()
    ui.setupUi(NewPackageDialog)
    NewPackageDialog.show()
    sys.exit(app.exec_())
