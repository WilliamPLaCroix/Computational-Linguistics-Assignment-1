import random
import re
import sys
import timeit
from collections import OrderedDict
from math import log

import matplotlib.pyplot as plt  # v3.3.4
import ngram

paths = {
    "jungle_book_path": "./junglebook.txt",
    "bible_path": "./kingjamesbible_tokenized.txt",
    "bulgarian_path": "./SETIMES.bg-tr.bg",
    "turkish_path": "./SETIMES.bg-tr.tr",
}

corpora_list = ["jungle_book", "bible", "bulgarian", "turkish"]
problems = ["problem 1", "problem 2", "problem 3"]


def main():
    """
    Basically just splash screen UI
    Individual problems are self-contained in functions
    All program functions are defined in alphabetical order
    """
    while True:
        # Query user action
        problem = user_input(
            "Which problem are would you like to test? Type:", problems
        )
        while problem == "problem 1":
            problem_1()
            # Repeat process?
            answer = user_input("Shall we load another corpus? ", ["yes", "no"])
            if answer == "no":
                break
        # Bulgarian SETIMES 4-gram maxed out at 16.8s runtime
        while problem == "problem 2":
            problem = problem_2(problem)  # needs an argument+return to exit loop

        # Problem 3 has outstandingly long runtime. Works fine on shorter corpora,
        # Jungle Book only takes 13s, but even just the Bible took my pc 6 minutes.
        # Avoid running this for the SETIMES corpora.

        while problem == "problem 3":
            problem_3()
            # Repeat process?
            answer = user_input("Shall we try another corpus? ", ["yes", "no"])
            if answer == "no":
                break
    return


def dictify_txt(corpus_tokenized, count_punct):
    word_dict = {}
    for word in corpus_tokenized:
        if count_punct == "no" and word.isalpha() == False:
            print(f"deleting {word} from dictionary...")
            continue
        word = word.lower().strip()
        # Checks dictionary for word, adds with count 1 when missing, increments count when present
        word_dict[word] = word_dict.get(word, 0) + 1
    # sorting by count
    word_dict = OrderedDict(
        sorted(word_dict.items(), key=lambda item: item[1], reverse=True)
    )
    return word_dict


def format_word(context, word, i, word_count):
    # end of utterance, go out with a bang "!"
    if i == (word_count - 1) and context[-1:].isalpha() == True:
        word = "!"
    # like before, unless there's already punctuation
    if i == (word_count - 1) and context[-1:].isalpha() == False:
        word = ""
    # sentence-case
    if context == "." or context == "!" or context == "?" or i == 0:
        word = word.capitalize()
    # some Bible style to spice things up
    if word == "i" or word == "lord" or word == "he" or word == "him" or word == "his":
        word = word.capitalize()
    # no spacing before punctuation
    if i == 0 or word[-1:].isalpha() == False or context == "'":
        formatted_word = word
    # spacing between words
    else:
        formatted_word = " " + word
    # remove style :(
    new_context = word.lower()
    return formatted_word, new_context


def get_positive_int(prompt):
    # Another variant on input(), which forces positive int user input
    while True:
        value = input(prompt)
        try:
            value = int(value)
        except ValueError:
            print("Please enter an positive, non-zero integer")
            continue
        if value <= 0:
            print("Please enter an positive, non-zero integer")
            continue
        return value


def listify_dict(word_dict):
    indexed_word_list = []
    index = 1  # rank starts counting at 1
    for item in word_dict:
        entry = (index, item, word_dict[item])  # rank, word, count
        indexed_word_list.append(entry)
        index += 1
    print("Corpus loaded and indexed")
    return indexed_word_list


def new_plot(indexed_word_list, corpus, axis):
    x_values = []
    y_values = []
    for word in indexed_word_list:
        x_values.append(word[0])  # word[0] is the rank
        y_values.append(word[2])  # word[2] is the count
    if axis == "linear":
        plt.plot(x_values, y_values)
        plt.title(
            f"Absolute frequency of words in {corpus.capitalize()}\n vs position in frequency list (linear)"
        )
        plt.xlabel("Position in frequency list")
        plt.ylabel("Absolute frequency")
        print("\nlinear plot successful")
    if axis == "log":
        plt.loglog(x_values, y_values)
        plt.title(
            f"Absolute frequency of words in {corpus.capitalize()}\n vs position in frequency list (log)"
        )
        plt.xlabel("Position in frequency list as log(x)")
        plt.ylabel("Absolute requency as log(y)")
        print("log plot successful")
    return plt.show()


