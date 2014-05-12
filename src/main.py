"""
Main module 
"""

import sys
from PyQt4 import QtGui
from gui import ImageWin

def main():
    app = QtGui.QApplication(sys.argv)
    window = ImageWin()
    window.setMouseTracking(True)
    window.setWindowTitle('Livewire Demo')
    window.show()
    window.setFixedSize(window.size())
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()    
