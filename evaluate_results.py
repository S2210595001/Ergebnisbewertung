import nltk
import re
from readability import Readability


def read_files(dir_name, number_of_examples=3):
    # read input file
    input_file = open(dir_name + "\\" + dir_name + "-input.txt", "r", encoding="utf-8")
    input_text = input_file.read()
    input_file.close()

    # read original medical report
    original_output_file = open(dir_name + "\\" + dir_name + "-output.txt", "r", encoding="utf-8")
    original_output_text = original_output_file.read()
    original_output_file.close()

    # read generated medical report
    generated_output_file = open(dir_name + "\\" + "Arztbrief_Max_Mustermann_" + str(number_of_examples) + ".txt", "r",
                                 encoding="utf-8")
    generated_output_text = generated_output_file.read()
    generated_output_file.close()
    return input_text, original_output_text, generated_output_text


def extract_personal_data(filename):
    # extract personal data from profile
    profile_file = open(filename, "r", encoding="utf-8")
    personal_data_dict = {}

    # read lines of profile.txt file
    for line in profile_file.readlines():
        description, data = line.split(":")
        data = data.strip()

        # extract data and save in dict
        if description.startswith("Geschlecht"):
            personal_data_dict["gender"] = data
        elif description.startswith("Anrede"):
            personal_data_dict["title"] = data
        elif description.startswith("Name"):
            personal_data_dict["name"] = data
        elif description.startswith("Strasse"):
            personal_data_dict["address"] = data
        elif description.startswith("Postleitzahl"):
            personal_data_dict["city"] = data
        elif description.startswith("Geburtsdatum"):
            personal_data_dict["birth_date"] = data
        elif description.startswith("Sozialversicherungsnummer"):
            personal_data_dict["svnr"] = data
        elif description.startswith("Datum"):
            personal_data_dict["visit_date"] = data
    profile_file.close()
    return personal_data_dict


def evaluate_structure(output_text):
    # evaluate structure
    structure_dict = {"personal_data": 0, "hospital_data": 0, "introduction": 0, "diagnosis": 0, "treatment": 0,
                      "summary": 0, "recommendation": 0, "medication": 0, "ending": 0, "greetings": 0}

    # evaluate personal data
    personal_data_match = re.search("[\w\s.]+\s[\w\d/.\s]+\s+[\d]+\s[\w]+", output_text)
    if personal_data_match is not None:
        structure_dict["personal_data"] = 5

    # evaluate hospital data
    hospital_data_regex = "Wiener Gesundheitsverbund\s*Klinik Hietzing\s*[\wü\-\s]+\s*1130 Wien, Wolkersbergenstraße 1\s*Vorstand:[\w\s.]+\s*Tel.: [\d\/+]+\s*Fax: [\d\/+]+\s*KHI.AUF@gesundheitsverbund.at\s*https:\/\/klinik-hietzing.gesundheitsverbund.at\s*Ambulanter Patientenbrief\s*Wien, [\d.]+"
    hospital_data_match = re.search(hospital_data_regex, output_text)
    if hospital_data_match is not None:
        structure_dict["hospital_data"] = 5

    # evaluate introduction sentence
    introduction_sentence_regex = "Wir berichten über den ambulanten Besuch von [\w\s.]+, geb. am [\d.]+, SV-Nr. [\d-]+, [\w]+ am [\d.]+ an unserer Abteilung in Behandlung war."
    introduction_sentence_match = re.search(introduction_sentence_regex, output_text)
    if introduction_sentence_match is not None:
        structure_dict["introduction"] = 5

    # evaluate headings
    if "Diagnose" in output_text:
        structure_dict["diagnosis"] = 15
    if "Durchgeführte Behandlung" in output_text:
        structure_dict["treatment"] = 15
    if "Zusammenfassung" in output_text:
        structure_dict["summary"] = 15
    if "Wir empfehlen" in output_text or "Empfehlungen" in output_text:
        structure_dict["recommendation"] = 15
    if "Medikamente" in output_text:
        structure_dict["medication"] = 15

    # evaluate ending text
    ending_regex = "Bitte suchen Sie zum nächst möglichen Zeitpunkt Ihren Hausarzt auf.\s*Bei Verschlechterung " \
                   "jederzeitige Wiedervorstellung möglich.\s*Die bisherige unveränderte Dauermedikation wurde nicht extra " \
                   "aufgelistet.\s*Unser Therapievorschlag dient als Grundlage für Ihre Weiterbehandlung. Es liegt im " \
                   "Ermessen des weiterbehandelnden Arztes, wirkstoffgleiche Arzneimittel (Generika) zu verschreiben.\s*" \
                   "Befunde und Konsilien liegen in Kopie bei."
    ending_match = re.search(ending_regex, output_text)
    if ending_match is not None:
        structure_dict["ending"] = 5

    # evaluate greeting
    greeting_match = ("Mit freundlichen Grüßen\s*Der Abteilungsvorstand", output_text)
    if greeting_match is not None:
        structure_dict["greetings"] = 5
    return structure_dict


def evaluate_correctness():
    print("")


def print_results(result_dict, evaluation_type):
    # print results and calculate percentage
    result_string = ""
    for description in result_dict:
        result = "yes" if result_dict[description] != 0 else "no"
        result_string += description
        result_string += ": "
        result_string += result
        result_string += "\n"
    print(result_string)
    print("The generated report has a " + evaluation_type + " score of", sum(result_dict.values()), "%.")


