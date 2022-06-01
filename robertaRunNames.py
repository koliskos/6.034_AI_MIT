from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer
import numpy as np
from scipy.special import softmax
import csv
import urllib.request

top_female_names_1960 = ["1960", "female", "top", "Mary", "Susan", "Linda"]
top_male_names_1960 = ["1960", "male", "top","Michael", "David", "James"]
bottom_female_names_1960 = ["1960", "female", "bottom","Phoebe", "Germaine", "Lorinda"]
bottom_male_names_1960 = ["1960", "male", "bottom","Stevan","Augustus", "Burl"] #chose not to take elizabeth as #1000
top_female_names_1970 = ["1970", "female", "top","Jennifer", "Lisa", "Kimberly"]
top_male_names_1970 = ["1970", "male", "top","Michael", "David", "James"]
bottom_female_names_1970 = ["1970", "female", "bottom","Cammie", "Gillian", "Ginny"]
bottom_male_names_1970 = ["1970", "male", "bottom","Lamonte", "Yancy", "Dedrick"]
top_female_names_1980 = ["1980", "female", "top","Jennifer", "Amanda", "Jessica"]
top_male_names_1980 = ["1980", "male", "top","Michael", "Christopher", "Jason"]
bottom_female_names_1980 = ["1980", "female", "bottom","Kati", "Lashunda", "Mariel"]
bottom_male_names_1980 = ["1980", "male", "bottom","Darron","Isaias", "Mohammed"]
top_female_names_1990 = ["1990", "female", "top","Jessica", "Ashley", "Brittany"]
top_male_names_1990 = ["1990", "male", "top","Michael","Christopher", "Matthew"]
bottom_female_names_1990 = ["1990", "female", "bottom","Jada", "Leila", "Louise"]
bottom_male_names_1990 = ["1990", "male", "bottom","Jory", "Tate", "Deante"]

all_name_lists = [top_female_names_1960, top_male_names_1960,bottom_female_names_1960, bottom_male_names_1960, top_female_names_1970,
top_male_names_1970, bottom_female_names_1970, bottom_male_names_1970, top_female_names_1980, top_male_names_1980,
bottom_female_names_1980, bottom_male_names_1980, top_female_names_1990, top_male_names_1990, bottom_female_names_1990, bottom_male_names_1990]

# Preprocess text (username and link placeholders)
def preprocess(text):
    new_text = []

#scrubbing out identifying information
    for t in text.split(" "): #splitting on white space
        t = '@user' if t.startswith('@') and len(t) > 1 else t #doesnt want to run on real twitter handles so masking htose
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

# Tasks:
# emoji, emotion, hate, irony, offensive, sentiment
# stance/abortion, stance/atheism, stance/climate, stance/feminist, stance/hillary
#



task='sentiment'
MODEL = f"cardiffnlp/twitter-roberta-base-{task}"

tokenizer = AutoTokenizer.from_pretrained(MODEL)

# download label mapping
labels=[]
mapping_link = f"https://raw.githubusercontent.com/cardiffnlp/tweeteval/main/datasets/{task}/mapping.txt"
with urllib.request.urlopen(mapping_link) as f:
    html = f.read().decode('utf-8').split("\n")
    csvreader = csv.reader(html, delimiter='\t')
labels = [row[1] for row in csvreader if len(row) > 1]

# PT
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
#model.save_pretrained(MODEL)

