import sys
import traceback
from datetime import datetime

from colorifix.colorifix import paint
from emoji import emojize
from requests import post

# ---- Utils


def emz(text):
    """emojize everything"""
    if isinstance(text, list):
        return [emz(t) for t in text]
    if isinstance(text, dict):
        return {k: emz(v) for k, v in text.items()}
    return emojize(text, variant="emoji_type")


# ---- Messages


def standard_message(update, top_message, bot_name, bot_url):
    """Build a standard log message"""
    user_name = update.effective_chat.username or update.effective_chat.first_name
    user_id = update.effective_chat.id
    user_mention = f"[{user_name}](tg://user?id={user_id})"
    now = datetime.now()
    return emojize(
        f"{top_message}\n"
        f"🤖 [{bot_name}]({bot_url})\n"
        f"📅 {now:%d.%m.%Y}\n"
        f"🕗 {now:%H:%M}\n"
        f"👤 {user_mention} (`{user_id}`)\n"
    )


def send_log(bot, channel, message, document=None):
    """Send a simple message to a channel"""
    if document:
        bot.send_document(
            channel,
            document,
            caption=emojize(message),
            parse_mode="Markdown",
        )
    else:
        bot.send_message(channel, emojize(message), parse_mode="Markdown")


def error_handler(
    update,
    context,
    channel,
    message,
    logger=None,
    exception=None,
    extra_info=None,
    log=True,
):
    """Log an error on terminal and a Telegram channel from a Telegram bot"""
    # error log on terminal
    user_data = context.user_data if update else "None"
    trace = (exception and exception.__traceback__) or sys.exc_info()[2]
    traceback_error = "".join(traceback.format_tb(trace))
    exp = exception or context.error
    traceback_msg = paint(
        f"[#229]{user_data}\n\n[#gray]{traceback_error}" f"[#red]{exp}", False
    )
    if logger:
        logger.warning(traceback_msg)
    else:
        print(traceback_msg)
    # send message to error channel
    if log:
        open("error.log", "w+").write(
            f"{user_data}\n\n"
            f"{extra_info or '...'}\n\n"
            f"{traceback_error}\n"
            f"> {exp}"
        )
        send_log(context.bot, channel, message, open("error.log", "r"))


def not_authorized_handler(update, context, bot_name, bot_url, channel):
    """Log an unauthorized access on a Telegram bot"""
    top_msg = "🙊 *NO AUTH USER* 🙈"
    message = standard_message(update, top_msg, bot_name, bot_url)
    send_log(context.bot, channel, message)


def send_sentry_log(token, chat, project_name, project_id, user, extra=None):
    """send a telegram log for Sentry"""
    sentry_url = "https://sentry.io/organizations/mortafix-inc/issues/?project="
    extra_line = extra + "\n" if extra else ""
    msg = f"🐞 *Project Error* 🐞\n\n🖥 _{project_name}_\n👤 {user}\n{extra_line}"
    # api call
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat,
        "text": msg,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "🦠 Go to Sentry", "url": f"{sentry_url}{project_id}"}]
            ]
        },
    }
    headers = {"Content-Type": "application/json"}
    return post(url, json=payload, headers=headers)
