from bondzai.media_handler import save_audio_raw_data, get_audio_raw_data, get_audio_metadata
import tempfile
import pytest
from pathlib import Path
import numpy as np

@pytest.mark.parametrize("fs", [16000, 48000]) 
@pytest.mark.parametrize("nb_channels", [1, 2, 4]) 
@pytest.mark.parametrize("depth", ["short", "long"]) 
@pytest.mark.parametrize("format", [(".wav", "audio/wav"), (".flac", "audio/x-flac")])  # Not test for (".mp3", "audio/mpeg") because lossy
def test_audio(format, depth, nb_channels, fs):
    TOLERANCE = 1e-4
    length = 1024
    bit_depth = 16 if depth == "short" else 32 if format[0] == ".wav" else 24

    with tempfile.TemporaryDirectory() as save_dir:
        data = (np.random.randint(-2 ** (bit_depth - 2), 2 ** (bit_depth - 2), length * nb_channels)).astype(np.float32) / 2 ** (bit_depth - 1)
        data = data.tolist()
        file_path = Path(save_dir) / ("test" + format[0])
        metadata = {"mime": format[1], "sample_rate": fs, "channels": nb_channels, "bit_depth": bit_depth}
        save_audio_raw_data(data, metadata, file_path)
        raw_data = get_audio_raw_data(file_path)
        metadata = get_audio_metadata(file_path)
        assert np.max(np.abs(np.asarray(raw_data) - np.asarray(data))) < TOLERANCE
        assert metadata["channels"] == nb_channels
        assert metadata["sample_rate"] == fs
        assert metadata["mime"] == format[1]
        assert metadata["bit_depth"] == bit_depth
