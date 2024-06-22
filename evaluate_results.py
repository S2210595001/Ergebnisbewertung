import re
import string
import spacy

# load german spacy model
nlp = spacy.load('de_core_news_sm')


def read_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        file_content = file.read()
    return file_content


def read_medication_file():
    # read list of medication names from file
    medication_list = []
    medication_file = open("medication_substance_list.txt", "r", encoding="utf-8")
    for medication_name in medication_file.readlines():
        medication_name = medication_name.strip()
        medication_list.append(medication_name)
    medication_file.close()
    return medication_list


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


def extract_medication_names_from_section(regex, text, medication_list_full):
    medication_names = []

    # search for medication names in text
    medication_input_match = re.search(regex, text)

    if medication_input_match is not None:
        medication = medication_input_match.group(1)

        # no changes in medication
        same_medication = False
        if "Dauermedikation" in medication:
            same_medication = True

        # split input
        medication_parts = medication.split("\n")
        for part in medication_parts:
            part.strip()
            potential_names = part.split(" ")

            # check all possible medication names
            for potential_medication in potential_names:
                potential_medication.strip()
                potential_medication = potential_medication.capitalize()

                # medication has to start with A-Z
                if potential_medication.startswith(tuple(string.ascii_uppercase)):
                    # check if potential medication is in list
                    if potential_medication.upper() in medication_list_full:
                        if medication_names != "" and potential_medication not in medication_names:
                            medication_names.append(potential_medication)
        if not medication_names and same_medication:      # medication stays the same
            return ["Dauermedikation"]
    return medication_names


def find_medication_names_in_input(input_text, medication_list):
    # search for medication in three sections of input
    medication_input_regex = "Weiteres Procedere:([\w\W]+)(TB für Kontrolle|Labor)"
    medication_names_input1 = extract_medication_names_from_section(medication_input_regex, input_text, medication_list)
    medication_input_regex = "Dekurs:([\w\W]+)Therapie"
    medication_names_input2 = extract_medication_names_from_section(medication_input_regex, input_text, medication_list)
    medication_input_regex = "Therapie:([\w\W]+)Kontrolle"
    medication_names_input3 = extract_medication_names_from_section(medication_input_regex, input_text, medication_list)
    return list(set(medication_names_input1 + medication_names_input2 + medication_names_input3))


def find_medication_names_in_output(generated_output_text, medication_list):
    # extract medication from generated_output
    medication_regex = "Medikamente:([\w\W]+)Bitte"
    return extract_medication_names_from_section(medication_regex, generated_output_text, medication_list)


def find_medication_names(input_text, generated_output_text, medication_list):
    medication_names_input = find_medication_names_in_input(input_text, medication_list)
    medication_names_output = find_medication_names_in_output(generated_output_text, medication_list)
    print(medication_names_input)
    print(medication_names_output)

    return medication_names_input, medication_names_output


def extract_diagnosis_from_section(section):
    # split result by lines, multiple results are possible
    diagnosis_list = section.split("\n")
    diagnosis_list_changed = []

    for element in diagnosis_list:
        element = re.sub("\.", "", element)
        element = re.sub("^\s*-+\s*", "", element)
        element = re.sub("^Va", "", element)
        element = re.sub("^Verdacht auf", "", element)
        element = re.sub("^\s*", "", element)

        if element not in ["", " "]:            # remove unwanted elements
            if " " in element:
                element_parts = element.split(" ")
                if "und" in element_parts:
                    element_parts.remove("und")
                for element_part in element_parts:
                    element_part = element_part.strip()
                    diagnosis_list_changed.append(element_part)
            else:
                diagnosis_list_changed.append(element)

    return diagnosis_list_changed


def find_diagnosis_section_in_input(input_text):
    # extract diagnosis from input
    diagnosis_input_regex = "Diagnose:([\w\W]+)Dekurs:"
    diagnosis_match = re.search(diagnosis_input_regex, input_text)

    if diagnosis_match is not None:
        diagnosis = diagnosis_match.group(1)
        return diagnosis
    return ""


