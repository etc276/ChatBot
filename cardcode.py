from bs4 import BeautifulSoup
import requests
import re

DECK_URL = "https://www.trumpfans.com/decks/"

def main():
    global DECK_URL
    resp = requests.get(url=DECK_URL)
    if resp.status_code != 200:
        print("error")
    dom = resp.text
    soup = BeautifulSoup(dom, 'html.parser')
    buttons = soup.find_all('p', hidden="", id=re.compile("^deck"))
    print(buttons[0].getText())


if __name__=='__main__':
    main()

