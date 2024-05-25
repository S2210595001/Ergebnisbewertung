import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

class DocumentProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Processor")

        # Frames
        self.frame1 = tk.Frame(self.root, padx=10, pady=10)
        self.frame1.pack()

        self.frame2 = tk.Frame(self.root, padx=10, pady=10)
        self.frame2.pack()

        self.action_frame = tk.Frame(self.root, pady=10)
        self.action_frame.pack()

        # Labels
        self.label1 = tk.Label(self.frame1, text="Document 1:")
        self.label1.pack(side=tk.LEFT)

        self.label2 = tk.Label(self.frame2, text="Document 2:")
        self.label2.pack(side=tk.LEFT)

        # File paths
        self.filepath1 = tk.StringVar()
        self.filepath2 = tk.StringVar()

        # Buttons
        self.upload_button1 = tk.Button(self.frame1, text="Upload", command=self.upload_file1)
        self.upload_button1.pack(side=tk.LEFT, padx=(10, 0))

        self.upload_button2 = tk.Button(self.frame2, text="Upload", command=self.upload_file2)
        self.upload_button2.pack(side=tk.LEFT, padx=(10, 0))

        self.action1_button = tk.Button(self.action_frame, text="Action 1", command=self.perform_action1)
        self.action1_button.pack(side=tk.LEFT, padx=(10, 0))

        self.action2_button = tk.Button(self.action_frame, text="Action 2", command=self.perform_action2)
        self.action2_button.pack(side=tk.LEFT)

    def upload_file1(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.filepath1.set(file_path)

    def upload_file2(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.filepath2.set(file_path)

    def perform_action1(self):
        file1 = self.filepath1.get()
        file2 = self.filepath2.get()

        if file1 and file2:
            # Replace this with your actual action 1 logic
            messagebox.showinfo("Action 1", f"Performing Action 1 on:\n{file1}\n{file2}")
        else:
            messagebox.showerror("Error", "Please upload both documents.")

    def perform_action2(self):
        file1 = self.filepath1.get()
        file2 = self.filepath2.get()

        if file1 and file2:
            # Replace this with your actual action 2 logic
            messagebox.showinfo("Action 2", f"Performing Action 2 on:\n{file1}\n{file2}")
        else:
            messagebox.showerror("Error", "Please upload both documents.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DocumentProcessorApp(root)
    root.mainloop()