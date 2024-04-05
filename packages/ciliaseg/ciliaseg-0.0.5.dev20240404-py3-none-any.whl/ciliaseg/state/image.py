from copy import copy
from hashlib import sha256
from typing import List, Tuple, Dict
from ciliaseg.state.stereocilia import Stereocilia
from torch import Tensor
import skimage.io as io

import numpy as np
import torch
import torch.nn as nn
import torchvision.ops  # nms
from PySide6.QtCore import QPointF, QLineF, Qt
from PySide6.QtGui import QImage

# import whorl.lib.frequency
# import whorl.lib.roi
# from whorl.gui.tree_widget_item import TreeWidgetItem
# from whorl.lib.adjust import _adjust
# from whorl.lib.histogram import histogram
# from whorl.state import Cell, StateItem, Synapse
import ciliaseg.eval.polygon


class SEMImage:
    """

    """

    def __init__(self):

        self.filepath = None
        self.image = None
        self.sha256_hash_of_image = None
        self.dtype = None
        self.filename = None
        self.device = 'cpu'
        self.model_out = None

        self.seleted: Stereocilia | None = None

        self.adjustments: List[Dict[str, int] | None] = [
            {"brightness": 0, "contrast": 1, 'channel': 0},
            {"brightness": 0, "contrast": 1, 'channel': 1},
            {"brightness": 0, "contrast": 1, 'channel': 2},
        ]

        self.stereocilia: List[Stereocilia] = []
        self._candidate_stereocilia = []

        self.nms_thr = 0.5
        self.stereocilia_thr = 0.5

        self._display_image_buffer = None

    def eval_model(self, model: nn.Module, mean: float = .3717, std: float = .1897):
        image: Tensor = torch.from_numpy(self.image)  # [X, Y ,3]
        image = image.permute(2, 0, 1).div(255).sub(mean).div(std).float()

        with torch.no_grad():
            out = model([image])[0]

        self.model_out = out
        print(out)
        self.model_out['polygons'] = [
            ciliaseg.eval.polygon.find_contours(out['masks'][i, 0, ...].permute(1,0).numpy()) for i in range(out['scores'].shape[0])]
        return self

    def update_polygons(self, polygon_threshold: float = 0.25):
        if self.model_out is None:
            return

        self.model_out['polygons-downsampled'] = [
            ciliaseg.eval.polygon.approximate_polygon(c, tolerance=polygon_threshold) for c in self.model_out['polygons']]

        return self

    def populate_stereocilia_from_model_out(self):
        if not self.model_out:
            return


        to_delete = [s for s in self.get_stereocilia() if not s.is_ground_truth()]
        self.set_stereocilia([s for s in self.get_stereocilia() if s.is_ground_truth()])
        del to_delete

        scores = self.model_out['scores']
        masks = self.model_out['masks']  # [N, 1, X, Y]
        labels = self.model_out['labels']
        boxes = self.model_out['boxes']
        polygons = self.model_out['polygons-downsampled']

        ind = torchvision.ops.nms(boxes, scores, self.nms_thr)

        for i in range(masks.shape[0]):
            if scores[i] < self.stereocilia_thr or i not in ind:
                continue

            _mask = masks[i, 0, ...]  # x, y
            poly = polygons[i]
            poly: List[QPointF] = ciliaseg.eval.polygon.polygon_to_qt(poly)

            s = Stereocilia() \
                .set_score(scores[i]) \
                .set_label(int(labels[i]) - 1) \
                .set_vertices(poly)

            self.add_stereocilia(s)

        return self

    def load_image(self, filepath):
        self.filepath = filepath
        _image = io.imread(filepath)

        if _image.ndim == 2:
            _image = _image[:, :, np.newaxis][:,:,[0,0,0]]


        if _image.max() > 256:

            const = 2 ** 15 if _image.max() < 2 ** 15 else 2 ** 16
            if _image.max() < 2 ** 13:
                const = 2 ** 13

            _image = _image / const
            _image = _image * 255
            _image = np.round(_image).astype(np.uint8)

        if _image.shape[0] < 5:  # sometimes the channel is first i guess..
            _image = _image.transpose(1, 2, 0)

        while _image.shape[-1] < 3:
            x, y, _ = _image.shape
            _image = np.concatenate((_image, np.zeros((x, y, 1), dtype=np.uint8)), axis=-1)

        _image = np.ascontiguousarray(_image[:, :, -3::].astype(np.uint8))

        self.image = _image
        self._display_image_buffer = _image.copy()

        return self

    def get_image_buffer_as_qimage(self):
        h, w, _ = self._display_image_buffer.shape

        _image = self._display_image_buffer[:, :, 0:3]
        _image = np.ascontiguousarray(_image.astype(np.uint8))

        return QImage(_image.data, w, h, 3 * w, QImage.Format_RGB888)

    def get_selected(self):
        selected = []
        for stereocilia in self.get_stereocilia():
            if stereocilia.is_selected():
                selected.append(stereocilia)
        return selected

    def delete_selected(self):
        " deletes all selected stereocilia "
        selected = self.get_selected()
        self.set_stereocilia([s for s in self.get_stereocilia() if not s.is_selected()])

        del selected

        return self

    def add_stereocilia(self, sterocilia: Stereocilia):
        self._candidate_stereocilia.append(sterocilia)
        # self._stereocilia_rejection_from_thr()
        return self

    def get_stereocilia(self) -> List[Stereocilia]:
        return self._candidate_stereocilia

    def set_stereocilia(self, stereocilia_list: List[Stereocilia]):
        self._candidate_stereocilia = stereocilia_list
        return self

    def remove_stereocilia(self, sterocilia):
        raise NotImplemented
        return self

    def get_pixmap(self):
        raise RuntimeError
        # return ???

    def set_thresholds(self, nms=0.5, thr=0.5):
        self.nms_thr = nms
        self.stereocilia_thr = thr

        return self

    def _stereocilia_rejection_from_thr(self):
        raise RuntimeError

    def populate_from_network_output(self, data_dict: Dict[str, Tensor]):
        raise NotImplemented
        return self

    def clear_stereocilia(self):
        self.seleted = None
        self.stereocilia = []
        self._candidate_stereocilia = []
        return self