def pair_count_txt(corpus_tokenized, ignore_list, punctuation_list=[]):
    word_pairs = {}
    word_list = ["."]
    for i in range(len(corpus_tokenized) - 1):
        word_1 = corpus_tokenized[i]
        word_2 = corpus_tokenized[i + 1]
        # filters out low word counts, and optionally punctuation
        if (
            word_1 in ignore_list
            or word_2 in ignore_list
            or word_1 in punctuation_list
            or word_2 in punctuation_list
        ):
            continue
        # Checks dictionary for word, adds with count 1 when missing, increments count when present
        word_pairs[(word_1, word_2)] = word_pairs.get((word_1, word_2), 0) + 1
        word_list.append(word_2)
    # sorting by count
    word_pairs = OrderedDict(
        sorted(word_pairs.items(), key=lambda item: item[1], reverse=True)
    )
    return word_pairs, len(word_list)


def pmi_word1_word2(word_pair_dict, word_dict, N):
    pmi_dict = {}
    """
    pmi_w1w2 = log(
                    (C_w1w2 * N) / 
                    (C_w1 * C_w2) 
                  )
    """
    for word_pair in word_pair_dict:
        C_w1w2 = word_pair_dict[word_pair]  # word_1 + word_2 absolute frequency
        C_w1 = word_dict[word_pair[0]]  # word_1 absolute frequency
        C_w2 = word_dict[word_pair[1]]  # word_2 absolute frequency
        pmi_w1w2 = round(log((C_w1w2 * N) / (C_w1 * C_w2)), 2)  # calculated PMI
        # create new entry in dict for each word pair as key, and word pair PMI as value
        pmi_dict[word_pair] = pmi_dict.get(word_pair, 0) + pmi_w1w2
    # sort dictionary by PMI
    pmi_dict = OrderedDict(
        sorted(pmi_dict.items(), key=lambda item: item[1], reverse=True)
    )
    return pmi_dict


"""
Problem 1
"""


def problem_1():
    # Query corpus
    corpus = user_input("Which corporus shall we examine? Type: ", corpora_list)
    # start runtime counter
    count_punct = user_input(
        "Do you want to include punctuation in word count? Type: ", ["yes", "no"]
    )
    timer_start = timeit.default_timer()
    # read .txt into dictionary
    word_list = tokenize_txt(f"{corpus}_path")
    word_dict = dictify_txt(word_list, count_punct)
    # index sorted dictionary by count
    indexed_word_list = listify_dict(word_dict)
    # plot those badboys
    new_plot(indexed_word_list, corpus, "linear")
    new_plot(indexed_word_list, corpus, "log")
    # calculate runtime
    timer_stop = timeit.default_timer()
    print("\nOperation completed in:", round(timer_stop - timer_start, 1), " seconds")
    # Press 'start' to continue... 10... 9... 8...
    return


"""
Problem 2
"""


def problem_2(problem):
    # Query corpus
    corpus = user_input("Which corporus shall we examine? Type: ", corpora_list)
    # start runtime counter
    timer_start = timeit.default_timer()
    # read .txt into list
    word_list = tokenize_txt(f"{corpus}_path")
    # calculate runtime
    timer_stop = timeit.default_timer()
    print("\nCorpus loaded in:", round(timer_stop - timer_start, 1), " seconds")
    # Query n value for n-gram
    n_choice = int(user_input("How many ns would you like to gram? ", ["2", "3", "4"]))
    # start runtime counter
    timer_start = timeit.default_timer()
    new_ngram = ngram.BasicNgram(n_choice, word_list)
    # calculate runtime
    timer_stop = timeit.default_timer()
    print("\nN-gram generated in:", round(timer_stop - timer_start, 1), " seconds")
    # Query word count for arbitrarily long text generation
    while True:
        word_count = get_positive_int(
            "How many words long do you want this utterance to be? (please specify an integer) "
        )
        # Generate pretty, formatted utterances
        utterance = word_salad(n_choice, new_ngram, word_list, word_count)
        # Sometimes shit happens, and we try again...
        if utterance == None:
            continue
        print(utterance)
        # Repeat process?
        answer = user_input("Shall we try again? ", ["yes", "no"])
        if answer == "no":
            problem = ""
            return problem


