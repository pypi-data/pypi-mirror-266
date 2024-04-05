from copy import copy
from hashlib import sha256
import numpy as np
from typing import List, Tuple, Dict, Any, TypedDict
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import random
from math import sqrt


class StyleDict(TypedDict):
    row1_border_color: QColor
    row1_fill_color: QColor
    row2_border_color: QColor
    row2_fill_color: QColor
    row3_border_color: QColor
    row3_fill_color: QColor
    vertex_point_larger_size: int
    vertex_point_smaller_size: int
    unselected_border_thickness: int
    selected_border_thickness: int
    scale: float


default_style: StyleDict = {
    'row1_border_color': QColor(255, 0, 0, 128),
    'row1_fill_color': QColor(255, 0, 0, 50),
    'row2_border_color': QColor(0, 255, 0, 128),
    'row2_fill_color': QColor(0, 255, 0, 50),
    'row3_border_color': QColor(0, 0, 255, 128),
    'row3_fill_color': QColor(0, 0, 255, 50),
    'vertex_point_larger_size': 8,
    'vertex_point_smaller_size': 5,
    'unselected_border_thickness': 1,
    'selected_border_thickness': 3,
    'scale': 1
}


class Stereocilia:
    """
    Object which can be drawn on a hair bundle
    """

    def __init__(self, parent=None, default_style: StyleDict = default_style):

        self.id = None
        self.vertices: List[QPointF] = []
        self.label: int | None = None
        self.score = None
        self._is_selected = False
        self._is_ground_truth = False
        self.parent = parent
        self.default_style_dict = default_style

        self.randcolor = QColor(*[random.randint(0, 255) for _ in range(3)])

    def is_selected(self):
        return self._is_selected

    def is_ground_truth(self):
        return self._is_ground_truth

    def select(self):
        self._is_selected = True
        return self

    def set_gt(self):
        self._is_ground_truth = True
        return self

    def deselect(self):
        self._is_selected = False
        return self

    def set_score(self, score):
        self.score = score
        return self

    def get_score(self):
        return self.score

    def set_vertices(self, vertices: List[QPointF]):
        self.vertices = vertices
        return self

    def set_vertex_at_index(self, vertex: QPointF, index: int):
        assert index < len(
            self.vertices), f'stereocilia {self} has {len(self.vertices)}, but tried to access vertex at index: {index}'
        raise RuntimeError('not needed')

        self.vertices[index] = vertex

    def get_vertices(self):
        return self.vertices

    def clear_vertices(self):
        self.vertices = []
        return self

    def set_label(self, label: str | int):
        _valid = {'short': 0, 'middle': 1, 'tall': 2}
        if isinstance(label, str):
            self.label = _valid[label]
        elif isinstance(label, int) and label in [0, 1, 2]:
            self.label = label
        else:
            raise ValueError(f'cannot self.label to invalid value: {label}')

        return self

    def get_label(self):
        return self.label

    def get_label_str(self):
        _valid = {0: 'short', 1: 'middle', 2: 'tall'}
        return _valid[self.label] if self.label is not None else ''

    def clear_label(self):
        self.label = None
        return self

    def paint(self, painter: QPainter, offset: QPointF, style: StyleDict):
        oldpen = painter.pen()

        style_dict = copy(self.default_style_dict)
        for k, v in style.items():
            style_dict[k] = v

        if self.label == 0:
            border_color = style_dict['row1_border_color']
            fill_color = style_dict['row1_fill_color']
        elif self.label == 1:
            border_color = style_dict['row2_border_color']
            fill_color = style_dict['row2_fill_color']
        elif self.label == 2:
            border_color = style_dict['row3_border_color']
            fill_color = style_dict['row3_fill_color']
        else:
            border_color = QColor(100, 100, 100, 255)
            fill_color = QColor(100, 100, 100, 255)

        pen = QPen()
        pen.setColor(border_color)

        if self.is_selected():
            pen.setWidthF(style_dict['selected_border_thickness'] / style_dict['scale'])
        else:
            pen.setWidthF(style_dict['unselected_border_thickness'] / style_dict['scale'])

        painter.setPen(pen)

        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        brush.setColor(fill_color)
        painter.setBrush(brush)

        verts = [v + offset for v in self.vertices]
        polygon = QPolygonF(verts)
        painter.drawPolygon(polygon)

        if self.is_selected():
            pen = QPen()
            pen.setCapStyle(Qt.RoundCap)
            pen.setWidthF(style_dict['vertex_point_larger_size'] / style_dict['scale'])
            pen.setColor('white')
            painter.setPen(pen)
            for v in verts:
                painter.drawPoint(v)

            pen.setWidthF(style_dict['vertex_point_smaller_size'] / style_dict['scale'])
            pen.setColor('black')
            painter.setPen(pen)
            for v in verts:
                painter.drawPoint(v)

        painter.setPen(oldpen)

    def is_inside(self, point: QPointF) -> bool:
        " returns true if the coordinate x,y is inside the polygon "
        return self.is_point_inside_polygon(point, self.vertices)

    def return_clicked_vertex(self, point: QPointF, thr: float) -> QPointF | None:
        distances = [self._dist(vert, point) for vert in self.vertices]
        mindist = float('inf')
        mindist_index = -1
        for i, dist in enumerate(distances):
            if dist < thr:
                mindist_index = i if dist <= mindist else mindist_index
                mindist = min(dist, mindist)
        if mindist_index == -1:
            return None
        else:
            return self.vertices[mindist_index]

    @staticmethod
    def _dist(a: QPointF, b: QPointF) -> float:
        return sqrt((b.x() - a.x()) ** 2 + (b.y() - a.y()) ** 2)

    @staticmethod
    def is_point_inside_polygon(point: QPointF,
                                vertices: List[QPointF]) -> bool:
        """
        Calculates if a point is inside a polygon.
            ien.setColor(color)

        :param point: [x0, y0]
        :param vertices: List[[x0, y0], ...]

        :return: True if a point is inside, false otherwise
        """
        # Implementation of the Ray Casting Algorithm
        # Source: https://stackoverflow.com/a/21337692
        x, y = point.x(), point.y()
        inside = False
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            if ((vertices[i].y() > y) != (vertices[j].y() > y) and
                    (x < (vertices[j].x() - vertices[i].x()) * (y - vertices[i].y()) / (
                            vertices[j].y() - vertices[i].y()) +
                     vertices[i].x())):
                inside = not inside
        return inside

    def x(self) -> List[float]:
        return [p.x() for p in self.vertices]

    def y(self) -> List[float]:
        return [p.y() for p in self.vertices]

    def bbox(self) -> Tuple[float, float, float, float]:
        """ x0, y0, x1, y1 """
        _x = self.x()
        _y = self.y()

        x0 = min(_x)
        x1 = max(_x)
        y0 = min(_y)
        y1 = max(_y)
        return (x0, y0, x1, y1)

    def closest_point_on_polygon(self, point: QPointF, thr: float) -> QPointF | None:
        if len(self.vertices) < 2:
            return None

        def _fit_line(x0, y0, x1, y1) -> Tuple[float, float]:
            m = (y1 - y0) / (x1 - x0 + 1e-8)
            b = y1 - m * x1
            return m, b

        def _closest_to_line(x, y, m, b):
            vert_x = (x + m * (y - b)) / (1 + m ** 2)
            # vert_x = min(max(vert_x, x0), x1)
            vert_y = x * m + b
            return vert_x, vert_y

        def _fast_dist(x0, y0, x1, y1) -> float:
            return (x1 - x0) ** 2 + (y1 - y0) ** 2

        mouse_x, mouse_y = point.x(), point.y()

        _line = [
            _fit_line(self.vertices[i].x(), self.vertices[i].y(), self.vertices[i-1].x(), self.vertices[i-1].y())
            for i
            in range(len(self.vertices))
        ]
        _close = [
            _closest_to_line(mouse_x, mouse_y, m, b) for (m, b) in _line
        ]

        dist = [
            _fast_dist(mouse_x, mouse_y, x0, y0) for (x0, y0) in _close
        ]

        ind = np.argmin(dist)

        if dist[ind] > thr:
            return None

        v0 = self.vertices[ind]
        v1 = self.vertices[ind - 1]

        x0, y0 = v0.x(), v0.y()
        x1, y1 = v1.x(), v1.y()

        m, b = _fit_line(x0, y0, x1, y1)

        vert_x = (mouse_x + m * (mouse_y - b)) / (1 + m ** 2)

        _x0 = min(x0, x1)
        _x1 = max(x0, x1)

        vert_x = min(max(vert_x, _x0), _x1)
        vert_y = vert_x * m + b

        print(f'{vert_y=} = {m=} * {vert_x=} + {b=}')
        return QPointF(vert_x, vert_y)

    def insert_vertex(self, vertex: QPointF):
        def _fit_line(x0, y0, x1, y1) -> Tuple[float, float]:
            m = (y1 - y0) / (x1 - x0 + 1e-8)
            b = y1 - m * x1
            return m, b

        def _closest_to_line(x, y, m, b):
            vert_x = (x + m * (y - b)) / (1 + m ** 2)
            # vert_x = min(max(vert_x, x0), x1)
            vert_y = x * m + b
            return vert_x, vert_y

        def _fast_dist(x0, y0, x1, y1) -> float:
            return (x1 - x0) ** 2 + (y1 - y0) ** 2

        mouse_x, mouse_y = vertex.x(), vertex.y()


        _line = [
            _fit_line(self.vertices[i].x(), self.vertices[i].y(), self.vertices[i-1].x(), self.vertices[i-1].y())
            for i
            in range(len(self.vertices))
        ]
        _close = [
            _closest_to_line(mouse_x, mouse_y, m, b) for (m, b) in _line
        ]

        dist = [
            _fast_dist(mouse_x, mouse_y, x0, y0) for (x0, y0) in _close
        ]

        ind = np.argmin(dist)

        self.vertices.insert(ind, vertex)
