import logging

import filetype
import fitz
from decouple import config
from telegram.ext import Updater, MessageHandler, Filters
from smally import optipng


def pdf2png(source, destdir):
    optipng_available = config('optipng', default=False)
    try:
        kind = filetype.guess(source)
        if kind is None:
            return False

        if kind.extension != 'pdf' and kind.mime != 'application/pdf':
            return False

        dpi = 150  # choose desired dpi here
        zoom = dpi / 72  # zoom factor, standard: 72 dpi
        magnify = fitz.Matrix(zoom, zoom)  # magnifies in x, resp. y direction

        doc = fitz.open(source, filetype='pdf')  # open document
        for page in doc:
            pix = page.get_pixmap(matrix=magnify)  # render page to an image
            dest_filename = f"{destdir}/page-{page.number}.png"
            pix.save(dest_filename)
            if optipng_available:
                optipng(dest_filename)
        return True

    except Exception as e:
        return False


def process_document(update, context):
    update.message.reply_text('Поймал документ')
    update.message.reply_chat_action(action='upload_document')
    dest_dir = config('dest_dir', default='decks') + '1/'
    file = update.message.effective_attachment.get_file()
    pdf = file.download(custom_path=dest_dir+'src.pdf')
    result = pdf2png(pdf, dest_dir)
    update.message.reply_text('Статус конверсии: ' + str(result))

def main():
    # Запускаем логгирование
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
    )
    logger = logging.getLogger(__name__)
    token = config('telegram_token', default='')
    updater = Updater(token)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.document, process_document))

    updater.start_polling()
    updater.idle()

    if __name__ == '__main__':
        main()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
