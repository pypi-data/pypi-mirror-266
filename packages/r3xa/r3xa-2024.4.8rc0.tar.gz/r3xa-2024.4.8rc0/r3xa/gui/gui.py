# -*- coding: utf-8 -*-
# # importing libraries
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import *
# import sys
# import json
# import warlock
#
#
# # creating a class
# # that inherits the QDialog class
# class Window(QDialog):
#     # constructor
#     def __init__(self, schema):
#         super(Window, self).__init__()
#
#         # json data
#         Schema = warlock.model_factory(schema)
#         self.instance = Schema(
#             title="coucou",
#         )
#
#         # setting window title
#         self.setWindowTitle("T-R3X")
#
#         self.createHeader()
#
#         # for group box
#         self.formGroupBox = QGroupBox("Form 1")
#
#         # creating spin box to select age
#         self.ageSpinBar = QSpinBox()
#
#         # creating combo box to select degree
#         self.degreeComboBox = QComboBox()
#
#         # adding items to the combo box
#         self.degreeComboBox.addItems(["BTech", "MTech", "PhD"])
#
#         # creating a line edit
#         self.nameLineEdit = QLineEdit()
#
#         # calling the method that create the form
#         self.createForm()
#
#         # creating a dialog button for ok and cancel
#         self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
#
#         # adding action when form is accepted
#         self.buttonBox.accepted.connect(self.getInfo)
#
#         # adding action when form is rejected
#         self.buttonBox.rejected.connect(self.reject)
#
#         # creating a vertical layout
#         mainLayout = QVBoxLayout()
#
#         # adding form group box to the layout
#         mainLayout.addWidget(self.headerGroupBox)
#
#         # adding form group box to the layout
#         mainLayout.addWidget(self.formGroupBox)
#
#         # adding button box to the layout
#         mainLayout.addWidget(self.buttonBox)
#
#         # setting lay out
#         self.setLayout(mainLayout)
#
#     def getQLabelFromObj(obj):
#         print(obj)
#
#     # get info method called when form is accepted
#     def getInfo(self):
#         # printing the form information
#         print("Person Name : {0}".format(self.nameLineEdit.text()))
#         print("Degree : {0}".format(self.degreeComboBox.currentText()))
#         print("Age : {0}".format(self.ageSpinBar.text()))
#
#         # closing the window
#         self.close()
#
#     def createHeader(self):
#         layout = QVBoxLayout()
#
#         # header group box
#         self.headerGroupBox = QGroupBox("T-REX")
#         schema_version = schema["properties"]["version"]
#         # self.headerVersionText = self.
#         QLabel(f"Format used: {schema_version}")
#
#         layout.addWidget(QLabel("Yolo"), alignment=Qt.AlignTop)
#         layout.addWidget(self.getQLabelFromObj(), alignment=Qt.AlignTop)
#         # layout.addStretch()
#         layout.setSizeConstraint(QLayout.SetFixedSize)
#         self.headerGroupBox.setLayout(layout)
#
#     # create form method
#     def createForm(self):
#         # creating a form layout
#         layout = QFormLayout()
#
#         # adding rows
#         # for name and adding input text
#         layout.addRow(QLabel("Name"), self.nameLineEdit)
#
#         # for degree and adding combo box
#         layout.addRow(QLabel("Degree"), self.degreeComboBox)
#
#         # for age and adding spin box
#         layout.addRow(QLabel("Age"), self.ageSpinBar)
#
#         # setting layout
#         self.formGroupBox.setLayout(layout)
#
#
# # main method
# if __name__ == "__main__":
#     # load schema
#     schema = json.load(open("schema.json"))
#
#     # create pyqt5 app
#     app = QApplication(sys.argv)
#
#     # create the instance of our Window
#     window = Window(schema)
#     window.setGeometry(100, 100, 100, 100)
#
#     # showing the window
#     window.show()
#
#     # start the app
#     sys.exit(app.exec())
