import html, configparser
from tkinter import Tk, StringVar, Text, END
import tkinter.ttk as ttk
from PIL import ImageTk
from ttkthemes import ThemedStyle
import pykakasi
from translate import Translator

import ocr

config = configparser.ConfigParser()
config.read('config.cfg')

TO_LANG = config.get('TRANSLATOR', 'TO_LANG')
FROM_LANG = config.get('TRANSLATOR', 'FROM_LANG')
EMAIL = config.get('TRANSLATOR', 'EMAIL') # https://mymemory.translated.net/doc/usagelimits.php
LOOK_UP_KANJI_URL = config.get('TRANSLATOR', 'LOOK_UP_KANJI_URL')

WINDOW_TITLE = config.get('FRAME', 'WINDOW_TITLE')
ICON_PATH = config.get('FRAME', 'ICON_PATH')
BG_COLOR = config.get('FRAME', 'BG_COLOR')
TEXT_FONT_SIZE = config.getint('FRAME', 'TEXT_FONT_SIZE')

kks = pykakasi.kakasi()
translator = Translator(to_lang=TO_LANG, from_lang=FROM_LANG, email=EMAIL)

class OCRWindow:
    def __init__(self):
        self.window = Tk()
        self.window.title(WINDOW_TITLE)
        self.window.iconbitmap(ICON_PATH)
        self.window.configure()
        
        self.style = ThemedStyle(self.window)
        self.ttkStyle = ttk.Style()
        self.ttkStyle.configure('TFrame', background=BG_COLOR)
        self.window.tk.call('source', 'theme/sun-valley.tcl') # https://github.com/rdbende/Sun-Valley-ttk-theme
        self.window.tk.call('set_theme', 'dark')

        self.frame = ttk.Frame(self.window, style='TFrame')
        self.frame.grid(sticky='SE')
        self.ocr_text = ''
        self.translation = ''
        self.romaji_text = ''

    def create_window(self, image) -> None:
        self.image = image
        img = ''
        try:
            img = ImageTk.PhotoImage(self.image)
            self.ocr_text, self.romaji_text, self.translation = self.get_ocr(self.image)
        except Exception as exc:
            print(exc)
            print('Exception!')

        self.create_ocr_text_group(self.ocr_text)
        self.create_romaji_text_group(self.romaji_text)
        self.create_translated_text_group(self.translation)
        self.create_image_frame(img)
        self.create_look_up_button(self.ocr_text)
        self.create_translate_button()
        self.create_another_screenshot_button()

        self.window.focus_force()
        self.window.mainloop()


    def create_ocr_text_group(self, original_text: str, label: str='OCR:') -> None:
        self.ocr_label = StringVar()
        self.ocr_label.set(label)
        ocr_text_label = ttk.Label(self.frame, textvariable=self.ocr_label)
        self.ocr_text_area = Text(self.frame, height=5, width=30, font=('default', TEXT_FONT_SIZE))
        self.ocr_text_area.insert(END, original_text)
        ocr_text_label.grid(column=0, row=0, pady=(20, 0))
        self.ocr_text_area.grid(column=0, row=1, padx=(20, 5))


    def create_romaji_text_group(self, romaji_text: str, label: str='Romaji:') -> None:
        self.romaji_label = StringVar()
        self.romaji_label.set(label)
        romaji_text_label = ttk.Label(self.frame, textvariable=self.romaji_label)
        self.romaji_text_area = Text(self.frame, height=5, width=30, font=('default', TEXT_FONT_SIZE))
        self.romaji_text_area.insert(END, romaji_text)
        romaji_text_label.grid(column=1, row=0, pady=(20, 0))
        self.romaji_text_area.grid(column=1, row=1, padx=(5, 5))


    def create_translated_text_group(self, text: str, label: str='English:') -> None:
        self.translated_label = StringVar()
        self.translated_label.set(label)
        translated_text_label = ttk.Label(self.frame, textvariable=self.translated_label)
        self.translated_text_area = Text(self.frame, height=5, width=30, font=('default', TEXT_FONT_SIZE))
        self.translated_text_area.insert(END, text)
        translated_text_label.grid(column=2, row=0, pady=(20, 0))
        self.translated_text_area.grid(column=2, row=1, padx=(5, 20))


    def create_image_frame(self, image) -> None:
        self.image_frame = ttk.Label(self.frame, image=image)
        self.image_frame.grid(columnspan=3, row=3, padx=20, pady=20)


    def create_look_up_button(self, ocr_text: str, button_text: str='Look up Kanji') -> None:
        self.look_up_kanji = ttk.Button(self.frame, text=button_text, command=lambda: self.open_browser(ocr_text))
        self.look_up_kanji.grid(column=0, row=2, pady=(5, 0))


    def create_translate_button(self, text: str='Translate again') -> None:
        self.translate_again = ttk.Button(self.frame, text=text, command=self.translate_again)
        self.translate_again.grid(column=2, row=2, pady=(5, 0))


    def create_another_screenshot_button(self, text: str='Take another screenshot') -> None:
        self.screenshot_button = ttk.Button(self.frame, text=text, command=self.get_image)
        self.screenshot_button.grid(row=4, columnspan=3, pady=5)


    def get_ocr(self, image) -> tuple:
        ocr_text = ocr.extract_from_image(image)
        ocr_text_list = ocr_text.split('\n')
        romaji_text = [
            [item['hepburn'] for item in kks.convert(text)]
            for text in ocr_text_list
        ]
        romaji_text = [' '.join(text) for text in romaji_text]
        romaji_text = '\n'.join(romaji_text)
        translation = translator.translate(ocr_text)
        translation = html.unescape(translation)
        return ocr_text, romaji_text, translation


    def open_browser(self, ocr_text: str) -> None:
        print('Looking up kanji...')
        import webbrowser
        webbrowser.open(LOOK_UP_KANJI_URL + ocr_text, new=2)


    def translate_again(self) -> None:
        ocr_text = self.ocr_text_area.get('1.0', 'end-1c')
        translation = translator.translate(ocr_text)
        translation = html.unescape(translation)
        self.translated_text_area.delete('1.0', END)
        self.translated_text_area.insert(END, translation)


    def get_image(self) -> None:
        self.window.destroy()
        from main import OCR
        ocr = OCR()
        ocr.get_image()