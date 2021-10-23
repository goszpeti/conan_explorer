from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QDir
import os
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import conan_app_launcher as this

class SandBoxItemModel(QStandardItemModel):

    def __init__(self, parent):
        super().__init__(parent)
        self.rootItem = self.invisibleRootItem()
        self.dirIcon =  parent.style().standardIcon(QtWidgets.QStyle.SP_DirIcon)
        self.fileIcon = parent.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)


    def setSandBoxDetails(self):
        names = [r"C:\Users\goszp\.conan\data\example", r"C:\Users\goszp\.conan\data\hedley"]
        self.populateSandBoxes(names)
    
    def populateSandBoxes(self, names):
        for name in names:
            parent = QStandardItem(self.dirIcon, name)
            parent.setAccessibleDescription(name)
            self.rootItem.appendRow(parent)
            self.createDirectoryItem(name, parent)
  
    def createDirectoryItem(self, dirName, parentItem):
        dir = QDir(dirName)
        subFolders = dir.entryInfoList(QDir.Dirs | QDir.Files | QDir.NoDotAndDotDot)
        for folderName in subFolders:
            if folderName.isFile():
                child = QStandardItem(self.fileIcon, folderName.fileName())
                child.setAccessibleDescription(folderName.filePath())
            else:
                child = QStandardItem(self.dirIcon, folderName.fileName())
                child.setAccessibleDescription(folderName.filePath())
            parentItem.appendRow(child)
            self.createDirectoryItem(folderName.filePath(), child)
