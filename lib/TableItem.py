class TableItem(object):
    def __init__(self, fault, parent=None):
        self.parentItem = parent
        self.childItems = []

        self.fault = fault

        self.itemData = (fault.number,
                         fault.catagory,
                         fault.text,
                         fault.literal)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def setData(self, data, column):
        tmp = list(self.itemData)
        if tmp[column] != data:
            tmp[column] = data
            self.itemData = tuple(tmp)

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

    def getFault(self):
        return self.fault
