"""Render every page of a PDF to PNG for visual verification.

    uv run --with pypdfium2 --with pillow python verify_pdf.py report.pdf outdir

Then Read the PNGs (especially figure pages) and check that figures show
what their captions claim before delivering the report.
"""
import os
import sys

import pypdfium2 as pdfium


def main():
    pdf_path, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    pdf = pdfium.PdfDocument(pdf_path)
    print("pages:", len(pdf))
    for i in range(len(pdf)):
        img = pdf[i].render(scale=1.3).to_pil()
        out = os.path.join(outdir, "page_%d.png" % (i + 1))
        img.save(out)
        print("wrote", out)


if __name__ == "__main__":
    main()
