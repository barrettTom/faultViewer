from PyQt5.QtCore import QSortFilterProxyModel

class Filter(QSortFilterProxyModel):
    def filterAcceptsRow(self, sourceRow, sourceParent):
        left = self.sourceModel().index(sourceRow, 0, sourceParent).data(0)
        right= self.sourceModel().index(sourceRow, 2, sourceParent).data(0)
        if left == right:
            return False
        else:
            return True
