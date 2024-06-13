from tkinter import *
import evaluate_results


def add_highlight_tag(highlight_words, text_widget, tag_name, section=""):
    idx1 = "1.0"
    idx2 = END
    # find start and stop index of section
    if section != "":
        section_words = section.split(" ")

        if len(section_words) > 2:
            start_word = section_words[0] + " " + section_words[1] + " " + section_words[2]
            end_word = section_words[len(section_words)-3] + " " + section_words[len(section_words)-2] + " " + section_words[len(section_words)-1]
        else:
            start_word = section_words[0]
            end_word = section_words[len(section_words)-1]

        idx1 = text_widget.search(start_word, "1.0", stopindex=END)
        if not idx1:
            idx1 = "1.0"
            print("No start index found")
        else:
            idx2 = text_widget.search(end_word, idx1, stopindex=END)
            if not idx2:
                print("No end index found")
                idx2 = END

        if tag_name == "diagnosis_tag":         # TODO: find error with start and end word
            idx1 = "1.0"
            idx2 = END

    # highlight specific words in section
    for word in highlight_words:
        #start = "1.0"
        start = idx1
        while True:
            pos = text_widget.search(word, start, idx2)
            if not pos:
                break
            end = f"{pos}+{len(word)}c"
            text_widget.tag_add(tag_name, pos, end)
            start = end


# C:\Users\magda\Documents\Studium\DSE\MA\Experimente\Experiment 13\5-1
# 5-2, 5-3

