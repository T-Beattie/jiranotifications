from win10toast import ToastNotifier
import datetime
import 2
import webbrowser
import jira_backend
import thread
import json
import os

from tickets_window import TicketUI

import sys
from PySide.QtCore import *
from PySide.QtGui import *


class App(QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setWindowTitle("Jira Notifications")
        self.settings_dict = {}

        self.load_settings()

        self.list_widget = QListWidget()
        self.tray = QSystemTrayIcon()
        self.toaster = ToastNotifier()
        self.start_btn = None
        self.stop_btn = None


        self.issues = []  
        self.incoming_tickets = []   

        self.my_thread = thread.start_new_thread(self.poll, ())

        self.setup_system_tray()
        self.setup_ui()
        self.setup_tickets()

        self.show()

    def setup_system_tray(self):
        icon = QIcon("JN.png")
        menu = QMenu()
        exitAction = menu.addAction("exit")
        exitAction.triggered.connect(sys.exit)

        self.tray.setIcon(icon)
        self.tray.setContextMenu(menu)   
        # Restore the window when the tray icon is double clicked.
        self.tray.activated.connect(self.restore_window) 
        self.tray.show()

    def setup_ui(self):
        self.setWindowIcon(QIcon('JN.png'))
        self.setMinimumWidth(600)

        centralWidget = QWidget(self)      
        layout = QVBoxLayout()    

        self.setCentralWidget(centralWidget) 

        self.info_label = QLabel('You can minimize this tool to the system tray and it will keep running in the background')
        self.info_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)

        h_widget = QWidget()
        h_layout = QHBoxLayout()

        self.start_btn = QPushButton('Start')
        self.start_btn.clicked.connect(self.start_polling)
        self.stop_btn = QPushButton('Stop')
        self.stop_btn.clicked.connect(self.stop_polling)
        self.stop_btn.setEnabled(False)

        h_layout.addWidget(self.start_btn)
        h_layout.addWidget(self.stop_btn)

        h_widget.setLayout(h_layout)

        layout.addWidget(self.info_label)
        # layout.addWidget(h_widget)

        self.list_widget.setStyleSheet("QListWidget::item { margin: 3px; }")  
        layout.addWidget(self.list_widget)  
           
        centralWidget.setLayout(layout)

    def start_polling(self):
        self.my_thread = thread.start_new_thread(self.poll, ())
        self.stop_btn.setEnabled(True)
        self.start_btn.setEnabled(False)

    def stop_polling(self):
        self.stop_btn.setEnabled(False)
        self.start_btn.setEnabled(True)

    def setup_tickets(self):
        self.list_widget.clear()
        index = 0
        for ticket in self.incoming_tickets:
            my_ticket_ui = TicketUI(ticket, self.list_widget, self.incoming_tickets,index)
            my_item = QListWidgetItem(self.list_widget)
            my_item.setSizeHint(QSize( 200, 100))

            self.list_widget.addItem(my_item)
            self.list_widget.setItemWidget(my_item, my_ticket_ui)
            index += 1

    def get_tickets_while_closed(self):
        tickets = jira_backend.get_issues_between_times(self.settings['last_run_time'])

    def save_settings(self):

        self.settings_dict['last_run_time'] = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%m/%d/%Y, %H:%M:%S")

        with open('settings.json', 'w') as outfile:
            json.dump(self.settings_dict, outfile)

    def load_settings(self):
        my_dir = os.path.dirname(os.path.realpath(__file__))
        if os.path.exists('{0}/{1}'.format(my_dir, 'settings.json')):
            with open('settings.json') as json_file:
                self.settings = json.load(json_file)

    def event(self, event):
        if (event.type() == QEvent.WindowStateChange and 
                self.isMinimized()):
            # The window is already minimized at this point.  AFAIK,
            # there is no hook stop a minimize event. Instead,
            # removing the Qt.Tool flag should remove the window
            # from the taskbar.
            self.setWindowFlags(self.windowFlags() & ~Qt.Tool)
            self.tray.show()
            return True
        else:
            return super(App, self).event(event)

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            'Stop Jira Notification Tool',"Are you sure to stop the tool? You will no longer receive notifications",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.save_settings()
            event.accept()
        else:
            self.tray.show()
            self.hide()
            event.ignore()

    def restore_window(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.tray.hide()
            # self.showNormal will restore the window even if it was
            # minimized.
            self.showNormal()

            self.setup_tickets()

    def poll(self):
        polling.poll(
            lambda: self.get_issues,
            step=60,
            check_success=self.is_correct_response,
            poll_forever=True,
        )
    
    def is_correct_response(self, response):
        """Check that the response returned 'success'"""
        print 'polling'
        self.display_toast()

    def get_issues(self):
        print 'test'
        return True

    def run(self):
        # Enter Qt application main loop        
        sys.exit(self.app.exec_())

    def display_toast(self):
        self.issues = jira_backend.get_new_issues()
        for issue in self.issues:
            my_issue = Issue(issue)
            goto_link = '{0}/browse/{1}'.format(jira_backend.BASE_URL,my_issue.key)
             # Show notification whenever needed
            self.incoming_tickets.append(my_issue)
            self.toaster.show_toast(
                "{0} created by {1}".format(my_issue.issue_type['name'], my_issue.creator['displayName']), 
                "{key} - {description}".format(key=my_issue.key, description=my_issue.summary), 
                threaded=True,
                icon_path="jn.ico",
                callback_on_click=lambda: webbrowser.open(goto_link, new=2)
            )  # 3 seconds


class Issue(object):

    def __init__(self, issue_dict):
        object.__init__(self)

        self.id = issue_dict['id']
        self.key = issue_dict['key']
        self.me = issue_dict['self']
        self.created = issue_dict['fields']['created']
        self.creator = issue_dict['fields']['creator']
        self.creator = issue_dict['fields']['creator']
        self.project = issue_dict['fields']['project']
        self.status = issue_dict['fields']['status']
        self.summary = issue_dict['fields']['summary']
        self.issue_type = issue_dict['fields']['issuetype']
        self.goto_link = '{0}/browse/{1}'.format(jira_backend.BASE_URL, self.key)

        self.issue_dict = issue_dict



if __name__ == "__main__":
    application = QApplication(sys.argv)
    application.setApplicationName("App Name")
    application.setApplicationVersion("1.1.1.1.1")
    application.setOrganizationName("dev name")

    win = App()
    sys.exit(application.exec_())