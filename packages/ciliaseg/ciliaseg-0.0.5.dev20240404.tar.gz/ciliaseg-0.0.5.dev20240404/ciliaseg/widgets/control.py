from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import warnings
import os

class NamedSliderSpinBox(QWidget):
    valueChanged = Signal(float)
    def __init__(self, name, min_val, max_val, step, init_val):
        super(NamedSliderSpinBox, self).__init__()

        spin_style = """
            QDoubleSpinBox {
                 padding-right: 3px; /* make room for the arrows */
                 border-width: 0px;
                 background-color: rgba(0,0,0,0);
                 margin: 0px 0px 0px 0px;
             }

        """

        self.spinbox = QDoubleSpinBox()
        self.spinbox.setRange(min_val, max_val)
        self.spinbox.setSingleStep(step)
        self.spinbox.setValue(init_val)
        self.spinbox.setMinimumWidth(50)
        self.spinbox.setStyleSheet(spin_style)

        self.slider =QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val*100)
        self.slider.setMaximum(max_val*100)
        self.slider.setValue(init_val * 100)
        self.slider.setTickInterval(step*100)
        # self.slider.setTickPosition(QSlider.TicksBelow)

        #signals

        self.slider.valueChanged.connect(self.update_spinbox_from_slider)
        self.slider.valueChanged.connect(self.emit_val_changed)

        self.spinbox.valueChanged.connect(self.update_slider_from_spinbox)
        self.spinbox.valueChanged.connect(self.emit_val_changed)

        group_layout = QHBoxLayout()
        group_layout.addWidget(self.slider, alignment=Qt.AlignTop)
        group_layout.addWidget(self.spinbox, alignment=Qt.AlignCenter)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(0)

        group = QGroupBox(name)
        group.setContentsMargins(0, 0, 0, 0)
        group.setLayout(group_layout)

        layout = QVBoxLayout()
        layout.addWidget(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setStyleSheet("""
                   QGroupBox {
                       background-color: None;
                       border: 0px solid black;
                       margin-top: 10px; /* leave space at the top for the title */
                       font-size: 10px;
                       border-radius: 5px;
                       }

                   QGroupBox::title {
                       subcontrol-origin: margin;
                       padding: 0 0px;
                   }

                   """)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.setLayout(layout)
    def update_slider_from_spinbox(self):
        """ changes slider from value of the spinbox """
        self.diable_signals()
        value = self.spinbox.value()
        self.slider.setValue(value*100)
        self.enalbe_signals()

    def update_spinbox_from_slider(self):
        """ changes spinbox from value of the slider """
        self.diable_signals()
        value = self.slider.value()
        self.spinbox.setValue(value/100)
        self.enalbe_signals()

    def diable_signals(self):
        self.spinbox.blockSignals(True)
        self.slider.blockSignals(True)

    def enalbe_signals(self):
        self.spinbox.blockSignals(False)
        self.slider.blockSignals(False)

    def emit_val_changed(self):
        self.valueChanged.emit(self.slider.value)

    def value(self):
        return self.spinbox.value()

    def setValue(self, value):
        self.spinbox.setValue(value / 100)
        self.slider.setValue(value)


class TextEdit(QTextEdit):
    def __init__(self, parent = None):
        super(TextEdit, self).__init__(parent)
        self.text_set = False

    def paintEvent(self, event):
        if not self.text_set:
            painter = QPainter(self.viewport())

            red_pen = QPen()
            red_pen.setColor(QColor(255, 0, 0, 60))
            red_pen.setWidth(15)

            white_pen = QPen()
            white_pen.setColor(QColor(255, 255, 255, 255))
            white_pen.setWidth(15)

            _x = -50
            for i in range(20):
                painter.setPen(red_pen)
                painter.drawLine(QLineF(_x, 0, 200+_x, 200))
                _x += 20

                painter.setPen(white_pen)
                painter.drawLine(QLineF(_x, 0, 200+_x, 200))

                _x += 20

        super(TextEdit, self).paintEvent(event)

class ModelFileSelector(QWidget):
    modelFileSelected = Signal(str)
    def __init__(self):
        super().__init__()
        self.file_path = None

        style = f"""
        QPushButton {{
            background-color: white;
            margin: 0px;
            padding: 0px;
            font-size: 12pt;
            font: bold;
            border-style: inset;
            border-width: 1px 1px 1px 1px; 
            border-color: black black black black; 
            background-color: white;
            }}
        QPushButton:pressed {{
        background-color: grey;
            border-style: inset;
            border-width: 1px;
            border-color: black;
            margin: 1px;
            padding: 2px;
            }}
        """
        self.setStyleSheet(style)

        # Create the button and label widgets
        self.button = QPushButton('SELECT MODEL', clicked=self.select_file)
        self.label = TextEdit('NOT SET')
        self.label.setReadOnly(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.label.setFixedHeight(30)
        self.label.setStyleSheet("""
        QTextEdit {
            margin: -1px 0px 0px 0px; 
            background-color: rgba(0,0,0,0);
            font: bold 16px;
            border: 1px solid black;
        }
        """)

        # Create a layout to contain the button and label
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        layout.setSpacing(0)
        layout.setContentsMargins(0,10,0,0)
        layout.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Set the fixed size of the widget
        # self.setFixedSize(QSize(250, 70))

    def set_file(self, file_path: str):
        _justfile = os.path.split(file_path)[-1]
        self.label.setText(_justfile)
        self.label.setFixedHeight(60)
        self.label.text_set = True
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setStyleSheet("""
        QTextEdit {
            background-color: rgba(0,0,0,0);
            font: 12px;
        }
        """)
        self.modelFileSelected.emit(str(self.file_path))
        self.file_path = _justfile
        self.label.update()

    def remove_file(self):
        self.label.setText('NOT SET')
        self.label.text_set = False
        self.label.setReadOnly(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.label.setFixedHeight(30)
        self.label.setStyleSheet("""
        QTextEdit {
            margin: -1px 0px 0px 0px; 
            background-color: rgba(0,0,0,0);
            font: bold 16px;
            border: 1px solid black;
        }
        """)

    def select_file(self):
        # Open a file dialog to choose a file
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select File')
        print(file_path)
        if file_path:
            # Update the label with the selected file path
            if not self.validate_model_file(self.file_path):
                self.file_path = None
                return

            self.file_path = file_path
            self.set_file(file_path)
        else:
            # No file selected, update the label to display 'None'
            self.file_path = None
            self.label.text_set = False
            self.label.setText('NOT SET')
            self.label.setFixedHeight(30)
            self.label.setAlignment(Qt.AlignCenter)
            self.label.setStyleSheet("""
            QTextEdit {
                margin: -1px 0px 0px 0px; 
                background-color: rgba(0,0,0,0);
                font: bold 16px;
                border: 1px solid black;
            }
            """)
            self.label.update()

    def validate_model_file(self, file):
        warnings.warn('Validation of model files not implemented')
        return True

class ControlWidget(QWidget):
    def __init__(self):
        super(ControlWidget, self).__init__()


        self.open_button = QPushButton('Open')
        self.save_csv_button = QPushButton('Save CSV')
        self.load_csv_button = QPushButton('Load from CSV')

        self.save_overlay_button = QPushButton('Save Overlay')
        self.next_file_button = QPushButton('-->')
        self.previous_file_button = QPushButton('<--')
        self.enable_move_mode_button = QPushButton('Move')
        self.enable_draw_mode_button = QPushButton('Draw')
        self.enable_edit_mode_button = QPushButton('Edit')
        self.run_model_button = QPushButton('Eval Model')
        self.delete_stereocilia_button = QPushButton('Delete')
        self.default_model_button = QPushButton('Load Default Model')

        self.stereocilia_class_selector = QComboBox()
        self.stereocilia_class_selector.addItems(['short', 'middle', 'tall'])
        self.stereocilia_class_selector.setCurrentIndex(0)

        self.selected_class_selector= QComboBox()
        self.selected_class_selector.addItems(['short', 'middle', 'tall'])
        self.selected_class_selector.setCurrentIndex(0)
        self.selected_class_selector.setDisabled(True)

        self.nms_slider = NamedSliderSpinBox(name='NMS Thr', min_val=0, max_val=1, step=0.01, init_val=0.5)
        self.prob_slider = NamedSliderSpinBox(name='Prob Thr', min_val=0, max_val=1, step=0.01, init_val=0.5)
        self.polygon_approx_slider = NamedSliderSpinBox(name='Polygon Downsample', min_val=0, max_val=10, step=0.2, init_val=0.25)

        self.model_selector = ModelFileSelector()

        file_group = QGroupBox('File')
        _layout = QVBoxLayout()
        _layout.addWidget(self.open_button)
        _layout.addWidget(self.save_csv_button)
        _layout.addWidget(self.load_csv_button)
        # _layout.addWidget(self.save_overlay_button)
        _lr_layout = QHBoxLayout()
        _lr_layout.addWidget(self.previous_file_button)
        _lr_layout.addWidget(self.next_file_button)
        _lr_layout.setContentsMargins(0,0,0,0)
        _layout.addLayout(_lr_layout)
        file_group.setLayout(_layout)

        mode_group = QGroupBox('Mode')
        _layout = QVBoxLayout()
        _layout.addWidget(self.enable_move_mode_button)
        _layout.addWidget(self.enable_draw_mode_button)
        _layout.addWidget(self.enable_edit_mode_button)
        _layout.addWidget(self.delete_stereocilia_button)

        form = QFormLayout()
        form.addRow(QLabel('Selected Label:'), self.selected_class_selector)
        form.addRow(QLabel('Default Label:'), self.stereocilia_class_selector)
        _layout.addLayout(form)
        mode_group.setLayout(_layout)

        eval_group = QGroupBox('Eval')
        _layout = QVBoxLayout()
        _layout.addWidget(self.model_selector)
        _layout.addWidget(self.default_model_button)
        _layout.addWidget(self.nms_slider)
        _layout.addWidget(self.prob_slider)
        _layout.addWidget(self.polygon_approx_slider)
        _layout.addWidget(self.run_model_button)
        eval_group.setLayout(_layout)

        layout = QVBoxLayout()
        layout.addWidget(file_group)
        layout.addWidget(mode_group)
        layout.addWidget(eval_group)
        layout.addStretch(10000)
        layout.setAlignment(Qt.AlignTop)

        self.setLayout(layout)

    def set_selected_class_label(self, label: str | None):
        print("CALLED!!! -> ", label)
        self.selected_class_selector.blockSignals(True)
        if not label:
            self.selected_class_selector.setCurrentIndex(0)
            self.selected_class_selector.setDisabled(True)

        else:
            _map = {'short': 0, 'middle': 1, 'tall': 1}
            self.selected_class_selector.setDisabled(False)
            self.selected_class_selector.setCurrentIndex(_map[label])

        self.selected_class_selector.blockSignals(False)
