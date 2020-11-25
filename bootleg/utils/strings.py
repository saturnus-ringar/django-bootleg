import difflib
import json
import random
import re
import unicodedata
from itertools import chain
from itertools import combinations
from pprint import pprint

from django.utils.safestring import mark_safe

from bootleg.utils import lists


# https://stackoverflow.com/a/50152237/9390372
def remove_non_printable(string):
    return ''.join(c for c in string if c.isprintable())


def remove_urls(string):
    return re.sub(r'http\S+', '', string)


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def list_to_lower(list):
    lower_case = []
    for word in list:
        lower_case.append(word.lower())
    return lower_case


def highlight(value, query):
    if query:
        highlighted_chunk = value
        regex = re.compile(query, re.UNICODE | re.IGNORECASE)
        m = regex.search(highlighted_chunk)
        if m:
            highlighted_chunk = regex.sub('<mark>' + m.group(0) + '</mark>', highlighted_chunk)
        return mark_safe(highlighted_chunk)
    else:
        return value


def get_random_emoji():
    emojis = ["ʕ◉ᴥ◉ʔ", "ʕ•̮͡•ʔ", "ʕ￫ᴥ￩ʔ", "(✿╹◡╹)", "⊂◉‿◉つ", "ヽ(ヅ)ノ",  "米＾－＾米", "●＞ω＜●",
              "(☞◑ω◑)☞", "(╭☞• ⍛• )╭☞", "(☞ ͡° ͜ʖ ͡°)☞", "（╭☞•́⍛•̀)╭☞", "(￣ー￣)ｂ"]
    return random.choice(emojis)


def append_slash(string):
    if not string.endswith("/"):
        string = string + "/"
    return string


def ends_with_slash(string):
    if not string[-1] == "/":
        return False
    return True


def get_all_string_combinations(string):
    string_parts = string.split(" ")
    if len(string_parts) > 8:
        raise Exception("Too many string parts")

    string_subsets = []
    subsets = chain(*map(lambda x: combinations(string_parts, x), range(0, len(string_parts)+1)))
    for subset in subsets:
        if subset:
            string_subsets.append(" ".join(list(subset)))

    return lists.remove_duplicates(sorted(string_subsets, key=len, reverse=True))


def contains_string_isolated(string, search, case_insensitive=True):
    if case_insensitive:
        string = string.lower()
        search = search.lower()

    if search not in string:
        return False

    string_parts = string.split(" ")
    search_parts = search.split(" ")

    if set(search_parts).issubset(set(string_parts)):
        return True

    return False


def string_words_are_equal(string1, string2, case_insensitive=True):
    if case_insensitive:
        string1 = string1.lower()
        string2 = string2.lower()

    if set(string1.split(" ")) == set(string2.split(" ")):
        return True

    return False


def string_contains_all_strings(string, strings):
    test_string = ""
    for s in strings:
        test_string += s + " "
    test_string = test_string.strip()
    return string_words_are_equal(test_string, string)


def all_alnum_chars_are_in_both_strings(string1, string2):
    chars1 = get_char_list_for_alnum_matching(string1)
    chars2 = get_char_list_for_alnum_matching(string2)
    if chars1 == chars2:
        # the chars are the same, woh!
        return True

    return False


def get_char_list_for_alnum_matching(string):
    string = string.lower().strip()
    alpha_numeric = strip_non_alphanumeric(string).strip()
    alpha_numeric = alpha_numeric.replace(" ", "")
    chars = set(alpha_numeric)
    return sorted(chars)


def dict_to_list_with_values(d):
    list = []
    for key, value in d.items():
        if value:
            list.append(key + " " + str(value))
        else:
            list.append(key)
    return list


def get_line_diff(text1, text2, model_revision=False):
    differ = difflib.Differ()
    if model_revision:
        data1 = json.loads(text1)["fields"]
        data2 = json.loads(text2)["fields"]
        diff_list = list(differ.compare(dict_to_list_with_values(data2),
                                        dict_to_list_with_values(data1)))
    else:
        diff_list = list(differ.compare(text2.splitlines(1), text1.splitlines(1)))

    diff = []

    for line in diff_list:
        if line[0] == '-':
            diff.append(line)
        if line[0] == '+':
            diff.append(line)

    return diff


def get_line_diff_sorted(text1, text2):
    diff = get_line_diff(text1, text2)
    additions = []
    deletions = []
    for line in diff:
        if len(line) > 1:
            if line.startswith("-"):
                deletions.append(line)
            elif line.startswith("+"):
                additions.append(line)

    return additions + deletions


def get_numbers_in_string(string):
    result = re.findall(r'[0-9]+', string)
    if result:
        return "".join(result)

    return None


# https://stackoverflow.com/a/1176023
def camel_to_snake(string):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()


def find_str(s, string):
    index = 0

    if string in s:
        c = string[0]
        for ch in s:
            if ch == c:
                if s[index:index+len(string)] == string:
                    return index

            index += 1

    return -1


def rreplace(s, old, new, occurrence=1):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def json_string_to_readable_html(json_string):
    return dict_to_html(json.loads(json_string))


