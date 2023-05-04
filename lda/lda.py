import os
import time
from gensim.corpora import Dictionary
from gensim.models import LdaModel
import logging
import pandas as pd
from gensim.test.utils import datapath
from gensim import models
import numpy as np

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)


def split_text(text):
    return text.split(" ")


def create_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory


def remove_rare_and_common_words(docs, no_below, no_above):
    """using gensim Dictionary object in order to filter common + rare words"""
    dictionary = Dictionary(docs)
    dictionary.filter_extremes(no_below=no_below, no_above=no_above)
    return dictionary


def create_bag_of_words(dictionary, docs):
    """creating bag of words out of filtered Dictionary gensim object"""
    corpus = [dictionary.doc2bow(doc) for doc in docs]
    return corpus


def run_lda_pipeline(base_dir, lemmatize_dir, results_dir):
    docs = []
    filenames_lst = []
    for filename in os.listdir(lemmatize_dir):
        text_file = open(os.path.join(lemmatize_dir, filename), "r",
                         encoding='utf8')
        text = text_file.read()
        text_file.close()
        splitted_text = split_text(text)
        docs.append(splitted_text)
        filenames_lst.append(filename)

    # TODO - change Dictionary Params
    dictionary = remove_rare_and_common_words(docs, 1, 0.5)
    corpus = create_bag_of_words(dictionary, docs)

    temp = dictionary[0]  # This is only to "load" the dictionary.
    id2word = dictionary.id2token

    # to modify hyper-parameters
    params_dict = {"num_topics": 13,
                   "chunksize": 2000,
                   "passes": 30,
                   "iterations": 400,
                   "eval_every": None,
                   "alpha": 0.6,
                   }
    model = LdaModel(
        corpus=corpus,
        id2word=id2word,
        chunksize=params_dict["chunksize"],
        alpha=params_dict["alpha"],
        eta='auto',
        iterations=params_dict["iterations"],
        num_topics=params_dict["num_topics"],
        passes=params_dict["passes"],
        eval_every=params_dict["eval_every"]
    )

    # giving a unique identifier for file
    model_identifier = int(time.time())

    # creating a directory for each model
    results_dir = create_dir(os.path.join(results_dir, f"{model_identifier}"))

    save_excel_dir = os.path.join(results_dir, f'topics.csv')
    pd.DataFrame(model.print_topics(num_topics=-1)).to_csv(save_excel_dir)

    # saving model object
    save_model_dir = os.path.join(results_dir, f'model')
    model_file = datapath(save_model_dir)
    model.save(model_file)

    # saving topics per document
    doc_topics_lst = []
    for doc_ind in range(len(docs)):
        doc_topics = model.get_document_topics(corpus[doc_ind])
        doc_filename = filenames_lst[doc_ind]
        for topic in doc_topics:
            doc_topics_lst.append((doc_filename,) + topic)

    save_doc_topics_dir = os.path.join(results_dir, f'docs_topics.csv')

    df = pd.DataFrame(doc_topics_lst,
                      columns=["filename", "topic_id", "topic_prob"])

    df = df.pivot(index="filename", columns="topic_id",
                  values="topic_prob").reset_index()
    df.replace(np.nan, 0).to_csv(save_doc_topics_dir)
    return corpus, save_model_dir


def load_lda_model(model_path, bow):
    """takes in model_path and bag of words (documents) and returns the model
    object + attributes
    model_path = full path including modelfile name"""
    model = models.ldamodel.LdaModel.load(model_path)
    return


if __name__ == "__main__":
    base_dir = r"C:\Users\noabi\PycharmProjects\University"
    lemmatize_dir = os.path.join(base_dir, r"TrankitLemmatizedTextTest")
    results_dir = os.path.join(base_dir, r"YapLdaResults")
    bow, save_mofel_dir = run_lda_pipeline(base_dir, lemmatize_dir,
                                           results_dir)
    load_lda_model(save_mofel_dir, bow)
