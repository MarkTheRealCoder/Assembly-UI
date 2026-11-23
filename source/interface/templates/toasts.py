from typing import Literal

from PyQt5.QtCore import QMargins, QSize
from PyQt5.QtGui import QFont
from pyqttoast import ToastPreset, ToastPosition

from source.platform import Desktop


def run_toast_config(parent):
    """Make toasts appear relative to the parent widget, on its screen."""
    from pyqttoast import Toast
    Toast.setAlwaysOnMainScreen(False)
    Toast.setPositionRelativeToWidget(parent)

def _scale_toast(toast, parent):
    """Scale the sizes, margins and fonts of the toast by the scale factor of the parent's screen."""
    factor = Desktop.getScaleFactor(parent)

    def scaled(value: int) -> int:
        return round(value * factor)

    def scaled_size(size: QSize) -> QSize:
        return QSize(scaled(size.width()), scaled(size.height()))

    def scaled_margins(margins: QMargins) -> QMargins:
        return QMargins(scaled(margins.left()), scaled(margins.top()), scaled(margins.right()), scaled(margins.bottom()))

    def scaled_font(font: QFont) -> QFont:
        result = QFont(font)
        result.setPointSizeF(font.pointSizeF() * factor * Desktop.getPointScale())
        return result

    toast.setIconSize(scaled_size(toast.getIconSize()))
    toast.setIconSeparatorWidth(max(1, scaled(toast.getIconSeparatorWidth())))
    toast.setCloseButtonIconSize(scaled_size(toast.getCloseButtonIconSize()))
    toast.setCloseButtonSize(scaled_size(toast.getCloseButtonSize()))
    toast.setBorderRadius(scaled(toast.getBorderRadius()))
    toast.setMargins(scaled_margins(toast.getMargins()))
    toast.setIconMargins(scaled_margins(toast.getIconMargins()))
    toast.setIconSectionMargins(scaled_margins(toast.getIconSectionMargins()))
    toast.setTextSectionMargins(scaled_margins(toast.getTextSectionMargins()))
    toast.setCloseButtonMargins(scaled_margins(toast.getCloseButtonMargins()))
    toast.setTextSectionSpacing(scaled(toast.getTextSectionSpacing()))
    toast.setTitleFont(scaled_font(toast.getTitleFont()))
    toast.setTextFont(scaled_font(toast.getTextFont()))

def create_toast(parent, text: str, _type: Literal["success", "error", "warning"] = "success"):
    """Show a toast with the text and the style of the given type."""
    from pyqttoast import Toast
    toast = Toast(parent)
    preset = ToastPreset.SUCCESS_DARK
    title = "Action succeded!"
    if _type == "error":
        preset = ToastPreset.ERROR_DARK
        title = "Action failed!"
    elif _type == "warning":
        title = "Warning!"
        preset = ToastPreset.WARNING_DARK
    toast.setPosition(ToastPosition.TOP_MIDDLE)
    toast.setTitle(title)
    toast.applyPreset(preset)
    _scale_toast(toast, parent)
    toast.setText(text)
    toast.show()

def toast_safe_exec(window, call: callable, *args, **kwargs) -> callable:
    """Return a function that runs call and shows an error toast instead of raising."""
    def safe_exec():
        try:
            return call(*args, **kwargs)
        except Exception as e:
            create_toast(window, f"An error occurred: {str(e)}", "error")
            return None
    return safe_exec