def find_diagnosis_section_in_output(generated_output_text):
    # extract diagnosis from generated output
    diagnosis_regex = "Diagnose[\w\s]*:\s*\n([\w\W]*?)(Anamnese|Status|Durchgeführte Behandlung)"
    diagnosis_match = re.search(diagnosis_regex, generated_output_text)

    if diagnosis_match is not None:
        diagnosis = diagnosis_match.group(1)
        return diagnosis
    return ""


def find_diagnosis_sections(input_text, generated_output_text):
    diagnosis_section_input = find_diagnosis_section_in_input(input_text)
    diagnosis_input = extract_diagnosis_from_section(diagnosis_section_input)
    diagnosis_section_output = find_diagnosis_section_in_output(generated_output_text)
    diagnosis_output = extract_diagnosis_from_section(diagnosis_section_output)
    #print(diagnosis_input)
    #print(diagnosis_output)

    return diagnosis_input, diagnosis_output


def extract_section(regex, text):
    # extract section from text
    regex_match = re.search(regex, text)
    if regex_match is not None:
        return regex_match.group(2)
    return ""


def extract_pos_keywords(section):
    text = nlp(section)

    # extract specific POS tags
    pos_keywords = []
    lemmas = []
    for token in text:
        if token.pos_ in ["NOUN", "PROPN"]:
            keyword = token.text
            lemma = token.lemma_       # lemmatization
            keyword = re.sub("^\s*-", "", keyword)
            if len(keyword) > 1:
                pos_keywords.append(keyword)
                if len(lemma) > 2:
                    lemmas.append(lemma)
    return pos_keywords, lemmas


def find_recommendation_section_in_input(input_text):
    # search for medication in two sections of input
    recommendation_input_regex = "()Weiteres Procedere:([\w\W]+?)(TB für Kontrolle|Labor|$)"
    recommendations_input = extract_section(recommendation_input_regex, input_text)
    recommendations_input = recommendations_input.strip()

    if not recommendations_input:
        recommendation_input_regex = "()Dekurs:([\w\W]+?)Therapie:"
        recommendations_input = extract_section(recommendation_input_regex, input_text)

    return recommendations_input


def find_recommendation_section_in_output(generated_output_text):
    # extract recommendation from generated output
    recommendation_regex = "(Empfehlungen|Wir empfehlen|Weiteres Procedere|Empf):\s*\n*([\w\W]+?)\n\n"
    return extract_section(recommendation_regex, generated_output_text)


def find_recommendation_sections(input_text, generated_output_text):
    recommendation_input = find_recommendation_section_in_input(input_text)
    _, pos_keywords_input = extract_pos_keywords(recommendation_input)
    #print(pos_keywords_input)

    recommendation_output = find_recommendation_section_in_output(generated_output_text)
    _, pos_keywords_output = extract_pos_keywords(recommendation_output)
    #print(pos_keywords_output)

    return pos_keywords_input, pos_keywords_output


def find_summary_section_in_output(generated_output_text):
    summary_regex = "()Zusammenfassung[\w\s]*:\s*\n([\w\W]*?)(Empfehlungen|Wir empfehlen|Weiteres Procedere|Empf|Therapie):"
    summary_output = extract_section(summary_regex, generated_output_text)

    return summary_output


def find_summary_section_in_input(input_text):
    summary_regex_input = "(Anamnese:|An.:)([\w\W]+?)(Status|FK):"
    summary_input1 = extract_section(summary_regex_input, input_text)
    summary_regex_input = "()Status:([\w\W]+)Befund:"
    summary_input2 = extract_section(summary_regex_input, input_text)

    return summary_input1, summary_input2


def find_summary_sections(input_text, generated_output_text):
    summary_input1, summary_input2 = find_summary_section_in_input(input_text)
    _, pos_keywords_input1 = extract_pos_keywords(summary_input1)
    _, pos_keywords_input2 = extract_pos_keywords(summary_input2)
    pos_keywords_input = list(set(pos_keywords_input1 + pos_keywords_input2))
    #print(pos_keywords_input)

    summary_output = find_summary_section_in_output(generated_output_text)
    _, pos_keywords_output = extract_pos_keywords(summary_output)
    #print(pos_keywords_output)

    return pos_keywords_input, pos_keywords_output


