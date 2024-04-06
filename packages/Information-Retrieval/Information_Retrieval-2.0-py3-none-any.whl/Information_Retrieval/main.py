def hello():
    print("Hello World!!!")
































# Stop Word
import nltk
import re
from nltk.corpus import stopwords

nltk.download('stopwords')
 
def Stop_Word_Removal_Code(filename):
    with open(filename, 'r', encoding='UTF-8') as file:
        data = file.read().lower()

    clean_data = re.sub(r'[^\w\s]', '', data)

    clean_data_list = clean_data.split()

    clean_data_list = sorted([word for word in clean_data_list if word not in stopwords.words('english')])

    return clean_data_list

































# Incident Matrix
from collections import OrderedDict

import sys
sys.path.insert(1, 'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1')

def Incident_Matrix_Creation_Code(documents):
    document_n = []
    for doc in documents:
        document_n.append(Stop_Word_Removal_Code(doc))

    merged_documents = []
    for doc in document_n:
        merged_documents = sorted(list(set(merged_documents).union(set(doc))))

    Incident_Matrix = []
    for word in merged_documents:
        flag = []
        
        for i in range(len(document_n)):
            if word in document_n[i]:
                flag.append(1)
            else:
                flag.append(0)

        Incident_Matrix.append([word] + flag + [' ', ' ', ' ', ' ', ' ', ' ', ' '])

    for word in Incident_Matrix:
        print(f'{word[0]: <20}\t{word[1]}\t{word[2]}\t{word[3]}\t{word[4]}\t{word[5]}\t{word[6]}\t{word[7]}')
        
    print('\n\n')


# Add document paths
# print(Incident_Matrix_Creation_Code([
#     'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_1.txt',
#     'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_2.txt',
#     'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_3.txt',
#     'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_4.txt'
#     ]))






























# Query Resolver
documents = [
    'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_1.txt',
    'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_2.txt',
    'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_3.txt',
    'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_4.txt'
    ]

sorted_dict_incident_matrix = Incident_Matrix_Creation_Code(documents) 

print('\n\n\n')

def flip_bits(string):
    output = ''
    for char in string:
        if char == '0':
            output += '1'
        elif char == '1':
            output += '0'
    return output

def bitwise_and(bin1, bin2):
    int_bin1 = int(bin1, 2)
    int_bin2 = int(bin2, 2)

    result = int_bin1 & int_bin2

    return bin(result)[2:].zfill(len(documents))

def bitwise_or(bin1, bin2):
    int_bin1 = int(bin1, 2)
    int_bin2 = int(bin2, 2)

    result = int_bin1 | int_bin2

    return bin(result)[2:].zfill(len(documents))


query = str(input('Enter a query : '))
query_list = query.upper().split()

print(query)
print(query_list)

for i in range(len(query_list)):
    if query_list[i] == 'NOT':
        query_list[i+1] = flip_bits(query_list[i+1])

print(query_list)

for entry in query_list:
    if entry == 'NOT':
        query_list.remove(entry)

print(query_list)

for i in range(1, len(query_list), 2):
    if query_list[i] == 'AND':
        query_list[i+1] = bitwise_and(query_list[i-1], query_list[i+1])
    elif query_list[i] == 'OR':
        query_list[i+1] = bitwise_or(query_list[i-1], query_list[i+1])

print(query_list)
print(query_list[-1])





























# K-gram
def K_Gram_Code():
    n = int(input("Enter the value for n in n-gram : "))

    filename = "P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_1.txt"

    with open(filename, 'r') as file:
        data = file.read().replace(" ", "$")

    data = f"${data}$"

    output = ""

    for i in range(0, len(data) - n + 1):
        output += data[i:i+n] + "\t"

    print(output)






























