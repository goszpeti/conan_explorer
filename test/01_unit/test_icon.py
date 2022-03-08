import sys
from pathlib import Path

from conan_app_launcher.ui.common.icon import extract_icon
from conan_app_launcher.ui.common.theming import set_style_sheet_option




def test_qss_helper():
    style_sheet = "text-align:middle"
    result = set_style_sheet_option(style_sheet, "background-color", "#B7B7B7")
    assert "text-align:middle;background-color:#B7B7B7;" in result
    style_sheet = """

    /*
    QSS template
    */
    color: #f8f8ff;
    * {
        color: #f8f8ff;
        font-size:10pt;
        background-color: #202020;
    }
    color: #f8f8ff;
    QTreeView::item:selected {
        border: 1px solid #6699CC;
    }
    QTreeView::item:selected:active{
        background: #6699CC;
    }
    QTreeView::item:selected:!active {
        background: #6699CC;
    }
    QTreeView::branch:closed:has-children {
        image: url(icons:forward_w.png);
    }
    """
    result = set_style_sheet_option(style_sheet, "background-color", "#B7B7B7", "QTreeView::item:selected")
    assert "QTreeView::item:selected {border: 1px solid #6699CC;background-color:#B7B7B7;}" in result



def test_extract_icon_from_exe(tmp_path, qtbot):
    """
    Tests, that an icon is extracted from different file types
    """

    # executable
    icon = extract_icon(Path(sys.executable))
    assert not icon.isNull()

    # textfile
    test_file = Path(tmp_path) / "test.txt"
    with open(test_file, "w") as f:
        f.write("test")
    icon = extract_icon(Path(tmp_path) / "test.txt")
    assert not icon.isNull()

    # non existant file -> null pointer icon
    icon = extract_icon(Path(tmp_path) / "nonexistant")
    assert icon.isNull()
