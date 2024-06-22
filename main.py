import asyncio
import logging
import sys
from pathlib import Path

from openai_model import OpenAIModel
from voice_to_text import voice_to_text

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message, InputFile, Voice, FSInputFile


class Settings(BaseSettings):
    bot_token: Optional[str] = Field(None, env='BOT_TOKEN')
    openai_token: Optional[str] = Field(None, env='OPENAI_TOKEN')
    assistant_id: Optional[str] = Field(None, env='ASSISTANT_ID')


settings = Settings(_env_file='.env')
model = OpenAIModel(settings.openai_token, settings.assistant_id)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Отправь мне голосовое сообщение!")

@dp.message()
async def voice_message_handler(message: Message) -> None:
    try:
        if message.content_type == ContentType.VOICE:
            file_id = message.voice.file_id
            voice = await message.bot.get_file(file_id)
            path_on_disk = f"voices/{file_id}.ogg"
            file_on_disk = Path("", path_on_disk)
            await message.bot.download_file(voice.file_path, destination=file_on_disk)

            message_text = voice_to_text(path_on_disk)
            model.submit_message(message_text)
            reply_text = model.get_reply()
            reply_speech = model.get_speech(reply_text)
            reply_on_disk = f'voice_replies/{file_id}_reply.ogg'
            reply_speech.write_to_file(reply_on_disk)

            await message.bot.send_voice(
                chat_id=message.chat.id,
                voice=FSInputFile(
                    path=reply_on_disk
                )
            )
        else:
            await message.answer("Лучше отправь голосовое сообщение, друг!")
    except TypeError:
        await message.answer("Прости, что-то пошло не так!")

async def main() -> None:
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