# Crawler
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def Crawler(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    text = soup.get_text(' ')
    images = soup.find_all('img')
    links = soup.find_all('a')

    print(text)
    print('\n\n\n')

    for image in images:
        crawled_image = image.get('src')
        print(crawled_image, end='\n')

    print('\n\n\n')

    for link in links:
        crawled_link = link.get('href')
        absolute_link = urljoin(url, crawled_link)
        print(absolute_link, end='\n')

url = 'https://unsplash.com'
Crawler(url)




























# Edit Distance
def Edit_Distance_Code():
    def Edit_Distance(word1, word2):
        edit_matrix = []
        word1_list = [*word_1]
        word2_list = [*word_2]

        for i in range(len(word1) + 1):
            mat = []
            for j in range(len(word2) + 1):
                mat.append(i+j)
            edit_matrix.append(mat)

        for i in range (1, len(edit_matrix)):
            for j in range(1, len(edit_matrix[i])):
                if word1_list[i-1] == word2_list[j-1]:
                    edit_matrix[i][j] = min((edit_matrix[i-1][j] + 1), (edit_matrix[i-1][j-1]), (edit_matrix[i][j-1] + 1))
                elif word1_list[i-1] != word2_list[j-1]:
                    edit_matrix[i][j] = min((edit_matrix[i-1][j] + 1), (edit_matrix[i-1][j-1] + 1), (edit_matrix[i][j-1] + 1))

        return edit_matrix[-1][-1]


    word_1 = 'ALICE'
    word_2 = 'PARIS'

    edit_distance = Edit_Distance(word_1, word_2)

    print(f'\nThe edit distance between {word_1} and {word_2} is {edit_distance}')






























# Cosine Similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def Cosine_Similarity():
    with open('Paragraph_1.txt', 'r', encoding='UTF-8') as file:
        doc1 = file.read()

    with open('Paragraph_2.txt', 'r', encoding='UTF-8') as file:
        doc2 = file.read()

    with open('Paragraph_3.txt', 'r', encoding='UTF-8') as file:
        doc3 = file.read()

    with open('Paragraph_4.txt', 'r', encoding='UTF-8') as file:
        doc4 = file.read()

    with open('Paragraph_5.txt', 'r', encoding='UTF-8') as file:
        doc5 = file.read()

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform([doc1, doc2, doc3, doc4, doc5])

    similarity_matrix = cosine_similarity(tfidf_matrix)

    print('Similarity Matrix')
    print(similarity_matrix)

    for i in range(len(similarity_matrix)):
        for j in range(len(similarity_matrix[i])):
            if similarity_matrix[i][j] > 0.7 and similarity_matrix[i][j] < 0.9999999:
                print(f'Documents {i} and {j} have cosine similarity of {similarity_matrix[i][j]}')




























# Cosine Similarity 2
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

def Cosine_Similarity_2():
    def cosine_similarity(v1, v2):
        dot_product = np.dot(v1, v2)
        nv1 = np.linalg.norm(v1)
        nv2 = np.linalg.norm(v2)

        if nv1 == 0 or nv2 == 0:
            return 0
        else:
            return dot_product / (nv1 * nv2)

    def preprocess_text(text):
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        words = [word.lower() for word in words if word.isalnum() and word.lower() not in stop_words]
        return ' '.join(words)

    def compute_similarity(data):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(data)

        tf_array = tfidf_matrix.toarray()
        tf_terms = vectorizer.get_feature_names_out()

        df = pd.DataFrame(tf_array, columns=tf_terms)

        arr = np.zeros((len(tf_array), len(tf_array)))

        for i in range(len(arr)):
            for j in range(len(arr)):
                arr[i][j] = cosine_similarity(tf_array[i], tf_array[j])

        df_arr = pd.DataFrame(arr)
        print(df_arr, end="\n\n")

        for i in range(len(df_arr)):
            for j in range(i + 1, len(df_arr)):
                if df_arr.iloc[i, j] > 0.7:
                    print(f"Documents {i+1} and {j+1} have cosine similarity: {df_arr.iloc[i, j]}")

    file_paths = [
        "P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_1.txt",
        "P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_2.txt",
        "P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_3.txt",
        "P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_4.txt",
        "P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_1/Paragraph_5.txt"
    ]
    data = [preprocess_text(open(i, 'r').read()) for i in file_paths]

    compute_similarity(data)





























# Soundex
def Soundex_Code():
    input_text = input("Enter a word: ").upper()
    print(f"Input text is {input_text}")

    soundex_word = input_text[0]

    rules = {
        "0": "AEIOUHW",
        "1": "BFPV",
        "2": "CGJKQSXZ",
        "3": "DT",
        "4": "L",
        "5": "MN",
        "6": "R"
    }

    for char in input_text[1:]:
        for key, value in rules.items():
            if char.upper() in value:
                soundex_word += key
                break

    print("Soundex key:", soundex_word)

    new_soundex_word = soundex_word[0]
    for i in range(1, len(soundex_word)):
        if soundex_word[i] != soundex_word[i - 1]:
            new_soundex_word += soundex_word[i]

    print("Soundex key without consecutive duplicates:", new_soundex_word)

    new_soundex_word = new_soundex_word.replace("0", "")

    print("Soundex key without consecutive duplicates and without '0':", new_soundex_word[:4])





























# Page Rank
import numpy as np 

def Page_Rank_Code():
    mat = np.array([
        [1/3, 1/2, 0],
        [1/3, 0, 1/2],
        [1/3, 1/2, 1/2]
    ])

    ini_mat = np.full((len(mat), 1), 1/len(mat))

    B = 0.8

    A = (B * mat) + ((1 - B) * ini_mat)
    print(A)

    temp = np.zeros_like(ini_mat)
    iteration = 1

    while True:
        ini_mat = np.dot(A, ini_mat)
        
        print(f"Iteration {iteration}")
        if np.allclose(ini_mat, temp, atol=1e-4):
            print("Converged!")
            print(ini_mat)
            break
        temp = ini_mat
        iteration += 1
        print(ini_mat)





























# Porter Stemmer
from nltk.stem import PorterStemmer

def Porter_Stemmer_Code():
    porter = PorterStemmer()

    words = ["running", "flies", "agreed", "plastered", "motoring", "conflated", "hunger", "fluttering"]

    for word in words:
        stemmed_word = porter.stem(word)
        print(f"{word} -> {stemmed_word}")





























# Collaborative Filtering
import csv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def Collaborative_Filtering():
    matrix_file = 'P2_INFORMATION_RETRIEVAL/PRACTICAL/Practical_10/data.csv' 
    with open(matrix_file, 'r') as file:
        reader = csv.reader(file)
        matrix = [list(map(int, row)) for row in reader]

    for i in range(len(matrix[0]) + 1):
        if i == 0:
            print("-", end="\t")
        else:
            print(i, end="\t")
    print()

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if j == 0:
                print(chr(i + 65), end="\t")
            if matrix[i][j] == 0:
                print("-", end="\t")
            else:
                print(matrix[i][j], end="\t")
        print("\n")

    cosine_similarity_score = [0, ]

    for i in range(len(matrix) - 1):
        vector1 = np.array(matrix[0]).reshape(1, -1)
        vector2 = np.array(matrix[i + 1]).reshape(1, -1)
        similarity_score = cosine_similarity(vector1, vector2)
        cosine_similarity_score.append(round(similarity_score.item(), 2))

    print(cosine_similarity_score)

    css = cosine_similarity_score.copy()
    max_1 = css.index(max(css))
    css.pop(max_1)
    max_2 = css.index(max(css))

    n = 9

    predicted_rating = ((matrix[max_1][n] * cosine_similarity_score[max_1]) +
                        (matrix[max_2][n] * cosine_similarity_score[max_2])) / (
                            cosine_similarity_score[max_1] + cosine_similarity_score[max_2])

    print(f"The predicted rating is {round(predicted_rating, 3)}")




























# Collaborative Cosine

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def Collab_Cosine():
    matrix_df = pd.read_csv('data.csv', header=None)

    print(matrix_df)

    cosine_similarities = cosine_similarity(matrix_df)
    print(cosine_similarities)

    max_similarities = cosine_similarities.max(axis=1)
    most_similar_indices = max_similarities.argsort()[-2:][::-1]

    index = 9
    predicted_rating = (matrix_df.iloc[most_similar_indices[0], index] * max_similarities[most_similar_indices[0]] +
                        matrix_df.iloc[most_similar_indices[1], index] * max_similarities[most_similar_indices[1]]) / (
                            max_similarities[most_similar_indices[0]] + max_similarities[most_similar_indices[1]])

    print(f"The predicted rating is {round(predicted_rating, 3)}")





























# Colaborative Nearest
def Collab_Nearest():
    import pandas as pd
    from sklearn.neighbors import NearestNeighbors
    from sklearn.metrics.pairwise import cosine_similarity

    matrix_df = pd.read_csv('data.csv', header=None)

    nn_model = NearestNeighbors(n_neighbors=2, metric='cosine')

    nn_model.fit(matrix_df)

    distances, indices = nn_model.kneighbors(matrix_df)
    cosine_similarities = cosine_similarity(matrix_df)

    most_similar_indices = indices[:, 1]

    index = 9 
    predicted_rating = (matrix_df.iloc[most_similar_indices[0], index] + matrix_df.iloc[most_similar_indices[1], index]) / 2

    print(f"The predicted rating is {round(predicted_rating, 3)}")