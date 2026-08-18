"""Getting text out of whatever he hands over.

The bug behind this file: Eyaas attached a lecture `.ppt`, only
`.pdf/.docx/.xlsx` were parsed, and the skip was recorded in a log line and
nowhere a person would look. He found out from a vague answer.

So there are two things to pin down — that the formats actually parse, and
that the ones that cannot say **why** and **what to do instead**. Fixtures are
built here rather than committed as binaries: a `.pptx` is a zip of XML, and a
test that builds one is a test that documents the format.
"""

from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from sidecar.core import extract

# ── fixtures, built rather than committed ─────────────────────────────

_SLIDE = (
    '<?xml version="1.0"?>'
    '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
    ' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
    "<p:cSld><p:spTree>{runs}</p:spTree></p:cSld></p:sld>"
)


def _slide_xml(*texts: str) -> bytes:
    runs = "".join(f"<a:t>{t}</a:t>" for t in texts)
    return _SLIDE.format(runs=runs).encode("utf-8")


def _pptx(tmp_path: Path, slides: list[list[str]], notes: list[str] | None = None) -> Path:
    target = tmp_path / "deck.pptx"
    with zipfile.ZipFile(target, "w") as archive:
        for index, texts in enumerate(slides, start=1):
            archive.writestr(f"ppt/slides/slide{index}.xml", _slide_xml(*texts))
        for index, note in enumerate(notes or [], start=1):
            archive.writestr(f"ppt/notesSlides/notesSlide{index}.xml", _slide_xml(note))
    return target


def _odt(tmp_path: Path, text: str) -> Path:
    target = tmp_path / "notes.odt"
    content = (
        '<?xml version="1.0"?>'
        '<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
        ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
        f"<office:body><text:p>{text}</text:p></office:body></office:document-content>"
    )
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("content.xml", content)
    return target


# ── PowerPoint ────────────────────────────────────────────────────────


def test_a_pptx_deck_is_read(tmp_path: Path) -> None:
    deck = _pptx(tmp_path, [["Information Security"], ["Threat models", "and attackers"]])

    text = extract.extract_or_raise(deck)

    assert "Information Security" in text
    assert "Threat models" in text
    assert "and attackers" in text


def test_slides_are_ordered_numerically_not_lexically(tmp_path: Path) -> None:
    """A string sort gives slide1, slide10, slide11, slide2 — a lecture read
    back in that order looks like the model hallucinating rather than like a
    parser bug, which is the worst kind of wrong to debug."""
    deck = _pptx(tmp_path, [[f"point {i}"] for i in range(1, 12)])

    text = extract.extract_or_raise(deck)

    assert text.index("point 2") < text.index("point 10")
    assert text.index("point 9") < text.index("point 11")


def test_speaker_notes_are_included(tmp_path: Path) -> None:
    """On a lecture deck the notes are often where the content actually is —
    the slide itself is five words and a diagram."""
    deck = _pptx(tmp_path, [["Overview"]], notes=["The exam covers chapters 1 to 4."])

    text = extract.extract_or_raise(deck)

    assert "chapters 1 to 4" in text


# ── the formats that used to be silently dropped ──────────────────────


def test_opendocument_is_read(tmp_path: Path) -> None:
    assert "rent is 1200" in extract.extract_or_raise(_odt(tmp_path, "The rent is 1200."))


def test_rtf_control_words_are_stripped(tmp_path: Path) -> None:
    target = tmp_path / "note.rtf"
    target.write_bytes(
        rb"{\rtf1\ansi{\fonttbl{\f0 Calibri;}}\f0\fs24 Meeting at four.\par Bring the deck.}"
    )

    text = extract.extract_or_raise(target)

    assert "Meeting at four." in text
    assert "Bring the deck." in text
    assert "fonttbl" not in text, "the font table is not prose"
    assert "rtf1" not in text


# ── archives ──────────────────────────────────────────────────────────


def test_a_zip_is_unpacked_and_its_members_read(tmp_path: Path) -> None:
    target = tmp_path / "course.zip"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("week1/notes.txt", "Symmetric encryption.")
        archive.writestr("week2/notes.md", "Public key infrastructure.")

    text = extract.extract_or_raise(target)

    assert "Symmetric encryption." in text
    assert "Public key infrastructure." in text
    assert "week1/notes.txt" in text, "each member is named, or the text has no provenance"


