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
        no_changes = "Dauermedikation"
        if no_changes in medication:
            return [no_changes]

        # split input
        medication_parts = medication.split("\n")
        for part in medication_parts:
            part.strip()
            potential_names = part.split(" ")
            # print(potential_names)

            # check all possible medication names
            for potential_medication in potential_names:
                potential_medication.strip()
                # potential_medication = potential_medication.upper()

                # medication has to start with A-Z
                if potential_medication.upper().startswith(tuple(string.ascii_uppercase)):
                    # check if potential medication is in list
                    if potential_medication.upper() in medication_list_full:
                        if medication_names != "" and potential_medication not in medication_names:
                            medication_names.append(potential_medication)
                            # print(potential_medication)
    return medication_names


def find_medication_names_in_input(input_text, medication_list):
    # search for medication in two sections of input
    medication_input_regex = "Weiteres Procedere:([\w\W]+)TB für Kontrolle"
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
        element = re.sub("^\s*-", "", element)
        element = re.sub("^\s*", "", element)
        if element not in ['', ' ']:            # remove unwanted elements
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
    #diagnosis_regex = "Diagnose:[-\s]+([\w\W]+)Durchgeführte Behandlung:"
    #diagnosis_regex = "Diagnose[\w\s]*:\n([\w\W]*?)\n+[\w\W]*:\n"
    diagnosis_regex = "Diagnose[\w\s]*:\s*\n([\w\W]*?)(Anamnese|Status|Durchgeführte Behandlung)"
    diagnosis_match = re.search(diagnosis_regex, generated_output_text)

    if diagnosis_match is not None:
        diagnosis = diagnosis_match.group(1)
        #print(diagnosis)
        return diagnosis
    return ""


def find_diagnosis_sections(input_text, generated_output_text):
    diagnosis_section_input = find_diagnosis_section_in_input(input_text)
    diagnosis_input = extract_diagnosis_from_section(diagnosis_section_input)

    diagnosis_section_output = find_diagnosis_section_in_output(generated_output_text)
    diagnosis_output = extract_diagnosis_from_section(diagnosis_section_output)

    return diagnosis_input, diagnosis_output


def extract_section(regex, text):
    regex_match = re.search(regex, text)
    #pos_keywords = []
    if regex_match is not None:
        section = regex_match.group(2)
        #print(recommendation)

        # extract pos keywords from recommendation
        #pos_keywords = extract_pos_keywords(recommendation)
        #print(pos_keywords)
    #return pos_keywords
        return section
    return ""


def extract_pos_keywords(section):
    text = nlp(section)

    # extract specific POS tags
    pos_keywords = []
    for token in text:
        if token.pos_ in ['NOUN', 'PROPN', 'VERB']:
            keyword = token.text
            keyword = re.sub("^\s*-", "", keyword)
            if len(keyword) > 1:
                pos_keywords.append(keyword)
    return pos_keywords


def find_recommendation_section_in_input(input_text):
    # search for medication in two sections of input
    recommendation_input_regex = "()Weiteres Procedere:([\w\W]+?)(TB für Kontrolle|Labor)"
    recommendations_input1 = extract_section(recommendation_input_regex, input_text)

    recommendation_input_regex = "()Empf([\w\W]+)Therapie"
    recommendations_input2 = extract_section(recommendation_input_regex, input_text)
    #return list(set(recommendations_input1 + recommendations_input2))
    return recommendations_input1, recommendations_input2


def find_recommendation_section_in_output(generated_output_text):
    # extract recommendation from generated output
    #recommendation_regex = "(Empfehlungen|Wir empfehlen|Weiteres Procedere|Empf):([\w\W]+)Medikamente:"
    recommendation_regex = "(Empfehlungen|Wir empfehlen|Weiteres Procedere|Empf):\s*\n*([\w\W]+?)\n\n"
    return extract_section(recommendation_regex, generated_output_text)


def find_recommendation_sections(input_text, generated_output_text):
    recommendation_input1, recommendation_input2 = find_recommendation_section_in_input(input_text)
    pos_keywords_input1 = extract_pos_keywords(recommendation_input1)
    pos_keywords_input2 = extract_pos_keywords(recommendation_input2)
    pos_keywords_input = list(set(pos_keywords_input1 + pos_keywords_input2))
    #print(pos_keywords_input)

    recommendation_output = find_recommendation_section_in_output(generated_output_text)
    pos_keywords_output = extract_pos_keywords(recommendation_output)
    #print(pos_keywords_output)

    return pos_keywords_input, pos_keywords_output


