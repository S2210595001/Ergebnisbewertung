from tkinter import *
import re


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

    root = Tk()
    root.title("Gegenüberstellung erhobene Befunde und generierter Arztbrief")

    # read text from files
    dir_name = "e91d3e5c-f642-4a1f-9e63-d68e3e10a37d"
    input_file = open(dir_name + "\\" + dir_name + "-input.txt", "r", encoding="utf-8")
    input_text = input_file.read()
    input_file.close()

    output_file = open(dir_name + "\\" + "Arztbrief_Max_Mustermann_5.txt", "r", encoding="utf-8")
    output_text = output_file.read()
    output_file.close()

    # text widget for input files
    text_widget_input = Text(root, height=10, width=30, wrap=WORD)
    # add tags for different colors
    text_widget_input.tag_configure("name_tag", background="yellow")
    # text_widget_input.tag_configure("highlight", background="red", foreground="black")
    text_widget_input.insert(END, input_text)
    # TODO: extract highlight words, e.g. with Regex
    highlight_words = ["Mustermann Max"]
    add_highlight_tag(highlight_words, text_widget_input, "name_tag")
    text_widget_input.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")

    # text widget for generated medical report
    text_widget_output = Text(root, height=10, width=30, wrap=WORD)
    # add tags for different colors
    text_widget_output.tag_configure("name_tag", background="yellow")
    text_widget_output.insert(END, output_text)
    highlight_words = ["Max Mustermann"]
    add_highlight_tag(highlight_words, text_widget_output, "name_tag")
    text_widget_output.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # configure resizing behavior
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.bind("<Configure>", on_configure)

    root.mainloop()


# TODO: find highlight words
#       extract from input or profile, then find in generated report
#       in opposite direction (extract from report and search in input) you don't know if something is missing

if __name__ == "__main__":
    main()
