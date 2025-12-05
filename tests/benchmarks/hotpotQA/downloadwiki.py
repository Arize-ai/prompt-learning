from dspy.utils import download
import tarfile
import ujson

# download("https://huggingface.co/dspy/cache/resolve/main/wiki.abstracts.2017.tar.gz")
# with tarfile.open("wiki.abstracts.2017.tar.gz", "r:gz") as tar:
#     tar.extractall()

corpus = []

with open("wiki.abstracts.2017.jsonl") as f:
    for line in f:
        line = ujson.loads(line)
        corpus.append(f"{line['title']} | {' '.join(line['text'])}")

print(len(corpus))

import bm25s
import Stemmer

stemmer = Stemmer.Stemmer("english")
corpus_tokens = bm25s.tokenize(corpus, stopwords="en", stemmer=stemmer)

retriever = bm25s.BM25(k1=0.9, b=0.4)
retriever.index(corpus_tokens)

retriever.save(
    "wiki17_abstracts", corpus=corpus, corpus_name="wiki17_abstracts_corpus.jsonl"
)
