
def escape_html(text):
    """
    Escapes HTML special characters in the given text.
    """
    if isinstance(text, str):
        return (text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
            .replace("'", '&#39;'))
    else:
        return text


def replace_numbers_with_emojis(text):
    # Emoji-Zuordnungen für Zahlen 0 bis 9
    emoji_map = {
        '0': '0️⃣',
        '1': '1️⃣',
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣'
    }
    # Ersetze jede Zahl im Text durch das entsprechende Emoji
    for number, emoji in emoji_map.items():
        text = text.replace(number, emoji)
    return text
