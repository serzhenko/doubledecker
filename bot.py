import fitz
import logging
from telegram.ext import Updater, MessageHandler, Filters
from decouple import config


def pdf2png(source, destdir):
    dpi = 150  # choose desired dpi here
    zoom = dpi / 72  # zoom factor, standard: 72 dpi
    magnify = fitz.Matrix(zoom, zoom)  # magnifies in x, resp. y direction
    doc = fitz.open(source)  # open document
    for page in doc:
        pix = page.get_pixmap(matrix=magnify)  # render page to an image
        pix.save(f"{destdir}/page-{page.number}.png")


def process_document(update, context):
    update.message.reply_text('Поймал документ')


def main():
    # Запускаем логгирование
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)
    token = config('telegramToken', default='')
    updater = Updater(token)
    dp = updater.dispatcher

    text_handler = MessageHandler(Filters.document, process_document)
    dp.add_handler(text_handler)

    updater.start_polling()
    updater.idle()

    if __name__ == '__main__':
        main()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
