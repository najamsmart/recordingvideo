import cv2
import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore

class EmployeeDataInput(QtWidgets.QDialog):
    def __init__(self):
        super(EmployeeDataInput, self).__init__()

        self.employee_id = QtWidgets.QLineEdit(self)
        self.name = QtWidgets.QLineEdit(self)
        self.depart = QtWidgets.QLineEdit(self)
        formLayout = QtWidgets.QFormLayout()

        formLayout.addRow("Employee ID:", self.employee_id)
        formLayout.addRow("Name:", self.name)
        formLayout.addRow("Depart:", self.depart)

        self.startButton = QtWidgets.QPushButton("Start Recording")
        self.stopButton = QtWidgets.QPushButton("Stop Recording")

        self.startButton.clicked.connect(self.start_recording)
        self.stopButton.clicked.connect(self.stop_recording)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(formLayout)
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)

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
        threading.Thread(target=self.video_capture.record).start()

    def stop_recording(self):
        self.set_is_recording(False)

    def set_is_recording(self, is_recording):
        self.is_recording = is_recording
        return is_recording


class VideoCapture:
    def __init__(self, employee_data, is_recording_func):
        self.video_name = f"{employee_data['id']}_{employee_data['name']}_{employee_data['depart']}.avi"
        self.folder_path = "./video/"
        self.cap = cv2.VideoCapture(0)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.folder_path + self.video_name, self.fourcc, 20.0, (640, 480))
        self.is_recording_func = is_recording_func
        self.is_recording = True

    def record(self):
        while self.is_recording:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
                cv2.imshow('Video Recording', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        self.is_recording_func(False)


def main():
    app = QtWidgets.QApplication([])

    dialog = EmployeeDataInput()
    dialog.exec_()


if __name__ == "__main__":
    main()