def evaluate_structure(output_text):
    # evaluate structure
    structure_dict = {"Persönliche_Daten": 0, "Krankenhaus_Daten": 0, "Einleitung": 0, "Diagnose": 0, "Behandlung": 0,
                      "Zusammenfassung": 0, "Empfehlungen": 0, "Medikamente": 0, "Abschluss": 0, "Unterschrift": 0}

    # evaluate personal data
    #personal_data_match = re.search("\n[A-Za-z.]+\s*\n{1,2}[\w\s]+\s*\n{1,2}[A-Za-z/.ß\s]+\s[\d\/A-Z]+\s*\n{1,2}[\d]+\s[\w]+\n", output_text)
    personal_data_match = re.search("\n[A-Za-z.]+\s*\n{1,2}[\w\s]+\s*\n{1,2}[A-Za-z/.ß\s\d\/A-Z]+\s*\n{1,2}[\d]+\s[\w]+\n", output_text)
    if personal_data_match is not None:
        structure_dict["Persönliche_Daten"] = 10

    # evaluate hospital data
    hospital_data_regex = "Wiener Gesundheitsverbund\s*Klinik Hietzing\s*[\wü\-\s]+\s*1130 Wien, Wolkersbergenstraße 1\s*Vorstand:[\w\s.\[\]]+\s*Tel.: [\d\/+]+\s*Fax: [\d\/+]+\s*KHI.[\w]+@gesundheitsverbund.at\s*https:\/\/klinik-hietzing.gesundheitsverbund.at\s+[-]*\s*"
    hospital_data_match = re.search(hospital_data_regex, output_text)
    if hospital_data_match is not None:
        structure_dict["Krankenhaus_Daten"] = 10

    # evaluate introduction sentence
    introduction_sentence_regex = "Wir berichten über den ambulanten Besuch von [\w\s.]+, geb. am [\d.]+, SV-Nr. [\d-]+, [\w]+ am [\d.]+ an unserer Abteilung in Behandlung war."
    introduction_sentence_match = re.search(introduction_sentence_regex, output_text)
    if introduction_sentence_match is not None:
        structure_dict["Einleitung"] = 10

    # evaluate headings
    if "Diagnose:" in output_text:
        structure_dict["Diagnose"] = 10
    if "Durchgeführte Behandlung:" in output_text:
        structure_dict["Behandlung"] = 10
    if "Zusammenfassung:" in output_text:
        structure_dict["Zusammenfassung"] = 10
    if "Wir empfehlen:" in output_text or "Empfehlungen:" in output_text or "Weiteres Procedere:" in output_text:
        structure_dict["Empfehlungen"] = 10
    if "Medikamente:" in output_text:
        structure_dict["Medikamente"] = 10

    # some header should not be there
    if "Status:" in output_text:
        structure_dict["Status"] = -10
    if "Befund:" in output_text:
        structure_dict["Befund"] = -10
    if "Labor:" in output_text:
        structure_dict["Labor"] = -10
    if "Therapie:" in output_text:
        structure_dict["Therapie"] = -10
    if "Kontrolle:" in output_text:
        structure_dict["Kontrolle"] = -10
    if "Pflege:" in output_text:
        structure_dict["Pflege"] = -10
    if "Laborchemische Befunde:" in output_text:
        structure_dict["Laborchemische Befunde"] = -10
    if "Laborergebnisse:" in output_text:
        structure_dict["Laborergebnisse"] = -10

    # evaluate ending sentences
    ending_sentences = ["Bei Verschlechterung jederzeitige Wiedervorstellung möglich.",
                        "Die bisherige unveränderte Dauermedikation wurde nicht extra aufgelistet.",
                        "Unser Therapievorschlag dient als Grundlage für Ihre Weiterbehandlung.",
                        "Es liegt im Ermessen des weiterbehandelnden Arztes, wirkstoffgleiche Arzneimittel \((z.B. )*Generika\) zu verschreiben.",
                        "Befunde und Konsilien liegen in Kopie bei.",
                        "Bitte suchen Sie zum (nächst möglichen|nächstmöglichen) Zeitpunkt Ihren Hausarzt auf."]
    # combine sentences, create pattern and find match
    regex_combined = "(?=.*" + ")(?=.*".join(ending_sentences) + ")"
    pattern = re.compile(regex_combined, re.DOTALL)
    match = pattern.search(output_text)
    if match:
        structure_dict["Abschluss"] = 10

    # evaluate greeting
    greeting_match = ("Mit freundlichen Grüßen\s*Der Abteilungsvorstand", output_text)
    if greeting_match is not None:
        structure_dict["Unterschrift"] = 10
    return structure_dict


