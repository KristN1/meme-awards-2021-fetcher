import selenium
import Messages
import time
import re
from datetime import datetime
from selenium.webdriver.common.by import By
import undetected_chromedriver.v2 as uc

driver = None
with open("last_page.txt", "r") as f:
    try:
        starting_page = int(f.read()) + 1
    except ValueError:
        starting_page = 482 # default
ending_page = 527

def remove_emoji(string): # https://gist.github.com/slowkow/7a7f61f495e3dbb7e3d767f97bd7304b
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def count_reactions(reactions: str):
    reactions_names = len(reactions.split(","))

    try:
        reactions_number = int(reactions.split(" and ")[1][0])
    except:
        return reactions_names

    else:
        return reactions_number + reactions_names

def get_msg_url(message: selenium.webdriver.remote.webelement.WebElement):
    message_buttons = message.find_elements(By.CLASS_NAME, "message-attribution-opposite li")

    return message_buttons[1].find_element(By.CSS_SELECTOR, "a").get_attribute("href")

def get_image(message: selenium.webdriver.remote.webelement.WebElement): # if you use anything else than imgur or yt, then sorry :)
    
    image = message.find_elements(By.CLASS_NAME, "bbImage") # uploaded directly to cubecraft
    image_imgur = message.find_elements(By.CLASS_NAME, "imgur-embed-iframe-pub") # imgur embed
    image_yt = message.find_elements(By.CSS_SELECTOR, "[frameborder='0']") # youtube embed
    
    try:
        return image[0].get_attribute("src")
    except IndexError:
        try:
            return image_imgur[0].get_attribute("src")
        except IndexError:
            try:
                return image_yt[0].get_attribute("src")
            except IndexError:
                return None
    
def handle_message(message: selenium.webdriver.remote.webelement.WebElement):
    username = remove_emoji(message.find_element(By.CLASS_NAME, "username").text)

    image = get_image(message)
    reactions = count_reactions(message.find_element(By.CLASS_NAME, "reactionsBar").text)
    posted_at_str = message.find_element(By.CLASS_NAME, "u-dt").get_attribute("datetime")
    posted_at = datetime.strptime(posted_at_str[:-5], "%Y-%m-%dT%H:%M:%S")

    url = get_msg_url(message)

    if posted_at.year == 2021 and image is not None:
        return Messages.Message(username, url, image, reactions, posted_at)
    else:
        return None

def handle_page(page_number):
    global driver
    driver = uc.Chrome()

    driver.get(f"https://www.cubecraft.net/threads/ccg-memes.10860/page-{page_number}")
    all_messages = driver.find_elements(By.CLASS_NAME, "message-inner")

    for message in all_messages:
        message_obj = handle_message(message)

        if message_obj is not None:
            message_obj.save()
    
    driver.close()


def main():
    page_number = starting_page
    while True:
        print(f"Handling page {page_number}")
        if page_number <= ending_page:
            handle_page(page_number)
            page_number += 1
        
            with open("last_page.txt", "w") as f:
                f.write(str(page_number))
        else:
            break

if __name__ == "__main__":
    main()