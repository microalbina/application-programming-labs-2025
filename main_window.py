import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, 
    QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QMessageBox, QTableWidget, QTableWidgetItem,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from main import FilePathIterator


class AudioPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.iterator = None
        
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)
        
        self.create_ui()
    

    def create_ui(self):
        """
        Пользовательский интерфейс.
        """

        self.resize(960, 640)
        self.setWindowTitle('Audioplayer')
            
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
            
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
            
        self.file_label = QLabel("Select the .csv file")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        left_layout.addWidget(self.file_label)
            
        self.csv_btn = QPushButton('.csv file')
        self.csv_btn.setMinimumHeight(50)
        self.csv_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #45a29e;
            }
            QPushButton:hover {
                background-color: #1f2833;
            }
        """)
        self.csv_btn.clicked.connect(self.select_csv_file)
        left_layout.addWidget(self.csv_btn)
            
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.table)
            
        self.btns = QWidget()
        btns_layout = QHBoxLayout(self.btns)
            
        self.play_btn = QPushButton('Play')
        self.play_btn.clicked.connect(self.play_file)
        self.play_btn.setEnabled(False)
            
        self.next_btn = QPushButton('Next')
        self.next_btn.clicked.connect(self.next_audio)
        self.next_btn.setEnabled(False)
            
        btns_layout.addWidget(self.play_btn)
        btns_layout.addWidget(self.next_btn)
            
        left_layout.addWidget(self.btns)
            

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
            
        self.current_track_label = QLabel("The track has not been selected yet")
        self.current_track_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_track_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            
        self.duration_label = QLabel("Duration: --:--")
        self.duration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        player_controls = QWidget()
        player_layout = QHBoxLayout(player_controls)
            
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.resume_btn = QPushButton("Resume")
        self.resume_btn.setEnabled(False)
            
        self.pause_btn.clicked.connect(self.player.pause)
        self.resume_btn.clicked.connect(self.player.play)
            
        player_layout.addWidget(self.pause_btn)
        player_layout.addWidget(self.resume_btn)
            
        right_layout.addStretch()
        right_layout.addWidget(self.current_track_label)
        right_layout.addWidget(self.duration_label)
        right_layout.addWidget(player_controls)
        right_layout.addStretch()

        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 1)
            
        self.player.durationChanged.connect(self.update_duration)
    

    def select_csv_file(self):
        """
        Выбор .csv файла с помощью диалогового окна.
        """

        file = QFileDialog.getOpenFileName(
            self,
            'Select the .csv file',
            '',
            '*.csv'
        )
        
        if file:
            self.load_files(file[0])
    

    def load_files(self, path: str):
        """
        Создание таблицы.
        """

        if not os.path.exists(path):
            QMessageBox.warning(self, "Error", f"This path doesn't exist: {path}")
            return
        
        self.iterator = FilePathIterator(annotation=path)
        self.file_label.setText(f".csv file: {os.path.basename(path)}")
            
        self.setup_table()
            
        self.iterator.index = 0
        self.table.selectRow(self.iterator.index)
            
        self.play_btn.setEnabled(True)
        self.next_btn.setEnabled(True)


    def setup_table(self):
        """
        Настройка и заполнение таблицы.
        """

        self.table.clear()
        
        self.table.setRowCount(len(self.iterator.paths))
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['File name'])
        
        for i, audio_path in enumerate(self.iterator.paths):
            audio_name = os.path.basename(audio_path)
            item = QTableWidgetItem(audio_name)
            self.table.setItem(i, 0, item)


    def next_audio(self):
        """
        Нахождение следущего элемента.
        """

        if not self.iterator:
            return
        
        try:
            next(self.iterator)
            self.table.selectRow(self.iterator.index)
                
        except StopIteration:
            self.iterator.index = 0
            self.table.selectRow(self.iterator.index)
    

    def play_file(self):
        """
        Воспроизведение выбранного файла.
        """

        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(True)
        
        file_path = next(self.iterator)
        self.iterator.index -= 1
        filename = os.path.basename(file_path)
            
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Error", f"File is not found: {file_path}")
            return

        try:  
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()
            self.current_track_label.setText(f"Now playing: {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Couldn't play audio: {str(e)}")
    

    def update_duration(self, duration):
        """
        Обновление длительности.
        """

        if duration > 0:
            seconds = duration // 1000
            minutes = seconds // 60
            seconds = seconds % 60
            self.duration_label.setText(f"Duration: {minutes}:{seconds:02d}")


def main():
    app = QApplication([])
    
    window = AudioPlayerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()