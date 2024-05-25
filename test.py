import spacy
import evaluate_results
import re

# Load English language model
#nlp = spacy.load('en_core_web_sm')
nlp = spacy.load('de_core_news_sm')

# read generated medical report
dir_name = "4345e4f5-99c1-4445-9ee3-ee93a7f06838"
generated_output_file_name = dir_name + "\\" + "Arztbrief_Max_Mustermann.txt"
generated_output_text = evaluate_results.read_file(generated_output_file_name)

recommendation_regex = "(Empfehlungen|Wir empfehlen):([\w\W]+)Medikamente:"
recommendation_match = re.search(recommendation_regex, generated_output_text)
if recommendation_match is not None:
    recommendation = recommendation_match.group(2)
#print(recommendation)
# Example text
text = "SpaCy is a very powerful NLP library in Python."
text = recommendation

# Process the text
doc = nlp(text)

# Tokenization and Lemmatization
for token in doc:
    print(token.text, token.lemma_)
print("---------------------------------------")

# Part-of-speech tagging
for token in doc:
    print(token.text, token.pos_)
print("---------------------------------------")

# Named Entity Recognition (NER)
for ent in doc.ents:
    print(ent.text, ent.label_)
print("---------------------------------------")

# Dependency Parsing
for token in doc:
    print(token.text, token.dep_, token.head.text, token.head.pos_)
print("---------------------------------------")

# Sentence Segmentation
for sent in doc.sents:
    print(sent.text)
print("---------------------------------------")

# Similarity
text1 = nlp("It's a warm summer day")
text2 = nlp("It's sunny outside")
print(text1.similarity(text2))