import pandas as pd
import os
import datetime
from trankit import Pipeline
import re


def file_logger(start_time, end_time, filename, file_ind):
    print(
        f"file {file_ind} \n processed {filename}\n start time {start_time} end_time {end_time}")
    return


def create_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return


def create_trankit_pipeline(cache_dir):
    return Pipeline('hebrew',
                    cache_dir='C:/Users/noabi/PycharmProjects/cache/')


def split_text(text):
    """taking file raw text and splitting it to sentences,
    returns 2-dimensional array containing splitted sentences"""
    return [re.split(' |,|\t|\.|:|-', sen) for sen in text.split("\n")]


def clean_text(splitted_text):
    """cleaning text from . ? and other signs. returns a list of lists,
    each list has a single element which is a word"""
    clean_text = []
    for sen in splitted_text:
        clean_sen = [''.join(i for i in word if i.isalpha()) for word in sen]
        clean_sen = [word for word in clean_sen if len(word) > 1]
        if clean_sen:
            clean_text.append(clean_sen)
    return clean_text


def run_trankit_file(pipeline, text):
    """processing a single file text and replacing words to be their lemma,
    returns a string"""
    # tokens = pipeline(text, is_sent=True)
    text_splitted = split_text(text)
    clean_text_splitted = clean_text(text_splitted)
    tokens = pipeline.lemmatize(clean_text_splitted)
    # tokens_df = pd.DataFrame.from_dict(
    #     [token["tokens"][0] for token in tokens["sentences"]])
    tokens = [[token.values() for token in sen] for sen in
              [sen["tokens"] for sen in tokens["sentences"]]]
    tokens = [[tuple(token) for token in sen] for sen in tokens]
    tokens_df = pd.DataFrame([t for lst in tokens for t in lst]
                             , columns=["index", "original", "lemma"])

    return " ".join(tokens_df["lemma"].values)


def save_trankit_file(lemmatize_dir, filename, text, file_ind):
    """saving new lemmatized text for the current filename in dir"""
    start_time = datetime.datetime.now()
    lemmatized_file = open(os.path.join(lemmatize_dir, filename), "w",
                           encoding='utf8')
    lemmatized_file.write(text)
    lemmatized_file.close()
    end_time = datetime.datetime.now()
    file_logger(start_time, end_time, filename, file_ind)
    return


def run_trankit_pipeline(base_dir, text_dir, lemmatize_dir, cache_dir):
    pipeline = create_trankit_pipeline(cache_dir)
    done_text = list(os.listdir(lemmatize_dir))
    print(f"starting pipeline at {datetime.datetime.now()}")
    file_ind = 1
    for filename in os.listdir(text_dir):
        if filename in done_text:
            continue
        text_file = open(os.path.join(text_dir, filename), "r",
                         encoding='utf8')
        text = text_file.read()
        text_file.close()
        lemmatized_text = run_trankit_file(pipeline, text)
        save_trankit_file(lemmatize_dir, filename, lemmatized_text, file_ind)
        file_ind += 1
    print(f"ending pipeline at {datetime.datetime.now()}")
    return


if __name__ == "__main__":
    base_dir = r"C:\Users\noabi\PycharmProjects\University"
    text_dir = os.path.join(base_dir, "NevoTxt")
    lemmatize_dir = os.path.join(base_dir, r"TrankitLemmatizedText")
    cache_dir = base_dir
    run_trankit_pipeline(base_dir, text_dir, lemmatize_dir, cache_dir)