"""
Problem 3
"""


def problem_3():
    # Query corpus
    corpus = user_input("Which corporus shall we examine? Type: ", corpora_list)
    # start runtime counter
    timer_start = timeit.default_timer()
    print(
        "Please be patient, this part runs in what feels like O(n^2) or O(2^n) time..."
    )
    # read .txt into dictionary for individual counts
    corpus_tokenized = tokenize_txt(f"{corpus}_path")
    word_dict = dictify_txt(corpus_tokenized, "yes")
    # filter for word counts < 10 and non-alpha characters
    ignore_list = [word for word, count in word_dict.items() if count < 10]
    punctuation_list = [
        word for word, count in word_dict.items() if word[-1:].isalpha() == False
    ]
    print("Counting word pairs. . .")
    # read .txt into dictionary for pair counts, ignoring words of count < 10, and non-alpha character words
    word_pairs_full, N_full = pair_count_txt(corpus_tokenized, ignore_list)
    print("Full list of word pairs counted and sorted by frequency.")
    word_pairs_no_punctuation, N_no_punctuation = pair_count_txt(
        corpus_tokenized, ignore_list, punctuation_list
    )
    print(
        "List of word pairs with punctuation removed counted and sorted by frequency."
    )
    timer_stop = timeit.default_timer()
    print(
        "\nCorpus loaded and indexed in:",
        round(timer_stop - timer_start, 1),
        " seconds...",
    )

    timer_start = timeit.default_timer()
    pmi_pairs_full = pmi_word1_word2(word_pairs_full, word_dict, N_full)
    print(
        "Full list of pmi values for word pairs, ignoring words with fewer than 10 occurrences, calculated!"
    )
    pmi_pairs_no_punctuation = pmi_word1_word2(
        word_pairs_no_punctuation, word_dict, N_no_punctuation
    )
    print(
        "List of pmi values for word pairs, ignoring punctuation and words with fewer than 10 occurrences, calculated!"
    )
    # rank the dictiopnaries by count
    indexed_word_pairs = listify_dict(pmi_pairs_full)
    indexed_word_pairs_no_punctuation = listify_dict(pmi_pairs_no_punctuation)
    top_20 = []
    bottom_20 = []
    top_20_no_punctuation = []
    bottom_20_no_punctuation = []
    for i in range(20):
        top_20.append((indexed_word_pairs[i][1], indexed_word_pairs[i][2]))
        bottom_20.append((indexed_word_pairs[-i][1], indexed_word_pairs[-i][2]))
        top_20_no_punctuation.append(
            (
                indexed_word_pairs_no_punctuation[i][1],
                indexed_word_pairs_no_punctuation[i][2],
            )
        )
        bottom_20_no_punctuation.append(
            (
                indexed_word_pairs_no_punctuation[-i - 1][1],
                indexed_word_pairs_no_punctuation[-i - 1][2],
            )
        )

    print("\nMost frequent 20 word pairs are as follows:")
    for listing in top_20:
        print(f"Word pair (w1,w2): {listing[0]}, pmi = {listing[1]}")
    print("\nLeast frequent 20 word pairs are as follows:")
    for listing in bottom_20:
        print(f"Word pair (w1,w2): {listing[0]}, pmi = {listing[1]}")
    print("\nMost frequent 20 word pairs, with punctuation removed, are as follows:")
    for listing in top_20_no_punctuation:
        print(f"Word pair (w1,w2): {listing[0]}, pmi = {listing[1]}")
    print("\nLeast frequent 20 word pairs, with punctuation removed, are as follows:")
    for listing in bottom_20_no_punctuation:
        print(f"Word pair (w1,w2): {listing[0]}, pmi = {listing[1]}")

    # calculate runtime
    timer_stop = timeit.default_timer()
    print("\nOperation completed in:", round(timer_stop - timer_start, 1), " seconds")
    return


