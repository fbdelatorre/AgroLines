import pytest

from distribution.qt_payload import (
    assert_widget_deployment,
    filter_collected,
    forbidden_family,
    inspect_tree,
    omit_system_copies,
)


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


def test_qml_debug_server_is_not_a_release_dependency(tmp_path):
    path = "PySide6/plugins/qmltooling/qmldbg_server.dll"
    assert filter_collected([(path, "PySide6/plugins/qmltooling")]) == []
    file = tmp_path / path
    file.parent.mkdir(parents=True)
    file.write_bytes(b"inert reintroduced debugger fixture")
    with pytest.raises(ValueError, match="reintroduced"):
        inspect_tree(tmp_path)


def test_external_qml_cannot_return_without_deployment_review(tmp_path):
    file = tmp_path / "PySide6/qml/QtQuick/Controls/qmldir"
    file.parent.mkdir(parents=True)
    file.write_text("module QtQuick.Controls")
    with pytest.raises(ValueError, match="reintroduced"):
        inspect_tree(tmp_path)


@pytest.mark.parametrize(
    "source",
    [
        "from PySide6.QtQml import QQmlEngine",
        "from PySide6 import QtQml",
        "import PySide6.QtQuickWidgets",
    ],
)
def test_new_qml_ui_requires_explicit_deployment_review(tmp_path, source):
    directory = tmp_path / "desktop"
    directory.mkdir()
    (directory / "future.py").write_text(source)
    with pytest.raises(ValueError, match="deployment review"):
        assert_widget_deployment(tmp_path)


def test_system_runtime_exclusion_is_exact_and_does_not_remove_msvc(tmp_path):
    from types import SimpleNamespace

    from scripts.native_inventory import file_hash

    source = tmp_path / "ucrtbase.dll"
    source.write_bytes(b"inert fixture, not a Windows runtime")
    analysis = SimpleNamespace(
        binaries=[
            ("ucrtbase.dll", str(source), "BINARY"),
            ("vcruntime140.dll", "untouched-msvc", "BINARY"),
        ]
    )
    retired = {"files": [{"destination": "ucrtbase.dll", "sha256": file_hash(source)}]}
    omit_system_copies(analysis, retired)
    assert analysis.binaries == [("vcruntime140.dll", "untouched-msvc", "BINARY")]
    analysis.binaries.append(("ucrtbase.dll", str(source), "BINARY"))
    source.write_bytes(b"changed bytes")
    with pytest.raises(ValueError, match="changed"):
        omit_system_copies(analysis, retired)
