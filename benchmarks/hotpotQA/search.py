import dspy
import bm25s
import Stemmer
import ujson

stemmer = Stemmer.Stemmer("english")
retriever = bm25s.BM25.load("/Users/priyanjindal/prompt-learning/benchmarks/hotpotQA/wiki17_abstracts", corpus_name="wiki17_abstracts_corpus.jsonl", load_corpus=True)
corpus = retriever.corpus

def search(query: str, k: int) -> list[dict]:
    tokens = bm25s.tokenize(query, stopwords="en", stemmer=stemmer, show_progress=False)
    results, scores = retriever.retrieve(tokens, k=k, n_threads=1, show_progress=False)
    
    # results[0] contains dicts with 'id' and 'text' keys
    # Extract titles and store full text in DOCS
    formatted_results = []
    for doc in results[0]:
        text = doc['text']
        
        # Parse title and content if in "title | content" format
        if " | " not in text:
            print("No title found in text")
            return []
        title, content = text.split(" | ", 1)
        formatted_results.append({"title": title, "content": content})
    
    return formatted_results


if __name__ == "__main__":
    results = search("What is the capital of France?", 10)
    print(f"Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result[:200]}...")  # Print first 200 chars of each result
    
    print(f"\nDOCS dictionary has {len(DOCS)} entries")
    print(f"Keys: {list(DOCS.keys())[:5]}")  # Show first 5 keys