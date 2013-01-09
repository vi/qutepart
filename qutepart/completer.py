"""Autocompletion widget and logic
"""

from PyQt4.QtCore import QAbstractItemModel, QModelIndex, QObject, QSize, Qt
from PyQt4.QtGui import QListView, QStyle, QStyledItemDelegate

from qutepart.htmldelegate import HTMLDelegate


class _CompletionModel(QAbstractItemModel):
    """QAbstractItemModel implementation for a list of completion variants
    """
    def __init__(self):
        QAbstractItemModel.__init__(self)

    def flags(self, index):
        """QAbstractItemModel method implementation
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def data(self, index, role):
        """QAbstractItemModel method implementation
        """
        if role == Qt.DisplayRole:
            text = "test data"
            typed = text[:6]
            notTyped = text[6:]
            return '<html><b>%s</b>%s</html>' % (typed, notTyped)
        else:
            return None
        
    def headerData(self, index):
        """QAbstractItemModel method implementation
        """
        return "the header"
    
    def rowCount(self, index):
        """QAbstractItemModel method implementation
        """
        return 7
    
    def columnCount(self, index):
        """QAbstractItemModel method implementation
        """
        return 1
    
    def index(self, row, column, parent = QModelIndex()):
        """QAbstractItemModel method implementation
        """
        return self.createIndex(row, column)
    
    def parent(self, index):
        """QAbstractItemModel method implementation
        """
        return QModelIndex()


class _ListView(QListView):
    """Completion list widget
    """
    def __init__(self, qpart, model):
        QListView.__init__(self, qpart.viewport())
        self.setItemDelegate(HTMLDelegate(self))
        
        qpart.setFocus()
        
        self._qpart = qpart
        self.setModel(model)
        
        qpart.cursorPositionChanged.connect(self._onCursorPositionChanged)
    
    def __del__(self):
        """Without this empty destructor Qt prints strange trace
            QObject::startTimer: QTimer can only be used with threads started with QThread
        when exiting
        """
        pass
    
    def _onCursorPositionChanged(self):
        """Cursor position changed. Update completion widget position
        """
        self.move(self._qpart.cursorRect().bottomRight())
    
    def sizeHint(self):
        """QWidget.sizeHint implementation
        Automatically resizes the widget according to rows count
        """
        width = super(_ListView, self).sizeHint().width()
        
        # drawn with scrollbar without +2. I don't know why
        height = self.sizeHintForRow(0) * self.model().rowCount(QModelIndex()) + 2
        
        return QSize(width, height)


class Completer(QObject):
    """Object listens Qutepart widget events, computes and shows autocompletion lists
    """
    def __init__(self, qpart):
        self._qpart = qpart
        
        self._widget = _ListView(qpart, _CompletionModel())
        self._widget.show()
