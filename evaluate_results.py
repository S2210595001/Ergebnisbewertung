import re
import bisect
import string


def read_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        file_content = file.read()
    return file_content


def binary_search(sorted_list, word):
    # search for word in a sorted list
    index = bisect.bisect_left(sorted_list, word)
    if index < len(sorted_list) and sorted_list[index] == word:
        return index
    else:
        return -1


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


def read_medication_file():
    # read list of medication names from file
    medication_list = []
    medication_file = open("medication_list_copy.txt", "r", encoding="utf-8")
    for medication_name in medication_file.readlines():
        medication_name = medication_name.strip()
        medication_list.append(medication_name)
    medication_file.close()
    return medication_list


def extract_medication_names(regex, text, medication_list_full):
    medication_names = []

    # search for medication names in text
    medication_input_match = re.search(regex, text)

    if medication_input_match is not None:
        medication = medication_input_match.group(1)
        # TODO: error in case it is not found (no match)

        # split input
        medication_parts = medication.split("\n")
        for part in medication_parts:
            part.strip()
            potential_names = part.split(" ")

            # check all possible medication names
            for potential_medication in potential_names:
                potential_medication.strip()
                potential_medication = potential_medication.upper()

                # medication has to start with A-Z
                if potential_medication.startswith(tuple(string.ascii_uppercase)):

                    # search in list of all medication names
                    if binary_search(medication_list_full, potential_medication) > -1:
                        if medication_names != "" and potential_medication not in medication_names:
                            medication_names.append(potential_medication)
    return medication_names


def extract_diagnosis(regex, text):
    diagnosis_match = re.search(regex, text)

    diagnosis_list = []
    if diagnosis_match is not None:
        diagnoses = diagnosis_match.group(1)
        diagnosis_list = diagnoses.split("\n")  # split result by lines, multiple diagnoses are possible
        element_to_remove = ''
        while element_to_remove in diagnosis_list:
            diagnosis_list.remove(element_to_remove)
        element_to_remove = ' '
        while element_to_remove in diagnosis_list:
            diagnosis_list.remove(element_to_remove)

    return diagnosis_list


