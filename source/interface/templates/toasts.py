from typing import Literal

from pyqttoast import ToastPreset, ToastPosition


def run_toast_config(parent):
    from pyqttoast import Toast
    Toast.setAlwaysOnMainScreen(False)
    Toast.setPositionRelativeToWidget(parent)

def create_toast(parent, text: str, _type: Literal["success", "error", "warning"] = "success"):
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
    toast.setText(text)
    toast.show()