import pandas as pd
import numpy as np 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tqdm import tqdm

# List of Genres learnt from training data
genre_list=['action','adult','adventure','animation','biography','comedy','crime','documentary','fantasy','game-show','history']

#Define a fallback genre for movies
failback_genre='unknown'

# Load the training set
try:
    with tqdm(total=50, desc='loading Train Data') as pbar:
        train_data= pd.read_csv(r'train_data.txt',sep=':::',header=None,names=['SerialNumbers','MOVIE_NAME','GENRE','MOVIE_PLOT'],engine='python')

        pbar.update(50)
except Exception as e:
    print(f"Error Loading train_data: {e}")
    raise
#Data preprocessing for training data
x_train = train_data['MOVIE_PLOT'].astype(str).apply(lambda doc: doc.lower())
genre_labels = [genre.split(', ') for genre in train_data['GENRE']]
mlb= MultiLabelBinarizer()
y_test = mlb.fit_transform(genre_labels)

#TF-IDF Vectorization
tfidf_vectorizer = TfidfVectorizer(max_features=5000)
#Fit and transform the training data with progress bar
with tqdm(total=50, desc="Vectorizing Training Data")as pbar:
    x_train_tfidf = tfidf_vectorizer.fit_transform(x_train)
    pbar.update(50)

#Train a MultiOutput Naive Bayes classifier using the training data
with tqdm(total=50, desc="Traing Model") as pbar:
    naive_bayens= MultinomialNB()
    multi_output_classifier = MultiOutputClassifier(naive_bayens)
    multi_output_classifier.fit(x_train_tfidf,y_test)
    pbar.update(50)

#Load your test dataset from test_data.txt
try:
    with tqdm (total=50, desc=" Loading Test data") as pbar:
        test_data = pd.read_csv('test_data.txt',sep=':::',header=None, names=['SerialNumber','MOVIE_NAME','MOVIE_PLOT'],engine='python')
        pbar.update(50)
except Exception as e:
    print(f"Error loading test_data: {e}")
    raise
#Data preprocessing for test data
x_test = test_data['MOVIE_PLOT'].astype(str).apply(lambda doc: doc.lower())

#Transform the test data with progress bar
with tqdm(total=50, desc='Vectorizing Test Data') as pbar:
    x_test_tfidf = tfidf_vectorizer.transform(x_test)
    pbar.update(50)

#predict genres on the test data
with tqdm(total=50, desc= 'Predicting on the Test Data') as pbar:
    y_pred = multi_output_classifier.predict(x_test_tfidf)
    pbar.update(50)

#Create a Dataframe for test data with movie names and predict genres
test_movie_names = test_data['MOVIE_NAME']
predicted_genres = mlb.inverse_transform(y_pred)
test_results= pd.DataFrame ({'MOVIE_NAME': test_movie_names, 'PREDICTED_GENRES': predicted_genres})

#Replace empty unpredicted genres with fallback genre
test_results['PREDICTED_GENRES'] = test_results['PREDICTED_GENRES'].apply(lambda genres: [failback_genre] if len(genres)==0 else genres)

#write the results to an output txt file with proper formatting 
with open("model_evalutation.txt","w",encoding="utf-8") as output_file:
    for _, row in test_results.iterrows():
        movie_name= row['MOVIE_NAME']
        genre_str = ', '.join(row['PREDICTED_GENRES'])
        output_file.write(f"{movie_name} ::: {genre_str}\n")

# Calculate evaluation metrics using training labels (as proxy)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Assuming you're using a multi-label classifier, you should predict on the test set instead of the train set.
y_test_pred = multi_output_classifier.predict(x_test_tfidf)

# Ensure that both y_test and y_test_pred have the same number of samples by truncating y_test if necessary
y_test = y_test[:len(y_test_pred)]

# Calculate evaluation metrics using the test set predictions
accuracy = accuracy_score(y_test, y_test_pred)
precision = precision_score(y_test, y_test_pred, average='micro')
recall = recall_score(y_test, y_test_pred, average='micro')
f1 = f1_score(y_test, y_test_pred, average='micro')

# Append the evaluation metrics to the output file
with open("model_evaluation.txt", "a", encoding="utf-8") as output_file:
    output_file.write("\n\nModel Evaluation Metrics: \n")
    output_file.write(f"Accuracy: {accuracy * 100:.2f}%\n")
    output_file.write(f"Precision: {precision:.2f}\n")
    output_file.write(f"Recall: {recall:.2f}\n")
    output_file.write(f"F1-score: {f1:.2f}\n")

print("Model evaluation results and metrics have been saved to 'model_evaluation.txt'.")
