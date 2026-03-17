import sys
from PyQt5.QtWidgets import QApplication, QInputDialog, QMainWindow, QTextEdit, QPushButton, QVBoxLayout,QFileDialog,QMessageBox
from PyQt5.QtGui import QIcon
from io import StringIO
import qdarktheme
import contextlib
import os



class AcronIDE(QMainWindow):
   def __init__(self):
      super(AcronIDE, self).__init__()
      
      self.IdeUi()
   def IdeUi(self):
      from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QListWidget, QToolBar
      # Icon Files for the buttons
      runicon = "res/icons/run.png"
      newfileicon = "res/icons/newfile.png"
      newfoldericon = "res/icons/newfolder.png"
      openfoldericon = "res/icons/openfolder"
      openfileicon = "res/icons/openfile"
      saveicon = "res/icons/save"
      # Windows Settings
      self.setGeometry(100, 100, 800, 600)
      self.setWindowTitle("AcronIDE")
      self.setWindowIcon(QIcon('res/icons/icon.png'))

      # Central widget and main layout
      central_widget = QWidget()
      main_layout = QHBoxLayout()
      central_widget.setLayout(main_layout)
      self.setCentralWidget(central_widget)

      # File Explorer Sidebar
      self.file_explorer = QListWidget()
      self.file_explorer.setFixedWidth(180)
      self.file_explorer.itemDoubleClicked.connect(self.handle_file_explorer_double_click)
      main_layout.addWidget(self.file_explorer)
      self.file_explorer_visible = True
      self.current_folder = None

      # Main area (vertical layout)
      main_area = QWidget()
      main_area_layout = QVBoxLayout()
      main_area.setLayout(main_area_layout)
      main_layout.addWidget(main_area)

      print(f"Your files will be saved in: {os.getcwd()}")

      # Toolbar for action buttons
      toolbar = QToolBar()
      runbtn = QPushButton("Run",self)
      runbtn.setIcon(QIcon(runicon))
      toolbar.addWidget(runbtn)
      runbtn.clicked.connect(self.runing)
      # Toggle File Explorer button
      toggle_explorer_btn = QPushButton("Toggle File Explorer")
      toggle_explorer_btn.clicked.connect(self.toggle_file_explorer)
      toolbar.addWidget(toggle_explorer_btn)
      # new file button
      newfilebtn = QPushButton("New File")
      newfilebtn.setIcon(QIcon(newfileicon))
      newfilebtn.clicked.connect(self.newfileevent)
      toolbar.addWidget(newfilebtn)
      newfolderbtn = QPushButton("New Folder")
      newfolderbtn.setIcon(QIcon(newfoldericon))
      newfolderbtn.clicked.connect(self.newfolderevent)
      toolbar.addWidget(newfolderbtn)
      #save button
      savebtn = QPushButton("Save")
      savebtn.setIcon(QIcon(saveicon))
      toolbar.addWidget(savebtn)
      # open folder functionality
      openfolderbtn = QPushButton("Open Folder")
      openfolderbtn.setIcon(QIcon(openfoldericon))
      openfolderbtn.clicked.connect(self.openfolderevent)
      toolbar.addWidget(openfolderbtn)
      # open file button
      openfilebtn = QPushButton("Open File")
      openfilebtn.setIcon(QIcon(openfileicon))
      openfilebtn.clicked.connect(self.openingfile)
      toolbar.addWidget(openfilebtn)
      main_area_layout.addWidget(toolbar)
      #output console
      self.outpot_console = QTextEdit(self)
      self.outpot_console.setReadOnly(True)
      main_area_layout.addWidget(self.outpot_console)
      # Main editor area
      self.editor = QTextEdit()
      self.editor.setPlaceholderText("Start coding...")
      main_area_layout.addWidget(self.editor)

   def runing(self):
      code = self.editor.toPlainText()
      output = StringIO()
      with contextlib.redirect_stdout(output):
         try:
            exec(code)
         except Exception as e:
            print(f"Error: {e}")
      self.outpot_console.setPlainText(output.getvalue())
   def openfolderevent(self):
      folder_path = QFileDialog.getExistingDirectory(self, 'Open Folder', os.getcwd())
      if folder_path:
         self.current_folder = folder_path
         self.populate_file_explorer(folder_path)

   def saveevent(self):

      if self.current_folder:
         options = QFileDialog.Options()
         file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", self.current_folder, "Text Files (*.txt);;All Files (*)", options=options)
         if file_path:
            with open(file_path, 'w') as f:
               f.write(self.editor.toPlainText())
            QMessageBox.information(self, "Success", f"File saved at: {file_path}")
            self.populate_file_explorer(self.current_folder)
      else:
         QMessageBox.warning(self, "No Folder Open", "Please open a folder first to save a file.")
   def populate_file_explorer(self, folder_path):
      self.file_explorer.clear()
      self.file_explorer.addItem(".. (Up one level)")
      try:
         for entry in os.listdir(folder_path):
            full_path = os.path.join(folder_path, entry)
            if os.path.isdir(full_path):
               self.file_explorer.addItem(f"[DIR] {entry}")
            else:
               self.file_explorer.addItem(entry)
      except Exception as e:
         QMessageBox.warning(self, "Error", f"Could not list folder: {e}")

   def handle_file_explorer_double_click(self, item):
      if not self.current_folder:
         return
      text = item.text()
      if text == ".. (Up one level)":
         parent = os.path.dirname(self.current_folder)
         if parent and os.path.exists(parent):
            self.current_folder = parent
            self.populate_file_explorer(parent)
      elif text.startswith("[DIR] "):
         folder_name = text[6:]
         new_folder = os.path.join(self.current_folder, folder_name)
         if os.path.isdir(new_folder):
            self.current_folder = new_folder
            self.populate_file_explorer(new_folder)
      else:
         file_path = os.path.join(self.current_folder, text)
         if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
               content = f.read()
            self.editor.setPlainText(content)

   def toggle_file_explorer(self):
      self.file_explorer_visible = not self.file_explorer_visible
      self.file_explorer.setVisible(self.file_explorer_visible)
   def openingfile(self):
      filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Python Files (*.py)")
      if filename:
         with open(filename, 'r') as file:
            content = file.read()
            self.editor.setPlainText(content)
   def newfileevent(self):
      # If a folder is open, create file in that folder
      if self.current_folder:
         options = QFileDialog.Options()
         file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", self.current_folder, "Python Files (*.py);;All Files (*)", options=options)
         if file_path:
            with open(file_path, 'w') as f:
               f.write('print("Hello World")')
            QMessageBox.information(self, "Success", f"File saved at: {file_path}")
            self.populate_file_explorer(self.current_folder)
      else:
         QMessageBox.warning(self, "No Folder Open", "Please open a folder first to create a file.")
   def newfolderevent(self):
      if not self.current_folder:
         QMessageBox.warning(self, "No Folder Open", "Please open a folder first to create a new folder.")
         return
      folder_name, ok = QInputDialog.getText(self, 'New Folder', 'Enter folder name:')
      if ok and folder_name:
         new_folder_path = os.path.join(self.current_folder, folder_name)
         if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            QMessageBox.information(self, "Success",f"Folder '{folder_name}' created!")
            self.populate_file_explorer(self.current_folder)
         else:
            QMessageBox.warning(self, "Error", "This folder already exists.")
               
            
if __name__ == '__main__':
   app = QApplication(sys.argv)
   stylesheet = qdarktheme.load_stylesheet("dark")
   app.setStyleSheet(stylesheet)
   ide = AcronIDE()
   ide.show()
   sys.exit(app.exec_())
   