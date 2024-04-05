import pathlib
import runpy
import sys


def test_invoke_sample(tmp_path, monkeypatch):
    sample = pathlib.Path('tests/sample.tar.zst')
    monkeypatch.setattr(
        sys,
        'argv',
        ['', '--extract', str(sample.resolve()), '--out-dir', str(tmp_path)],
    )
    runpy.run_module('jaraco.zstd', run_name='__main__')
    assert tmp_path.joinpath('sample.txt').read_text(encoding='utf-8') == 'hello zstd\n'