def test_a_tar_gz_is_unpacked(tmp_path: Path) -> None:
    target = tmp_path / "bundle.tar.gz"
    payload = b"the archived note"
    with tarfile.open(target, "w:gz") as archive:
        info = tarfile.TarInfo("inner.txt")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))

    assert "the archived note" in extract.extract_or_raise(target)


def test_an_archive_of_binaries_still_lists_what_is_in_it(tmp_path: Path) -> None:
    """"What is in this zip" is a real question with a real answer even when
    nothing inside is readable prose."""
    target = tmp_path / "photos.zip"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("a.raw", b"\x00\x01\x02")

    assert "a.raw" in extract.extract_or_raise(target)


def test_a_member_count_bomb_is_capped(tmp_path: Path) -> None:
    """This is the one path that unpacks untrusted input, and a zip bomb is a
    plausible thing to be sent rather than a thought experiment."""
    target = tmp_path / "many.zip"
    with zipfile.ZipFile(target, "w") as archive:
        for i in range(extract.MAX_ARCHIVE_MEMBERS * 3):
            archive.writestr(f"f{i}.txt", f"line {i}")

    text = extract.extract_or_raise(target)

    assert text.count("--- ") <= extract.MAX_ARCHIVE_MEMBERS


def test_a_path_traversal_member_is_refused(tmp_path: Path) -> None:
    """Nothing here writes to disk, so `../../` cannot escape anywhere — but a
    name shaped like that says something about intent, and reading it into a
    prompt is not obviously safer than writing it."""
    target = tmp_path / "evil.zip"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("../../escaped.txt", "should not be read")
        archive.writestr("fine.txt", "should be read")

    text = extract.extract_or_raise(target)

    assert "should not be read" not in text
    assert "should be read" in text


def test_an_archive_inside_an_archive_is_listed_not_opened(tmp_path: Path) -> None:
    """One level is a mail attachment; two is someone finding out what
    happens."""
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as nested:
        nested.writestr("deep.txt", "buried treasure")
    target = tmp_path / "outer.zip"
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("inner.zip", inner.getvalue())
        archive.writestr("top.txt", "surface")

    text = extract.extract_or_raise(target)

    assert "surface" in text
    assert "buried treasure" not in text


# ── the ones that cannot be read, and say why ─────────────────────────


@pytest.mark.parametrize(
    ("suffix", "modern"),
    [(".ppt", ".pptx"), (".doc", ".docx"), (".xls", ".xlsx")],
)
def test_legacy_office_names_the_fix_rather_than_the_failure(
    tmp_path: Path, suffix: str, modern: str
) -> None:
    """The actual incident: a lecture `.ppt` was skipped and the only record
    was a log line. "Unsupported file type" would have been almost as
    useless — the message has to say what to do."""
    target = tmp_path / f"lecture{suffix}"
    target.write_bytes(b"\xd0\xcf\x11\xe0")  # the OLE2 magic

    with pytest.raises(extract.Unsupported) as raised:
        extract.extract_or_raise(target)

    assert modern in str(raised.value)
    assert "Save As" in str(raised.value) or "save as" in str(raised.value)


def test_an_unknown_type_lists_what_does_work(tmp_path: Path) -> None:
    target = tmp_path / "clip.mkv"
    target.write_bytes(b"\x00")

    with pytest.raises(extract.Unsupported) as raised:
        extract.extract_or_raise(target)

    assert "archives" in str(raised.value)


def test_extract_text_never_raises_for_the_background_sweep(tmp_path: Path) -> None:
    """The two entry points differ on purpose. One corrupt PDF in Downloads
    must not stop the walk; a file the user chose to hand over is the opposite
    case and wants the reason."""
    target = tmp_path / "lecture.ppt"
    target.write_bytes(b"\xd0\xcf\x11\xe0")

    assert extract.extract_text(target) == ""


# ── the two extension sets ────────────────────────────────────────────


def test_archives_are_attachable_but_never_indexed() -> None:
    """`should_index` drives a throttled walk over Documents, Desktop and
    Downloads. Archives in that set would have ARIA quietly unpacking every
    zip on the machine, on a timer."""
    assert ".zip" in extract.ATTACHABLE
    assert ".zip" not in extract.INDEXABLE
    assert extract.INDEXABLE < extract.ATTACHABLE


def test_the_formats_he_asked_for_are_all_attachable() -> None:
    wanted = (".pptx", ".docx", ".xlsx", ".pdf", ".odt", ".ods", ".odp", ".epub", ".rtf", ".zip")
    for suffix in wanted:
        assert suffix in extract.ATTACHABLE, suffix
