import os
from typing import List

from pdf2image import convert_from_path
from oemer import Oemer
import music21 as m21


def convert_pdf_to_images(pdf_path: str, output_dir: str = "pdf_pages") -> List[str]:
    """Convert a PDF into a list of image paths."""
    os.makedirs(output_dir, exist_ok=True)
    pages = convert_from_path(pdf_path)
    image_paths = []
    for i, page in enumerate(pages):
        img_path = os.path.join(output_dir, f"page_{i + 1}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)
    return image_paths


def run_omr_on_images(image_paths: List[str], output_xml: str = "score.musicxml") -> str:
    """Run Optical Music Recognition on the given images."""
    oemer = Oemer()
    oemer.process(image_paths, output_xml)
    return output_xml


def generate_chord_accompaniment(score: m21.stream.Score) -> m21.stream.Part:
    """Generate a simple piano accompaniment part from the chords of the score."""
    chords = score.chordify()
    piano_part = m21.stream.Part()
    piano_part.insert(0, m21.instrument.Piano())

    for measure in chords.measures(0, None):
        measure_chords = measure.getElementsByClass(m21.chord.Chord)
        if not measure_chords:
            # Insert a rest if no harmony was detected
            rest = m21.note.Rest()
            rest.duration = m21.duration.Duration(4)
            piano_part.append(rest)
            continue
        # Use the first chord found in the measure
        chord = measure_chords[0]
        new_chord = m21.chord.Chord(chord.pitches)
        new_chord.duration = m21.duration.Duration(4)  # whole note
        piano_part.append(new_chord)
    return piano_part


def create_accompanied_score(score: m21.stream.Score) -> m21.stream.Score:
    """Combine the original score with a generated accompaniment."""
    piano_part = generate_chord_accompaniment(score)
    combined = m21.stream.Score()
    for part in score.parts:
        combined.append(part)
    combined.append(piano_part)
    return combined


def process_input(input_path: str) -> m21.stream.Score:
    """Full pipeline: OCR/OMR the input and generate accompaniment."""
    _, ext = os.path.splitext(input_path)
    if ext.lower() == ".pdf":
        image_paths = convert_pdf_to_images(input_path)
    else:
        image_paths = [input_path]
    xml_path = run_omr_on_images(image_paths)
    score = m21.converter.parse(xml_path)
    accompanied = create_accompanied_score(score)
    return accompanied


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Generate playback and chord accompaniment from sheet music")
    parser.add_argument("input", help="Path to sheet music image or PDF")
    parser.add_argument("--midi", default="output.mid", help="Path for output MIDI file")
    parser.add_argument("--xml", default="output_with_accompaniment.musicxml", help="Path for output MusicXML file")
    args = parser.parse_args()

    score = process_input(args.input)
    score.write("midi", fp=args.midi)
    score.write("musicxml", fp=args.xml)
    print(f"Saved MIDI to {args.midi} and MusicXML to {args.xml}")


if __name__ == "__main__":
    main()
