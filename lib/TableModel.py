from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QBrush, QColor
import lxml.etree as ET

from lib.TableItem import TableItem
from lib.Fault import Fault

class TableModel(QAbstractTableModel):
    def __init__(self, path, parent=None):
        super(TableModel, self).__init__(parent)

        #header = Fault("Fault Number", "Catagory", "Suggested Text", "Literal")
        #self.rootItem = TreeItem(header)

        self.path = path

        self.highlight = False
        self.fix100 = False

        self.setupModel(path)

    def save(self,path=None):
        if path is None:
            path = self.path

        #self.tree.write(path, encoding='utf-8', standalone=True)

    def rowCount(self, parent):
        return len(self.faults)

    def columnCount(self, parent):
        return 4

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 3:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    """
    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()
    """

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        #elif role != Qt.DisplayRole:
        #    return None

        if index.column() == 0:
            return QVariant(self.faults[index.row()].number)
        if index.column() == 1:
            return QVariant(self.faults[index.row()].catagory)
        if index.column() == 2:
            return QVariant(self.faults[index.row()].text)
        if index.column() == 3:
            return QVariant(self.faults[index.row()].literal)

        """
        item = index.internalPointer()

        if role == Qt.BackgroundRole:
            return self.getColor(item)

        if role == Qt.EditRole:
            return item.data(index.column())

        return item.data(index.column())
        """

    def getColor(self, item):
        if self.highlight:
            numbers = [fault.number for fault in self.faults]
            if numbers.count(item.data(0)) > 1:
                return QBrush(Qt.red)
        if self.fix100:
            numbers = [31,32,34,35,40,70,71]
            if item.row() in numbers:
                return QBrush(Qt.green)

    def setData(self, index, value, role):
        try:
            """
            item = index.internalPointer()

                dataPath = item.data(0).split(":")
                element = self.findHW(dataPath)

                element.text = ET.CDATA(value)

                item.setData(value, index.column())
            """
            return True
        except:
            print("Editing Error.")
            return False

    def setupModel(self, path):
        self.parser = ET.XMLParser(strip_cdata=False, resolve_entities=False)
        self.tree = ET.parse(path, parser=self.parser)
        self.root = self.tree.getroot()
        self.faults = self.getFaults()

    def getFaults(self):
        faults = []

        for program in self.root.iter("Program"):
            for rung in program.iter("Rung"):
                fault = Fault(program, rung)
                if fault.valid: faults.append(fault)

        faults = sorted(faults, key=lambda fault : fault.number)

        faults = self.genEmptyFaults(faults)

        faults = sorted(faults, key=lambda fault : fault.number)

        faults = [self.catagoryFix(fault) for fault in faults]

        faults = [self.numberFix(fault) for fault in faults]

        return faults

    def genEmptyFaults(self, faults):
        emptyfaults = []
        for i in list(range(1000)):
            fault = Fault(i)
            emptyfaults.append(fault)

        duplicates = []
        for fault in faults:
            if emptyfaults[fault.number].catagory == "":
                emptyfaults[fault.number] = fault
            else:
                duplicates.append(fault)

        for fault in duplicates:
            emptyfaults.insert(fault.number, fault)

        return emptyfaults

    def catagoryFix(self, fault):
        if fault.catagory.find("Warning") != -1:
            fault.catagory = "M"
        elif fault.catagory.find("Stop") != -1:
            fault.catagory = "C"
        elif fault.catagory.find("Abort") != -1:
            fault.catagory = "I"
        return fault

    def numberFix(self, fault):
        n = str(fault.number)
        if len(n) == 1:
            fault.number = "Fault_00" + n
        if len(n) == 2:
            fault.number = "Fault_0" + n
        if len(n) == 3:
            fault.number = "Fault_" + n
        if fault.text == "":
            fault.text = fault.number
        return fault

    def highlightToggle(self):
        self.highlight = not self.highlight

    def fix100Toggle(self):
        self.fix100 = not self.fix100

        if self.fix100:
            child = self.rootItem.child(31)
            child.setData(child.data(2).replace("G6","G5"),2)

            child = self.rootItem.child(32)
            child.setData(child.data(2).replace("G6","G5"),2)

            child = self.rootItem.child(34)
            child.setData(child.data(2).replace("G6","G5"),2)

            child = self.rootItem.child(35)
            child.setData(child.data(2).replace("G6","G4"),2)

            child = self.rootItem.child(40)
            child.setData(child.data(2).replace("G6","G5"),2)

            child = self.rootItem.child(70)
            child.setData(child.data(2).replace("G9","G3"),2)

            child = self.rootItem.child(71)
            child.setData(child.data(2).replace("G9","G3"),2)

        else:
            child = self.rootItem.child(31)
            child.setData(child.data(2).replace("G5","G6"),2)

            child = self.rootItem.child(32)
            child.setData(child.data(2).replace("G5","G6"),2)

            child = self.rootItem.child(34)
            child.setData(child.data(2).replace("G5","G6"),2)

            child = self.rootItem.child(35)
            child.setData(child.data(2).replace("G4","G6"),2)

            child = self.rootItem.child(40)
            child.setData(child.data(2).replace("G5","G6"),2)

            child = self.rootItem.child(70)
            child.setData(child.data(2).replace("G3","G9"),2)

            child = self.rootItem.child(71)
            child.setData(child.data(2).replace("G3","G9"),2)
