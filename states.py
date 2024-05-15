from aiogram.fsm.state import StatesGroup, State

class Gen(StatesGroup):
    text_prompt = State()
    audio_promt = State()
    voice_from_text = State()
    text_from_audio = State()
    wolfram_solution = State()