# TODO: def extract_summary(), def extract_recommendations(), def extract_treatment


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

    # read input file
    input_file_name = dir_name + "\\" + dir_name + "-input.txt"
    input_text = read_file(input_file_name)

    # read original medical report
    output_file_name = dir_name + "\\" + dir_name + "-output.txt"
    original_output_text = read_file(output_file_name)

    # read generated medical report
    number_of_examples = 5
    generated_output_file_name = dir_name + "\\" + "Arztbrief_Max_Mustermann_" + str(number_of_examples) + ".txt"
    generated_output_text = read_file(generated_output_file_name)

    # extract personal data
    profile_file_name = dir_name + "\\" + "profile.txt"
    personal_data_dict = extract_personal_data(profile_file_name)

    # read list of medication names from file
    medication_list = read_medication_file()


    # evaluate structure
    structure_dict = evaluate_structure(generated_output_text)
    #print_results(structure_dict, "structure")


    # evaluate correctness (check that information in the generated output can be found in the input)
    # correctness_dict = evaluate_correctness(structure_dict, input_text, generated_output_text)
    correctness_dict = {"personal_data": 0, "hospital_data": 0, "introduction": 0, "diagnosis": 0, "treatment": 0,
                        "summary": 0, "recommendation": 0, "medication": 0, "ending": 0, "greetings": 0}
    # print_results(correctness_dict, "correctness")

    # evaluate missing information (information that is in the input but not the generated output)
    # correctness_dict = evaluate_missingness(structure_dict, input_text, generated_output_text)
    # missingness_dict = {"personal_data": 0, "hospital_data": 0, "introduction": 0, "diagnosis": 0, "treatment": 0,
    #                    "summary": 0, "recommendation": 0, "medication": 0, "ending": 0, "greetings": 0}
    # print_results(missingness_dict, "missingness")



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
    # extract diagnosis from generated output
    diagnosis_regex = "Diagnose:([\w\W]+)Durchgeführte Behandlung:"
    diagnosis_output = extract_diagnosis(diagnosis_regex, generated_output_text)
    #print(diagnosis_output)

    # extract diagnosis from input
    diagnosis_input_regex = "Diagnose:([\w\W]+)Dekurs:"
    diagnosis_input = extract_diagnosis(diagnosis_input_regex, input_text)

    #print(diagnosis_input)
    # TODO: add to dict

    # TODO: correctness of treatment
    # extract treatment
    treatment_regex = "Durchgeführte Behandlung:([\w\W]+)Zusammenfassung:"
    treatment_match = re.search(treatment_regex, generated_output_text)
    if treatment_match is not None:
        treatment = treatment_match.group(1)
        #print(treatment)

    treatment_regex_input = "Erhobene Befunde:([\w\W]+)Anamnese:"
    treatment_match = re.search(treatment_regex_input, input_text)
    if treatment_match is not None:
        treatment = treatment_match.group(1)
        #print(treatment)
        treatment_parts = treatment.split("\n")
        print(treatment_parts)
        #for part in treatment_parts:
            #part.strip()
            #treatment_lines = part.split(" ")
            #print(treatment_lines)



    # TODO: correctness of summary
    # laborwerte überprüfen, überprüfen ob wirklich erhöht oder nicht
    # extract summary
    summary_regex = "Zusammenfassung:([\w\W]+)Empfehlungen:"
    summary_match = re.search(summary_regex, generated_output_text)
    if summary_match is not None:
        summary = summary_match.group(1)
        #print(summary)

    # TODO: correctness of recommendation
    # extract recommendation
    recommendation_regex = "Empfehlungen:([\w\W]+)Medikamente:"
    recommendation_match = re.search(recommendation_regex, generated_output_text)
    if recommendation_match is not None:
        recommendation = recommendation_match.group(1)
        #print(recommendation)

    # TODO: correctness of medication
    #  alle aufgelisteten medikamente müssen im input vorkommen
    #  -> also alle medikamente identifizieren, mit dosierung
    #  ev. über hauptwörter? über regex? über zeile mit mg?
    #  "dauermedikation weiter wie bisher" auch möglich

    # extract medication from generated_output
    medication_regex = "Medikamente:([\w\W]+)Bitte"
    medication_names_output = extract_medication_names(medication_regex, generated_output_text, medication_list)
    #print(medication_names_output)

    # for input search for medication in two sections
    medication_input_regex = "Weiteres Procedere:([\w\W]+)TB für Kontrolle"
    medication_names_input1 = extract_medication_names(medication_input_regex, input_text, medication_list)
    medication_input_regex = "Dekurs:([\w\W]+)Therapie"
    medication_names_input2 = extract_medication_names(medication_input_regex, input_text, medication_list)
    medication_names_input = list(set(medication_names_input1 + medication_names_input2))
    #print(medication_names_input)

    # check for generated medication names if they can be found in the input
    for medication_name in medication_names_output:
        if medication_name in medication_names_input:
            print("In Input")
            print(medication_name)
            # TODO: add to correctness dict or not
            #   korrekt, wenn alle medikamente auch im input vorkommen
            #   oder wenn keine medikamente angeführt sind, sondern nur dauermedikation
            #   sonst nicht

    # TODO: wenn "Dauermedikation wie bisher", dann ist das auch korrekt
    #  aber nur, wenn sonst nichts angeführt ist



    # ending and greetings are correct if they have the right structure
    if structure_dict["ending"] != 0:
        correctness_dict["ending"] = 5
    if structure_dict["greetings"] != 0:
        correctness_dict["greetings"] = 5

    # print_results(correctness_dict, "correctness")
    # print_results for missingness



if __name__ == '__main__':
    main()
