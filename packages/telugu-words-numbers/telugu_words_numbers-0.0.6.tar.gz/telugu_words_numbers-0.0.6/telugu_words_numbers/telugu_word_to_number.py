# importing required libraries
import sys
sys.path.append("./")
from text2digits import text2digits
from difflib import SequenceMatcher
import re
import os
import json
import numpy as np
from typing import Tuple, Union


class TeluguWordsToNumber:

    # constructor to define constants
    def __init__(self) -> None:

        # creating an instance of the text2digit
        self.t2d = text2digits.Text2Digits()

        # get the json files path
        self.dir_name = os.path.dirname(__file__)
        self.tel_num_json = os.path.join(self.dir_name, "json_files", "telugu_numbers.json")
        self.tel_cur_json = os.path.join(self.dir_name, "json_files", "telugu_currency_units.json")
        
        # load the json files
        self.num_word_dict = self.json_load_method(self.tel_num_json)["telugu_dict"]
        self.currency_units_dict = self.json_load_method(self.tel_cur_json)["telugu_units"]

        # thresholds of unigram and bigram
        self.unigram_threshold, self.bigram_threshold = 0.8, 0.9

    # method to load json files
    def json_load_method(self,
                         filename: str
                    ) -> dict:

        with open(filename, "r", encoding="utf8") as f:
            num_word_dict = json.load(f)
            f.close()

        return num_word_dict

    # method for reversing the telugu_dictionary and removing spaces of keys and values
    def reverse_numbers_dict(self) -> dict:

        tel_dict_clean = {}

        for key, value in self.num_word_dict.items():
            for v in value:
                tel_dict_clean[v.lower().strip()] = key.lower().strip()

        tel_dict_clean = dict(
                sorted(tel_dict_clean.items(), key=lambda item: int(item[1]), reverse=True)
            )

        return tel_dict_clean

    # method for creating separate dictionaries for the numbers having one, two and more than two number text
    def create_num_dict(self) -> Tuple[dict, dict]:

        tel_dict_clean = self.reverse_numbers_dict()

        tel_dict_1 = {}  # dict for numbers with single word
        tel_dict_2 = {}  # dict for numbers with two word

        for key, value in tel_dict_clean.items():
            if len(key.split()) == 1:
                tel_dict_1[key] = value
            elif len(key.split()) == 2:
                tel_dict_2[key] = value

        return tel_dict_1, tel_dict_2

    # method to handle 1000s pattern
    def handle_thousand_pattern(self,
                                text: str
                            ) -> Union[int, None]:

        sent_num = re.sub(r"\D", " ", text)
        sent_num = re.sub(" +", " ", sent_num).strip()

        l = []
        flag = False
        for i in sent_num.split():
            l.append(float(i))
            if len(i) == 4:
                flag = True

        if flag and l:
            return sum(l)
        else:
            return None

    # method logic for telugu rupees and paise
    def rupees_paise_logic(self,
                           text: str
                        ) -> Union[int, float]:

        # get the paise and rupees variations
        paise_variations = self.currency_units_dict["paise_unit"]
        rupees_variations = self.currency_units_dict["rupees_unit"]

        if any(variation in text for variation in paise_variations):
            try:
                if any(variation in text for variation in rupees_variations):
                    for variation in rupees_variations:
                        if variation in text:
                            parts = text.split(variation)
                            paise_amount = self.t2d.convert(parts[1])
                            paise_amount = float(re.sub(r"\D", "", paise_amount))

                            rupees_amount = self.t2d.convert(parts[0])
                            rupees_amount = float(re.sub(r"\D", "", rupees_amount))
                            amt = rupees_amount + (paise_amount / 100)
                else:
                    txt_amt = self.t2d.convert(text)
                    amt = self.handle_thousand_pattern(txt_amt)
                    if amt:
                        amt = amt / 100
                    else:
                        amt = float(re.sub(r"\D", "", txt_amt)) / 100
            except:
                amt = 0
        else:
            try:
                txt_amt = self.t2d.convert(text)
                amt = self.handle_thousand_pattern(txt_amt)
                if not amt:
                    amt = float(re.sub(r"\D", "", txt_amt))
            except:
                amt = 0

        return amt

    # method for n-gram (uni-gram and bi-gram)
    def n_gram_method(self,
                      text_org: str
                    ) -> str:

        # calling create_num_dict to get number dictionaries
        tel_dict_1, tel_dict_2 = self.create_num_dict()

        text_list = text_org.split()

        # logic for bi-gram
        n = 0
        for i in range(len(text_list)):
            if n + 1 != len(text_list):
                word = " ".join((text_list[n], text_list[n + 1]))
                n = n + 1

                num_list = []
                org_word_list = []
                dict_word_list = []
                for key, val in tel_dict_2.items():
                    similarity_ratio = SequenceMatcher(None, word, key).ratio()
                    if similarity_ratio >= self.bigram_threshold:
                        num_list.append(similarity_ratio)
                        org_word_list.append(word)
                        dict_word_list.append(key)

                if num_list:
                    org_word = org_word_list[np.argmax(num_list)]
                    dict_word = dict_word_list[np.argmax(num_list)]
                    text_org = text_org.replace(org_word, tel_dict_2[dict_word])

        # logic for uni-gram
        for i in range(len(text_list)):
            num_list = []
            org_word_list = []
            dict_word_list = []
            for key, val in tel_dict_1.items():
                word = text_list[i]
                similarity_ratio = SequenceMatcher(None, word, key).ratio()
                if similarity_ratio >= self.unigram_threshold:
                    num_list.append(similarity_ratio)
                    org_word_list.append(word)
                    dict_word_list.append(key)

            if num_list:
                org_word = org_word_list[np.argmax(num_list)]
                dict_word = dict_word_list[np.argmax(num_list)]
                text_org = text_org.replace(org_word, tel_dict_1[dict_word])

        return text_org

    # method logic for indic word to num
    def word_number_conversion(self,
                               text_org: str,
                            ) -> Tuple[int, Union[str, None], str]:

        try:
            text_org = self.n_gram_method(text_org)

            text_org = (
                    text_org.replace("200", "2 100")
                    .replace("300", "3 100")
                    .replace("400", "4 100")
                    .replace("500", "5 100")
                    .replace("600", "6 100")
                    .replace("700", "7 100")
                    .replace("800", "8 100")
                    .replace("900", "9 100")
                )

            # calling telugu_paise_logic function for paise logic
            num = self.rupees_paise_logic(text_org)

            # applying number logic with package text2digit
            converted_text = self.t2d.convert(text_org)
            return num, converted_text

        except:
            num = 0
            return num, None