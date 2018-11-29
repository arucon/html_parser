import sys
import re
import pprint
import logging.handlers
import argparse

import urllib


class HTMLParser(object):
    """
    HTML Parser
    sort letter and number by ascending
    html mode ignore tag, text mode include all
    chunk by quotient
    print quotient and remainder
    """
    def __init__(self, url, mode, quotient):
        """
        init
        :param url: url for parse
        :param mode: mode for parse / html or text
        :param quotient: quotient for chunk / int
        """
        self.url = url
        self.mode = mode
        self.quotient = quotient

        self.req_i = 0

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    @staticmethod
    def clean_html(raw_html):
        """
        staticmethod for remove tag
        :param raw_html: raw html content
        :return: html removed content
        """
        return re.sub(re.compile('<.*?>'), '', raw_html)

    def request_post(self):
        """
        request url by url open
        if connect fail, try reconnect
        :return: response
        """
        try:
            rsp = urllib.urlopen(self.url)
        except IOError as e:
            self.logger.info(e)
            self.logger.info("ReTry to URL: " + str(self.url))
            if self.req_i < 2:
                self.req_i += 1
                self.logger.info("ReTry to URL: " + str(self.url))
                rsp = self.request_post()
            else:
                self.req_i = 0
                rsp = None
        return rsp

    def parse_content(self):
        """
        parse content only alphabet and integer
        :return: parsed letter and number
        """
        rsp = self.request_post()
        if not rsp:
            self.logger.info("URL IS ILLEGAL")
            sys.exit()

        raw_html = rsp.read()
        if self.mode == 'html':
            html = self.clean_html(raw_html)
        elif self.mode == 'text':
            html = raw_html
        else:
            self.logger.info("MODE IS ILLEGAL")
            sys.exit()

        letters = re.sub(r"[^A-Za-z]+", '', html)
        numbers = re.sub(r"[^0-9]+", '', html)
        return letters, numbers

    @staticmethod
    def sort_content(contents):
        """
        sorting contents
        :param contents:
        :return:
        """
        return ''.join(sorted(contents)).strip()

    @staticmethod
    def sort_letter(list_letters):
        """
        sort alphabet by ascending
        :param list_letters:
        :return:
        """
        return sorted(list_letters, key=lambda a: sum(([a[:i].lower(), a[:i]] for i in range(1, len(a)+1)), []))

    @staticmethod
    def merge_list(list_letters, list_numbers):
        """
        merge letter and number list by cross
        :param list_letters:
        :param list_numbers:
        :return:
        """
        list_m = []
        for i in range(len(list_letters) + len(list_numbers)):
            if list_letters:
                list_m.append(list_letters.pop(0))
            if list_numbers:
                list_m.append(list_numbers.pop(0))
        return list_m

    def chunk_list(self, src_list):
        """
        chunk list by quotient
        :param src_list: source list to chunk
        :return: nested quot list, remainder list
        """
        c_list = (list(self.chunks(src_list, self.quotient)))
        quot = []
        remainder = []
        if len(c_list[-1]) < self.quotient:
            remainder = c_list.pop()
        if c_list:
            quot = c_list
        return quot, remainder

    @staticmethod
    def chunks(l, n):
        """
        chunk list
        if use python 3 version, change xrange to range
        :param l:
        :param n:
        :return:
        """
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    @staticmethod
    def pretty_print(l):
        """
        pprint for print
        :param l: list or string for print
        :return: None
        """
        pprint.pprint(l)

    def run(self):
        """
        Main code for run
        :return: nested quot list, remainder list
        """
        self.logger.info("HTML PARSER START ...")

        self.logger.info("Parsing HTML")
        str_letter, str_number = self.parse_content()

        self.logger.info("Sorting Letter")
        list_letter = list(self.sort_content(str_letter))
        list_letter = self.sort_letter(list_letter)

        self.logger.info("Sorting Number")
        list_number = list(self.sort_content(str_number))

        self.logger.info("Merge List")
        list_merged = self.merge_list(list_letter, list_number)

        self.logger.info("Chunk List")
        return self.chunk_list(list_merged)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='Type URL / http://www.wemakeprice.com')
    parser.add_argument('mode', help='Type html or text')
    parser.add_argument('quotient', type=int, help='Type integer 1 ~ n')
    args = parser.parse_args()

    test_parser = HTMLParser(args.url, args.mode, args.quotient)
    q, r = test_parser.run()

    test_parser.pretty_print("Quotient")
    test_parser.pretty_print(q)
    test_parser.pretty_print("Remainder")
    test_parser.pretty_print(r)