def evaluate_correctness(structure_dict, personal_data_dict, medication_list, input_text, generated_output_text):
    # evaluate correctness (check that information in the generated output can be found in the input)
    correctness_dict = {"Persönliche_Daten": 0, "Krankenhaus_Daten": 0, "Einleitung": 0, "Diagnose_korrekt": 0,
                        "Diagnose_vollständig": 0, "Zusammenfassung": 0, "Empfehlungen_vollständig": 0, "Medikamente_korrekt": 0,
                        "Medikamente_vollständig": 0, "Abschluss": 0}

    # correctness of personal data
    if structure_dict["Persönliche_Daten"] != 0 and personal_data_dict["address"]:  # no need to check for correctness if element is not there
        personal_data_regex = personal_data_dict["title"] + "\s*" + personal_data_dict["name"] + "\s*" + \
                              personal_data_dict["address"].replace("/", "\/") + "\s*" + personal_data_dict["city"]
        personal_data_match = re.search(personal_data_regex, generated_output_text)
        if personal_data_match is not None:
            correctness_dict["Persönliche_Daten"] = 10

    # correctness of hospital data
    if structure_dict["Krankenhaus_Daten"] != 0:
        hospital_data_regex = "Wiener Gesundheitsverbund\s*Klinik Hietzing\s*[\wü\-\s]+\s*1130 Wien, Wolkersbergenstraße 1\s*Vorstand: [\w\s.]+\s*Tel.: \+43\/01\/80110\/2224\s*Fax: \+43/80110\/2678\s*KHI.[\w]+@gesundheitsverbund.at\s*https:\/\/klinik-hietzing.gesundheitsverbund.at\s*"
        hospital_data_match = re.search(hospital_data_regex, generated_output_text)
        if hospital_data_match is not None:
            correctness_dict["Krankenhaus_Daten"] = 10

    # correctness of introduction
    if structure_dict["Einleitung"] != 0:
        pronoun = "die" if personal_data_dict["gender"] == "W" else "der"
        introduction_sentence = "Wir berichten über den ambulanten Besuch von " + personal_data_dict["title"] + " " + \
                                personal_data_dict["name"] + ", geb. am " + personal_data_dict["birth_date"] + \
                                ", SV-Nr. " + personal_data_dict["svnr"] + ", " + pronoun + " am " + \
                                personal_data_dict["visit_date"] + " an unserer Abteilung in Behandlung war."
        if introduction_sentence in generated_output_text:
            correctness_dict["Einleitung"] = 10

    # check for diagnosis if it can be found in the input
    diagnosis_input, diagnosis_output = find_diagnosis_sections(input_text, generated_output_text)
    diagnosis_input_lower = [word.lower() for word in diagnosis_input]          # case of the words should not matter
    diagnosis_output_lower = [word.lower() for word in diagnosis_output]
    correct_diagnosis = True
    for diagnosis in diagnosis_output_lower:
        if diagnosis not in diagnosis_input_lower:
            correct_diagnosis = False
    if correct_diagnosis:
        correctness_dict["Diagnose_korrekt"] = 10

    # check for diagnosis in input if it can be found in the output
    missing_diagnosis = False
    for diagnosis in diagnosis_input_lower:
        if diagnosis not in diagnosis_output_lower:
            missing_diagnosis = True
    if not missing_diagnosis:
        correctness_dict["Diagnose_vollständig"] = 10

    # check correctness of summary
    summary_input, summary_output = find_summary_sections(input_text, generated_output_text)
    # check that a certain percentage of keywords can be found in input
    percentage_threshold = 0.45
    correct_words = 0
    for recommendation_output in summary_output:
        if recommendation_output in summary_input:
            correct_words = correct_words + 1
    if summary_output:
        correct_percentage = correct_words / len(summary_output)
        print("Summary Score:", correct_percentage)
        if correct_percentage >= percentage_threshold:
            correctness_dict["Zusammenfassung"] = 10

    # check correctness of recommendations
    recommendations_input, recommendations_output = find_recommendation_sections(input_text, generated_output_text)
    # check that a certain percentage of keywords can be found in input
    percentage_threshold = 0.6
    correct_words = 0
    # check that recommendations are complete
    for recommendation_input in recommendations_input:
        if recommendation_input in recommendations_output:
            correct_words = correct_words+1
    if recommendations_input:
        correct_percentage = correct_words/len(recommendations_input)
        print("Recommendation Score:", correct_percentage)
        if correct_percentage >= percentage_threshold:
            correctness_dict["Empfehlungen_vollständig"] = 10

    # check correctness of medication
    medication_names_input, medication_names_output = find_medication_names(input_text, generated_output_text, medication_list)
    # check for generated medication names if they can be found in the input
    correct_medication = True
    for medication_name_output in medication_names_output:
        if medication_name_output not in medication_names_input:
            correct_medication = False
    if not medication_names_input and "Dauermedikation" in medication_names_output:  # no changes in medication
        correct_medication = True
    elif medication_names_input and not medication_names_output:
        correct_medication = False
    if correct_medication:
        correctness_dict["Medikamente_korrekt"] = 10

    # check for medication name in input if it can be found in the output
    missing_medication = False
    for medication in medication_names_input:
        if medication not in medication_names_output:
            missing_medication = True
    if medication_names_input and not missing_medication:
        correctness_dict["Medikamente_vollständig"] = 10

    # ending is correct if it has the right structure
    if structure_dict["Abschluss"] != 0:
        correctness_dict["Abschluss"] = 10

    return correctness_dict


