# Prompt 97

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_documents(file_paths):
    documents = []
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            documents.append(file.read())
    return documents

def compute_cosine_similarity(documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    cosine_sim = cosine_similarity(tfidf_matrix)
    return cosine_sim

def rank_matches(cosine_sim, file_paths):
    matches = []
    for i in range(len(cosine_sim)):
        for j in range(i + 1, len(cosine_sim)):
            similarity = cosine_sim[i][j]
            matches.append((file_paths[i], file_paths[j], similarity))
    matches.sort(key=lambda x: x[2], reverse=True)
    return matches

def main():
    file_paths = [
        'document1.txt',
        'document2.txt',
        'document3.txt'
    ]
    documents = load_documents(file_paths)
    cosine_sim = compute_cosine_similarity(documents)
    matches = rank_matches(cosine_sim, file_paths)
    
    for match in matches:
        print(f"Match: {match[0]} and {match[1]} with similarity score {match[2]}")

if __name__ == "__main__":
    main()