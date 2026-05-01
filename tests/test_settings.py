from pathlib import Path

from slidedrop.settings import SessionSettings, SettingsStore


def test_settings_round_trip(tmp_path: Path) -> None:
    store = SettingsStore(tmp_path / "settings.json")
    settings = SessionSettings(
        last_used_folder=tmp_path,
        libreoffice_path=tmp_path / "soffice.exe",
        open_output_when_finished=True,
        conversion_timeout_seconds=120,
        skip_if_unchanged=True,
        export_speaker_notes=False,
    )

    store.save(settings)
    loaded = store.load()

    assert loaded.last_used_folder == tmp_path
    assert loaded.libreoffice_path == tmp_path / "soffice.exe"
    assert loaded.open_output_when_finished is True
    assert loaded.conversion_timeout_seconds == 120
    assert loaded.skip_if_unchanged is True
    assert loaded.export_speaker_notes is False
