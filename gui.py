import tkinter as tk
from tkinter import filedialog, messagebox

import evaluate_results

class FileComparison:
    def __init__(self, root):
        self.root = root
        self.root.title("File Comparison")

        # Labels to show file names
        self.input_label = tk.Label(root, text="Input: None")
        self.input_label.pack()
        self.output_label = tk.Label(root, text="Output: None")
        self.output_label.pack()
        self.profile_label = tk.Label(root, text="Profile: None")
        self.profile_label.pack()

        # Buttons to upload files
        self.upload_input_button = tk.Button(root, text="Upload Input", command=self.upload_input)
        self.upload_input_button.pack()
        self.upload_output_button = tk.Button(root, text="Upload Output", command=self.upload_output)
        self.upload_output_button.pack()
        self.upload_profile_button = tk.Button(root, text="Upload Profile", command=self.upload_profile)
        self.upload_profile_button.pack()

        # Button to compare files
        self.compare_button = tk.Button(root, text="Compare Files", command=self.compare_files)
        self.compare_button.pack()

        # Text fields to show results
        self.structure_result_text = tk.Text(root, height=1, width=30)
        self.structure_result_text.pack()
        self.correctness_result_text = tk.Text(root, height=1, width=30)
        self.correctness_result_text.pack()

        # Initialize file paths and contents
        self.input_path = None
        self.output_path = None
        self.profile_path = None

        self.input_content = None
        self.output_content = None
        self.profile_content = None

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

    def compare_files(self):
        if not self.input_path or not self.output_path or not self.profile_path:
            messagebox.showerror("Error", "Please upload all three files before comparing.")
            return

        # compare files
        # extract personal data
        personal_data_dict = evaluate_results.extract_personal_data(self.profile_path)

        # read list of medication names from file
        medication_list = evaluate_results.read_medication_file()

        # evaluate structure
        structure_dict = evaluate_results.evaluate_structure(self.output_content)
        structure_score = evaluate_results.print_results(structure_dict, "structure")

        # evaluate correctness
        correctness_dict = evaluate_results.evaluate_correctness(structure_dict, personal_data_dict, medication_list, self.input_content, self.output_content)
        correctness_score = evaluate_results.print_results(correctness_dict, "correctness")

        # Dummy comparison logic
        # Replace this with your actual comparison logic
        result1 = "Struktur Score: " + str(structure_score) + "%"            # Example comparison result for file 1 and file 2
        result2 = "Korrektheit Score: " + str(correctness_score) + "%"       # Example comparison result for file 2 and file 3

        # Display results
        self.structure_result_text.delete(1.0, tk.END)
        self.structure_result_text.insert(tk.END, result1)
        self.correctness_result_text.delete(1.0, tk.END)
        self.correctness_result_text.insert(tk.END, result2)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileComparison(root)
    root.mainloop()
