from tkinter import *
import re

import evaluate_results


def add_highlight_tag(highlight_words, text_widget, tag_name):
    # highlight specific words
    for word in highlight_words:
        start = "1.0"
        while True:
            pos = text_widget.search(word, start, stopindex=END)
            if not pos:
                break
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
    dir_name = "b87f9c99-fdd1-42ae-bb39-d84b7d7e8771"
    input_file = open(dir_name + "\\" + dir_name + "-input.txt", "r", encoding="utf-8")
    input_text = input_file.read()
    input_file.close()

    output_file = open(dir_name + "\\" + "Arztbrief_Max_Mustermann.txt", "r", encoding="utf-8")
    generated_output_text = output_file.read()
    output_file.close()

    profile_filename = dir_name + "\\" + dir_name + "-profile.txt"
    profile_file = open(profile_filename, "r", encoding="utf-8")
    profile_text = profile_file.read()
    profile_file.close()

    # read list of medication names from file
    # only consider medication names from output
    medication_list = evaluate_results.read_medication_file()
    medication_names_input, medication_names_output = evaluate_results.find_medication_names_in_input_output(input_text, generated_output_text, medication_list)
    #print(medication_names_input, medication_names_output)

    # extract personal data
    personal_data_dict = evaluate_results.extract_personal_data(profile_filename)
    filtered_dict = {k: v for k, v in personal_data_dict.items() if k != "gender"}      # exclude gender
    personal_data = list(filtered_dict.values())
    #print(personal_data)

    # extract diagnosis
    diagnosis_input, diagnosis_output = evaluate_results.find_diagnosis_section_in_input_output(input_text, generated_output_text)


    # text widget for input files
    text_widget_input = Text(root, height=10, width=10, wrap=WORD)
    # add tags for different colors
    text_widget_input.tag_configure("medication_tag", background="orange")
    text_widget_input.tag_configure("diagnosis_tag", background="#800080")
    text_widget_input.insert(END, input_text)
    add_highlight_tag(medication_names_output, text_widget_input, "medication_tag")
    add_highlight_tag(diagnosis_input, text_widget_input, "diagnosis_tag")
    text_widget_input.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


    # text widget for profile
    text_widget_profile = Text(root, height=10, width=10, wrap=WORD)
    # add tags for different colors
    text_widget_profile.tag_configure("personal_data_tag", background="yellow")
    text_widget_profile.tag_configure("medication_tag", background="orange")
    text_widget_profile.insert(END, profile_text)
    add_highlight_tag(personal_data, text_widget_profile, "personal_data_tag")
    add_highlight_tag(medication_names_output, text_widget_profile, "medication_tag")
    text_widget_profile.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


    # text widget for generated medical report
    text_widget_output = Text(root, height=10, width=40, wrap=WORD)
    # add tags for different colors
    text_widget_output.tag_configure("personal_data_tag", background="yellow")
    text_widget_output.tag_configure("medication_tag", background="orange")
    text_widget_output.tag_configure("diagnosis_tag", background="#800080")
    text_widget_output.insert(END, generated_output_text)
    add_highlight_tag(personal_data, text_widget_output, "personal_data_tag")
    add_highlight_tag(medication_names_output, text_widget_output, "medication_tag")
    add_highlight_tag(diagnosis_output, text_widget_output, "diagnosis_tag")
    text_widget_output.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

    # configure resizing behavior
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.bind("<Configure>", on_configure)

    root.mainloop()


# TODO: find highlight words
#       extract from input or profile, then find in generated report
#       in opposite direction (extract from report and search in input) you don't know if something is missing

# TODO:
#  Meldung ausgeben, wenn Tags in Input und Output nicht zusammenpassen

# TODO:
#   drittes Fenster für profile
#   sollte eigentlich in erster spalte darunter sein

if __name__ == "__main__":
    main()
