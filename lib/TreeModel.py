from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QBrush, QColor
import lxml.etree as ET

from lib.TreeItem import TreeItem

class TreeModel(QAbstractItemModel):
    def __init__(self, path, parent=None):
        super(TreeModel, self).__init__(parent)

        header ={"number"   : "Fault Number",
                 "catagory" : "Catagory",
                 "text"     : "Suggested Text",
                 "literal"  : "Literal"}
        self.rootItem = TreeItem(header)

        self.path = path

        self.highlight = False
        self.fix100 = False

        self.setupModel(path)

    def save(self,path=None):
        if path is None:
            path = self.path

        #self.tree.write(path, encoding='utf-8', standalone=True)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 3:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

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

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.BackgroundRole:
            return self.getColor(item)

        if role == Qt.EditRole:
            return item.data(index.column())

        if role != Qt.DisplayRole:
            return None

        return item.data(index.column())

    def getColor(self, item):
        if self.highlight:
            numbers = [fault['number'] for fault in self.faults]
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
        self.getFaults()
        self.draw()

    def getFaults(self):
        self.faults = []

        for program in self.root.iter("Program"):
            for rung in program.iter("Rung"):
                fault = self.getFault(program, rung)
                if fault: self.faults.append(fault)

        self.faults = sorted(self.faults, key=lambda fault : fault['number'])

        self.faults = self.genEmptyFaults(self.faults)

        self.faults = sorted(self.faults, key=lambda fault : fault['number'])

        self.faults = [self.catagoryFix(fault) for fault in self.faults]

        self.faults = [self.numberFix(fault) for fault in self.faults]

    def getFault(self, program, rung):
        fault = {   'number'    : "",
                    'catagory'  : "",
                    'text'      : "",
                    'literal'   : ""}

        textElement = str(rung.findall("Text")[0].text)

        f = textElement.find("AOI_Fault_Set_Reset")
        if f == -1:
            return False

        textElement = textElement[f:]
        p = textElement.find(')')
        textElement = textElement[:p].split(',')[2:4]
        fault['number'] = int(textElement[0])
        fault['catagory'] = textElement[1]

        fault.update(self.getFaultComment(program, rung))

        return fault

    def getFaultComment(self, program, rung):

        comment = {}

        literal = rung.findall("Comment")

        if literal:
            literal = literal[0].text
            comment['literal'] = literal.split('\n')[2]

            if len(comment['literal'].split(':')) == 2:
                comment['text'] = comment['literal'].split(':')[1]
            elif len(comment['literal'].split(':')) == 3:
                comment['text'] = comment['literal'].split(':')[1] + comment['literal'].split(':')[2]

            name = program.attrib['Name'].split("_")[1]
            mtn = name[:3]
            stn = name[3:]
            if stn == "":
                stn = "G3"
            if mtn[0] == '5':
                loop = "07"
            elif mtn[0] == '6':
                loop = "08"
            elif mtn[0] == '7':
                loop = "09"
            else:
                loop = "10"

            try:
                f = comment['text'][1:].find(" ") + 1

                sensor = comment['text'][1:f]

                comment['text'] = comment['text'][f:]

                comment['text'] = loop + mtn + "_" + stn + "_" + sensor + ":" + comment['text']
            except:
                comment['text'] = "ERROR: NOT CORRECT FORMAT"

        return comment

    def genEmptyFaults(self, faults):
        emptyfaults = []
        for i in list(range(1000)):
            fault = {   'number'    : i,
                        'catagory'  : "",
                        'text'      : "",
                        'literal'   : ""}

            emptyfaults.append(fault)

        duplicates = []
        for fault in faults:
            if emptyfaults[fault['number']]['catagory'] == "":
                emptyfaults[fault['number']] = fault
            else:
                duplicates.append(fault)

        for fault in duplicates:
            emptyfaults.insert(fault['number'], fault)

        return emptyfaults

    def catagoryFix(self, fault):
        if fault['catagory'].find("Warning") != -1:
            fault['catagory'] = "M"
        elif fault['catagory'].find("Stop") != -1:
            fault['catagory'] = "C"
        elif fault['catagory'].find("Abort") != -1:
            fault['catagory'] = "I"
        return fault

    def numberFix(self, fault):
        n = str(fault['number'])
        if len(n) == 1:
            fault['number'] = "Fault_00" + n
        if len(n) == 2:
            fault['number'] = "Fault_0" + n
        if len(n) == 3:
            fault['number'] = "Fault_" + n
        if fault['text'] == "":
            fault['text'] = fault['number']
        return fault

    def highlightToggle(self):
        self.highlight = not self.highlight

    def draw(self):
        for fault in self.faults:
            item = TreeItem(fault, self.rootItem)
            self.rootItem.appendChild(item)

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
