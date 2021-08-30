from win10toast import ToastNotifier

toaster = ToastNotifier()

def show_toast(title: str, message: str, duration: int=600, icon_path: str='icon.ico', threaded: bool=True) -> None:
    toaster.show_toast(title, message, duration=duration, icon_path=icon_path, threaded=threaded)