def tokenize_txt(corpus, punctuation_list=[]):
    word_list = []
    try:
        # File I/O
        with open(paths[corpus], "r", encoding="utf-8") as file:
            file_string = file.read()
    except FileNotFoundError:
        sys.exit(f"Could not find {corpus}, exiting...")
    cleaned_file = re.sub(r"([.,;:\'\"\[\]\{\}\/\(\)])", r" \1 ", file_string)
    words = cleaned_file.split()
    for word in words:
        if word not in punctuation_list:
            word = word.lower().strip()
            word_list.append(word)
    return word_list


def user_input(prompt, options):
    """
    This function is basically just input(), but forces user to enter one of the listed options.
    It makes navigating via terminal more pleasant (avoids crashes due to typos)
    """
    while True:
        try:
            choice = input(
                f"{prompt} {', '.join(options)} - or press ctrl+d to exit\n"
            ).lower()
            if choice not in options:
                print("\nPlease select from the options given:")
                continue
        except EOFError:
            sys.exit("Goodbye!")
        return choice


def word_salad(n_choice, ngram, word_list, word_count):
    """
    Could I have made this into 3 separate functions to be more concise? Probably.
    Could I have intelligently designed my function to take variable arguments in order
        to accommodate 1 < n < 5? Less likely... Here's what you get instead:
    """
    sentence = "\n    "  # nice first-line indent

    """
    bi-gram section
    """
    if n_choice == 2:
        context = (
            "."  # I wanted the first word of output to be a good "sentence starter"
        )
        for i in range(word_count):
            word_probability = ngram[context,]
            try:
                word = word_probability.generate()
            except IndexError:
                print("missing data for context, try a different text / number of n's")
                return
            # format_word() handles spacing and capitalization
            formatted_word, new_context = format_word(context, word, i, word_count)
            # append new word, shift context down one
            sentence += formatted_word
            context = new_context
    """
    tri-gram section
    """
    if n_choice == 3:
        random.seed()
        context_2 = (
            "."  # I wanted the first word of output to be a good "sentence starter"
        )
        """
        I wasn't sure how to handle starter words for n > 2, so I forced it to randomly generate a 
        valid context based on seen data from the corpus. Not sure if this is the best way...
        """
        while True:
            # makes ngram based on random word choice
            context_1 = random.choice(word_list)
            seed = ngram[
                context_1,
                context_2,
            ]
            try:
                # checks that that word pair is seen in probablity data
                word = seed.generate()
            except IndexError:
                continue
            break

        for i in range(word_count):
            word_probability = ngram[
                context_1,
                context_2,
            ]
            try:
                word = word_probability.generate()
            except IndexError:
                print("missing data for context, try a different text or value for n")
                return
            # format_word() primarily handles spacing and capitalization, with some Bible-style flair
            formatted_word, new_context = format_word(context_2, word, i, word_count)
            # append new word, shift context down one
            sentence += formatted_word
            context_1 = context_2
            context_2 = new_context
    """
    quad-gram section
    """
    if n_choice == 4:
        random.seed()
        context_3 = (
            "."  # I wanted the first word of output to be a good "sentence starter"
        )
        """
        I wasn't sure how to handle starter words for n > 2, so I forced it to randomly generate a 
        valid context based on seen data from the corpus. Not sure if this is the best way...
        """
        while True:
            # makes ngram based on random word choice
            context_1 = random.choice(word_list)
            context_2 = random.choice(word_list)
            seed = ngram[
                context_1,
                context_2,
                context_3,
            ]
            try:
                # checks that that word sequence is seen in probablity data
                word = seed.generate()
            except IndexError:
                continue
            break

        for i in range(word_count):
            word_probability = ngram[context_1, context_2, context_3]
            try:
                word = word_probability.generate()
            except IndexError:
                print("missing data for context, try a different text or value for n")
                return
            # format_word() handles spacing and capitalization
            formatted_word, new_context = format_word(context_3, word, i, word_count)
            # append new word, shift context by one
            sentence += formatted_word
            context_1 = context_2
            context_2 = context_3
            context_3 = new_context
    # fingers crossed!
    return sentence


if __name__ == "__main__":
    main()
