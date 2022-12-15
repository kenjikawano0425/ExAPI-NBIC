import pickle
import dawg
import spacy
nlp = spacy.load("en_core_web_sm")

import os
resources_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../../resources"
    )
)



def Road_dictionary(name):

    taglist_filepath = os.path.join(resources_dir, f"{name}_tag.pickle")
    alllist_filepath = os.path.join(resources_dir, f"{name}_dawg.pickle")

    with open(taglist_filepath, 'rb') as f:
        taglist = pickle.load(f)
    with open(alllist_filepath, 'rb') as f:
        completion_dawg = pickle.load(f)
    return taglist, completion_dawg


def DawgMatchingAnnotator(paragraph, name):
    taglist, completion_dawg = Road_dictionary(name)
    annotated_list = []
    doc = nlp(paragraph, disable=["ner", "lemmatizer", "textcat"])
    for chunk in doc.noun_chunks:
        if not chunk.text.lower() in nlp.Defaults.stop_words:
            if len(chunk.text.lower()) > 1:
                start = chunk.start_char
                end = chunk.start_char + len(chunk.text)
                subwordslist = chunk.text.split(" ")
                subwordslist.reverse()
                subwords = [
                    " ".join(list(reversed(subwordslist[0:i+1]))) for i in range(len(subwordslist))
                ]
                for subword in subwords:
                    if subword.lower() in completion_dawg and len(subword) > 1:
                        for tags in taglist:
                            if subword.lower() in tags:
                                start = chunk.start_char + (len(chunk.text) - len(subword))
                                annotated_list.append([start, end, paragraph[start:end], tags[0]])

    return annotated_list