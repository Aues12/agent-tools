"""Minimal OOXML fixture writer; no python-docx dependency."""
from pathlib import Path
from xml.sax.saxutils import escape
import zipfile


def make_docx(path: Path, paragraphs: list[tuple[str, str]], *, media: bool = False, floating: bool = False) -> Path:
    rows = []
    for style, text in paragraphs:
        style_xml = ('<w:pPr><w:pStyle w:val="Heading1"/></w:pPr>' if style == "h1" else
                     '<w:pPr><w:pStyle w:val="Heading2"/></w:pPr>' if style == "h2" else "")
        runs = ''.join('<w:r><w:tab/></w:r>' if part == "\t" else '<w:r><w:t xml:space="preserve">'+escape(part)+'</w:t></w:r>'
                       for part in __import__('re').split(r'(\t)', text))
        rows.append('<w:p>'+style_xml+runs+'</w:p>')
    draw = '<wp:anchor/>' if floating else ''
    document = '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><w:body>'+''.join(rows)+draw+'</w:body></w:document>'
    styles = ('<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
              '<w:style w:styleId="Heading1"><w:name w:val="heading 1"/></w:style>'
              '<w:style w:styleId="Heading2"><w:name w:val="heading 2"/></w:style></w:styles>')
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('word/document.xml', document)
        archive.writestr('word/styles.xml', styles)
        if media:
            archive.writestr('word/media/image1.emf', b'fake')
    return path