def find_summary_section_in_output(generated_output_text):
    # regex: endet mit nächster überschrift und doppelpunkt mit absatz
    # Früher: ()Zusammenfassung:([\w\W]+?)(Empfehlungen|Wir empfehlen|Weiteres Procedere|Empf|Therapie):
    # 1: Zusammenfassung[\w\s:]*\n([\w\sÄÜOäüö,.]*)\n\n
    #summary_regex = "()Zusammenfassung[\w\s]*:\n([\w\W]*?)\n+[\w\W]*:\n"
    summary_regex = "()Zusammenfassung[\w\s]*:\s*\n([\w\W]*?)(Empfehlungen|Wir empfehlen|Weiteres Procedere|Empf|Therapie)"
    summary_output = extract_section(summary_regex, generated_output_text)
    #print(summary_output)
    return summary_output


def find_summary_section_in_input(input_text):
    # TODO: identify right sections
    summary_regex_input = "()Anamnese:([\w\W]+?)(Status|FK):"
    summary_input1 = extract_section(summary_regex_input, input_text)
    summary_regex_input = "()Status:([\w\W]+)Befund:"
    summary_input2 = extract_section(summary_regex_input, input_text)
    #return list(set(summary_input1 + summary_input2))
    return summary_input1, summary_input2


def find_summary_sections(input_text, generated_output_text):
    summary_input1, summary_input2 = find_summary_section_in_input(input_text)
    pos_keywords_input1 = extract_pos_keywords(summary_input1)
    pos_keywords_input2 = extract_pos_keywords(summary_input2)
    pos_keywords_input = list(set(pos_keywords_input1 + pos_keywords_input2))

    summary_output = find_summary_section_in_output(generated_output_text)
    pos_keywords_output = extract_pos_keywords(summary_output)

    return pos_keywords_input, pos_keywords_output


def evaluate_structure(output_text):
    # evaluate structure
    structure_dict = {"Persönliche_Daten": 0, "Krankenhaus_Daten": 0, "Einleitung": 0, "Diagnose": 0, "Behandlung": 0,
                      "Zusammenfassung": 0, "Empfehlungen": 0, "Medikamente": 0, "Abschluss": 0, "Unterschrift": 0}

    # evaluate personal data
    personal_data_match = re.search("[\w\s.]+\s[\w\d/.\s]+\s+[\d]+\s[\w]+", output_text)
    if personal_data_match is not None:
        structure_dict["Persönliche_Daten"] = 5

    # evaluate hospital data
    hospital_data_regex = "Wiener Gesundheitsverbund\s*Klinik Hietzing\s*[\wü\-\s]+\s*1130 Wien, Wolkersbergenstraße 1\s*Vorstand:[\w\s.\[\]]+\s*Tel.: [\d\/+]+\s*Fax: [\d\/+]+\s*KHI.AUF@gesundheitsverbund.at\s*https:\/\/klinik-hietzing.gesundheitsverbund.at\s+[-]*\s*Ambulanter Patientenbrief\s*Wien, [\d.]+"
    hospital_data_match = re.search(hospital_data_regex, output_text)
    if hospital_data_match is not None:
        structure_dict["Krankenhaus_Daten"] = 5
    # evaluate introduction sentence
    introduction_sentence_regex = "Wir berichten über den ambulanten Besuch von [\w\s.]+, geb. am [\d.]+, SV-Nr. [\d-]+, [\w]+ am [\d.]+ an unserer Abteilung in Behandlung war."
    introduction_sentence_match = re.search(introduction_sentence_regex, output_text)
    if introduction_sentence_match is not None:
        structure_dict["Einleitung"] = 5

    # evaluate headings
    if "Diagnose" in output_text:
        structure_dict["Diagnose"] = 15
    if "Durchgeführte Behandlung" in output_text:
        structure_dict["Behandlung"] = 15
    if "Zusammenfassung" in output_text:
        structure_dict["Zusammenfassung"] = 15
    if "Wir empfehlen" in output_text or "Empfehlungen" in output_text:
        structure_dict["Empfehlungen"] = 15
    if "Medikamente" in output_text:
        structure_dict["Medikamente"] = 15

    # evaluate ending text
    ending_regex = "Bitte suchen Sie zum (nächst möglichen|nächstmöglichen) Zeitpunkt Ihren Hausarzt auf.\s*Bei Verschlechterung " \
                   "jederzeitige Wiedervorstellung möglich.\s*Die bisherige unveränderte Dauermedikation wurde nicht extra " \
                   "aufgelistet.\s*Unser Therapievorschlag dient als Grundlage für Ihre Weiterbehandlung. Es liegt im " \
                   "Ermessen des weiterbehandelnden Arztes, wirkstoffgleiche Arzneimittel \(Generika\) zu verschreiben.\s*" \
                   "Befunde und Konsilien liegen in Kopie bei."
    ending_match = re.search(ending_regex, output_text)
    if ending_match is not None:
        structure_dict["Abschluss"] = 5

    # evaluate greeting
    greeting_match = ("Mit freundlichen Grüßen\s*Der Abteilungsvorstand", output_text)
    if greeting_match is not None:
        structure_dict["Unterschrift"] = 5
    return structure_dict


