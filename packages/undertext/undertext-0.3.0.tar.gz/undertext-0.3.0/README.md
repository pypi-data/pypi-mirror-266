# undertext
library to load, edit and save different formats of subtitles

[![PyPI - Version](https://img.shields.io/pypi/v/undertext)
](https://pypi.org/project/undertext/)

> [!NOTE]
> This Project is under development. Come back soon for updates

<!-- TOC -->
* [undertext](#undertext)
  * [Installation](#installation)
  * [File Formats](#file-formats)
  * [Examples](#examples)
  * [CLI](#cli)
<!-- TOC -->

## Installation

```shell
pip3 install undertext
```

## File Formats

| ext    | name                      | read  | write | Flags |
|--------|---------------------------|-------|-------|-------|
| `.ass` | Advanced SubStation Alpha | ❌     | ❌     | TT    |
| `.sbv` | SubViewer                 | ✅     | ✅     | TT    |
| `.srt` | SubRip                    | ✅     | ✅     | TT    |
| `.ssa` | Sub Station Alpha         | ❌     | ❌     | TT    |
| `.sub` | MicroDVD                  | ✅     | ✅     | TF    |
| `.vtt` | WebVTT                    | ✅     | ✅     | TT    |

<small>Listed formats that are currently unsupported may be added at a later version</small>

Flag Information:
```text
T. = Text Based
B. = Bitmap Based
.T = Time-Based
.F = Frame-Based
```

## Examples

```python
import undertext

captions = undertext.loads("example.en.srt")
undertext.dumps(captions, "example.en.vtt")
```

```python
import undertext

captions = [
    undertext.Caption(start=0, end=10, text="Hello"),
    undertext.Caption(start=10, end=20, text="World"),
]
undertext.dumps(captions, "out.srt")
```

## CLI

> [!NOTE]
> During the installation the `undertext` command should be installed and then available.
> If this didn't work you can invoke it with `python3 -m undertext` instead.

```shell
$ cat example.vtt
WEBVTT

00:00:00.000 --> 00:00:01.000
hello world 0

00:00:02.000 --> 00:00:03.000
hello world 2

00:00:04.000 --> 00:00:05.000
hello world 4

00:00:06.000 --> 00:00:07.000
hello world 6

00:00:08.000 --> 00:00:09.000
hello world 8
$ undertext read example.vtt
<00:00:00.000 -> 00:00:01.000> 'hello world 0'
<00:00:02.000 -> 00:00:03.000> 'hello world 2'
<00:00:04.000 -> 00:00:05.000> 'hello world 4'
<00:00:06.000 -> 00:00:07.000> 'hello world 6'
<00:00:08.000 -> 00:00:09.000> 'hello world 8'
```
```shell
$ undertext convert example.vtt output.srt 
$ cat output.srt
1
00:00:00,000 --> 00:00:01,000
hello world 0

2
00:00:02,000 --> 00:00:03,000
hello world 2

3
00:00:04,000 --> 00:00:05,000
hello world 4

4
00:00:06,000 --> 00:00:07,000
hello world 6

5
00:00:08,000 --> 00:00:09,000
hello world 8
```
