import pytest
import os
from PyQt5.QtWidgets import QApplication
import PyQt5
from PIL import Image
from image_quality_sampler.GUI.views.central_view import CentralView
from image_quality_sampler.GUI.dialogs.sampling_initialization_dialog import (
    SamplingInitializationView,
)


# This fixture ensures that tests run in the QApplication event loop
@pytest.fixture(scope="module")
def app():
    return QApplication([])


def test_central_view_title(qtbot):
    window = CentralView()
    qtbot.addWidget(window)
    assert window.windowTitle() == "AMS Quality Control Interface"


def test_central_view_default_size(qtbot):
    window = CentralView()
    qtbot.addWidget(window)
    assert window.size().width() == 800
    assert window.size().height() == 600


def test_menu_bar_exists(qtbot):
    window = CentralView()
    qtbot.addWidget(window)
    assert window.menuBar() is not None


def test_file_menu_exists(qtbot):
    window = CentralView()
    qtbot.addWidget(window)
    assert window.menuBar().actions()[0].text() == "File"


def test_start_sampling_action_exists(qtbot):
    window = CentralView()
    qtbot.addWidget(window)
    file_menu = window.menuBar().actions()[0].menu()
    assert file_menu.actions()[0].text() == "Start Sampling"


def test_open_sampling_initialization_view(qtbot, mocker):
    window = CentralView()
    qtbot.addWidget(window)

    # Mock the SamplingInitializationView class
    mock_sampling_init_view = mocker.patch(
        f"{CentralView.__module__}.SamplingInitializationView", autospec=True
    )

    file_menu = window.menuBar().actions()[0].menu()
    start_sampling_action = file_menu.actions()[0]

    assert not mock_sampling_init_view.called
    start_sampling_action.trigger()
    assert mock_sampling_init_view.called


def test_initialization(qtbot, mocker):
    central_view_mock = mocker.MagicMock()
    view = SamplingInitializationView(central_view_mock)
    qtbot.addWidget(view)

    assert view.folderInput.text() == ""
    assert view.sampleSizeInput.text() == ""
    assert view.rejectionSizeInput.text() == ""


def test_browse_folder(qtbot, mocker):
    central_view_mock = mocker.MagicMock()
    view = SamplingInitializationView(central_view_mock)
    qtbot.addWidget(view)

    mocker.patch(
        "PyQt5.QtWidgets.QFileDialog.getExistingDirectory",
        return_value="/path/to/folder",
    )

    view.browseButton.click()
    assert view.folderInput.text() == "/path/to/folder"


def test_start_sampling_invalid_folder(qtbot, mocker):
    central_view_mock = mocker.MagicMock()
    view = SamplingInitializationView(central_view_mock)
    qtbot.addWidget(view)

    view.folderInput.setText("/invalid/path")

    # Mock the QMessageBox to prevent it from actually showing up
    mocker.patch("PyQt5.QtWidgets.QMessageBox.warning")

    view.startButton.click()

    # Check that the QMessageBox.warning was called with the expected message
    PyQt5.QtWidgets.QMessageBox.warning.assert_called_once_with(
        view, "Error", "Please select a valid folder."
    )


def test_start_sampling_folder_without_images(qtbot, mocker, tmpdir):
    central_view_mock = mocker.MagicMock()
    view = SamplingInitializationView(central_view_mock)
    qtbot.addWidget(view)

    # Use a temporary directory without images
    view.folderInput.setText(str(tmpdir))

    # Mock the QMessageBox to prevent it from actually showing up
    mocker.patch("PyQt5.QtWidgets.QMessageBox.warning")

    view.startButton.click()

    # Check that the QMessageBox.warning was called with the expected message
    PyQt5.QtWidgets.QMessageBox.warning.assert_called_once_with(
        view, "Error", "The selected folder does not contain any images."
    )


def test_start_sampling_invalid_sample_sizes(qtbot, mocker, tmpdir):
    central_view_mock = mocker.MagicMock()
    view = SamplingInitializationView(central_view_mock)
    qtbot.addWidget(view)

    # Create a dummy image in the temporary directory
    with open(tmpdir / "image.jpg", "w") as f:
        f.write("dummy image content")

    # Set a valid folder but invalid sample sizes
    view.folderInput.setText(str(tmpdir))
    view.sampleSizeInput.setText("abc")
    view.rejectionSizeInput.setText("def")

    # Mock the QMessageBox to prevent it from actually showing up
    mocker.patch("PyQt5.QtWidgets.QMessageBox.warning")

    view.startButton.click()

    # Check that the QMessageBox.warning was called with the expected message
    PyQt5.QtWidgets.QMessageBox.warning.assert_called_once_with(
        view, "Error", "Numbers are not valid."
    )


def test_start_sampling_sample_size_greater_than_images(qtbot, mocker, tmpdir):
    central_view_mock = mocker.MagicMock()
    view = SamplingInitializationView(central_view_mock)
    qtbot.addWidget(view)

    # Create a dummy image in the temporary directory
    with open(tmpdir / "image.jpg", "w") as f:
        f.write("dummy image content")

    # Set folder and sample sizes
    view.folderInput.setText(str(tmpdir))
    view.sampleSizeInput.setText("10")
    view.rejectionSizeInput.setText("1")

    # Mock the QMessageBox to prevent it from actually showing up
    mocker.patch("PyQt5.QtWidgets.QMessageBox.warning")

    view.startButton.click()

    # Check that the QMessageBox.warning was called with the expected message
    PyQt5.QtWidgets.QMessageBox.warning.assert_called_once_with(
        view,
        "Error",
        "Sample size cannot be greater than the number of images.",
    )


def test_start_sampling_valid_input(qtbot, mocker, tmpdir):
    central_view_mock = mocker.MagicMock()
    view = SamplingInitializationView(central_view_mock)
    qtbot.addWidget(view)

    # Create some dummy images in the temporary directory
    for i in range(5):
        img = Image.new("RGB", (60, 30), color=(73, 109, 137))
        img_path = os.path.join(str(tmpdir), f"image_{i}.jpg")
        img.save(img_path)

    # Set a valid folder and valid sample and rejection sizes
    view.folderInput.setText(str(tmpdir))
    view.sampleSizeInput.setText("3")
    view.rejectionSizeInput.setText("2")

    # Mock the ImageSamplingView to prevent it from actually showing
    mock = mocker.patch(
        f"{SamplingInitializationView.__module__}.ImageSamplingView",
        autospec=True,
    )

    view.startButton.click()
    mock.assert_called_once_with(
        view.folderInput.text(),
        int(view.sampleSizeInput.text()),
        int(view.rejectionSizeInput.text()),
        central_view_mock,
    )