def evaluate_correctness(structure_dict, personal_data_dict, medication_list, input_text, generated_output_text):
    # evaluate correctness (check that information in the generated output can be found in the input)
    # correctness_dict = evaluate_correctness(structure_dict, input_text, generated_output_text)
    #correctness_dict = {"personal_data": 0, "hospital_data": 0, "introduction": 0, "diagnosis": 0,
    #                    "diagnosis_complete": 0, "summary": 0, "recommendation": 0, "recommendations_complete": 0,
    #                    "medication": 0, "medication_complete": 0, "ending": 0}
    correctness_dict = {"Persönliche_Daten": 0, "Krankenhaus_Daten": 0, "Einleitung": 0, "Diagnose_korrekt": 0,
                        "Diagnose_vollständig": 0, "Zusammenfassung": 0, "Empfehlungen_vollständig": 0, "Medikamente_korrekt": 0,
                        "Medikamente_vollständig": 0, "Abschluss": 0}

    # correctness of personal data
    if structure_dict["Persönliche_Daten"] != 0:  # no need to check for correctness if element is not there
        personal_data_regex = personal_data_dict["title"] + "\s*" + personal_data_dict["name"] + "\s*" + \
                              personal_data_dict["address"].replace("/", "\/") + "\s*" + personal_data_dict["city"]
        personal_data_match = re.search(personal_data_regex, generated_output_text)
        if personal_data_match is not None:
            correctness_dict["Persönliche_Daten"] = 5
            # print("personal data is correct")

    # correctness of hospital data
    if structure_dict["Krankenhaus_Daten"] != 0:
        hospital_data_regex = "Wiener Gesundheitsverbund\s*Klinik Hietzing\s*[\wü\-\s]+\s*1130 Wien, Wolkersbergenstraße 1\s*Vorstand: [\w\s.]+\s*Tel.: \+43\/01\/80110\/2224\s*Fax: \+43/80110\/2678\s*KHI.AUF@gesundheitsverbund.at\s*https:\/\/klinik-hietzing.gesundheitsverbund.at\s*Ambulanter Patientenbrief\s*Wien, [\d.]+"
        hospital_data_match = re.search(hospital_data_regex, generated_output_text)
        if hospital_data_match is not None:
            correctness_dict["Krankenhaus_Daten"] = 5
            # print("hospital data is correct")

    # correctness of introduction
    if structure_dict["Einleitung"] != 0:
        pronoun = "die" if personal_data_dict["gender"] == "W" else "der"
        introduction_sentence = "Wir berichten über den ambulanten Besuch von " + personal_data_dict["title"] + " " + \
                                personal_data_dict["name"] + ", geb. am " + personal_data_dict["birth_date"] + \
                                ", SV-Nr. " + personal_data_dict["svnr"] + ", " + pronoun + " am " + \
                                personal_data_dict["visit_date"] + " an unserer Abteilung in Behandlung war."
        if introduction_sentence in generated_output_text:
            correctness_dict["Einleitung"] = 5


    # check for diagnosis if it can be found in the input
    diagnosis_input, diagnosis_output = find_diagnosis_sections(input_text, generated_output_text)
    correct_diagnosis = True
    for diagnosis in diagnosis_output:
        if diagnosis not in diagnosis_input:
            correct_diagnosis = False
    if correct_diagnosis:
        correctness_dict["Diagnose_korrekt"] = 15

    # check for diagnosis in input if it can be found in the output
    missing_diagnosis = False
    for diagnosis in diagnosis_input:
        if diagnosis not in diagnosis_output:
            missing_diagnosis = True
    if not missing_diagnosis:
        correctness_dict["Diagnose_vollständig"] = 10


    # check correctness of summary
    summary_input, summary_output = find_summary_sections(input_text, generated_output_text)
    # check that a certain percentage of keywords can be found in input
    # TODO: find optimal threshold -> 0.2 or 0.25 would work, or find better method
    percentage_threshold = 0.2
    correct_words = 0
    for recommendation_output in summary_output:
        if recommendation_output in summary_input:
            correct_words = correct_words + 1
    correct_percentage = correct_words / len(summary_output)
    if correct_percentage >= percentage_threshold:
        correctness_dict["Zusammenfassung"] = 15
    #print(correct_words)
    #print(len(summary_output))
    #print(correct_percentage)


    # check correctness of recommendations
    recommendations_input, recommendations_output = find_recommendation_sections(input_text, generated_output_text)
    # check that a certain percentage of keywords can be found in input
    percentage_threshold = 0.6
    correct_words = 0
    #for recommendation_output in recommendations_output:
    #    if recommendation_output in recommendations_input:
    #        correct_words = correct_words+1
    #correct_percentage = correct_words/len(recommendations_output)
    #if correct_percentage > percentage_threshold:
    #    correctness_dict["Empfehlungen"] = 15

    for recommendation_input in recommendations_input:
        if recommendation_input in recommendations_output:
            correct_words = correct_words+1
    correct_percentage = correct_words/len(recommendations_input)
    if correct_percentage >= percentage_threshold:
        correctness_dict["Empfehlungen"] = 15
    #print(correct_percentage)


    # check correctness of medication
    medication_names_input, medication_names_output = find_medication_names(input_text, generated_output_text, medication_list)
    # check for generated medication names if they can be found in the input
    correct_medication = True
    for medication_name_output in medication_names_output:
        if medication_name_output not in medication_names_input:
            correct_medication = False
    if not medication_names_input and "Dauermedikation" in medication_names_output:  # no changes in medication
        correct_medication = True
    if correct_medication:
        correctness_dict["Medikamente_korrekt"] = 15

    # check for medication name in input if it can be found in the output
    missing_medication = False
    for medication in medication_names_input:
        if medication not in medication_names_output:
            missing_medication = True
    if not missing_medication:
        correctness_dict["Medikamente_vollständig"] = 10


    # ending and greetings are correct if they have the right structure
    if structure_dict["Abschluss"] != 0:
        correctness_dict["Abschluss"] = 5

    return correctness_dict


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
    print()


