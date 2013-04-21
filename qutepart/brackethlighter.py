"""Bracket highlighter.
Calculates list of QTextEdit.ExtraSelection
"""

import time

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTextCursor, QTextEdit


class BracketHighlighter:
    """Bracket highliter.
    Calculates list of QTextEdit.ExtraSelection
    
    Currently, this class might be just a set of functions.
    Probably, it will contain instance specific selection colors later
    """
    _MAX_SEARCH_TIME_SEC = 0.02
    
    _START_BRACKETS = '({['
    _END_BRACKETS = ')}]'
    _ALL_BRACKETS = _START_BRACKETS + _END_BRACKETS
    _OPOSITE_BRACKET = dict( (bracket, oposite)
                    for (bracket, oposite) in zip(_START_BRACKETS + _END_BRACKETS, _END_BRACKETS + _START_BRACKETS))
    
    def _iterateDocumentCharsForward(self, block, startcolumn):
        """Traverse document forward. Yield (block, column, char)
        Raise UserWarning if time is over
        """
        # Chars in the start line
        endTime = time.clock() + self._MAX_SEARCH_TIME_SEC
        for column, char in list(enumerate(block.text()))[startcolumn:]:
            yield block, column, char
        block = block.next()
        
        # Next lines
        while block.isValid():
            for column, char in enumerate(block.text()):
                yield block, column, char
            
            if time.clock() > endTime:
                raise UserWarning('Time is over')
            
            block = block.next()
    
    def _iterateDocumentCharsBackward(self, block, startcolumn):
        """Traverse document forward. Yield (block, column, char)
        Raise UserWarning if time is over
        """
        # Chars in the start line
        endTime = time.clock() + self._MAX_SEARCH_TIME_SEC
        for column, char in reversed(list(enumerate(block.text()[:startcolumn]))):
            yield block, column, char
        block = block.previous()
        
        # Next lines
        while block.isValid():
            for column, char in reversed(list(enumerate(block.text()))):
                yield block, column, char
            
            if time.clock() > endTime:
                raise UserWarning('Time is over')
            
            block = block.previous()
    
    def _findMatchingBracket(self, bracket, block, column):
        """Find matching bracket for the bracket.
        Return (block, column) or (None, None)
        Raise UserWarning, if time is over
        TODO improve this method sometimes for skipping strings and comments
        """
        if bracket in self._START_BRACKETS:
            charsGenerator = self._iterateDocumentCharsForward(block, column + 1)
        else:
            charsGenerator = self._iterateDocumentCharsBackward(block, column)

        depth = 1
        oposite = self._OPOSITE_BRACKET[bracket]
        for block, column, char in charsGenerator:
            if char == oposite:
                depth -= 1
                if depth == 0:
                    return block, column
            elif char == bracket:
                depth += 1
        else:
            return None, None
    
    def _makeMatchSelection(self, block, column, matched):
        """Make matched or unmatched QTextEdit.ExtraSelection
        """
        selection = QTextEdit.ExtraSelection()

        if matched:
            bgColor = Qt.green
        else:
            bgColor = Qt.red
        
        selection.format.setBackground(bgColor)
        selection.cursor = QTextCursor(block)
        selection.cursor.setPositionInBlock(column)
        selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
        
        return selection

    def _highlightBracket(self, bracket, block, column):
        """Highlight bracket and matching bracket
        Return (list of QTextEdit.ExtraSelection's,
                    (highlightedBracketStartBlock,
                     highlightedBracketEndBlock,
                     highlightedColumn))
        or ([], None, None, None)
        """
        try:
            matchedBlock, matchedColumn = self._findMatchingBracket(bracket, block, column)
        except UserWarning:  # not found, time is over
            return [], None  # highlight nothing
        
        if matchedBlock is not None:
            if block.blockNumber() < matchedBlock.blockNumber():
                startBlock = block
                endBlock = matchedBlock
            else:
                endBlock = block
                startBlock = matchedBlock
            return [self._makeMatchSelection(block, column, True),
                    self._makeMatchSelection(matchedBlock, matchedColumn, True)], \
                        (startBlock, endBlock, matchedColumn)
        else:
            return [self._makeMatchSelection(block, column, False)], None
    
    def extraSelectionsAndHighlightedBrackets(self, block, column):
        """List of QTextEdit.ExtraSelection's, which highlighte brackets
        """
        blockText = block.text()
        
        if column > 0 and blockText[column - 1] in self._ALL_BRACKETS:
            return self._highlightBracket(blockText[column - 1], block, column - 1)
        elif column < len(blockText) and blockText[column] in self._ALL_BRACKETS:
            return self._highlightBracket(blockText[column], block, column)
        else:
            return [], None
