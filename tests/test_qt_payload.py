import pytest

from distribution.qt_payload import filter_collected, forbidden_family, inspect_tree


@pytest.mark.parametrize(
    "path",
    [
        "PySide6.QtCharts",
        "_internal/PySide6/Qt6Graphs.dll",
        "_internal/PySide6/qml/QtQuick3D/qmldir",
        "PySide6/qml/QtQuick/Timeline/BlendTrees/plugins.qmltypes",
        "PySide6/qml/QtQuick/VirtualKeyboard/Styles/style.qml",
        "PySide6/QtDataVisualization.pyd",
        "PySide6/QtQuick3D.pyi",
        "PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll",
        "PySide6/plugins/qmltooling/qmldbg_quick3dprofiler.dll",
    ],
)
def test_forbidden_qt_includes_plugins_qml_data_and_python(path, tmp_path):
    assert forbidden_family(path)
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"reintroduced component")
    with pytest.raises(ValueError, match="reintroduced"):
        inspect_tree(tmp_path)


@pytest.mark.parametrize(
    "path",
    [
        "PySide6/Qt6Quick.dll",
        "PySide6/Qt6Qml.dll",
        "PySide6/QtShaderTools.pyd",
        "PySide6/qml/Qt3D/Core/quick3dcoreplugin.dll",
        "PySide6/qml/Qt5Compat/GraphicalEffects/qtgraphicaleffectsplugin.dll",
        "PySide6/QtWebEngineCore.pyd",
        "PySide6/plugins/platforms/qwindows.dll",
    ],
)
def test_required_or_unresolved_components_are_not_removed_by_name(path):
    assert not forbidden_family(path)
    assert filter_collected([(path, "destination")]) == [(path, "destination")]


def test_python_module_guard(tmp_path):
    with pytest.raises(ValueError, match="QtCharts"):
        inspect_tree(tmp_path, ["PySide6.QtCharts"])