## directory names:
# 4345e4f5-99c1-4445-9ee3-ee93a7f06838
# 8553e774-4b58-4e8b-b2a5-af7bd01d678c
# 9582eb56-5413-4442-98f7-dcf307c6e1dc
# 32898a7b-b5c1-4236-8cf7-e395e865295d
# 575715a5-5fbb-4bd3-bb0d-872b2358e712
# b87f9c99-fdd1-42ae-bb39-d84b7d7e8771
# 01c03085-7087-4ebd-8e48-ef902741b3ea
## 3aa04e8d-26da-4e35-ab27-37c7659cefd6

# C:\Users\magda\Documents\Studium\DSE\MA\Experimente\Experiment 13\5-1
# 5-1, 5-2, 5-3

def main():
    # read text from files
    #dir_name = "01c03085-7087-4ebd-8e48-ef902741b3ea"
    dir_name = "C:\\Users\\magda\\Documents\\Studium\\DSE\\MA\\Experimente\\Experiment 13"
    file_number = "5-1"

    # read input file
    #input_file_name = dir_name + "\\" + dir_name + "-input.txt"
    input_file_name = dir_name + "\\" + file_number + "\\" + file_number + "-input.txt"
    input_text = read_file(input_file_name)

    # read original medical report
    #output_file_name = dir_name + "\\" + dir_name + "-output.txt"
    #original_output_text = read_file(output_file_name)

    # read generated medical report
    number_of_examples = 5
    #generated_output_file_name = dir_name + "\\" + "Arztbrief_Max_Mustermann_" + str(number_of_examples) + ".txt"
    #generated_output_file_name = dir_name + "\\" + "Arztbrief_Max_Mustermann.txt"
    generated_output_file_name = dir_name + "\\" + file_number + "\\" + file_number + "-output.txt"
    generated_output_text = read_file(generated_output_file_name)

    # extract personal data
    #profile_file_name = dir_name + "\\" + dir_name + "-profile.txt"
    profile_file_name = dir_name + "\\" + file_number + "\\" + file_number + "-profile.txt"
    personal_data_dict = extract_personal_data(profile_file_name)

    # read list of medication names from file
    medication_list = read_medication_file()

    # --------------------------------------------------------------------------------------------------------
    # evaluate structure
    structure_dict = evaluate_structure(generated_output_text)
    print_results(structure_dict, "structure")

    # evaluate correctness
    correctness_dict = evaluate_correctness(structure_dict, personal_data_dict, medication_list, input_text, generated_output_text)
    print_results(correctness_dict, "correctness")


if __name__ == '__main__':
    main()
