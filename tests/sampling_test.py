import pytest
import os
from PIL import Image
from PyQt5.QtWidgets import QMessageBox
from image_quality_sampler.GUI.views.image_sampling_view import (
    ImageSamplingView,
)


@pytest.fixture
def setup_view(qtbot, mocker, tmpdir):
    central_view_mock = mocker.MagicMock()
    # Create some dummy images in the temporary directory
    for i in range(5):
        img = Image.new("RGB", (60, 30), color=(73, 109, 137))
        img_path = os.path.join(str(tmpdir), f"image_{i}.jpg")
        img.save(img_path)
    view = ImageSamplingView(str(tmpdir), 5, 3, central_view_mock)
    view.exit_flag = False
    qtbot.addWidget(view)
    return view


def test_initialization(setup_view, tmpdir):
    view = setup_view
    assert view.folder_path == str(tmpdir)
    assert view.sample_size == 5
    assert view.rejection_size == 3
    assert len(view.images) == 5


def test_display_image(setup_view):
    view = setup_view

    view.display_image()

    # Check if metadata label is updated correctly
    assert "File type: JPEG" in view.metadata_label.text()

    # Check progression and rejection counters
    assert view.progressionLabel.text() == "Progression: 1/5"
    assert view.rejectionsLabel.text() == "Rejections: 0/3"


def test_accept_image(mocker, setup_view):
    view = setup_view

    # Mock QMessageBox to prevent it from showing
    mocker.patch.object(QMessageBox, "information")

    # Accept the first image
    view.accept_image()

    # Check progression counter
    assert view.progressionLabel.text() == "Progression: 2/5"

    # Accept all remaining images
    for _ in range(4):
        view.accept_image()

    # Check if all images have been processed
    assert not view.exit_flag


def test_reject_image(mocker, setup_view):
    view = setup_view

    # Mock QMessageBox to prevent it from showing
    mocker.patch.object(QMessageBox, "warning")

    # Reject the first image
    view.reject_image()

    # Check rejection counter
    assert view.rejectionsLabel.text() == "Rejections: 1/3"

    # Reject until the rejection limit is reached
    view.reject_image()
    view.reject_image()

    # Check if the batch has been rejected
    assert view.rejections == 3


def test_zoom_in(setup_view):
    view = setup_view
    initial_zoom = view.graphics_view.transform().m11()
    view.zoom_in()
    assert view.graphics_view.transform().m11() > initial_zoom


def test_zoom_out(setup_view):
    view = setup_view
    initial_zoom = view.graphics_view.transform().m11()
    view.zoom_out()
    assert view.graphics_view.transform().m11() < initial_zoom


def test_zoom_1_1(setup_view):
    view = setup_view
    view.zoom_1_1()
    assert view.graphics_view.transform().m11() == 1.0


def test_close_event(mocker, setup_view):
    view = setup_view
    view.exit_flag = True
    # Mock QMessageBox to simulate user clicking "Yes" to confirm exit
    mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.Yes)

    # Trigger the close event
    event = mocker.MagicMock()
    view.closeEvent(event)

    # Check if the event was accepted (meaning the window was closed)
    assert event.accept.called

    # Check if the main window is shown
    assert view.main_window.show.called


def test_close_event_ignore(mocker, setup_view):
    view = setup_view
    view.exit_flag = True
    # Mock QMessageBox to simulate user clicking "Yes" to confirm exit
    mocker.patch.object(QMessageBox, "question", return_value=QMessageBox.No)

    # Trigger the close event
    event = mocker.MagicMock()
    view.closeEvent(event)

    # Check if the event was accepted (meaning the window was closed)
    assert event.ignore.called