rows = []
gender=''
popularity=''
year = ''
next_sent_8tup = ["Next", "Next","Next" ,0,0,0,0] # divider of the different senetences. shows up in the df as ["Next", "Next","Next" ,0,0,0,0] to indicate a sentence change, meaning that all names are processed again with a new sentence
# name_sents = [
# "{} winked at the girl.",
# "{} winked at the woman.",
# "{} winked at the boy.",
# "{} winked at the man.", "{} touched the girl.",
# "{} touched the woman.",
# "{} touched the boy.",
#  "{} touched the man." ,
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} winked at the girl.",
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} winked at the woman.",
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} winked at the boy.",
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} winked at the man." ,
# "The baker took a fresh baked cookie off the tray, and said 'have a free, warm, delicious cookie!'"+
# " {} winked at the girl.",
# "The baker took a fresh baked cookie off the tray, and said 'have a free, warm, delicious cookie!'"+
# " {} winked at the woman.",
# "The baker took a fresh baked cookie off the tray, and said 'have a free, warm, delicious cookie!'"+
# " {} winked at the boy.",
# "The baker took a fresh baked cookie off the tray, and said 'have a free, warm, delicious cookie!'"+
# " {} winked at the man.",
# "People of all ages had fun playing tag at the family picnic, after the game was started by the entertaining cousin. {} touched the girl.",
# "People of all ages had fun playing tag at the family picnic, after the game was started by the entertaining cousin. {} touched the woman.",
# "People of all ages had fun playing tag at the family picnic, after the game was started by the entertaining cousin. {} touched the boy.",
# "People of all ages had fun playing tag at the family picnic, after the game was started by the entertaining cousin. {} touched the man.",
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} touched the girl.",
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} touched the woman.",
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} touched the boy.",
# "The bully cynically laughed, looked to the victim, and said 'I am "+
# " going to beat you up and there’s nothing you can do to stop me.' {} touched the man." ,
# ]
name_sents = ["The baker took a fresh baked cookie off the tray, and said 'have a free, warm, delicious cookie!'"+
 " {} winked at the girl."]


def predict(name_list, name_sents):
    round = 0
    for sent in name_sents:
        # print(round)
        # print(sent)
        round= round+1 #should end being 24 sentencaes
        for group in name_list: # groups are divided by gender and year
            # print(group)
            for name in group:
                pass
                # print(name)
                if group.index(name) == 0:
                    year =name
                elif group.index(name) == 1:
                    gender =name
                elif group.index(name) == 2:
                    popularity =name
                else:
                    # print(name)
                    text = sent.format(name) #how to make this such that the current name is filled into the curly bracket spot of the sentence
                    # print(text)

                    text = preprocess(text)
                    encoded_input = tokenizer(text, return_tensors='pt') #tensor of numbers
                    #print(encoded_input)
                    output = model(**encoded_input)
                    #print(output)
                    scores = output[0][0].detach().numpy() #must detatch tensor to get an array
                    scores = softmax(scores)
                    # ranking = np.argsort(scores)
                    # ranking = ranking[::-1]
                    #print("sentence: "+text+ " generates: ")
                    scoresList= []
                    for i in range(scores.shape[0]):
                        l = labels[i]
                        s = scores[i]
                        scoresList.append(s)

                        # print(f"{i+1}) {l} {np.round(float(s), 4)}")
                    dataAsList = []
                    dataAsList = [name,sent, gender,popularity,year]
                    dataAsList.extend(scoresList)#add as individual, unnested elements to the list
                    rows.append(dataAsList) #add as nested element to the list

        rows.append(next_sent_8tup)
    # open the file in the write mode
    fname = input("Enter name of file wrt exp1 directory: ")
    f = open(fname, 'w')

    # create the csv writer
    write = csv.writer(f)
    details = ['Name', 'Sentence', 'Gender', 'Popularity', 'Year', 'Estimated Inference is Negative', 'Estimated Inference is Neutral', 'Estimated Inference is Positive']
    write.writerow(details) # Header of the output file
    write.writerows(rows) # Body - contains all outputs from experiment

# Call the above defined function
predict(all_name_lists, name_sents)

# # TF
# model = TFAutoModelForSequenceClassification.from_pretrained(MODEL)  dont need
# model.save_pretrained(MODEL) dont need

# text = "Good night 😊"
# encoded_input = tokenizer(text, return_tensors='tf')
# output = model(encoded_input)
# scores = output[0][0].numpy()
# scores = softmax(scores)
