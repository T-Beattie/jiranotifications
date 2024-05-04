from PySide import QtGui, QtCore
import webbrowser
import jira_backend

class TicketUI(QtGui.QFrame):

    def __init__(self, issue, list_widget, incoming_tickets, index):
        QtGui.QFrame.__init__(self)
        self.issue = issue
        self.list_widget = list_widget
        self.incoming_tickets = incoming_tickets
        self.index = index

        self.setup_ui()

    def setup_ui(self):
        self.grid_layout = QtGui.QGridLayout(self)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setHorizontalSpacing(5)
        self.grid_layout.setVerticalSpacing(2)
        self.setStyleSheet("background-color:#b6b9e0; border-radius:50px;")

        summary = QtGui.QLabel(self.issue.summary)
        summary.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        summary.setWordWrap(True)
        key = QtGui.QLabel(self.issue.key)
        key.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        creator = QtGui.QLabel(self.issue.creator['displayName'])
        creator.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        go_to_btn = QtGui.QPushButton('Go to issue')
        go_to_btn.clicked.connect(self.go_to_link)

        close_ticket = QtGui.QPushButton('X')
        close_ticket.setMaximumWidth(30)
        close_ticket.setMinimumHeight(30)
        close_ticket.clicked.connect(self.close_me)

        self.grid_layout.addWidget(key, 0, 0, 1, 2)
        self.grid_layout.addWidget(summary, 1, 0, 1, 4)
        self.grid_layout.addWidget(creator, 0, 2, 1, 2)
        self.grid_layout.addWidget(go_to_btn, 2,0,1,4)

        self.grid_layout.addWidget(close_ticket, 0, 4,1,1)

        self.setLayout(self.grid_layout)
    
    def go_to_link(self):
        goto_link = '{0}/browse/{1}'.format(jira_backend.BASE_URL ,self.issue.key)
        webbrowser.open(goto_link, new=2)

    def close_me(self):
        self.list_widget.takeItem(self.list_widget.currentRow())
        self.incoming_tickets.pop(self.index)