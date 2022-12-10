import fitz


def pdf2png(source, destdir):
    dpi = 150  # choose desired dpi here
    zoom = dpi / 72  # zoom factor, standard: 72 dpi
    magnify = fitz.Matrix(zoom, zoom)  # magnifies in x, resp. y direction
    doc = fitz.open(source)  # open document
    for page in doc:
        pix = page.get_pixmap(matrix=magnify)  # render page to an image
        pix.save(f"{destdir}/page-{page.number}.png")
