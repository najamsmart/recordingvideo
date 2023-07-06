import cv2
import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore

VIDEO_DISPLAY_SIZE = (640, 480)


class EmployeeDataInput(QtWidgets.QDialog):
    def __init__(self):
        super(EmployeeDataInput, self).__init__()

        self.setWindowTitle("Employee Dashboard")
        self.setGeometry(100, 100, 800, 600)

        self.employee_id = QtWidgets.QLineEdit(self)
        self.name = QtWidgets.QLineEdit(self)
        self.depart = QtWidgets.QLineEdit(self)
        formLayout = QtWidgets.QFormLayout()

        formLayout.addRow("Employee ID:", self.employee_id)
        formLayout.addRow("Name:", self.name)
        formLayout.addRow("Depart:", self.depart)

        self.startButton = QtWidgets.QPushButton("Start Recording", self)
        self.stopButton = QtWidgets.QPushButton("Stop Recording", self)

        self.startButton.clicked.connect(self.start_recording)
        self.stopButton.clicked.connect(self.stop_recording)

        self.startButton.setStyleSheet("QPushButton { background-color: #3cb371; }"
                                        "QPushButton:pressed { background-color: #008000; }")
        self.stopButton.setStyleSheet("QPushButton { background-color: #ff6347; }"
                                       "QPushButton:pressed { background-color: #8b0000; }")

        logo = QtGui.QPixmap('logo/logo_dark.png')
        self.logoLabel = QtWidgets.QLabel(self)
        self.logoLabel.setPixmap(logo)

        self.videoLabel = QtWidgets.QLabel(self)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(formLayout)
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.videoLabel)
        layout.addWidget(self.logoLabel, alignment=QtCore.Qt.AlignRight)

        self.video_capture = None
        self.is_recording = False

    def start_recording(self):
        employee_data = {
            "id": self.employee_id.text(),
            "name": self.name.text(),
            "depart": self.depart.text(),
        }

        self.video_capture = VideoCapture(employee_data, self.set_is_recording)
        self.is_recording = True
        self.video_capture.frame_ready.connect(self.display_video_frame)

        # Change button colors
        self.startButton.setEnabled(False)
        self.startButton.setStyleSheet("QPushButton { background-color: #008000; }")
        self.stopButton.setEnabled(True)
        self.stopButton.setStyleSheet("QPushButton { background-color: #ff6347; }")

        threading.Thread(target=self.video_capture.record).start()

    def stop_recording(self):
        self.set_is_recording(False)

        # Change button colors
        self.startButton.setEnabled(True)
        self.startButton.setStyleSheet("QPushButton { background-color: #3cb371; }")
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("QPushButton { background-color: #8b0000; }")

        # Close the current window and restart the application
        self.close()
        main()


    # def stop_recording(self):
    #     self.set_is_recording(False)

    #     # Change button colors
    #     self.startButton.setEnabled(True)
    #     self.startButton.setStyleSheet("QPushButton { background-color: #3cb371; }")
    #     self.stopButton.setEnabled(False)
    #     self.stopButton.setStyleSheet("QPushButton { background-color: #8b0000; }")

    def set_is_recording(self, is_recording):
        self.is_recording = is_recording
        return is_recording

    @QtCore.pyqtSlot(QtGui.QImage)
    def display_video_frame(self, image):
        self.videoLabel.setPixmap(QtGui.QPixmap.fromImage(image))

    def closeEvent(self, event):
        if self.is_recording:
            self.stop_recording()
            event.ignore()
        else:
            event.accept()


class VideoCapture(QtCore.QObject):
    frame_ready = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, employee_data, is_recording_func):
        super().__init__()

        self.video_name = f"{employee_data['id']}_{employee_data['name']}_{employee_data['depart']}.avi"
        self.folder_path = "./video/"
        self.file_path = os.path.join(self.folder_path, self.video_name)
        self.cap = cv2.VideoCapture('rtsp://admin:disruptlab54321@192.168.0.8:554/1')
        # self.cap = cv2.VideoCapture(0)
        
        # Use the actual camera resolution for the VideoWriter
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.file_path, self.fourcc, 20.0, (frame_width, frame_height))
        self.is_recording_func = is_recording_func
        self.is_recording = True

    def record(self):
        while self.is_recording:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                p = convert_to_Qt_format.scaled(VIDEO_DISPLAY_SIZE[0], VIDEO_DISPLAY_SIZE[1], QtCore.Qt.KeepAspectRatio)
                self.frame_ready.emit(p)

        self.cap.release()
        self.out.release()


    def stop(self):
        self.is_recording_func(False)


def main():
    app = QtWidgets.QApplication([])

    dialog = EmployeeDataInput()
    dialog.show()

    app.exec_()


if __name__ == "__main__":
    main()
