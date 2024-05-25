import spacy

# Load English language model
nlp = spacy.load('en_core_web_sm')

# Example text
text = "SpaCy is a very powerful NLP library in Python."

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