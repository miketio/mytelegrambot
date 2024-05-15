from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
menu = [
    [InlineKeyboardButton(text="Ask Chat Bot", callback_data="generate_text"),
    InlineKeyboardButton(text="Audio from Youtube", callback_data="generate_audio")],
    [InlineKeyboardButton(text="Convert text to voice", callback_data="generate_voice"),
    InlineKeyboardButton(text="Download music from VK", callback_data="download_music")],
    [InlineKeyboardButton(text="File converter", callback_data="convert_file"),
    InlineKeyboardButton(text="WolframAlpha solution", callback_data="wolfram_solution")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])