# http://stackoverflow.com/a/20843828
def dict_to_html(obj, indent=1):
    if isinstance(obj, list):
        htmls = []
        for k in obj:
            htmls.append(dict_to_html(k, indent+1))

        return '[<div style="margin-left: %dem">%s</div>]' % (indent, ',<br>'.join(htmls))

    if isinstance(obj, dict):
        htmls = []
        for k,v in obj.items():
            htmls.append("<span style='color: #888'>%s</span>: %s" % (k, dict_to_html(v, indent+1)))
            #htmls.append("%s: %s" % (k, dict_to_html(v, indent+1)))

        return '{<div style="margin-left: %dem">%s</div>}' % (indent, ',<br>'.join(htmls))

    return str(obj)


def case_insensitive_replace(string, old, new):
    pattern = re.compile(old, re.IGNORECASE)
    return pattern.sub(new, string)


def is_similar_sequence(seq1, seq2):
    ratio = difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()
    if ratio >= 0.55:
        return True
    else:
        return False


def get_similarity_ratio(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()


def string_are_in_one_of_the_strings(string1, string2):
    if not string1 or not string2:
        return False

    if string1.lower() in string2.lower():
        return True
    if string2.lower() in string1.lower():
        return True

    return False


def strip_numeric(string):
    ret_string = " "
    for char in string:
        if not char.isdigit() and char != " ":
            ret_string += char

    return ret_string.strip()


def strip_non_alphanumeric(string):
    ret_string = " "
    for char in string:
        if char.isalnum() or char == " ":
            ret_string += char

    return ret_string.strip()


def strip_non_alphanumeric_as_last_char(string):
    last_char = string[-1:]
    if not last_char.isalnum():
        string = string[:-1]
    return string


def strip_end(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]


def strip_start(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def strip_word_if_string_ends_with(text, end_string):
    string = ""
    for word in text.split():
        if not word.lower().endswith(end_string.lower()):
            string += word + " "
    return string.strip()


def split_string_by_non_alpha_numeric(string):
    excluded_chars = ["&"]
    split_chars = []
    for char in string:
        if not char.isalnum() and char != " " and char not in excluded_chars:
            split_chars.append(char)

    regex = '|'.join(map(re.escape, split_chars))
    split = re.split(regex, string)
    # trim the strings
    split = [x.strip(' ') for x in split]
    # remove empty strings and return
    return filter(None, split)


def truncate(string, max_length=50):
    if string:
        return (string[:max_length] + '...') if len(string) > max_length else string
    else:
        return None


def filter_non_alpha_numeric(strings, min_length=3):
    return_strings = []
    for string in strings:
        if len(string) > min_length:
            test_string = string.replace(" ", "")
            if not test_string.isalnum():
                return_strings.append(string)
    return return_strings


def cleanup_raw_text(text):
    if text:
        text = replace_linebreaks_with_space(text)
        return remove_duplicated_spaces(text).strip()
    else:
        return None


def remove_duplicated_spaces(string):
    return " ".join(string.split())


def replace_linebreaks_with_space(string):
    if string:
        return string.replace("\n", " ").replace("\r", " ").strip()
    return ""


def remove_line_breaks(string):
    if string:
        return string.replace("\n", " ").replace("\r", " ").strip()
    return None


def nl2br(string):
    string = "<br />".join(string.split("\n"))
    string = "<br />".join(string.split("\\n"))
    string = "<br />".join(string.split("\n"))
    string = "<br />".join(string.split("\\r"))
    return mark_safe(string)


# not using this below atm. but keeping it
def get_similarity_score(seq1, seq2, print_debug=False):
    initial_ratio = get_similarity_ratio(seq1, seq2)
    seq1 = strip_non_alphanumeric(seq1)
    seq2 = strip_non_alphanumeric(seq2)
    seq1_parts = list(set(filter(None, seq1.split(" "))))
    seq2_parts = list(set(filter(None, seq2.split(" "))))

    seq1_parts, seq2_parts = make_lists_equally_long(seq1_parts, seq2_parts)
    words_and_ratios = []

    total_split_words_similarity_ratio = 0
    for word1 in seq1_parts:
        total_word_similarity_ratio = 0
        for word2 in seq2_parts:
            similarity_ratio = get_similarity_ratio(word1, word2)
            total_word_similarity_ratio += similarity_ratio

        # for debugging
        words_and_ratios.append({"word": word1,
                                 "similarity_ratio": total_word_similarity_ratio})
        total_split_words_similarity_ratio += total_word_similarity_ratio

    if print_debug:
        print("---------------------------------------")
        print("seq1: ", seq1)
        print("seq2: ", seq2)
        print("initial ratio: ", initial_ratio)
        print("total_split_words_similarity_ratio: ", total_split_words_similarity_ratio)
        pprint(words_and_ratios)

    total_ratio = initial_ratio + (total_split_words_similarity_ratio / len(seq1_parts))
    return int(total_ratio * 100)


def make_lists_equally_long(list1, list2):
    if len(list1) == len(list2):
        return list1, list2

    ret_list1 = []
    ret_list2 = []

    if len(list1) < len(list2):
        for index, string in enumerate(list2):
            ret_list2.append(string)
            try:
                ret_list1.append(list1[index])
            except IndexError:
                ret_list1.append("")

    if len(list2) < len(list1):
        for index, string in enumerate(list1):
            ret_list1.append(string)
            try:
                ret_list2.append(list2[index])
            except IndexError:
                ret_list2.append("")

    return ret_list1, ret_list2


def get_string_split_as_list(string, split_char=" ", lowercase=False):
    if not string:
        return []

    string_list = []
    for word in string.split(split_char):
        if lowercase:
            string_list.append(word.lower())
        else:
            string_list.append(word)

    return string_list
