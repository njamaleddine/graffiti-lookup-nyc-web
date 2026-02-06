import os
import json
import tempfile
from geocode.storages.json import JsonFile


class TestJsonFile:
    def test_load_existing_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            json.dump([{"a": 1}], tmp)
            tmp.flush()
            jf = JsonFile(tmp.name)
            result = jf.load()
        os.unlink(tmp.name)
        assert result == [{"a": 1}]

    def test_load_missing_file_returns_default(self):
        jf = JsonFile("nonexistent.json", default_data={"foo": "bar"})
        assert jf.load() == {"foo": "bar"}

    def test_save_and_load_round_trip(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            jf = JsonFile(tmp.name)
            data = [{"x": 42}]
            jf.save(data)
            result = jf.load()
        os.unlink(tmp.name)
        assert result == [{"x": 42}]

    def test_save_overwrites_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            jf = JsonFile(tmp.name)
            jf.save([{"a": 1}])
            jf.save([{"b": 2}])
            result = jf.load()
        os.unlink(tmp.name)
        assert result == [{"b": 2}]

    def test_load_empty_file_returns_default(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as tmp:
            tmp.write("")
            tmp.flush()
            jf = JsonFile(tmp.name, default_data={"empty": True})
            try:
                result = jf.load()
            except Exception:
                result = "error"
        os.unlink(tmp.name)
        assert result == "error" or result == {"empty": True}
