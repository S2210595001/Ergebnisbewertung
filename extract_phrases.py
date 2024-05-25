import evaluate_results
import re

import spacy

# Load the spaCy model
nlp = spacy.load('de_core_news_sm')

def extract_phrases(text):
    doc = nlp(text)

    # Extract keywords using noun chunks
    phrases = [chunk.text for chunk in doc.noun_chunks]

    # Extract named entities
    entities = [ent.text for ent in doc.ents]

    # Extract specific POS tags (Nouns and Proper Nouns)
    pos_keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN', 'VERB']]

    return phrases, entities, pos_keywords


# read generated medical report
dir_name = "4345e4f5-99c1-4445-9ee3-ee93a7f06838"
generated_output_file_name = dir_name + "\\" + "Arztbrief_Max_Mustermann.txt"
generated_output_text = evaluate_results.read_file(generated_output_file_name)

# extract summary
#summary_regex = "Zusammenfassung:([\w\W]+)(Empfehlungen|Wir empfehlen):"
#summary_match = re.search(summary_regex, generated_output_text)
#if summary_match is not None:
#    summary = summary_match.group(1)
#phrases, entities, pos_keywords = extract_phrases(summary)
#print("Extracted phrases for summary:", phrases)
#print("Extracted entities for summary:", entities)
#print("Extracted pos_keywords for summary:", pos_keywords)

# extract recommendation
recommendation_regex = "(Empfehlungen|Wir empfehlen):([\w\W]+)Medikamente:"
recommendation_match = re.search(recommendation_regex, generated_output_text)
if recommendation_match is not None:
    recommendation = recommendation_match.group(2)
print(recommendation)
phrases, entities, pos_keywords = extract_phrases(recommendation)
print("Extracted phrases for recommendation:", phrases)
print("Extracted entities for recommendation:", entities)
print("Extracted pos_keywords for recommendation:", pos_keywords)

# extract treatment
#treatment_regex = "Durchgeführte Behandlung:([\w\W]+)Zusammenfassung:"
#treatment_match = re.search(treatment_regex, generated_output_text)
#if treatment_match is not None:
#    treatment = treatment_match.group(1)
#phrases, entities, pos_keywords = extract_phrases(treatment)
#print("Extracted phrases for treatment:", phrases)
#print("Extracted entities for treatment:", entities)
#print("Extracted pos_keywords for treatment:", pos_keywords)

# extract medication
#medication_regex = "Medikamente:([\w\W]+)(Bitte|Bei|Die|Unser|diktiert)"
#medication_input_match = re.search(medication_regex, generated_output_text)
#if medication_input_match is not None:
#    medication = medication_input_match.group(1)
#phrases, entities, pos_keywords = extract_phrases(medication)
#print("Extracted phrases for medication:", phrases)
#print("Extracted entities for medication:", entities)
#print("Extracted pos_keywords for medication:", pos_keywords)



