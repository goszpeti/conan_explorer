"""
Test the self written qt gui components, which can be instantiated without
using the whole application (standalone).
"""
from pathlib import Path

import conan_app_launcher.app as app  # using gobal module pattern
from conan_app_launcher.ui import main_window
from conans.model.ref import ConanFileReference
from PyQt5 import QtCore, QtWidgets

Qt = QtCore.Qt
TEST_REF = "zlib/1.2.11@_/_"

# For debug:
# from pytestqt.plugin import _qapp_instance
# while True:
#    _qapp_instance.processEvents()



def test_pkgs_sel_view(ui_no_refs_config_fixture, qtbot, mocker):
    cfr = ConanFileReference.loads(TEST_REF)
    pkg_path = app.conan_api.get_path_or_install(cfr)
    main_gui = main_window.MainWindow()
    main_gui.show()
    main_gui.load(ui_no_refs_config_fixture)

    qtbot.addWidget(main_gui)
    qtbot.waitExposed(main_gui, timeout=3000)

    main_gui.ui.main_toolbox.setCurrentIndex(1) # changes to local explorer page
    model = main_gui.local_package_explorer.pkg_sel_model
    assert model
    assert main_gui.ui.package_select_view.findChildren(QtCore.QObject)
    assert main_gui.ui.package_select_view.model().columnCount() == 1

    model.rootItem.itemData[0] == "Packages"
    model.rootItem.childCount() == main_gui.ui.package_select_view.model().rowCount()

    found_tst_pkg = False
    for pkg in model.rootItem.childItems:
        if pkg.itemData[0] == str(cfr):
            found_tst_pkg = True
            # check it's child
            assert pkg.child(0).data(0) in ["Windows_x64_vs16_release", "Linux_x64_gcc9_release"]
    assert found_tst_pkg
    # select package (ref, not profile)
    index = model.index(0, 0, QtCore.QModelIndex())
    item = index.internalPointer()
    for i in range(model.rootItem.childCount()):
        index = model.index(i, 0, QtCore.QModelIndex())
        item = model.index(i, 0, QtCore.QModelIndex()).internalPointer()
        print(item.itemData[0])
        if item.itemData[0] == str(cfr):
            break
    view_model = main_gui.ui.package_select_view.model()
    sel_model = main_gui.ui.package_select_view.selectionModel()
    sel_model.select(view_model.mapFromSource(
        index), QtCore.QItemSelectionModel.ClearAndSelect)
    sel_model.currentIndex()
    assert not main_gui.local_package_explorer.fs_model  # view not changed

    # check right view initialized at the correct path and path got written in label
    main_gui.ui.package_select_view.expand(view_model.mapFromSource(index))
    chi = index.child(0, 0)
    item = chi.internalPointer()
    sel_model.select(view_model.mapFromSource(chi), QtCore.QItemSelectionModel.ClearAndSelect)
    main_gui.ui.package_select_view.selectionModel().currentRowChanged.emit(
        index, chi)

    assert main_gui.local_package_explorer.fs_model  # view selected
    assert Path(main_gui.local_package_explorer.fs_model.rootPath()) == pkg_path