def main():
    # read text from files
    # dir_name = "e91d3e5c-f642-4a1f-9e63-d68e3e10a37d"
    dir_name = "b87f9c99-fdd1-42ae-bb39-d84b7d7e8771"
    number_of_examples = 5
    input_text, original_output_text, generated_output_text = read_files(dir_name, number_of_examples)

    # extract personal data
    profile_filename = dir_name + "\\" + "profile.txt"
    personal_data_dict = extract_personal_data(profile_filename)

    # evaluate structure
    structure_dict = evaluate_structure(generated_output_text)
    # print_results(structure_dict, "structure")

    # evaluate correctness
    # correctness_dict = evaluate_correctness(structure_dict, input_text, generated_output_text)
    correctness_dict = {"personal_data": 0, "hospital_data": 0, "introduction": 0, "diagnosis": 0, "treatment": 0,
                        "summary": 0, "recommendation": 0, "medication": 0, "ending": 0, "greetings": 0}

    # correctness of personal data
    if structure_dict["personal_data"] != 0:  # no need to check for correctness if element is not there
        personal_data_regex = personal_data_dict["title"] + "\s*" + personal_data_dict["name"] + "\s*" + \
                              personal_data_dict["address"].replace("/", "\/") + "\s*" + personal_data_dict["city"]
        personal_data_match = re.search(personal_data_regex, generated_output_text)
        if personal_data_match is not None:
            correctness_dict["personal_data"] = 5
            # print("personal data is correct")

    # correctness of hospital data
    if structure_dict["hospital_data"] != 0:
        hospital_data_regex = "Wiener Gesundheitsverbund\s*Klinik Hietzing\s*[\wü\-\s]+\s*1130 Wien, Wolkersbergenstraße 1\s*Vorstand: [\w\s.]+\s*Tel.: \+43\/01\/80110\/2224\s*Fax: \+43/80110\/2678\s*KHI.AUF@gesundheitsverbund.at\s*https:\/\/klinik-hietzing.gesundheitsverbund.at\s*Ambulanter Patientenbrief\s*Wien, [\d.]+"
        hospital_data_match = re.search(hospital_data_regex, generated_output_text)
        if hospital_data_match is not None:
            correctness_dict["hospital_data"] = 5
            # print("hospital data is correct")

    # correctness of introduction
    if structure_dict["introduction"] != 0:
        pronoun = "die" if personal_data_dict["gender"] == "W" else "der"
        introduction_sentence = "Wir berichten über den ambulanten Besuch von " + personal_data_dict["title"] + " " + \
                                personal_data_dict["name"] + ", geb. am " + personal_data_dict["birth_date"] + \
                                ", SV-Nr. " + personal_data_dict["svnr"] + ", " + pronoun + " am " + \
                                personal_data_dict["visit_date"] + " an unserer Abteilung in Behandlung war."
        if introduction_sentence in generated_output_text:
            correctness_dict["introduction"] = 5

    # TODO: correctness of diagnosis
    # extract diagnosis
    diagnosis_regex = "Diagnose:([\w\W]+)Durchgeführte Behandlung:"
    diagnosis_match = re.search(diagnosis_regex, generated_output_text)
    if diagnosis_match is not None:
        diagnosis = diagnosis_match.group(1)
        # print(diagnosis)

    # TODO: correctness of treatment
    # extract treatment
    treatment_regex = "Durchgeführte Behandlung:([\w\W]+)Zusammenfassung:"
    treatment_match = re.search(treatment_regex, generated_output_text)
    if treatment_match is not None:
        treatment = treatment_match.group(1)
        # print(treatment)

    # TODO: correctness of summary
    # laborwerte überprüfen, überprüfen ob wirklich erhöht oder nicht
    # extract summary
    summary_regex = "Zusammenfassung:([\w\W]+)Empfehlungen:"
    summary_match = re.search(summary_regex, generated_output_text)
    if summary_match is not None:
        summary = summary_match.group(1)
        # correctness_dict["hospital_data"] = 5
        # print("hospital data is correct")

    # TODO: correctness of recommendation
    # extract recommendation
    recommendation_regex = "Empfehlungen:([\w\W]+)Medikamente:"
    recommendation_match = re.search(recommendation_regex, generated_output_text)
    if recommendation_match is not None:
        recommendation = recommendation_match.group(1)
        # print(recommendation)

    # TODO: correctness of medication
    #  alle aufgelisteten medikamente müssen im input vorkommen
    #  -> also alle medikamente identifizieren, mit dosierung
    #  ev. über hauptwörter? über regex? über zeile mit mg?
    #  "dauermedikation weiter wie bisher" auch möglich
    # extract medication
    medication_regex = "Medikamente:([\w\W]+)Bitte"
    medication_match = re.search(medication_regex, generated_output_text)
    if medication_match is not None:
        medication = medication_match.group(1)
        # print(medication)

    # ending and greetings are correct if they have the right structure
    if structure_dict["ending"] != 0:
        correctness_dict["ending"] = 5
    if structure_dict["greetings"] != 0:
        correctness_dict["greetings"] = 5
    # print_results(correctness_dict, "correctness")

    # TODO: understandability
    #  readability
    #  https://pypi.org/project/py-readability-metrics/
    # r = Readability(summary + " " + recommendation + " " + medication)

    # print(r.flesch_kincaid())
    # print(r.flesch())
    # r.gunning_fog()
    # r.coleman_liau()
    # r.dale_chall()
    # r.ari()
    # r.linsear_write()
    # r.smog()
    # r.spache()

    # TODO: test automated metrics
    #  score to compare text to original generated output
    #  maybe useful for diagnose, durchgeführte behandlung, zusammenfassung, empfehlungen, medikamente
    #  https://blog.paperspace.com/automated-metrics-for-evaluating-generated-text/

    # bleu_score = nltk.translate.bleu_score.sentence_bleu([input_text], output_text)
    # print(bleu_score)
    #
    # rouge score


if __name__ == '__main__':
    main()
