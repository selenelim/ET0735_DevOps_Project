import pytest
from unittest.mock import patch, MagicMock
import burglar_detection  # This is your script

def test_sound_buzzer(monkeypatch):
    # Track GPIO output calls
    output_calls = []
    monkeypatch.setattr(burglar_detection.GPIO, "output", lambda pin, state: output_calls.append((pin, state)))
    monkeypatch.setattr(burglar_detection.time, "sleep", lambda x: None)

    burglar_detection.sound_buzzer(duration=1)

    assert output_calls == [(burglar_detection.BUZZER_PIN, True), (burglar_detection.BUZZER_PIN, False)]

@patch("burglar_detection.camera.capture")
def test_capture_image(mock_capture):
    result = burglar_detection.capture_image("test.jpg")
    mock_capture.assert_called_once_with("test.jpg")
    assert result == "test.jpg"

@patch("builtins.open", new_callable=pytest.mock.mock_open, read_data=b"fake-image-data")
@patch("burglar_detection.smtplib.SMTP_SSL")
def test_send_email(mock_smtp_ssl, mock_open):
    mock_smtp = MagicMock()
    mock_smtp_ssl.return_value.__enter__.return_value = mock_smtp

    burglar_detection.send_email("intruder.jpg")

    assert mock_smtp.login.called
    assert mock_smtp.send_message.called

@patch("burglar_detection.GPIO.input", return_value=0)  # Simulate intrusion detected
@patch("burglar_detection.sound_buzzer")
@patch("burglar_detection.capture_image", return_value="image.jpg")
@patch("burglar_detection.send_email")
def test_monitor_breach_once(mock_send_email, mock_capture, mock_buzzer, mock_gpio_input):
    # Force monitor_breach to exit after one loop iteration
    with patch("burglar_detection.time.sleep", side_effect=KeyboardInterrupt):
        with pytest.raises(KeyboardInterrupt):
            burglar_detection.monitor_breach()

    mock_buzzer.assert_called_once()
    mock_capture.assert_called_once()
    mock_send_email.assert_called_once_with("image.jpg")
