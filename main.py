import configparser
from pynput.keyboard import Listener
from pynput.mouse import Controller
import PIL.ImageGrab
import keyboard

# comment line below if not using Windows 10
import toaster
from view import OCRWindow

config = configparser.ConfigParser()
config.read('config.cfg')

MULTIPLE_MONITOR_SCREEN = config.getboolean('MAIN', 'MULTIPLE_MONITOR_SCREEN')

class OCR():
    """
    Listens to the trigger key to start capturing the image and then opens 
    a TKinter window that shows the captured image with both OCR text and English translation \n
    `trigger_key` The key that starts the process to the capture of the image \n
    `capture_key` The key used to get the cursor position (initial and final positions) \n
    `exit_key_1` The first key in the combination to stop the script \n
    `exit_key_2` The second key in the combination to stop the script
    """
    def __init__(self, trigger_key: str='print_screen', capture_key: str='ctrl_l', exit_key_1: str='ctrl', exit_key_2: str='q'):
        self.cursor_pos = []
        self.mouse = Controller()
        self.trigger_key = trigger_key
        self.capture_key = capture_key
        self.exit_key_1 = exit_key_1
        self.exit_key_2 = exit_key_2


    def start(self) -> None:
        print('Program started.')
        while True:
            try:
                if keyboard.is_pressed(self.exit_key_1) and keyboard.is_pressed(self.exit_key_2):
                    break
                elif keyboard.is_pressed(self.trigger_key):
                    self.get_image()
            except Exception as exc:
                print(exc)
                main()


    def _image_crop(self, im) -> None:
        """Get two positions from the mouse cursor and 
        crop the screenshot from clipboard based on them"""
        self._get_cursor_pos()
        if self.cursor_pos == []:
            return im
        pos1_x, pos1_y = self.cursor_pos[0]
        pos2_x, pos2_y = self.cursor_pos[1]
        self.cursor_pos.clear()
        return im.crop((pos1_x, pos1_y, pos2_x, pos2_y))
    

    def _get_cursor_pos(self) -> None:
        """Listens to the keyboard to get the cursor position"""
        with Listener(on_press=self._on_press) as self.listener:
            self.listener.join()


    def _on_press(self, key: str) -> None:
        """When the capture key is pressed on the keyboard, 
        the cursor position is appended to a list"""
        key = str(key)
        if self.capture_key in key:
            x, y = self.mouse.position
            self.cursor_pos.append([x, y])
            if self.cursor_pos.__len__() == 2:
                self.listener.stop()


    def get_image(self) -> None:
        """Takes a screenshot of the whole screen, crop the image to return only the 
        area the user chose and opens a TKinter window frame to show the OCR"""
        im =  PIL.ImageGrab.grab(all_screens=MULTIPLE_MONITOR_SCREEN)
        # comment line below if not using Windows 10
        toaster.show_toast('Select the part of the screen', f'Press {self.capture_key} on the first point and then on the second point to make a rectangle', duration=5)
        im_crop = self._image_crop(im)
        ocr_window = OCRWindow()
        ocr_window.create_window(im_crop)


def main():
    ocr = OCR()
    ocr.start()

if __name__ == '__main__':
    main()