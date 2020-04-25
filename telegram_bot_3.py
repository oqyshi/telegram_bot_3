from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Обычный обработчик, как и те, которыми мы пользовались раньше.
# Но с дополнительными параметрами, которые раньше не использовали:
# job_queue - очередь задач, в которую мы добавим свою задачу.
# chat_data - словарь для передачи данных, между обработчиками сообщений от того же собеседника.

# Обычный обработчик, как и те, которыми мы пользовались раньше.
def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id
    try:
        # args[0] должен содержать значение аргумента (секунды таймера)
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, не умеем возвращаться в прошлое')
            return

        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        if 'job' in context.chat_data:
            old_job = context.chat_data['job']
            old_job.schedule_removal()
        new_job = context.job_queue.run_once(task, due, context=chat_id)
        # Запоминаем созданную задачу в данных чата.
        context.chat_data['job'] = new_job
        # Присылаем сообщение о том, что всё получилось.
        update.message.reply_text(f'Вернусь через {due} секунд')

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set <секунд>')


def task(context):
    job = context.job
    context.bot.send_message(job.context, text='Вернулся!')

def unset_timer(update, context):
    # Проверяем, что задача ставилась
    if 'job' not in context.chat_data:
        update.message.reply_text('Нет активного таймера')
        return
    job = context.chat_data['job']
    # планируем удаление задачи (выполнится, когда будет возможность)
    job.schedule_removal()
    # и очищаем пользовательские данные
    del context.chat_data['job']
    update.message.reply_text('Хорошо, вернулся сейчас!')


def main():
    updater = Updater("YOUR_TOKEN", use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("set_timer", set_timer, pass_job_queue=True, pass_chat_data=True, pass_args=True))
    dp.add_handler(CommandHandler("unset_timer", unset_timer, pass_chat_data=True))

    updater.start_polling()
    print('Bot started')
    updater.idle()


if __name__ == '__main__':
    main()