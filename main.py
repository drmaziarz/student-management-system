import sqlite3
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton, QMainWindow, \
    QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QGridLayout, QLabel, \
    QMessageBox


class DatabaseConnection:
    """
    A class for connecting to a SQLite database.

    This class provides a simple way to connect to a SQLite database file. The default filename for the database file
    is 'database.db', but you can specify a different filename when creating an instance of the class.

    Attributes:
        database_file (str): The filename of the SQLite database file to connect to.

    Methods:
        connect(): Creates a connection to the SQLite database file and returns the connection object.
    """

    def __init__(self, database_file="database.db"):
        """
        Initializes a new instance of the DatabaseConnection class.

        Args:
            database_file (str): The filename of the SQLite database file to connect to. Defaults to 'database.db'.
        """
        self.database_file = database_file

    def connect(self):
        """
        Creates a connection to the SQLite database file and returns the connection object.

        Returns:
            sqlite3.Connection: A connection object that can be used to execute SQLite commands on the database.
        """
        connection = sqlite3.connect(self.database_file)
        return connection


class MainWindow(QMainWindow):
    """
    This class defines the main window for a student management system. The window contains a menu bar with options for
    adding, editing, and searching for student records. It also contains a table that displays the student data in rows
    and columns. Users can select a cell in the table to edit or delete a record, and a status bar at the bottom of the
    window displays buttons for editing or deleting the selected record.
    """

    def __init__(self):
        """
        Initialize the main window with a title, size, and menu bar options. Creates a table with four columns and sets
        it as the central widget. Creates a toolbar with buttons for adding and searching for records. Also creates a
        status bar.
        """
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(500, 400)

        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student_action = QAction(QIcon('icons/add.png'), "Add Student", self)
        file_menu_item.addAction(add_student_action)
        add_student_action.triggered.connect(self.insert)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon('icons/search.png'), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        # Create status bar and ass status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        """Display buttons for editing or deleting a selected record in the status bar."""

        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        """Load the student data into the table from a database."""
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        """Open a dialog for inserting a new student record."""
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        """Open a dialog for searching for a student record."""
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        """Open a dialog for editing a selected student record."""
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        """Open a dialog for deleting a selected student record."""
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        """Open a dialog with information about the student management system."""
        dialog = AboutDialog()
        dialog.exec()


class InsertDialog(QDialog):
    """
        A dialog window for inserting new student data.

    The InsertDialog class allows users to add new student data to the application
    by entering the student's name, course, and mobile number. Once the user has
    entered the required information and clicked the Submit button, the new student
    record is added to the database and the main window is updated to show the new
    data.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        """Insert the new student data into the database and update the main window."""
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()


def no_result_found():
    """Display a message box when no search results were found."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setWindowTitle("No Results Found")
    msg_box.setText("No search results were found.")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.exec()


class SearchDialog(QDialog):
    """
    A dialog window to search for a student by name.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student Records")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        """
        Search for a student with the name entered in the student_name widget.

        Query the database for all students with the given name, and select
        the corresponding row(s) in the main window's QTableWidget. Close the
        dialog window after the search is complete.
        """
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = cursor.fetchall()
        if not rows:
            no_result_found()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()
        self.close()


class EditDialog(QDialog):
    """
    A dialog box for editing student data.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = main_window.table.currentRow()

        # Get od from selected row
        self.student_id = main_window.table.item(index, 0).text()

        student_name = main_window.table.item(index, 1).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        """Update the student data in the database"""
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        student_id = self.student_id

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (name, course, mobile, student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()


class DeleteDialog(QDialog):
    """A dialog window for deleting a student record from the database"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close)

    def delete_student(self):
        """Delete the selected student record from the database and update the main window table."""
        index = main_window.table.currentRow()
        # Get selected row index and student id
        student_id = main_window.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class AboutDialog(QMessageBox):
    """A dialog window that displays information about the application."""

    def __init__(self):
        """Initializes an instance of the AboutDialog class.

        The dialog window displays information about the application, including its version and release date."""
        super().__init__()

        self.setWindowTitle("About")
        self.setIcon(QMessageBox.Icon.Information)
        self.StandardButton(QMessageBox.StandardButton.Ok)
        content = """
        This app was created using PyQt6 library.
        Verion 1.0
        Released 01.04.2023
        """
        self.setText(content)


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
