import hashlib
import uuid
from datetime import datetime

from PyQt5.Qt import *
def hint_dialog(widget: QWidget, title: str, content: str) -> None:
    """
    display a dialog with choose button
    :param widget: the dialog rely on the father window
    :param icon_path: the dialog icon path
    :param title: the dialog title word
    :param content: the dialog content is used to hint user's
    :return: None
    """
    tip_box = QMessageBox(QMessageBox.Information, title, content)
    #tip_box.setWindowIcon(QIcon(icon_path))
    submit = tip_box.addButton(widget.tr('确定'), QMessageBox.YesRole)
    tip_box.setModal(True)
    tip_box.exec_()
    if tip_box.clickedButton() == submit:
        pass
    else:
        return

def get_md5_str(content: str, encode_type: str, upper_or_lower: int) -> str:
    """
    get md5 encrypt content
    :param content: need to encrypt content
    :param encode_type: the content encode type
    :param upper_or_lower: return the encrypt content format, '1' means return upper string and another numbers means
    return lower string.
    :return: the encrypt content with md5
    example:
    >>get_md5_str('123', 'utf-8', 1)
    >>202CB962AC59075B964B07152D234B70
    >>get_md5_str('123', 'utf-8', 0)
    >>202cb962ac59075b964b07152d234b70
    """
    m = hashlib.md5()
    content = content.encode(encode_type)
    m.update(content)
    if upper_or_lower == 1:
        return m.hexdigest().upper()
    else:
        return m.hexdigest().lower()

def get_uuid1() -> uuid:
    """
    get the uuid str
    :return: the uuid1 object
    """
    return uuid.uuid1()

def get_current_time():
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return dt
