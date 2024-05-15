from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram import flags
from aiogram.fsm.context import FSMContext
import utils
import config
from states import Gen
import keyboards as kb
import text
import os
from stt import STT
from tts import TTS
from pathlib import Path

file_info = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getFile?file_id="
file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/"


router = Router()
tts = TTS()
stt = STT()

#@router.message()
@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)

@router.message(F.text == "Меню")
@router.message(F.text == "Выйти в меню")
@router.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message, state: FSMContext):
    await state.clear()  # Очищаем состояние пользователя
    await msg.answer(text.menu, reply_markup=kb.menu)

@router.callback_query(F.data == "generate_text")
async def input_text_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.text_prompt)
    await clbck.message.edit_text(text.gen_text)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.exit_kb)

@router.message(Gen.text_prompt)
@flags.chat_action("typing")
async def generate_text(msg: Message, state: FSMContext):
    prompt = msg.text
    mesg = await msg.answer(text.gen_wait)
    res = await utils.generate_text(prompt)
    if not res:
        return await mesg.edit_text(text.gen_error, reply_markup=kb.iexit_kb)
    await mesg.edit_text(res[0], disable_web_page_preview=True)


@router.callback_query(F.data == "generate_audio")
async def input_audio_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.audio_promt)
    await clbck.message.edit_text(text.gen_text)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.exit_kb)

@router.message(Gen.audio_promt)
@flags.chat_action("typing")
async def generate_text(msg: Message, state: FSMContext):
    prompt = msg.text
    mesg = await msg.answer(text.gen_wait)
    folder_name = "Youtube"
    filename_audio, video_title = await utils.audio_from_Youtube(prompt, folder_name)
    await mesg.delete()
    audio_file = FSInputFile(filename_audio, filename=video_title)
    await msg.answer_audio(audio_file)
    os.remove(filename_audio)
    await state.clear()

@router.callback_query(F.data == "generate_voice")
async def input_gen_voice_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.voice_from_text)
    await clbck.message.edit_text(text.gen_voice)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.exit_kb)



@router.message(Gen.voice_from_text)
async def cmd_text(msg: Message, state: FSMContext):
    """
    Обработчик на получение текста
    """
    await msg.answer("Текст получен")

    out_filename = tts.text_to_ogg(msg.text)

    # Отправка голосового сообщения
    audio_path = Path("", out_filename)
    audio_file = FSInputFile(audio_path, filename='audio.ogg')
    await msg.answer_audio(audio_file)
    os.remove(audio_path)
    await state.clear()

@router.message(Command("voice"))
async def allow_voice(msg: Message,state: FSMContext):
    await state.set_state(Gen.text_from_audio)
    await msg.answer(text.allow_voice)

# Хэндлер на получение голосового и аудио сообщения
@router.message((F.content_type.in_({'audio', 'voice'})) & bool((Gen.text_from_audio)))
async def voice_message_handler(msg: Message, state: FSMContext):
    """
    Обработчик на получение голосового и аудио сообщения.
    """
    if msg.content_type == types.ContentType.VOICE:
        file_id = msg.voice.file_id
    elif msg.content_type == types.ContentType.AUDIO:
        file_id = msg.audio.file_id
    else:
        await msg.reply("Формат документа не поддерживается")
        return
    file_on_disk = utils.download_file(file_id, "audio_files")
    text = stt.audio_to_text(file_on_disk)
    if not text:
        text = "Формат документа не поддерживается"
    await msg.answer(text)
    os.remove(file_on_disk)  # Удаление временного файла
    await state.clear()

@router.callback_query(F.data == "wolfram_solution")
async def input_gen_voice_prompt(clbck: CallbackQuery, state: FSMContext):
    await state.set_state(Gen.wolfram_solution)
    await clbck.message.edit_text(text.gen_voice)
    await clbck.message.answer(text.gen_exit, reply_markup=kb.exit_kb)

@router.message(Gen.wolfram_solution)
async def cmd_text(msg: Message, state: FSMContext):
    prompt = msg.text   
    mesg = await msg.answer(text.gen_wait) 
    result_text = await utils.wolfram_solution(prompt)
    await mesg.edit_text(result_text, disable_web_page_preview=True)
    await state.clear()