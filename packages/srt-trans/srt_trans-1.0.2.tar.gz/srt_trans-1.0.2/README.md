# srt_trans
## Translage any SubRip file from any source language to any target language, and merger them into the target SubRip(.srt) file.

# How to usage:

```bash
Usage: srt_trans test_file.srt [-src_lang en -dest_lang zh-CN -proxy http://youdomain:your_port]
Example:
    srt_trans ./test_video.mkv
    srt_trans ./test_video.mkv -src_lang en -dest_lang zh-TW
    srt_trans ./test_video.mkv -src_lang en -dest_lang zh-CN -proxy http://127.0.0.1:8118
    srt_trans ./test/test_file.srt
    srt_trans ./test/test_file.srt -src_lang en -dest_lang zh-TW
    srt_trans ./test/test_file.srt -src_lang en -dest_lang ja
    srt_trans ./test/test_file.srt -src_lang en -dest_lang zh-CN
    srt_trans ./test/test_file.srt -src_lang en -dest_lang fr -proxy http://127.0.0.1:8118
```

# Package
```bash
pip install wheel
python setup.py sdist bdist_wheel
```

# Publish to pypi
```bash
pip install twine
twine upload dist/*
```

# Installation
## srt_trans is available on pypi. To intall it you can:
```bash
sudo pip install srt_trans
```