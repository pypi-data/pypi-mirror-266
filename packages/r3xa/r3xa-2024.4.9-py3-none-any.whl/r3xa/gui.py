# -*- coding: utf-8 -*-
# # importing libraries
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import *
# import sys
# import json
# import slugify
#
# from r3xa.utils import get_schema, slugify_file_name
# from r3xa.validation import validate
# from r3xa.metadata import MetaData
#
#
# def pyqtislameaf(field):
#
#     if isinstance(field, QLineEdit):
#         try:
#             return float(field.text())
#         except Exception:
#             return field.text()
#     elif isinstance(field, QTextEdit):
#         return field.toPlainText()
#
#     return field.text()
#
# class Window(QDialog):
#
#     def __init__(self, json_file_name: str = None):
#         super(Window, self).__init__()
#
#         self.setMaximumHeight(300)
#
#         # set output
#         output = self.outputWidget()
#
#         self.schema = get_schema()
#         self.json_file_name = json_file_name
#         try:
#             self.json = json.load(open(self.json_file_name, "r")) if self.json_file_name else {}
#         except FileNotFoundError as e:
#             self.json = {}
#             print(e)
#             self.outputText.setText(str(e))
#             self.outputText.setStyleSheet("color: #e22;")
#
#         self.metadata = MetaData()
#         self.metadata.load_json(self.json)
#
#         # setting window title
#         self.setWindowTitle("R3XA meta data editor")
#
#         # buid header
#         header = self.headerWidget()
#
#         # build tabs for meta data forms
#         form = QTabWidget()
#
#         global_tab = self.globalTab()
#         form.addTab(global_tab, 'Global')
#
#         json_tab = self.jsonTab()
#         form.addTab(json_tab, 'JSON')
#
#         settings_tab = self.settingsTab()
#         form.addTab(settings_tab, 'Settings')
#
#         # save / load button
#         buttons = self.buttonsWidget()
#
#         # main layout
#         layout = QVBoxLayout()
#         layout.addWidget(header)
#         layout.addWidget(form)
#         layout.addWidget(output)
#         layout.addWidget(buttons)
#         layout.addStretch()
#
#         self.setLayout(layout)
#
#     def headerWidget(self):
#         header = f"""<h3>{self.schema["title"]}</h3>
#         <p>{self.schema["description"]}</p>
#         <p><i>Version {self.schema["properties"]["version"]["const"]}</i></p>
#         <p></p>
#         """
#         return QLabel(header)
#
#
#     def display_form(self, section_key, payload, properties, required, layout):
#
#         # get required arguments for global parameters
#         for k, v in properties.items():
#
#             r = "*" if k in required else ""
#             label = QLabel(f'<b>{v["title"]}{r}</b>')
#             if r:
#                 label.setStyleSheet("color: #e22;")
#             layout.addRow(label, QLabel(f'{v["description"]}'))
#
#             string_like = ["string", "#/$defs/types/uri", "#/$defs/types/string"]
#             if v.get("type") in string_like or v.get("$ref") in string_like:
#                 # handle field type and default value
#                 if k == "description":
#                     input_field = QTextEdit()
#                     input_field.setText(payload.get(k, ""))
#                     input_field.setTabChangesFocus(True)
#                 else:
#                     input_field = QLineEdit()
#                     input_field.setText(payload.get(k, ""))
#                     input_field.editingFinished.connect(self.onEditingFinished)
#
#                 # handle read only
#                 if "const" in v:
#                     input_field.setText(v["const"])
#                     input_field.setReadOnly(True)
#                     input_field.setStyleSheet("color: #aaa;")
#                 elif k == "id":
#                     input_field.setReadOnly(True)
#                     input_field.setStyleSheet("color: #aaa;")
#
#                 layout.addRow(QLabel(""), input_field)
#                 setattr(self, f"{section_key}_{k}", input_field)
#
#                 # handle example
#                 if isinstance(v.get("examples"), list):
#                     examples = QLabel(f'<i>e.g.</i> {"; ".join(v["examples"])}')
#                     examples.setStyleSheet("color: #aaa; margin-bottom: 10px;")
#                     layout.addRow(QLabel(""), examples)
#
#             elif v.get("$ref") in ["#/$defs/types/unit"]:
#                 line = QFrame()
#                 line.setFrameShape(QFrame.HLine)
#                 line.setFrameShadow(QFrame.Sunken)
#                 layout.addRow(line)
#
#                 unit = self.schema["$defs"]["types"]["unit"]
#                 unit_required = unit["required"]
#                 for unit_k, unit_v in unit["properties"].items():
#                     r = "*" if unit_k in unit_required else ""
#                     label = QLabel(f'{unit_k}{r}')
#                     if r:
#                         label.setStyleSheet("color: #e22;")
#                     input_field = QLineEdit()
#                     input_field.setText(str(payload.get(k, {}).get(unit_k, "")))
#                     input_field.editingFinished.connect(self.onEditingFinished)
#                     setattr(self, f"{section_key}_{k}/{unit_k}", input_field)
#                     layout.addRow(label, input_field)
#
#                 # handle example
#                 if isinstance(v.get("examples"), list):
#                     examples = QLabel(f'<i>e.g.</i> {"; ".join(v["examples"])}')
#                     examples.setStyleSheet("color: #aaa; margin-bottom: 10px;")
#                     layout.addRow(QLabel(""), examples)
#
#                 line = QFrame()
#                 line.setFrameShape(QFrame.HLine)
#                 line.setFrameShadow(QFrame.Sunken)
#                 layout.addRow(line)
#
#             else:
#                 print(v)
#
#     def globalTab(self):
#
#         layout = QFormLayout()
#         layout.addRow(QLabel("<h3>Global meta data</h3>"))
#
#         self.json_file_name_field = QLineEdit(self.json_file_name if self.json_file_name else "")
#         self.json_file_name_field.editingFinished.connect(self.onEditingFileName)
#         layout.addRow(f'<b>JSON file</b>', self.json_file_name_field)
#
#         ignored = ["data_sets", "settings", "data_sources"]
#         properties = {k: v for k, v in self.schema["properties"].items() if k not in ignored}
#         required = self.schema["required"]
#         self.display_form("field_global", self.json, properties, required, layout)
#
#         tab = QWidget()
#         tab.setLayout(layout)
#
#         return tab
#
#     def jsonTab(self):
#         layout = QVBoxLayout()
#         self.rawJson = QTextEdit()
#         self.rawJson.setText(json.dumps(self.json, indent=2))
#         self.rawJson.setReadOnly(True)
#         self.rawJson.setAcceptRichText(True)
#         self.rawJson.setStyleSheet("color: #aaa;")
#         layout.addWidget(self.rawJson)
#
#         tab = QWidget()
#         tab.setLayout(layout)
#         return tab
#
#     def settingsTab(self):
#
#         mainLayout = QVBoxLayout()
#
#         #######
#         # Combo box to select edit/create setting
#         #######
#
#         selectLayout = QFormLayout()
#         self.settingComboBox = QComboBox()
#
#         # create a new settings from schema
#         for k, v in self.schema["$defs"]["setting"].items():
#             self.settingComboBox.addItem(f'New {k} setting', userData=f"new_{k}")
#
#         # get all settings from schema
#         for setting in self.metadata.settings:
#             self.settingComboBox.addItem(f'Edit {setting.title}', userData=f"edit_{setting.id}")
#
#         # setup layout
#         selectLayout.addRow(QLabel('<b>Manage your settings</b>'), self.settingComboBox)
#         selectWidget = QWidget()
#         selectWidget.setLayout(selectLayout)
#         mainLayout.addWidget(selectWidget)
#
#         # setup trigger
#         self.settingComboBox.currentIndexChanged.connect(self.onSettingComboBox)
#
#         ######
#         # Form to edit/create settings
#         ######
#         self.settingFormLayout = QFormLayout()
#         # formLayout.addRow(QLabel("coucou"))
#         formWidget = QWidget()
#         formWidget.setLayout(self.settingFormLayout)
#         mainLayout.addWidget(formWidget)
#         mainLayout.addStretch()
#
#         tab = QWidget()
#         tab.setLayout(mainLayout)
#         return tab
#
#     def onSettingComboBox(self, index):
#         # delete all self attribute of previous settingCombo
#         for  k in [k for k in self.__dict__ if k[:14] == "field_setting/"]:
#             delattr(self, k)
#         # and clear layout
#         self.clearLayout(self.settingFormLayout)
#
#         combo_box = self.settingComboBox
#         key = combo_box.currentData()
#
#         # parse key
#         action = key.split("_")[0]
#         setting_id = "_".join(key.split("_")[1:])
#
#         if action == "edit":
#             # get setting from json
#             setting = [s for s in self.json["settings"] if s["id"] == setting_id][0]
#             properties = self.schema["$defs"]["setting"][setting["kind"]]["properties"]
#             required = self.schema["$defs"]["setting"][setting["kind"]]["required"]
#
#             section_key = f'field_setting/{setting["kind"]}'
#
#             self.display_form(section_key, setting, properties, required, self.settingFormLayout)
#
#         self.outputText.setText(f"{action.title()} {setting_id}")
#         self.outputText.setStyleSheet("color: #aaa;")
#
#
#     def outputWidget(self):
#         layout = QFormLayout()
#         self.outputText = QTextEdit()
#         self.outputText.setReadOnly(True)
#         layout.addRow(self.outputText)
#         output = QWidget()
#         output.setLayout(layout)
#         return output
#
#     def buttonsWidget(self):
#         layout = QFormLayout()
#         saveButton = QPushButton('save file')
#         layout.addRow(saveButton)
#         buttons = QWidget()
#         buttons.setLayout(layout)
#
#         saveButton.clicked.connect(self.save)
#         return buttons
#
#     def update_metadata_from_fields(self):
#         # get global fields
#         payload = {}
#         payload_setting = {}
#         for k, v in self.__dict__.items():
#             if k[:12] == "field_global" and pyqtislameaf(v):
#                 json_key = k.split("_")[-1]
#                 json_val = pyqtislameaf(v)
#                 payload[json_key] = json_val
#             elif k[:14] == "field_setting/":
#                 print(k, v)
#                 splt = k.split("/")
#                 json_key = splt[1].split("_")[1]
#                 json_val = pyqtislameaf(v)
#                 if len(splt) == 3:
#                     json_sub_key = splt[2]
#                     if json_key not in payload_setting:
#                         payload_setting[json_key] = {}
#                     payload_setting[json_key][json_sub_key] = json_val
#                 else:
#                     payload_setting[json_key] = json_val
#             else:
#                 pass
#                 # print(k, v)
#
#         if len(payload_setting):
#             payload["settings"] = [payload_setting]
#         self.metadata.load_json(payload)
#         self.json = self.metadata.get_json()
#
#     def validate_metadata(self):
#         try:
#             validate(self.json)
#         except Exception as e:
#             print(e)
#             self.outputText.setText(str(e))
#             self.outputText.setStyleSheet("color: #e22;")
#         else:
#             self.outputText.setText("Valid JSON file")
#             self.outputText.setStyleSheet("color: #2a2;")
#
#     def save(self):
#         # update json file name
#         self.onEditingFinished()  # update display if last edit is a text field
#         self.json_file_name = pyqtislameaf(self.json_file_name_field)
#         self.update_metadata_from_fields()
#
#         try:
#             name = self.json_file_name
#             if self.json_file_name[-5:] == ".json":
#                 name = self.json_file_name.replace(".json", "")
#             self.metadata.save_json(name=name)
#             self.outputText.setText(f"JSON file saved: {name}.json")
#             self.outputText.setStyleSheet("color: #2a2;")
#
#         except Exception as e:
#             print(e)
#             self.outputText.setText(str(e))
#             self.outputText.setStyleSheet("color: #e22;")
#
#     def onEditingFileName(self):
#         self.json_file_name = pyqtislameaf(self.json_file_name_field)
#         if not len(self.json_file_name):
#             self.json_file_name = None
#             return
#
#         if not self.json_file_name[-5:] == ".json":
#             self.json_file_name += ".json"
#         self.json_file_name = slugify_file_name(self.json_file_name)
#         self.json_file_name_field.setText(self.json_file_name)
#
#
#     def onEditingFinished(self):
#         self.update_metadata_from_fields()
#
#         # edit file name if None and title set
#         if self.json_file_name is None and "title" in self.json:
#             self.json_file_name = slugify.slugify(self.json["title"]) + ".json"
#             self.json_file_name_field.setText(self.json_file_name)
#
#         # edit json raw
#         self.rawJson.setText(json.dumps(self.json, indent=2))
#         self.validate_metadata()
#
#
#     def clearLayout(self, layout):
#         while layout.count():
#             item = layout.takeAt(0)
#             widget = item.widget()
#             if widget:
#                 widget.deleteLater()
