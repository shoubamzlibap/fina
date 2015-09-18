#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
from PySide.QtGui import QApplication, QWidget, QIcon, QLabel, QToolTip, QFont
from PySide.QtGui import QPushButton, QMessageBox

class FinaWindow(QWidget):
    """ 
    Our main window class
    """
    # Constructor function
    def __init__(self, app):
        QWidget.__init__(self)
        #QToolTip.setFont(QFont("Decorative", 8, QFont.Condensed))
        self.app = app
        self.setWindowTitle('Finanz Analyse')
        self.setToolTip('Hauptfenster')
        # x,y,w,h
        self.setGeometry(300, 300, 300, 140)
        self.icon_file = 'face-kiss.png'
        appIcon = QIcon(self.icon_file)
        self.setWindowIcon(appIcon)
        # Buttons
        self.set_button(title='Daten hinzufuegen', position=(50,10), action=self.add_data)
        self.set_button(title='Transaktionen gruppieren', position=(50,40),
            action=self.group_transactions)
        self.set_button(title='Transaktionen auswerten', position=(50,70),
            action=self.analyze_transactions)
        self.set_button(title='Schliessen', position=(50,100), action=self.quit_app)

    def quit_app(self):
        """ Function to confirm a message from the user
        """
        userInfo = QMessageBox.question(self, 'Bestätigung',
        'Das Programm wird geschlossen. Willst Du das wirklich?',
        QMessageBox.Yes | QMessageBox.No)
        if userInfo == QMessageBox.Yes:
            self.app.quit()
        if userInfo == QMessageBox.No:
            pass

    def set_button(self, title='', position=(), action=None):
        """
        Set a generic button

        title: str, title of the butten
        position: tuple, position of the button
        action: a callable that should be executed uppon button push

        """
        myButton = QPushButton(title, self)
        myButton.move(position[0], position[1])
        myButton.clicked.connect(action)

    def add_data(self):
        print('Adding data')

    def group_transactions(self):
        print('Grouping transactions')

    def analyze_transactions(self):
        print('Analyzing data')

    def show(self):
        """
        A workaround for the issue that show() itself is not enough
        to show the window - somehow it needs the repaint.
        Need to sort this out
        """
        super(FinaWindow, self).show()
        self.repaint()

if __name__ == '__main__':
    # Exception Handling
    try:
        myApp = QApplication(sys.argv)
        myWindow = FinaWindow(myApp)
        myWindow.show()
        myApp.exec_()
        sys.exit(0)
    except NameError:
        print("Name Error:", sys.exc_info()[1])
    except SystemExit:
        print("Closing Window...")
    except Exception:
        print (sys.exc_info()[1])
