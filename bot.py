import filetype
import fitz
import os
from decouple import config
from telegram.ext import Updater, MessageHandler, CommandHandler, ContextTypes, filters, Application
import logging
from smally import optipng

from data_models import *


def generate_url(deck_id):
    return config('www_root') + 'view/' + str(deck_id) + '/'


def generate_embed(deck_id):
    return '<iframe src="' + config('www_root') + 'embed/' + str(deck_id) + '/"></iframe>'


def pdf2png(source, dest_dir):
    try:
        kind = filetype.guess(source)
        if kind is None:
            return False, -1

        if kind.extension != 'pdf' and kind.mime != 'application/pdf':
            return False, -1

        dpi = 150
        zoom = dpi / 72
        magnify = fitz.Matrix(zoom, zoom)

        doc = fitz.open(source, filetype='pdf')  # open document
        for page in doc:
            pix = page.get_pixmap(matrix=magnify)  # render page to an image
            dest_filename = f"{dest_dir}/page-{page.number}.png"
            pix.save(dest_filename)

        return True, len(doc)

    except Exception as e:
        return False, -1


def optimize_png(dest_dir, num_pages):
    try:
        for i in range(num_pages):
            dest_filename = f"{dest_dir}/page-{i}.png"
            optipng(dest_filename)
        return True
    except Exception as e:
        return False


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    name = f'{update.message.chat.first_name} {update.message.chat.last_name}'
    user, created = User.get_or_create(telegram_id=update.message.chat.id,
                                       username=update.message.chat.username,
                                       name=name)
    if created:
        await update.message.reply_text(f"Привет, <b>{name}</b>! Приятно познакомиться.", parse_mode='html')
        await update.message.reply_text("Отправляй мне PDF-файлы, чтобы получить код для встраивания на сайт.")
    else:
        await update.message.reply_text('Готов к работе! Жду PDF-ок.')


async def process_document(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Поймал документ. Начинаю обработку...')
    await update.message.reply_chat_action(action='upload_document')

    user = User.get(User.telegram_id == update.message.chat.id)
    deck = Deck.create(slides_count=-1, user_id=user)

    dest_dir = config('decks_dir', default='decks') + str(deck.id) + '/'
    os.makedirs(dest_dir, exist_ok=True)

    file = await update.message.effective_attachment.get_file()
    pdf = await file.download_to_drive(custom_path=dest_dir + 'src.pdf')
    result, num_pages = pdf2png(pdf, dest_dir)
    if result:
        deck.status, deck.slides_count = Deck.STATUS['PROCESSED'], num_pages
        await update.message.reply_text('Конвертация успешна...')
        deck.save()

    if config('optipng', default=False):
        await update.message.reply_text('Оптимизируем изображения...')
        await update.message.reply_chat_action(action='upload_document')
        optimize_png(dest_dir, num_pages)
        await update.message.reply_text('Оптимизация завершена!')

    url, embed_code = generate_url(deck.id), generate_embed(deck.id)
    links = f'[Ссылка для просмотра презентации]({url})\n\nКод для вставки:\n```\n{embed_code}\n```'
    # print(links)
    await update.message.reply_text(links, parse_mode='MarkdownV2')


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING
    )
    logger = logging.getLogger(__name__)
    try:
        token = config('telegram_token', default='')
        application = Application.builder().token(token).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(MessageHandler(filters.Document.FileExtension("pdf"), process_document))

        application.run_polling()
    except Exception as e:
        print('Could not start a bot poller')


if __name__ == '__main__':
    main()
