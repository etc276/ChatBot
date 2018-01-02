from bs4 import BeautifulSoup
import requests
import re

DECK_URL = "https://www.trumpfans.com/decks/"

def get_deck_code():
    global DECK_URL
    resp = requests.get(url=DECK_URL)
    if resp.status_code != 200:
        print("error")
    dom = resp.text
    soup = BeautifulSoup(dom, 'html.parser')
    decks = soup.find_all('p', hidden="", id=re.compile("^deck"))
    codes = []
    for deck in decks:
        codes.append(deck.getText())
    
    return codes

