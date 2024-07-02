import tkinter as tk
from tkinter import *
from tkinter import messagebox, filedialog

import evaluate_results

class FileComparison:
    def __init__(self, root):
        self.root = root
        self.root.title("File Comparison")

        # Buttons to upload files
        self.upload_input_button = tk.Button(root, text="Upload Input", command=self.upload_input)
        self.upload_input_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.input_label = tk.Label(root, text="Input: None")
        self.input_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.upload_profile_button = tk.Button(root, text="Upload Profile", command=self.upload_profile)
        self.upload_profile_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        self.profile_label = tk.Label(root, text="Profile: None")
        self.profile_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.upload_output_button = tk.Button(root, text="Upload Output", command=self.upload_output)
        self.upload_output_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.output_label = tk.Label(root, text="Output: None")
        self.output_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Add some space before the compare button
        self.spacer = tk.Frame(root, height=10)
        self.spacer.grid(row=6, column=0, columnspan=2)

        # Button to compare files
        self.compare_button = tk.Button(root, text="Compare Files", command=self.compare_files)
        self.compare_button.grid(row=7, column=0, padx=5, pady=5)
        self.visualize_button = tk.Button(root, text="Visualize Results", command=self.visualize_results)
        self.visualize_button.grid(row=7, column=1, padx=5, pady=5)

        # Text fields to show results
        self.structure_result_text = tk.Text(root, height=1, width=30)
        self.structure_result_text.grid(row=8, column=0, columnspan=2, padx=5, pady=5)
        self.correctness_result_text = tk.Text(root, height=1, width=30)
        self.correctness_result_text.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

        # Initialize file paths and contents
        self.input_path = None
        self.output_path = None
        self.profile_path = None

        self.input_content = None
        self.output_content = None
        self.profile_content = None
        self.personal_data_dict = None

        # read list of medication names from file
        self.medication_list = evaluate_results.read_medication_file()

    def upload_file(self, specific_string):
        while True:
            file_path = filedialog.askopenfilename()
            if not file_path:
                return None  # If the user cancels the dialog, return None
            if specific_string in file_path:
                return file_path
            else:
                messagebox.showwarning("Warning", f"Selected file does not contain '{specific_string}'. Please select another file.")

    def upload_input(self):
        self.input_path = self.upload_file("input")
        if self.input_path:
            self.input_label.config(text=f"Input: {self.input_path}")
            with open(self.input_path, "r", encoding="utf-8") as file:
                self.input_content = file.read()

                if self.input_content.__contains__("persönliche_Daten = "):         # file also contains personal data
                    content_split = self.input_content.split("persönliche_Daten = ")
                    content = content_split[0]
                    content = content.replace("erhobene_Befunde = \"\"\"\n", "")
                    content = content.replace("\"\"\"", "")
                    self.input_content = content

    def upload_output(self):
        self.output_path = self.upload_file("output")
        if self.output_path:
            self.output_label.config(text=f"Output: {self.output_path}")
            with open(self.output_path, "r", encoding="utf-8") as file:
                self.output_content = file.read()

    def upload_profile(self):
        self.profile_path = self.upload_file("profile")
        if self.profile_path:
            self.profile_label.config(text=f"Profile: {self.profile_path}")
            with open(self.profile_path, "r", encoding="utf-8") as file:
                self.profile_content = file.read()

                # extract personal data
                self.personal_data_dict = evaluate_results.extract_personal_data(self.profile_path)

    def compare_files(self):
        if not self.input_path or not self.output_path or not self.profile_path:
            messagebox.showerror("Error", "Please upload all three files before comparing.")
            return

        # evaluate structure
        structure_dict = evaluate_results.evaluate_structure(self.output_content)
        structure_score = evaluate_results.print_results(structure_dict, "structure", True)

        # evaluate correctness
        correctness_dict = evaluate_results.evaluate_correctness(structure_dict, self.personal_data_dict, self.medication_list, self.input_content, self.output_content)

        correctness_score = evaluate_results.print_results(correctness_dict, "correctness", True)

        # Compare files
        structure_result = "Struktur Score: " + str(structure_score) + "%"            # Example comparison result for file 1 and file 2
        correctness_result = "Korrektheit Score: " + str(correctness_score) + "%"       # Example comparison result for file 2 and file 3

        # Display results
        self.structure_result_text.delete(1.0, tk.END)
        self.structure_result_text.insert(tk.END, structure_result)
        self.correctness_result_text.delete(1.0, tk.END)
        self.correctness_result_text.insert(tk.END, correctness_result)


    def add_highlight_tag(self, highlight_words, text_widget, tag_name, section=""):
        start_index = "1.0"
        end_index = END

        # find start and stop index of section
        if section != "":
            section_words = section.split(" ")

            if len(section_words) > 2:  # consider three words to find correct start and end indices
                start_word = section_words[0] + " " + section_words[1] + " " + section_words[2]
                end_word = section_words[-3] + " " + section_words[-2] + " " + section_words[-1]
            else:
                start_word = section_words[0]
                end_word = section_words[-1]

            start_index = text_widget.search(start_word, "1.0", stopindex=END)
            end_index = text_widget.search(end_word, start_index, stopindex=END)
            end_index = f"{end_index}+{len(end_word)}c"  # move end index to end of section

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


    def visualize_results(self):
        def on_configure(event):
            # update size of text boxes when window is resized
            text_widget_input.config(width=event.width // 20, height=event.height // 20)
            text_widget_output.config(width=event.width // 20, height=event.height // 20)
            text_widget_profile.config(width=event.width // 20, height=event.height // 20)

        if not self.input_path or not self.output_path or not self.profile_path:
            messagebox.showerror("Error", "Please upload all three files before visualizing.")
            return

        visualization_window = tk.Toplevel(self.root)
        visualization_window.title("Gegenüberstellung erhobene Befunde und generierter Arztbrief")
        visualization_window.geometry("600x400")

        # extract personal data
        filtered_dict = {k: v for k, v in self.personal_data_dict.items() if k != "gender" and v != ''}  # exclude gender
        personal_data = list(filtered_dict.values())

        # extract medication names
        medication_names_input = evaluate_results.extract_medication_names_from_section("([\W\w]+)", self.input_content, self.medication_list)
        medication_names_output = evaluate_results.extract_medication_names_from_section("([\W\w]+)", self.output_content, self.medication_list)

        # extract diagnosis
        diagnosis_section_input = evaluate_results.find_diagnosis_section_in_input(self.input_content)
        diagnosis_section_output = evaluate_results.find_diagnosis_section_in_output(self.output_content)
        diagnosis_output = evaluate_results.extract_diagnosis_from_section(diagnosis_section_output)
        diagnosis_input = evaluate_results.extract_diagnosis_from_section(diagnosis_section_input)

        # extract recommendations
        recommendation_section_input = evaluate_results.find_recommendation_section_in_input(self.input_content)
        recommendation_section_output = evaluate_results.find_recommendation_section_in_output(self.output_content)
        recommendations_input, _, recommendations_output, _ = evaluate_results.find_recommendation_sections(self.input_content, self.output_content)

        # extract summary
        summary_sections_input = evaluate_results.find_summary_section_in_input(self.input_content)
        summary_section_output = evaluate_results.find_summary_section_in_output(self.output_content)
        summary_input, _, summary_output, _ = evaluate_results.find_summary_sections(self.input_content, self.output_content)

        # define colors
        yellow = "#FFF68F"
        orange = "#FFA54F"
        red = "#FF6347"
        green = "#9BCD9B"
        purple = "#CDB5CD"

        # text widget for input files
        text_widget_input = Text(visualization_window, height=10, width=10, wrap=WORD)
        # add tags for different colors
        text_widget_input.tag_configure("medication_tag", background=orange)
        text_widget_input.tag_configure("diagnosis_tag", background=red)
        text_widget_input.tag_configure("recommendation_tag", background=green)
        text_widget_input.tag_configure("summary_tag", background=purple)
        text_widget_input.insert(END, self.input_content)
        self.add_highlight_tag(medication_names_input, text_widget_input, "medication_tag")
        self.add_highlight_tag(diagnosis_input, text_widget_input, "diagnosis_tag", diagnosis_section_input)
        self.add_highlight_tag(recommendations_input, text_widget_input, "recommendation_tag", recommendation_section_input)
        for summary in summary_sections_input:
            self.add_highlight_tag(summary_input, text_widget_input, "summary_tag",
                              summary)  # only show keywords from output
        text_widget_input.tag_raise("medication_tag")  # ensure medication tag is applied last
        text_widget_input.tag_raise("diagnosis_tag")
        text_widget_input.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # text widget for profile
        text_widget_profile = Text(visualization_window, height=10, width=10, wrap=WORD)
        # add tags for different colors
        text_widget_profile.tag_configure("personal_data_tag", background=yellow)
        text_widget_profile.insert(END, self.profile_content)
        self.add_highlight_tag(personal_data, text_widget_profile, "personal_data_tag")
        text_widget_profile.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # text widget for generated medical report
        text_widget_output = Text(visualization_window, height=10, width=40, wrap=WORD)
        # add tags for different colors
        text_widget_output.tag_configure("personal_data_tag", background=yellow)
        text_widget_output.tag_configure("medication_tag", background=orange)
        text_widget_output.tag_configure("diagnosis_tag", background=red)
        text_widget_output.tag_configure("recommendation_tag", background=green)
        text_widget_output.tag_configure("summary_tag", background=purple)
        text_widget_output.insert(END, self.output_content)
        self.add_highlight_tag(personal_data, text_widget_output, "personal_data_tag")
        self.add_highlight_tag(diagnosis_output, text_widget_output, "diagnosis_tag", diagnosis_section_output)
        self.add_highlight_tag(recommendations_output, text_widget_output, "recommendation_tag",
                          recommendation_section_output)
        self.add_highlight_tag(summary_output, text_widget_output, "summary_tag", summary_section_output)
        self.add_highlight_tag(medication_names_output, text_widget_output, "medication_tag")
        text_widget_output.tag_raise("medication_tag")
        text_widget_output.tag_raise("diagnosis_tag")
        text_widget_output.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # configure resizing behavior
        visualization_window.grid_rowconfigure(0, weight=1)
        visualization_window.grid_rowconfigure(1, weight=1)
        visualization_window.grid_columnconfigure(0, weight=1)
        visualization_window.grid_columnconfigure(1, weight=1)
        visualization_window.bind("<Configure>", on_configure)


if __name__ == "__main__":
    root = tk.Tk()
    app = FileComparison(root)
    root.mainloop()
