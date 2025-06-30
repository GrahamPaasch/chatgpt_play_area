# Sheet Music Accompaniment Generator

This repository contains a Python script for generating a simple piano accompaniment from scanned sheet music.

The script uses optical music recognition via the `oemer` library to convert images or PDFs of scores into MusicXML, analyzes the chords with `music21`, and outputs a new score with a basic accompaniment part.

## Usage

```
python3 sheet_accompaniment.py path/to/score.pdf
```

Outputs `output.mid` and `output_with_accompaniment.musicxml` in the current directory.
