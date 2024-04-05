import glob
import json
import os.path
from typing import *
from typing import List
import wget

import numpy as np
import skimage.io as io
import torch
from torch import Tensor

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ciliaseg.gui.canvas import ImageCanvasWidget
from ciliaseg.widgets.control import ControlWidget
from ciliaseg.state.image import SEMImage
from ciliaseg.state.stereocilia import Stereocilia
from ciliaseg.eval.model import get_model, load_model
import ciliaseg.utils.io

__MODEL_LINK__ = 'https://www.dropbox.com/s/okp29b7v54gadg5/Jul27_SEM_Segmentaiton_model.trch?dl=1'
__MODEL_PATH__ = 'Jul27_SEM_Segmentaiton_model.trch'

class MainApplication(QMainWindow):
    def __init__(self):
        super(MainApplication, self).__init__()

        self.model = None

        # --- qt stuff ---
        self.setFocusPolicy(Qt.StrongFocus)
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)
        self.worker_queue: List[List[QRunnable]] = []

        self.canvas = ImageCanvasWidget()
        self.control_widget = ControlWidget()

        self.setCentralWidget(self.canvas)

        self.files_in_dir = []

        self.left_dock = QDockWidget('Dockable', self)
        self.left_dock.setWidget(self.control_widget)
        self.left_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.left_dock.setTitleBarWidget(QWidget(None))
        self.left_dock.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_dock)

        self.resize(1200, 800)

        self.link_slots_and_signals()

        self.active_image = None

        # self.active_image = SEMImage().load_image(filepath='/Users/chrisbuswinka/Dropbox (Partners HealthCare)/Annotations/Stereocilia/16k 3 16k_14w cre+ 2020-02-21 230-11.TIF')
        # self.canvas.setActiveImage(self.active_image)
        # self.load_model('/Users/chrisbuswinka/Dropbox (Partners HealthCare)/public_models/Nov22_17-08-29_CHRISUBUNTU.trch')
        # self.eval_model()

        # assert os.path.exists('/Users/chrisbuswinka/Dropbox (Partners HealthCare)/Annotations/Stereocilia/16k 2 16k_14w cre+ 2020-02-21 230-11.csv')
        #

        self.canvas.zoomToScreen()

        # self.load_csv(path='/Users/chrisbuswinka/Dropbox (Partners HealthCare)/Annotations/Stereocilia/16k 3 16k_14w cre+ 2020-02-21 230-11.csv')

    def link_slots_and_signals(self):

        self.control_widget.enable_move_mode_button.clicked.connect(self.canvas.enableMoveMode)
        self.control_widget.enable_draw_mode_button.clicked.connect(self.canvas.enableDrawStereociliaMode)
        self.control_widget.enable_edit_mode_button.clicked.connect(self.canvas.enableEditStereociliaMode)
        self.control_widget.delete_stereocilia_button.clicked.connect(self.canvas.deleteSelected)
        self.control_widget.selected_class_selector.currentTextChanged.connect(self.canvas.setDefaultClassLabel)
        self.canvas.selected_stereocilia.connect(self.control_widget.set_selected_class_label)
        self.control_widget.run_model_button.clicked.connect(self.eval_model)

        self.control_widget.nms_slider.valueChanged.connect(self.update_model_output_from_thr_sliders)
        self.control_widget.prob_slider.valueChanged.connect(self.update_model_output_from_thr_sliders)
        self.control_widget.polygon_approx_slider.valueChanged.connect(self.update_model_from_polygon_slider)
        self.control_widget.polygon_approx_slider.valueChanged.connect(self.canvas.abortAction)

        self.control_widget.model_selector.modelFileSelected.connect(self.load_model)
        self.control_widget.default_model_button.clicked.connect(self.load_default_model)

        self.control_widget.open_button.clicked.connect(self.open_image)
        self.control_widget.next_file_button.clicked.connect(self.next_image)
        self.control_widget.previous_file_button.clicked.connect(self.previous_image)
        self.control_widget.save_csv_button.clicked.connect(self.save_csv)
        self.control_widget.load_csv_button.clicked.connect(self.load_csv)



    def update_model_from_polygon_slider(self):
        if self.active_image is None:
            return

        poly_thr = self.control_widget.polygon_approx_slider.value()
        self.active_image.update_polygons(poly_thr)
        self.update_model_output_from_thr_sliders()

        self.canvas.update()

    def update_model_output_from_thr_sliders(self):
        nms = self.control_widget.nms_slider.value()
        thr = self.control_widget.prob_slider.value()

        if self.active_image is not None:
            self.active_image.set_thresholds(nms, thr)
            self.active_image.populate_stereocilia_from_model_out()

        self.canvas.update()

    def load_default_model(self):
        # path = os.path.split(__MODEL_LINK__)[-1].replace('?dl=1', '')
        path = __MODEL_PATH__
        if not os.path.exists(path):
            print('downloading!')
            wget.download(__MODEL_LINK__)
        else:
            print('LOADED', os.path.exists(__MODEL_PATH__), __MODEL_PATH__)
        # path = '/Users/chrisbuswinka/Dropbox (Partners HealthCare)/public_models/Nov22_17-08-29_CHRISUBUNTU.trch'
        self.model = load_model(
            get_model(),
            path
        )
        self.model.eval()
        self.control_widget.model_selector.blockSignals(True)
        self.control_widget.model_selector.set_file(path)
        self.control_widget.model_selector.blockSignals(False)
        print('done')

    def load_model(self, path):
        self.model = load_model(
            get_model(),
            path
        )
        self.model.eval()

    def eval_model(self):
        print('trying to eval the model')
        if self.model is None or self.active_image is None:
            return
        (self.active_image
         .eval_model(self.model, 0, 1)
         .update_polygons(self.control_widget.polygon_approx_slider.value())
         .populate_stereocilia_from_model_out()
         )  # adds stereocilia internally
        self.canvas.update()

    def set_active_image(self, image: SEMImage):
        self.active_image = image
        self.canvas.setActiveImage(image)
        self.update()

    def open_image(self):
        """ launch file choose dialog and try to get the next file """
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select File')
        path, name = os.path.split(file_path)
        ext = os.path.splitext(name)[-1]
        self.set_active_image(SEMImage().load_image(filepath=file_path))
        self.files_in_dir = glob.glob(os.path.join(path, f'*{ext}'))
        print(path + f'*{ext}', self.files_in_dir)
        self.file_index = 0
        for i, f in enumerate(self.files_in_dir):
            if f == file_path:
                self.file_index = i
                break

    def next_image(self):
        if self.files_in_dir:
            self.file_index = min(len(self.files_in_dir), self.file_index + 1)
            file_path = self.files_in_dir[self.file_index]
            self.set_active_image(SEMImage().load_image(filepath=file_path))

    def previous_image(self):
        """ glob the folder of the current image and attempt to load the next image """
        if self.files_in_dir:
            self.file_index = max(0, self.file_index - 1)
            file_path = self.files_in_dir[self.file_index]
            self.set_active_image(SEMImage().load_image(filepath=file_path))

    def save_csv(self):
        """ save the segmentation masks as a csv for the image, suitable for training """
        if self.active_image is not None:
            filepath, ext = os.path.splitext(self.active_image.filepath)
            print(filepath + '.csv')
            ciliaseg.utils.io.save_image_as_csv(self.active_image, filepath + '.csv')

    def load_csv(self, path = None):
        if self.active_image is not None:
            if not path:
                file_path, _ = QFileDialog.getOpenFileName(self, 'Select Saved CSV File')
            else:
                file_path = path

            stereocilia_list = []
            assert os.path.exists(file_path), 'shit doesnt exist!'
            if file_path:
                with open(file_path, 'r') as file:
                    keys = file.readline().split(',')
                    print(keys)

                    line = file.readline()
                    while line:
                        line = line.split(',')
                        stereocilia_list.append({k: v for k, v in zip(keys, line)})
                        line = file.readline()

            self.active_image.clear_stereocilia()

            for _s in stereocilia_list:
                """
                            poly = polygons[i]
                poly: List[QPointF] = ciliaseg.eval.polygon.polygon_to_qt(poly)

                s = Stereocilia() \
                    .set_score(scores[i]) \
                    .set_label(int(labels[i]) - 1) \
                    .set_vertices(poly)
                """
                print('verts')
                print( _s['x_vertices'].replace('[', '').replace(']','').split(' '))
                x = [float(x) for x in _s['x_vertices'].replace('[', '').replace(']','').split(' ') if x]
                y = [float(y) for y in _s['y_vertices'].replace('[', '').replace(']','').split(' ') if y]
                poly = [QPointF(_x, _y) for _x, _y in zip(x, y)]

                s = (Stereocilia()
                     .set_score(float(_s['score']))
                     .set_label(_s['type'])
                     .set_vertices(poly)
                     .set_gt()
                     )
                self.active_image.add_stereocilia(s)


    def save_overlay(self):
        """ save the segmentation masks as an overlay, for publicaiton """
        print('notimplemented')
