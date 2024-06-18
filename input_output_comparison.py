from tkinter import *
import evaluate_results


def add_highlight_tag(highlight_words, text_widget, tag_name, section=""):
    start_index = "1.0"
    end_index = END

    # find start and stop index of section
    if section != "":
        section_words = section.split(" ")

        if len(section_words) > 2:             # consider three words to find correct start and end indices
            start_word = section_words[0] + " " + section_words[1] + " " + section_words[2]
            end_word = section_words[-3] + " " + section_words[-2] + " " + section_words[-1]
        else:
            start_word = section_words[0]
            end_word = section_words[-1]

        start_index = text_widget.search(start_word, "1.0", stopindex=END)
        end_index = text_widget.search(end_word, start_index, stopindex=END)
        end_index = f"{end_index}+{len(end_word)}c"           # move end index to end of section

    # highlight specific words in section
    for word in highlight_words:
        start = start_index
        end_of_section = False
        while not end_of_section:
            # search for position of word in the text
            pos = text_widget.search(word, start, end_index)
            if not pos:
                end_of_section = True
            else:
                end = f"{pos}+{len(word)}c"
                text_widget.tag_add(tag_name, pos, end)
                start = end


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
    dir_name = "C:\\Users\\magda\\Documents\\Studium\\DSE\\MA\\Synthetische Daten"
    file_number = "5-10"


    # read input file
    input_file = open(dir_name + "\\" + file_number + "\\" + file_number + "-input.txt", "r", encoding="utf-8")
    input_text = input_file.read()
    input_file.close()

    # read generated output file
    output_file = open(dir_name + "\\" + file_number + "\\" + file_number + "-output.txt", "r", encoding="utf-8")
    generated_output_text = output_file.read()
    output_file.close()

    # read profile file
    profile_filename = dir_name + "\\" + file_number + "\\" + file_number + "-profile.txt"
    profile_file = open(profile_filename, "r", encoding="utf-8")
    profile_text = profile_file.read()
    profile_file.close()


    # read list of medication names from file
    medication_list = evaluate_results.read_medication_file()
    medication_names_input = evaluate_results.extract_medication_names_from_section("([\W\w]+)", input_text, medication_list)
    medication_names_output = evaluate_results.extract_medication_names_from_section("([\W\w]+)", generated_output_text, medication_list)

    # extract personal data
    personal_data_dict = evaluate_results.extract_personal_data(profile_filename)
    filtered_dict = {k: v for k, v in personal_data_dict.items() if k != "gender" and v != ''}      # exclude gender
    personal_data = list(filtered_dict.values())

    # extract diagnosis
    diagnosis_section_input = evaluate_results.find_diagnosis_section_in_input(input_text)
    diagnosis_section_output = evaluate_results.find_diagnosis_section_in_output(generated_output_text)
    diagnosis_output = evaluate_results.extract_diagnosis_from_section(diagnosis_section_output)
    diagnosis_input = evaluate_results.extract_diagnosis_from_section(diagnosis_section_input)
    print(diagnosis_input)
    print(diagnosis_output)
    print(diagnosis_section_input)
    print(diagnosis_section_output)

    # extract recommendations
    recommendation_section_input = evaluate_results.find_recommendation_section_in_input(input_text)
    recommendation_section_output = evaluate_results.find_recommendation_section_in_output(generated_output_text)
    recommendation_output, _ = evaluate_results.extract_pos_keywords(recommendation_section_output)
    recommendation_input, _ = evaluate_results.extract_pos_keywords(recommendation_section_input)

    # extract summary
    summary_section_input, _ = evaluate_results.find_summary_section_in_input(input_text)
    summary_section_output = evaluate_results.find_summary_section_in_output(generated_output_text)
    summary_output, _ = evaluate_results.extract_pos_keywords(summary_section_output)
    summary_input, _ = evaluate_results.extract_pos_keywords(summary_section_input)


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
    add_highlight_tag(recommendation_input, text_widget_input, "recommendation_tag", recommendation_section_input)
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
    text_widget_output.tag_raise("medication_tag")
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