def print_results(result_dict, evaluation_type, show_output=True):
    # print results and calculate percentage
    result_string = ""
    for description in result_dict:
        if result_dict[description] > 0:
            result = "yes"
        else:
            result = "no"
        result_string += description
        result_string += ": "
        result_string += result
        result_string += "\n"
    score = sum(result_dict.values())
    if show_output:
        print(result_string)
        print("The generated report has a " + evaluation_type + " score of", score, "%.")
        print()
    return score


def main():
    # read text from files
    #dir_name = "C:\\Users\\magda\\Documents\\Studium\\DSE\\MA\\Synthetische Daten"
    #file_number = "5-9"            # 5-1 to 5-15

    dir_name = "C:\\Users\\magda\\Documents\\Studium\\DSE\\MA\\Praxis\\Experimente"
    file_number = "6"

    # read input file
    #input_file_name = dir_name + "\\" + file_number + "\\" + file_number + "-input.txt"
    input_file_name = dir_name + "\\" + file_number + "\\" + "input.txt"
    input_text = read_file(input_file_name)

    # read generated medical report
    #generated_output_file_name = dir_name + "\\" + file_number + "\\" + file_number + "-output.txt"
    generated_output_file_name = dir_name + "\\" + file_number + "\\" + "output.txt"
    generated_output_text = read_file(generated_output_file_name)

    # extract personal data
    #profile_file_name = dir_name + "\\" + file_number + "\\" + file_number + "-profile.txt"
    profile_file_name = dir_name + "\\" + file_number + "\\" + "profile.txt"
    personal_data_dict = extract_personal_data(profile_file_name)

    # read list of medication names from file
    medication_list = read_medication_file()


    # evaluate structure
    structure_dict = evaluate_structure(generated_output_text)
    print_results(structure_dict, "structure")

    # evaluate correctness
    correctness_dict = evaluate_correctness(structure_dict, personal_data_dict, medication_list, input_text, generated_output_text)
    print_results(correctness_dict, "correctness")


if __name__ == '__main__':
    main()
