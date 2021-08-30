import pytesseract

def extract_from_image(img, custom_config='--psm 5') -> str:
    text = pytesseract.image_to_string(img, lang='jpn_vert', config=custom_config)
    return text.strip().translate(str.maketrans('', '', ' \t\r'))