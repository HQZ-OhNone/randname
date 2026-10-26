"""
Copyright (C) 2026 HQZ-OhNone <ohnone_hqz@outlook.com>

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.
"""

"""主题背景图层：自动裁切、渐变模糊与菜单/状态栏阴影。"""

from math import ceil

from PySide6.QtCore import QRect, QRectF, QTimer, Qt
from PySide6.QtGui import (
    QColor,
    QImage,
    QLinearGradient,
    QPainter,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QGraphicsBlurEffect,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QWidget,
)


def cover_source_rect(src_width: int, src_height: int, target_width: int, target_height: int) -> QRect:
    """返回 cover 裁切时从原图取用的矩形。"""
    src_width = max(1, int(src_width))
    src_height = max(1, int(src_height))
    target_width = max(1, int(target_width))
    target_height = max(1, int(target_height))
    if src_width * target_height > src_height * target_width:
        width = max(1, round(src_height * target_width / target_height))
        height = src_height
        x = (src_width - width) // 2
        y = 0
    else:
        width = src_width
        height = max(1, round(src_width * target_height / target_width))
        x = 0
        y = (src_height - height) // 2
    return QRect(x, y, width, height)


def contain_target_rect(src_width: int, src_height: int, target_width: int, target_height: int) -> QRect:
    """返回 contain 模式中图片在目标区域内的居中矩形。"""
    src_width = max(1, int(src_width))
    src_height = max(1, int(src_height))
    target_width = max(1, int(target_width))
    target_height = max(1, int(target_height))
    scale = min(target_width / src_width, target_height / src_height)
    width = max(1, int(round(src_width * scale)))
    height = max(1, int(round(src_height * scale)))
    return QRect((target_width - width) // 2, (target_height - height) // 2, width, height)


class BackgroundWidget(QWidget):
    """铺在中央区域底层的背景图层。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._config = None
        self._source = QPixmap()
        self._cache = QPixmap()
        self._cache_key = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._rebuild)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # ------------------------------------------------------------------ public
    def set_background(self, config: dict | None):
        """设置背景；传入 None 表示关闭。"""
        if not config:
            self.clear()
            return
        path = config.get("path", "")
        pixmap = QPixmap(str(path)) if path else QPixmap()
        if pixmap.isNull():
            self.clear()
            return
        self._config = dict(config)
        self._source = pixmap
        self._cache_key = None
        self._schedule(immediate=True)

    def clear(self):
        self._config = None
        self._source = QPixmap()
        self._cache = QPixmap()
        self._cache_key = None
        self._timer.stop()
        self.update()

    def clear_cache(self):
        """保留图片，只丢弃重建缓存。"""
        self._cache = QPixmap()
        self._cache_key = None
        self._schedule(immediate=True)

    def has_image(self) -> bool:
        return self._config is not None and not self._source.isNull()

    # ------------------------------------------------------------------ events
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.has_image():
            self._schedule()

    def paintEvent(self, event):
        if not self.has_image() or self._cache.isNull():
            return
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.setOpacity(float(self._config.get("opacity", 1.0)))
            painter.drawPixmap(0, 0, self._cache)
            painter.setOpacity(1.0)
            dim = float(self._config.get("dim", 0.0))
            if dim > 0:
                painter.fillRect(self.rect(), QColor(0, 0, 0, int(round(dim * 255))))
            self._draw_shadows(painter)
        finally:
            painter.end()

    # ------------------------------------------------------------------ build
    def _schedule(self, immediate: bool = False):
        self._timer.start(0 if immediate else 120)

    def _rebuild(self):
        if not self.has_image():
            return
        width = self.width()
        height = self.height()
        if width <= 0 or height <= 0:
            return
        dpr = max(1.0, float(self.devicePixelRatioF()))
        target_width = max(1, int(round(width * dpr)))
        target_height = max(1, int(round(height * dpr)))
        config = self._config or {}
        key = (
            self._source.cacheKey(),
            target_width,
            target_height,
            config.get("fit_mode"),
            config.get("blur_radius"),
            config.get("blur_direction"),
        )
        if key == self._cache_key and not self._cache.isNull():
            return
        sharp = self._fit_pixmap(target_width, target_height, str(config.get("fit_mode", "cover")))
        radius = float(config.get("blur_radius", 0.0)) * dpr
        if radius > 0:
            blurred = self._blur_pixmap(sharp, radius)
        else:
            blurred = sharp
        direction = str(config.get("blur_direction", "uniform"))
        if radius <= 0 or direction == "uniform":
            result = blurred
        else:
            result = self._gradient_blend(sharp, blurred, direction)
        result.setDevicePixelRatio(dpr)
        self._cache = result
        self._cache_key = key
        self.update()

    def _fit_pixmap(self, target_width: int, target_height: int, fit_mode: str) -> QPixmap:
        source = self._source
        if fit_mode == "cover":
            rect = cover_source_rect(source.width(), source.height(), target_width, target_height)
            return source.copy(rect).scaled(
                target_width,
                target_height,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        canvas = QPixmap(target_width, target_height)
        canvas.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas)
        try:
            if fit_mode == "tile":
                painter.drawTiledPixmap(0, 0, target_width, target_height, source)
            elif fit_mode == "center":
                x = (target_width - source.width()) // 2
                y = (target_height - source.height()) // 2
                painter.drawPixmap(x, y, source)
            else:  # contain
                rect = contain_target_rect(
                    source.width(), source.height(), target_width, target_height
                )
                painter.drawPixmap(
                    rect,
                    source.scaled(
                        rect.size(),
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    ),
                )
        finally:
            painter.end()
        return canvas

    @staticmethod
    def _blur_pixmap(pixmap: QPixmap, radius: float) -> QPixmap:
        """用 QGraphicsBlurEffect 渲染模糊图，四周留边避免边缘变暗。"""
        if radius <= 0:
            return pixmap
        pad = int(ceil(radius)) + 2
        width = pixmap.width()
        height = pixmap.height()
        padded = QImage(
            width + pad * 2,
            height + pad * 2,
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        padded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(padded)
        try:
            painter.drawPixmap(pad, pad, pixmap)
        finally:
            painter.end()

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(QPixmap.fromImage(padded))
        effect = QGraphicsBlurEffect()
        effect.setBlurRadius(radius)
        effect.setBlurHints(QGraphicsBlurEffect.BlurHint.QualityHint)
        item.setGraphicsEffect(effect)
        scene.addItem(item)
        scene_rect = QRectF(0, 0, padded.width(), padded.height())
        scene.setSceneRect(scene_rect)

        result = QImage(padded.size(), QImage.Format.Format_ARGB32_Premultiplied)
        result.fill(Qt.GlobalColor.transparent)
        painter = QPainter(result)
        try:
            scene.render(painter, scene_rect, scene_rect)
        finally:
            painter.end()
        return QPixmap.fromImage(result.copy(pad, pad, width, height))

    @staticmethod
    def _gradient_blend(sharp: QPixmap, blurred: QPixmap, direction: str) -> QPixmap:
        width = sharp.width()
        height = sharp.height()
        masked = blurred.copy()
        painter = QPainter(masked)
        try:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
            if direction == "horizontal":
                gradient = QLinearGradient(0, 0, width, 0)
            elif direction == "vertical":
                gradient = QLinearGradient(0, 0, 0, height)
            elif direction == "diagonal":
                gradient = QLinearGradient(0, 0, width, height)
            else:
                center = QRectF(0, 0, width, height).center()
                limit = (width * width + height * height) ** 0.5 / 2.0
                gradient = QRadialGradient(center, max(1.0, limit))
            if direction == "out-center":
                gradient.setColorAt(0.0, QColor(255, 255, 255, 255))
                gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
            else:
                gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
                gradient.setColorAt(1.0, QColor(255, 255, 255, 255))
            painter.fillRect(0, 0, width, height, gradient)
        finally:
            painter.end()
        result = sharp.copy()
        painter = QPainter(result)
        try:
            painter.drawPixmap(0, 0, masked)
        finally:
            painter.end()
        return result

    def _draw_shadows(self, painter: QPainter):
        config = self._config or {}
        size = float(config.get("shadow_size", 0.0))
        opacity = float(config.get("shadow_opacity", 0.0))
        if size <= 0 or opacity <= 0:
            return
        alpha = int(round(max(0.0, min(1.0, opacity)) * 255))
        width = self.width()
        height = self.height()
        band = max(1, int(round(size)))
        painter.setOpacity(1.0)

        top = QLinearGradient(0, 0, 0, band)
        top.setColorAt(0.0, QColor(0, 0, 0, alpha))
        top.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(QRect(0, 0, width, band), top)

        bottom = QLinearGradient(0, height - band, 0, height)
        bottom.setColorAt(0.0, QColor(0, 0, 0, 0))
        bottom.setColorAt(1.0, QColor(0, 0, 0, alpha))
        painter.fillRect(QRect(0, height - band, width, band), bottom)


__all__ = ["BackgroundWidget", "cover_source_rect", "contain_target_rect"]