def main():
    def on_configure(event):
        # update size of text boxes when window is resized
        text_widget_input.config(width=event.width // 20, height=event.height // 20)
        text_widget_output.config(width=event.width // 20, height=event.height // 20)
        text_widget_profile.config(width=event.width // 20, height=event.height // 20)

    root = Tk()
    root.title("Gegenüberstellung erhobene Befunde und generierter Arztbrief")
    root.geometry("600x400")

    # read text from files
    #dir_name = "01c03085-7087-4ebd-8e48-ef902741b3ea"
    dir_name = "C:\\Users\\magda\\Documents\\Studium\\DSE\\MA\\Experimente\\Experiment 13"
    file_number = "5-1"

    # read input file
    # input_file_name = dir_name + "\\" + dir_name + "-input.txt"
    #input_file = open(dir_name + "\\" + dir_name + "-input.txt", "r", encoding="utf-8")
    input_file = open(dir_name + "\\" + file_number + "\\" + file_number + "-input.txt", "r", encoding="utf-8")
    input_text = input_file.read()
    input_file.close()

    #output_file = open(dir_name + "\\" + "Arztbrief_Max_Mustermann.txt", "r", encoding="utf-8")
    output_file = open(dir_name + "\\" + file_number + "\\" + file_number + "-output.txt", "r", encoding="utf-8")
    generated_output_text = output_file.read()
    output_file.close()

    #profile_filename = dir_name + "\\" + dir_name + "-profile.txt"
    profile_filename = dir_name + "\\" + file_number + "\\" + file_number + "-profile.txt"
    profile_file = open(profile_filename, "r", encoding="utf-8")
    profile_text = profile_file.read()
    profile_file.close()


    # read list of medication names from file
    # only consider medication names from output
    medication_list = evaluate_results.read_medication_file()
    medication_names_input, medication_names_output = evaluate_results.find_medication_names(input_text, generated_output_text, medication_list)
    #print(medication_names_input, medication_names_output)
    #print(medication_names_input)

    # extract personal data
    personal_data_dict = evaluate_results.extract_personal_data(profile_filename)
    filtered_dict = {k: v for k, v in personal_data_dict.items() if k != "gender" and v != ''}      # exclude gender
    personal_data = list(filtered_dict.values())
    #print(personal_data)

    # extract diagnosis
    diagnosis_section_input = evaluate_results.find_diagnosis_section_in_input(input_text)
    #print(diagnosis_section_input)
    diagnosis_section_output = evaluate_results.find_diagnosis_section_in_output(generated_output_text)
    diagnosis_output = evaluate_results.extract_diagnosis_from_section(diagnosis_section_output)
    diagnosis_input = evaluate_results.extract_diagnosis_from_section(diagnosis_section_input)
    #print(diagnosis_input)
    #print(diagnosis_section_input)
    #print(diagnosis_output)
    #print(diagnosis_section_output)

    # extract recommendations
    #recommendation_input, recommendation_output = evaluate_results.find_recommendation_sections(input_text, generated_output_text)
    recommendation_section_input1, recommendation_section_input2 = evaluate_results.find_recommendation_section_in_input(input_text)
    recommendation_section_output = evaluate_results.find_recommendation_section_in_output(generated_output_text)
    recommendation_output = evaluate_results.extract_pos_keywords(recommendation_section_output)
    recommendation_input1 = evaluate_results.extract_pos_keywords(recommendation_section_input1)
    recommendation_input2 = evaluate_results.extract_pos_keywords(recommendation_section_input2)

    # extract summary
    #summary_input, summary_output = evaluate_results.find_summary_sections(input_text, generated_output_text)
    summary_section_input, _ = evaluate_results.find_summary_section_in_input(input_text)
    summary_section_output = evaluate_results.find_summary_section_in_output(generated_output_text)
    summary_output = evaluate_results.extract_pos_keywords(summary_section_output)
    summary_input = evaluate_results.extract_pos_keywords(summary_section_input)
    #print(summary_output)


    # define colors
    yellow = "#FFF68F"
    orange = "#FFA54F"
    red = "#FF6347"
    green = "#9BCD9B"
    purple = "#CDB5CD"


    # text widget for input files
    text_widget_input = Text(root, height=10, width=10, wrap=WORD)
    # add tags for different colors
    text_widget_input.tag_configure("medication_tag", background=orange)
    text_widget_input.tag_configure("diagnosis_tag", background=red)
    text_widget_input.tag_configure("recommendation_tag", background=green)
    text_widget_input.tag_configure("summary_tag", background=purple)
    text_widget_input.insert(END, input_text)
    add_highlight_tag(medication_names_input, text_widget_input, "medication_tag")
    add_highlight_tag(diagnosis_input, text_widget_input, "diagnosis_tag", diagnosis_section_input)
    add_highlight_tag(recommendation_input1, text_widget_input, "recommendation_tag", recommendation_section_input1)
    add_highlight_tag(recommendation_input2, text_widget_input, "recommendation_tag", recommendation_section_input2)
    add_highlight_tag(summary_input, text_widget_input, "summary_tag", summary_section_input)
    text_widget_input.tag_raise("medication_tag")        # ensure medication tag is applied last
    text_widget_input.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


    # text widget for profile
    text_widget_profile = Text(root, height=10, width=10, wrap=WORD)
    # add tags for different colors
    text_widget_profile.tag_configure("personal_data_tag", background=yellow)
    text_widget_profile.insert(END, profile_text)
    add_highlight_tag(personal_data, text_widget_profile, "personal_data_tag")
    text_widget_profile.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


    # text widget for generated medical report
    text_widget_output = Text(root, height=10, width=40, wrap=WORD)
    # add tags for different colors
    text_widget_output.tag_configure("personal_data_tag", background=yellow)
    text_widget_output.tag_configure("medication_tag", background=orange)
    text_widget_output.tag_configure("diagnosis_tag", background=red)
    text_widget_output.tag_configure("recommendation_tag", background=green)
    text_widget_output.tag_configure("summary_tag", background=purple)
    text_widget_output.insert(END, generated_output_text)
    add_highlight_tag(personal_data, text_widget_output, "personal_data_tag")
    add_highlight_tag(diagnosis_output, text_widget_output, "diagnosis_tag", diagnosis_section_output)
    add_highlight_tag(recommendation_output, text_widget_output, "recommendation_tag", recommendation_section_output)
    add_highlight_tag(summary_output, text_widget_output, "summary_tag", summary_section_output)
    add_highlight_tag(medication_names_output, text_widget_output, "medication_tag")
    text_widget_output.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")


    # configure resizing behavior
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.bind("<Configure>", on_configure)

    root.mainloop()


if __name__ == "__main__":
    main()
