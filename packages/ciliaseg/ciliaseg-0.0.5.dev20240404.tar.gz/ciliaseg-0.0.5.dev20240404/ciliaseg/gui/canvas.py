from copy import copy
from typing import List, Tuple, Dict

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from ciliaseg.state.image import SEMImage
from ciliaseg.state.stereocilia import Stereocilia, StyleDict


class ImageCanvasWidget(QWidget):
    rescaled = Signal(float)  # when image is re-scaled
    updated_state = Signal()  # when a child is added to the piece
    children_removed = Signal(list)  # when a child(ren) is removed
    mouse_position_signal = Signal(list)  # emitted when mouse moves (for footer)
    selected_child_changed = Signal(list)  # selected child changed
    selected_stereocilia = Signal(str)
    liveUpdateRegionChanged = Signal(list)  # live mode dragged around
    modeChanged = Signal(str)

    def __init__(self, image: SEMImage = None):
        super(ImageCanvasWidget, self).__init__()
        palette = QPalette()
        palette.setColor(QPalette.Window, "gray")
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # conts
        self.VERTEX_CLICK_TRH = 10

        # state
        self.active_image: SEMImage = image

        # Where we draw the image
        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.pixmap = None

        # Constants about where we are looking...
        self.center = QPointF(0.0, 0.0)
        self.painter = QPainter()
        self._last_drag_pos = QPointF(0.0, 0.0)
        self._pixmap_offset = QPointF()
        self._dragging = [False, False]  # flags for it we are moving around..

        self._last_center_ratio = (0.0, 0.0)
        self._current_center_ratio = (0.0, 0.0)

        # Interactivity modes --------------
        self.move_mode = True
        self.draw_stereocilia_mode = False
        self.edit_stereocilia_mode = False

        # Annotation -----------
        self._default_stereocilia_label = 'short'  # short middle tall
        self.polygon_buffer = []

        # polygon for stereocila region drawing
        self._draw_mouse_position = None
        self._mouse_position = None
        self._editable_vertex = None
        self._potential_new_vert = None

        # image viewer state
        self.scale = 1.0
        self._temp_ratio = (0.0, 0.0)

        # where is the mouse?
        self.mouse_position = QPointF()
        self.setMouseTracking(True)


    def abortAction(self):
        """ gracefully handles when the esc key is pressed """
        self._draw_mouse_position = None
        self._mouse_position = None
        self._editable_vertex = None
        self.polygon_buffer = []
        self.update()


    def setDefaultClassLabel(self, label):
        self._default_stereocilia_label = label

        if self.active_image is not None:
            for stereocilia in self.active_image.get_selected():
                stereocilia.set_label(label)

        self.update()
    def disableAllInteractivityModes(self):
        self.move_mode = False
        self.edit_stereocilia_mode = False
        self.draw_stereocilia_mode = False

    def enableMoveMode(self):
        self.disableAllInteractivityModes()
        self.move_mode = True
        self.update()

    def enableDrawStereociliaMode(self):
        self.disableAllInteractivityModes()
        self.draw_stereocilia_mode = True
        self.update()

    def enableEditStereociliaMode(self):
        self.disableAllInteractivityModes()
        self.edit_stereocilia_mode = True
        self.update()

    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(ImageCanvasWidget, self).minimumSizeHint()

    def zoomBy(self, scalefactor: float, offset: QPointF | None = None):
        """
        Zooms by a scale factor up or down. scale factor must be POSITIV

        :param scalefactor: scale factor. 1.1 zooms by in by 10% at 110% zoom.
        :return:
        """
        if scalefactor > 1.0 and self.scale >= 20:
            scalefactor = 1.0
        elif scalefactor < 1.0 and self.scale < 0.01:
            scalefactor = 1.0

        # we need viewport size before and after scaling to zoom to the center
        _ss0 = self._get_viewport_size()  # init viewport size
        self.scale = self.scale * scalefactor
        _ss1 = self._get_viewport_size()  # after viewport size

        # how much do we change the pixmap offset such that we zoom to the center...
        dx = 0.5 * (_ss0.x() - _ss1.x())
        dy = 0.5 * (_ss0.y() - _ss1.y())

        # set the new _pixmap_offset
        self._pixmap_offset = QPointF(
            self._pixmap_offset.x() - dx, self._pixmap_offset.y() - dy
        )

        self.rescaled.emit(scalefactor)
        self.update()

    def zoomIn(self):
        self.zoomBy(1.1)

    def zoomOut(self):
        self.zoomBy(1 / 1.1)

    def zoomReset(self):
        self.scale = 1.0

    def zoomToScreen(self):
        """
        zooms to fit the entire image in the screen.
        DOES NOT place the image in the center of the screen. For that, go to self.resetImageToViewport()
        """
        if self.pixmap is not None:
            # get height of the current view and of the pixmap (image)
            w0, h0 = self.pixmap.width(), self.pixmap.height()
            w1, h1 = self.width(), self.height()

            print(w0, w1, h0, h1, end=' ')

            if w0 > w1 or h0 > h1:  # zooms out if the image is much smaller
                _scale = max(w1 / w0, h1 / h0)
            else:  # zooms in otherwise
                _scale = min(w1 / w0, h1 / h0)
            print(f'{_scale=}, {w1/w0=}, {h1/h0=}')
        else:
            _scale = 1

        self.zoomReset()  # have to reset the zoom first.
        self.zoomBy(_scale)

    def _get_viewport_size(self):
        return QPointF(self.width() / self.scale, self.height() / self.scale)

    def _get_pixmap_size(self):
        return QPointF(self.pixmap.width(), self.pixmap.height())

    def point_outside_pixmap(self, x, y) -> bool:
        x0, y0 = self._pixmap_offset

    def resetImageToViewport(self):
        """
        Set the current zoom to the perfectly fit the image into the viewport.
        Centers the image as best it can. Calls a view refresh.
        """
        self.zoomToScreen()

        # now we center the image...
        if self.pixmap is not None:
            w, h = self.pixmap.width(), self.pixmap.height()
            sw, sh = (
                self.width() / self.scale,
                self.height() / self.scale,
            )  # screenwidth, screenheight
            x = (sw - w) / 2
            y = (sh - h) / 2
            self._pixmap_offset = QPointF(x, y)
            self.zoomBy(
                1.0
            )  # we have to do this to update the _pixmap_offset... kinda dumb... im dumb..
            self.update()

    def wheelEvent(self, event):
        """zooms in and out if you scroll"""
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 15.0
        num_steps = min(num_steps, 0.1) if num_steps > 0 else max(num_steps, -0.1)
        self.zoomBy(pow(0.1, num_steps))

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.mouse_position = event.position()
        pos = event.position()
        _x = (pos.x() / self.scale) - self._pixmap_offset.x()
        _y = (pos.y() / self.scale) - self._pixmap_offset.y()

        self.mouse_position_signal.emit([_x, _y])

        if not self.active_image:
            return

        # Drag the screen around!
        if (
                event.buttons() == Qt.MiddleButton or event.buttons() == Qt.RightButton
        ) and not self._dragging[0]:
            self._dragging[1] = True
            self._last_drag_pos = event.position()

        # This is such that if someone tries to click while already dragging, it just fails..
        if event.buttons() == Qt.LeftButton | Qt.RightButton and self._dragging[1]:
            self._last_drag_pos = QPointF()
            self._dragging[1] = False
        elif (
                event.buttons() == Qt.MiddleButton | Qt.LeftButton or event.buttons() == Qt.LeftButton | Qt.RightButton
        ) and self._dragging[0]:
            self._last_drag_pos = QPointF()
            self._dragging[0] = False

        if event.buttons() != Qt.LeftButton:
            self.update()
            return

        if self.move_mode and not self._dragging[1]:
            self._dragging[0] = True
            self._last_drag_pos = event.position()

        if self.draw_stereocilia_mode:
            self.polygon_buffer.append(QPointF(_x, _y))

        if self.edit_stereocilia_mode:
            press = QPointF(_x, _y)

            if any(s.is_selected() for s in self.active_image.get_stereocilia()):
                for s in self.active_image.get_stereocilia():
                    if s.is_selected():
                        self._editable_vertex: QPointF = s.return_clicked_vertex(press, self.VERTEX_CLICK_TRH)

                        if self._editable_vertex is None:
                            self._potential_new_vert = s.closest_point_on_polygon(press, self.VERTEX_CLICK_TRH*2500)
                            s.insert_vertex(self._potential_new_vert)
                            self._editable_vertex = self._potential_new_vert
                            self._potential_new_vert = None

            if not self._editable_vertex:
                self.selected_stereocilia.emit('')
                for s in self.active_image.get_stereocilia():
                    s.deselect()
                for s in self.active_image.get_stereocilia():
                    if s.is_inside(press):
                        s.select()
                        self.selected_stereocilia.emit(s.get_label_str())


        self.update()



    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        self.mouse_position = event.position()
        pos = event.position()
        _x = (pos.x() / self.scale) - self._pixmap_offset.x()
        _y = (pos.y() / self.scale) - self._pixmap_offset.y()

        # Moves the pixmap around...
        if (
                (event.buttons() == Qt.LeftButton and self.move_mode)
                or event.buttons() == Qt.MiddleButton
                or event.buttons() == Qt.RightButton
        ) and any(self._dragging):
            pos = event.position()
            if self._last_drag_pos is not None:
                self._pixmap_offset += (pos - self._last_drag_pos) / self.scale
                self._last_drag_pos = pos
            self.zoomBy(1.0)

        if self.draw_stereocilia_mode and self.polygon_buffer:
            self._draw_mouse_position = QPointF(_x, _y)

        if self.edit_stereocilia_mode and self._editable_vertex:
            self._editable_vertex.setX(_x)
            self._editable_vertex.setY(_y)

        if self.edit_stereocilia_mode and not self._editable_vertex:
            selected = self.active_image.get_selected()
            s = selected[0] if selected else None
            if s is not None:
                self._potential_new_vert = self.active_image.get_selected()[0].closest_point_on_polygon(QPointF(_x, _y), self.VERTEX_CLICK_TRH * 2500)

        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mouse_position = event.position()
        pos = event.position()
        _x = (pos.x() / self.scale) - self._pixmap_offset.x()
        _y = (pos.y() / self.scale) - self._pixmap_offset.y()

        if (
                event.button() == Qt.MiddleButton or event.button() == Qt.RightButton
        ) and self._dragging[
            1
        ]:  # can always move by pressing the middle button down
            pos = event.position()
            if self._last_drag_pos is not None:
                self._pixmap_offset += pos - self._last_drag_pos
            self._last_drag_pos = QPointF()
            self._dragging[1] = False

        if (
                event.button() == Qt.LeftButton and self.move_mode and self._dragging[0]
        ):  # if you're in move mode then you can click and drag.
            pos = event.position()
            if self._last_drag_pos:  # need to do this to avoid double click bug..
                self._pixmap_offset += pos - self._last_drag_pos
            self._last_drag_pos = QPointF()
            self._dragging[0] = False

        self._editable_vertex = None
        self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.mouse_position = event.position()
        pos = event.position()
        _x = (pos.x() / self.scale) - self._pixmap_offset.x()
        _y = (pos.y() / self.scale) - self._pixmap_offset.y()

        if self.draw_stereocilia_mode:

            stereocilia = Stereocilia() \
                .set_vertices(self.polygon_buffer) \
                .set_label(self._default_stereocilia_label) \
                .set_score(1.0) \
                .set_gt()

            self.active_image.add_stereocilia(stereocilia)
            self.polygon_buffer = []

        self._editable_vertex = None
        self.update()

    def getCurrentWindowCoords(self) -> List[float]:
        x0 = -self._pixmap_offset.x()
        y0 = -self._pixmap_offset.y()
        x1 = self.width() / self.scale + x0
        y1 = self.height() / self.scale + y0
        return [x0, y0, x1, y1]

    def addStereocilia(self):
        raise NotImplemented

    def deleteSelected(self):
        if self.active_image is not None:
            self.active_image.delete_selected()


            self.update()

    def setActiveImage(self, image: SEMImage):
        self.active_image = image
        self.setImage(self.active_image.get_image_buffer_as_qimage())

        self.resetImageToViewport()

    def setImage(self, image: QImage):
        """gets a pixmap from the image, assigns to self.pixmap, and calls a pixmap update"""
        self.image = image
        self.pixmap = QPixmap.fromImage(self.image)
        self.zoomToScreen()
        self.update()

    def adjustImage(self):
        raise NotImplemented

    def paintEvent(self, event):
        """main render loop. Everything drawn on the screen goes here"""
        self.painter.begin(self)
        self.painter.scale(self.scale, self.scale)

        self._paint_pixmap()  # draws the image

        if self.edit_stereocilia_mode or self.draw_stereocilia_mode:
            self._paint_center_cross()
            self._paint_polygon_buffer()
            self._paint_potential_vert()
        self._paint_current_mode()
        self._paint_stereocilia()
        self.painter.end()

    def _paint_center_cross(self):
        p = self.painter
        _x, _y = (
            self.mouse_position.x() / self.scale,
            self.mouse_position.y() / self.scale,
        )
        _w, _h = self.width() / self.scale, self.height() / self.scale

        _pen = self.painter.pen()
        pen = QPen()
        pen.setColor(QColor(255, 255, 255))
        pen.setWidthF(0.5 / self.scale)
        p.setPen(pen)

        # draw a cross at the cursor position
        p.drawLine(QPointF(0.0, _y), QPointF(_w, _y))  # horrizontal line
        p.drawLine(QPointF(_x, 0.0), QPointF(_x, _h))  # horrizontal line

    def _paint_current_mode(self):
        """draws the text at the bottom"""
        p = self.painter

        screensize = QPointF(self.width(), self.height()) / self.scale

        x = screensize.x() * 0.02
        y = screensize.y() * 0.98

        _pen = p.pen()
        _font = p.font()

        pen = QPen()
        pen.setWidthF(10 / self.scale)
        pen.setCapStyle(Qt.RoundCap)
        pen.setColor(QColor(255, 0, 0))
        font = QFont()
        font.setPointSizeF(font.pointSize() / self.scale)

        p.setPen(pen)
        p.setFont(font)

        if self.move_mode:
            text = "MOVE"
        elif self.draw_stereocilia_mode:
            text = "DRAW STEREOCILIA"
        elif self.edit_stereocilia_mode:
            text = "EDIT STEREOCILIA"
        else:
            raise RuntimeError("UNKOWN MODE")

        p.drawText(QPointF(x, y), text)

        p.setPen(_pen)
        p.setFont(_font)

    def _paint_potential_vert(self):
        if not self._potential_new_vert:
            return

        p = self.painter
        pen = QPen()
        pen.setWidthF(6 / self.scale)
        color = QColor('yellow')
        pen.setColor(color)

        p.setPen(pen)

        p.drawPoint(self._potential_new_vert + self._pixmap_offset)

    def _paint_polygon_buffer(self):
        if not self.polygon_buffer:
            return

        p = self.painter
        pen = QPen()
        pen.setWidthF(2 / self.scale)
        color = QColor('red')
        pen.setColor(color)

        verts = [v + self._pixmap_offset for v in self.polygon_buffer]
        if self._draw_mouse_position:
            verts += [self._draw_mouse_position + self._pixmap_offset]

        p.setPen(pen)
        p.drawConvexPolygon(verts)

        pen.setColor(QColor(255, 255, 255))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidthF(5 / self.scale)
        p.setPen(pen)
        for point in verts:
            p.drawPoint(point)

        pen.setColor(QColor(0, 0, 0))
        pen.setCapStyle(Qt.RoundCap)
        pen.setWidthF(4 / self.scale)
        p.setPen(pen)
        for point in verts:
            p.drawPoint(point)

    def _paint_stereocilia(self):
        if self.pixmap is not None and self.active_image is not None:
            p = self.painter
            pen = QPen()
            pen.setWidthF(2 / self.scale)
            color = QColor('green')
            pen.setColor(color)
            p.setPen(pen)


            if not self.edit_stereocilia_mode:
                for s in self.active_image.get_stereocilia():
                    s.paint(p, self._pixmap_offset, {'scale': self.scale})
            else:
                if any(s.is_selected() for s in self.active_image.get_stereocilia()):
                    for s in self.active_image.get_stereocilia():
                        if s.is_selected():
                            s.paint(p, self._pixmap_offset, {'scale': self.scale})
                else:
                    for s in self.active_image.get_stereocilia():
                        s.paint(p, self._pixmap_offset, {'scale': self.scale})

    def _paint_pixmap(self):
        """paints the image to QLabel"""
        if self.pixmap is not None:
            p = self.painter
            p.drawPixmap(self._pixmap_offset, self.pixmap)
            p.setClipping(True)
