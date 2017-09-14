from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from PyQt5.QtGui import QBrush, QColor

import csv
import lxml.etree as ET
import codecs
import os

from lib.Fault import Fault

class TableModel(QAbstractTableModel):
    def __init__(self, path, parent=None):
        super(TableModel, self).__init__(parent)

        self.highlight = False
        self.check = False
        self.fix100 = False

        self.path = path
        self.parser = ET.XMLParser(strip_cdata=False, resolve_entities=False)
        self.tree = ET.parse(path, parser=self.parser)
        self.root = self.tree.getroot()
        self.faults = self.getFaults()

    def headerData(self, column, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if   column == 0: return QVariant("Fault Number")
            elif column == 1: return QVariant("Catagory")
            elif column == 2: return QVariant("Suggested Text")
            elif column == 3: return QVariant("Literal")

        return QVariant()

    def rowCount(self, parent):
        return len(self.faults)

    def columnCount(self, parent):
        return 4

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() == 3 or index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        if role == Qt.BackgroundRole:
            return self.getColor(index)

        if role == Qt.EditRole:
            if index.column() == 0:
                return self.faults[index.row()].number
            elif index.column() == 3:
                return self.faults[index.row()].literal

        if role != Qt.DisplayRole:
            return None

        if index.column() == 0:
            return QVariant(self.faults[index.row()].number)
        if index.column() == 1:
            return QVariant(self.faults[index.row()].catagory)
        if index.column() == 2:
            return QVariant(self.faults[index.row()].text)
        if index.column() == 3:
            return QVariant(self.faults[index.row()].literal)

        return QVariant()

    def getColor(self, index):
        if self.highlight:
            numbers = [fault.number for fault in self.faults]
            if numbers.count(self.faults[index.row()].number) > 1:
                return QBrush(Qt.red)
        if self.fix100:
            numbers = [31,32,34,35,40,70,71]
            if index.row() in numbers:
                return QBrush(Qt.green)
        if self.check:
            numbers = [6,7,11,12,13,14,24,28,31,32,34,40,70,71]
            if index.row() in numbers:
                return QBrush(Qt.yellow)

    def setData(self, index, value, role):
        try:
            if index.column() == 0:
                self.faults[index.row()].giveNumber(value)
                self.faults = self.remEmptyFaults(self.faults)
                self.faults = self.genEmptyFaults(self.faults)
                self.faults = sorted(self.faults, key = lambda fault : fault.number)  

            elif index.column() == 3:
                self.faults[index.row()].giveLiteral(value)
            return True
        except:
            print("Editing Error.")
            return False

    def save(self,path=None):
        if path is None:
            path = self.path

        self.tree.write(path+'utf-8', encoding='utf-8', standalone=True)

        with codecs.open(path+'utf-8', 'r', 'utf-8') as sourceFile:
            with codecs.open(path, 'w', 'utf-8-sig') as targetFile:
                contents = sourceFile.read()
                contents = contents.replace("\n", "\r\n")
                targetFile.write(contents)

        os.remove(path+'utf-8')

    def export(self, path):
        with open(path+'.csv', 'w', newline = '') as csvFile:
            writer = csv.writer(csvFile)
            for fault in self.faults:
                writer.writerow([fault.number, fault.catagory, fault.text, fault.literal])

    def getFaults(self):
        faults = []

        for program in self.root.iter("Program"):
            for rung in program.iter("Rung"):
                fault = Fault(program, rung)
                if fault.valid: faults.append(fault)
        
        faults = self.genEmptyFaults(faults)

        return faults

    def genEmptyFaults(self, faults):
        emptyfaults = []
        for i in list(range(1000)):
            fault = Fault(i)
            emptyfaults.append(fault)

        duplicates = []
        for fault in faults:
            if emptyfaults[fault.index].catagory == "":
                emptyfaults[fault.index] = fault
            else:
                duplicates.append(fault)

        for fault in duplicates:
            emptyfaults.insert(fault.index, fault)

        return emptyfaults

    def remEmptyFaults(self, faults):
        faultsToBeRemoved = []
        for fault in faults:
            if fault.catagory == "":
                faultsToBeRemoved.append(fault)

        for fault in faultsToBeRemoved:
            faults.remove(fault)

        return faults

    def highlightToggle(self):
        self.highlight = not self.highlight

    def checkToggle(self):
        self.check = not self.check

    def fix100Toggle(self):
        self.fix100 = not self.fix100

        if self.fix100:
            fault = self.faults[31]
            fault.text = fault.text.replace("G6", "G5")

            fault = self.faults[32]
            fault.text = fault.text.replace("G6", "G5")

            fault = self.faults[34]
            fault.text = fault.text.replace("G6", "G5")

            fault = self.faults[35]
            fault.text = fault.text.replace("G6", "G4")

            fault = self.faults[40]
            fault.text = fault.text.replace("G6", "G5")

            fault = self.faults[70]
            fault.text = fault.text.replace("G9", "G3")

            fault = self.faults[71]
            fault.text = fault.text.replace("G9", "G3")

        else:
            fault = self.faults[31]
            fault.text = fault.text.replace("G5", "G6")

            fault = self.faults[32]
            fault.text = fault.text.replace("G5", "G6")

            fault = self.faults[34]
            fault.text = fault.text.replace("G5", "G6")

            fault = self.faults[35]
            fault.text = fault.text.replace("G4", "G6")

            fault = self.faults[40]
            fault.text = fault.text.replace("G5", "G6")

            fault = self.faults[70]
            fault.text = fault.text.replace("G3", "G9")

            fault = self.faults[71]
            fault.text = fault.text.replace("G3", "G9")
