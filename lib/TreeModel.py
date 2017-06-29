from PyQt5.QtCore import Qt, QAbstractItemModel, QModelIndex
from PyQt5.QtGui import QBrush, QColor
import lxml.etree as ET

from lib.TreeItem import TreeItem

class TreeModel(QAbstractItemModel):
    def __init__(self, path, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(["Fault Number", "Catagory", "Suggested Text", "Literal"])

        self.path = path

        self.isHighlighted = False

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

        if index.column() == 2:
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
        return QBrush(Qt.transparent)
        if self.isHighlighted:
            if item.data(1) != item.data(3):
                return QBrush(QColor(159,87,85))
        if item.depth == 0:
            return QBrush(QColor(157,159,85))
        elif item.depth == 1:
            return QBrush(QColor(85,157,159))
        elif item.depth == 2:
            return QBrush(QColor(85,120,159))
        elif item.depth == 3:
            return QBrush(QColor(87,85,159))
        elif item.depth == 4:
            return QBrush(QColor(120,159,85))

    def setData(self, index, value, role):
        try:
            item = index.internalPointer()

            if index.column() == 3:

                dataPath = item.data(0).split(":")
                element = self.findHW(dataPath)

                element.text = ET.CDATA(value)

                item.setData(value, index.column())

            elif index.column() == 3:
                dataPath = item.data(2).split(".")
                element = self.findPA(dataPath)

                element.text = ET.CDATA(value)

                item.setData(value, index.column())

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

    def highlight(self):
        self.isHighlighted = not self.isHighlighted

    def draw(self):
        for fault in self.faults:
            item = TreeItem([fault['number'], fault['catagory'], fault['text'], fault['literal']], self.rootItem)
            self.rootItem.appendChild(item)

    def fix100(self):
        if not self.fix100Button.isChecked():
            self.treewidget.clear()
            self.textFix100(False)
            self.draw()
            self.colorFix100(False)

        else:
            self.treewidget.clear()
            self.textFix100(True)
            self.draw()
            self.colorFix100(True)

        if self.highlightButton.isChecked():
            self.highlight()
        if self.hideButton.isChecked():
            self.hide()

    def textFix100(self, forwards):
        if forwards:
            self.faults[31]['text'] = self.faults[31]['text'].replace("G6","G5")
            self.faults[32]['text'] = self.faults[32]['text'].replace("G6","G5")
            self.faults[34]['text'] = self.faults[34]['text'].replace("G6","G5")
            self.faults[35]['text'] = self.faults[35]['text'].replace("G6","G4")
            self.faults[40]['text'] = self.faults[40]['text'].replace("G6","G5")
            self.faults[70]['text'] = self.faults[70]['text'].replace("G9","G3")
            self.faults[71]['text'] = self.faults[71]['text'].replace("G9","G3")

        else:
            self.faults[31]['text'] = self.faults[31]['text'].replace("G5","G6")
            self.faults[32]['text'] = self.faults[32]['text'].replace("G5","G6")
            self.faults[34]['text'] = self.faults[34]['text'].replace("G5","G6")
            self.faults[35]['text'] = self.faults[35]['text'].replace("G4","G6")
            self.faults[40]['text'] = self.faults[40]['text'].replace("G5","G6")
            self.faults[70]['text'] = self.faults[70]['text'].replace("G3","G9")
            self.faults[71]['text'] = self.faults[71]['text'].replace("G3","G9")

    def colorFix100(self, color):
        children = []
        root = self.treewidget.invisibleRootItem()
        children.append(root.child(31))
        children.append(root.child(32))
        children.append(root.child(34))
        children.append(root.child(35))
        children.append(root.child(40))
        children.append(root.child(70))
        children.append(root.child(71))

        for child in children:
            if color:
                child.setBackground(2, Qt.green)
            else:
                child.setBackground(2, Qt.white)

    def hide(self):
        if not self.hideButton.isChecked():
            root = self.treewidget.invisibleRootItem()
            count = root.childCount()
            for i in range(count):
                child = root.child(i)
                if child.text(1) == "":
                    child.setHidden(False)
            self.hideButton.setChecked(False)
        else:
            root = self.treewidget.invisibleRootItem()
            count = root.childCount()
            for i in range(count):
                child = root.child(i)
                if child.text(1) == "":
                    child.setHidden(True)
            self.hideButton.setChecked(True)

    def highlight(self):
        if not self.highlightButton.isChecked():
            root = self.treewidget.invisibleRootItem()
            count = root.childCount()

            for i in range(count):
                child = root.child(i)
                child.setBackground(0, Qt.white)

            self.highlightButton.setChecked(False)
        else:
            root = self.treewidget.invisibleRootItem()
            count = root.childCount()
            tmp = [x['number'] for x in self.faults]
            for i in range(count):
                child = root.child(i)
                if tmp.count(child.text(0)) != 1:
                    child.setBackground(0, Qt.red)

            self.highlightButton.setChecked(True)
