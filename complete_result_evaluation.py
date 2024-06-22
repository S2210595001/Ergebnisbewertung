import os
import pandas as pd

import evaluate_results

# Define the base directory
base_dir = "C:\\Users\\magda\\Documents\\Studium\\DSE\\MA\\Praxis\\Experimente"

# Define the folder names
folders = ["6", "7", "8", "9"]

# Initialize an empty DataFrame with the specified structure
columns = ['Prompt', 'Befundname', 'Anzahl Bsp', 'Str WH 1', 'Korr WH 1', 'Str WH 2', 'Korr WH 2', 'Str WH 3', 'Korr WH 3', 'Avg. Struktur', 'Avg. Korrektheit']
df = pd.DataFrame(columns=columns)


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def compare_files(input_file_path, profile_file_path, output_file_path):
    #with open(input_file_path, 'r') as input_file:

    # compare files
    # extract personal data
    personal_data_dict = evaluate_results.extract_personal_data(profile_file_path)

    # read list of medication names from file
    medication_list = evaluate_results.read_medication_file()

    output_content = read_file(output_file_path)
    input_content = read_file(input_file_path)

    # evaluate structure
    structure_dict = evaluate_results.evaluate_structure(output_content)
    structure_score = evaluate_results.print_results(structure_dict, "structure", False)

    # evaluate correctness
    correctness_dict = evaluate_results.evaluate_correctness(structure_dict, personal_data_dict, medication_list,
                                                             input_content, output_content)
    correctness_score = evaluate_results.print_results(correctness_dict, "correctness", False)

    return structure_score, correctness_score
    #print(f"Comparing {input_file_path} and {profile_file_path} with {output_file_path}:")


# Iterate through each folder
for folder in folders:
    folder_path = os.path.join(base_dir, folder)

    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Paths to input.txt and profile.txt
        input_file_path = os.path.join(folder_path, "input.txt")
        profile_file_path = os.path.join(folder_path, "profile.txt")

        # Ensure input.txt and profile.txt exist
        if os.path.isfile(input_file_path) and os.path.isfile(profile_file_path):
            # List all files in the folder
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                # Check if it's an output file with the specific naming convention
                if os.path.isfile(file_path) and filename.startswith("output-") and filename.endswith(".txt"):
                    parts = filename.split('-')
                    if len(parts) == 5:
                        dir_name = parts[1]
                        prompt_name = parts[2]
                        example_count = parts[3]
                        example_number = parts[4].split('.')[0]

                        if dir_name.isdigit() and prompt_name.isdigit() and example_count in ['1', '3', '5'] and example_number in ['1', '2', '3']:
                            if example_number == "1":  # save entries to df
                                new_row = {
                                    "Prompt": prompt_name,
                                    "Befundname": dir_name,
                                    "Anzahl Bsp": example_count,
                                }
                                df.loc[len(df)] = new_row

                            # Define the condition to filter rows
                            condition = (df["Prompt"] == prompt_name) & (df["Befundname"] == dir_name) & (df["Anzahl Bsp"] == example_count)
                            # Find the index where the condition is true
                            index_to_update = df[condition].index

                            # get comparison results for structure and correctness
                            structure_result, correctness_result = compare_files(input_file_path, profile_file_path, file_path)

                            if not index_to_update.empty:
                                structure_column_to_update = "Str WH " + example_number
                                correctness_column_to_update = "Korr WH " + example_number

                                # Update the value in column at the filtered index
                                df.loc[index_to_update, structure_column_to_update] = structure_result
                                df.loc[index_to_update, correctness_column_to_update] = correctness_result

                            #df = df.append(comparison_result, ignore_index=True)


# Calculate averages for 'Avg. Struktur' and 'Avg. Korrektheit'
df['Avg. Struktur'] = df[[f'Str WH {i}' for i in range(1, 4)]].mean(axis=1)
df['Avg. Korrektheit'] = df[[f'Korr WH {i}' for i in range(1, 4)]].mean(axis=1)

# Display the DataFrame
#print(df)
df.to_csv("result.csv", sep=";", decimal=",")