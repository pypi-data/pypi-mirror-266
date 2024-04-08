import logging
import time
import urllib

import requests
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.parse
import pinyin as pin_to_num

from .Dictionary import Dictionary

class YellowBridgeDictionary(Dictionary):

    def __init__(self, debug_level):
        self.logger = logging.getLogger('autoanki.ybdict')
        self.logger.setLevel(debug_level)
        self.logger.debug(f"logger active")
        self.logger.info("Loading Yellowbridge...")

    def find_word(self, word, cache_number=None):
        '''
        Helper function for complete_unfinished_dictionary_records() Takes a word (one or more characters),
        finds them on YellowBridge, and adds them to the dictionary
        :param word: The word to find on YellowBridge.
        :param cache_number: The secondary page number for a word with multiple definitions. (See comments in body of
        function)
        :return:
        '''
        if word == None or word == '':
            return

        self.logger.debug("Finding: " + repr(word))

        urlx = "http://www.yellowbridge.com/chinese/dictionary.php?word="
        url = urlx + urllib.parse.quote(word)
        if cache_number is not None:
            url += "&cache=" + cache_number

        driver = webdriver.Chrome()
        response = driver.get(url)
        html = driver.page_source
        # response = requests.get(url, headers={ 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'})
        yellowbridge_soup = BeautifulSoup(html, "html.parser")
        main_data = yellowbridge_soup.find(id='mainData')
        self.logger.debug(yellowbridge_soup)

        # Some definitions will show up on the page differently because they have multiple meanings/pronunciations
        # These pages link to other pages with a different 'cache' number
        # Default 了 page:
        # https://www.yellowbridge.com/chinese/dictionary.php?word=%E4%BA%86
        # Page for le:
        # https://www.yellowbridge.com/chinese/dictionary.php?word=%E4%BA%86&cache=5114
        # Page for laio:
        # https://www.yellowbridge.com/chinese/dictionary.php?word=%E4%BA%86&cache=5115
        # To solve this, return `find_word()` with the first cache number
        if not main_data:
            self.logger.debug("Main data not found. Multiple definitions")
            # print("This is not a definition page. getting all sub-pages")
            matching_results = yellowbridge_soup.find(id='multiRow')
            # Grab first row. This is usually the most common definition
            rows = matching_results.find_all('tr')
            if not rows:
                self.logger.error("No rows found ")
                return None
            # print(row.find('a'))
            href = str(row.find('a')['href'])
            # print(href)
            cache_number_from_href = href.split("word=")[1].split("&")[1].replace("cache=", "")

            return self.find_word(word, cache_number_from_href)

        definition = \
        traditional_script = \
        pinyin = \
        pinyin_num = \
        part_of_speech = \
        hsk_level = \
        top_level = \
        composing_words = None

        main_data = main_data.find_all('tr')

        # Collect all necessary information from the page:
        for row in main_data:
            row_info_type = row.find('td').getText()
            row_info = row.find_all('td')[1].getText()
            # print(row_info_type + ":")
            # print(row_info)
            if row_info_type == "English Definition":
                definition = row_info
            elif row_info_type == "Simplified Script":
                simplified_script = row_info
            elif row_info_type == "Traditional Script":
                traditional_script = row_info.split("P")[0]
            elif row_info_type == "Pinyin":
                pinyin = row_info
                pinyin_num = pin_to_num.get(word, format="numerical")
            elif row_info_type == "Part of Speech":
                part_of_speech = row_info
            elif row_info_type == "Proficiency Test Level":
                proficiency_level = row_info
                if "HSK=" in proficiency_level:
                    hsk_level = proficiency_level.split("HSK=")[1].split(";")[0]
                if "TOP=" in proficiency_level:
                    top_level = proficiency_level.split("TOP=")[1].split(";")[0]

        word_decomposition_soup = yellowbridge_soup.find(id='wordDecomp')
        if len(word) > 1:
            composing_words_list = word_decomposition_soup.find_all('tr')
            composing_words = ""
            for composing_word in composing_words_list:
                composing_words += str(composing_word.find_all('td')[0].find('a').getText()) + ";"

        # This is all of the information that has been collected
        # print([definition, simplified_script, traditional_script,pinyin,pinyin_num, part_of_speech,hsk_level,top_level,composing_words])
        params = [traditional_script, part_of_speech, pinyin, pinyin_num,
                  composing_words, hsk_level, top_level, definition, word]
        # Add the information for this word to the database
        return params

    def size(self):
        return 0

