from PyQt5.QtWidgets import QTableWidgetItem


class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        return int(self.text()) < int(other.text())
