import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import csv
import os
import logging


csv_file_path = "styles.csv"
KEY = ["Prompt", "Negative prompt", "Other"]
KEYS = ['prompt', 'negative_prompt']

# Check if styles.csv exists
if not os.path.isfile("styles.csv"):
    # Create a new styles.csv file with headers
    with open('styles.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'prompt', 'negative_prompt'])
        writer.writerow(['example name', 'example prompt', 'example negative prompt'])

with open('styles.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    rows = []
    header = next(reader)
    for row in reader:
        updated_row = []
        for item in row:
            item = item.strip().replace('"', '').replace("'", '')
            updated_row.append(item)
        rows.append(updated_row)

with open('styles.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)

# Create the GUI
root = tk.Tk()
root.title("Prompt Reveal")
root.geometry("1000x275")


def get_style_names():
    with open('styles.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # Skip the header row
        names = [row[0] for row in reader]
    return names

def delete_style(name):
    # Read in the contents of the CSV file
    with open('styles.csv', 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = [row for row in reader]

    # Find the row to delete
    index = next((i for i, row in enumerate(rows) if row['name'] == name), None)

    if index is not None:
        # Remove the row from the list of rows
        rows.pop(index)

        # Write the updated rows back to the CSV file
        with open('styles.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)

        # Update the dropdown list
        dropdown_var.set('')
        dropdown_menu['menu'].delete(0, 'end')
        for name in get_style_names():
            dropdown_menu['menu'].add_command(label=name, command=lambda name=name: select_style(name))

        # Clear the text boxes
        for key in KEY:
            text_boxes[key].delete("1.0", "end")


def select_style(name):
    # Update the dropdown variable
    dropdown_var.set(name)

    # Update the text boxes with the selected row's values
    with open('styles.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        row = next(row for row in reader if row['name'] == name)
        text_boxes[KEY[0]].delete("1.0", "end")
        text_boxes[KEY[0]].insert("1.0", row["prompt"])
        text_boxes[KEY[1]].delete("1.0", "end")
        text_boxes[KEY[1]].insert("1.0", row["negative_prompt"])

def delete_style_button():
    # Get the name of the currently selected style
    name = dropdown_var.get()

    # Call the delete_style function to delete the style
    delete_style(name)

    # Update the dropdown list
    get_style_names()


def update_text_widgets(name):
    # Find the selected row by name
    with open('styles.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get('name') == name:
                # Update the text boxes with the row's values
                text_boxes[KEY[0]].delete("1.0", "end")
                text_boxes[KEY[0]].insert("1.0", row.get("prompt"))
                text_boxes[KEY[1]].delete("1.0", "end")
                text_boxes[KEY[1]].insert("1.0", row.get("negative_prompt"))
                break
        else:
            # No matching row found
            logging.error(f"No row found with name '{name}'")
        get_style_names()


def save_button():
    # Get the values from the text fields
    name = save_field.get('1.0', 'end').strip()
    prompt = text_boxes[KEY[0]].get("1.0", tk.END).strip()
    negative_prompt = text_boxes[KEY[1]].get("1.0", tk.END).strip()

    # Create a dictionary with the values
    row_dict = {"name": name, "prompt": prompt, "negative_prompt": negative_prompt}

    if row_dict['name']:
        # Write the row to the CSV file
        write_row_to_csv(csv_file_path, row_dict)

        # Clear the text fields
        save_field.delete('1.0', tk.END)
        text_boxes[KEY[0]].delete("1.0", tk.END)
        text_boxes[KEY[1]].delete("1.0", tk.END)
        text_boxes[KEY[2]].delete("1.0", tk.END)

        # Update the dropdown list
        dropdown_var.set('')
        dropdown_menu['menu'].delete(0, 'end')
        for name in get_style_names():
            dropdown_menu['menu'].add_command(label=name, command=lambda name=name: select_style(name))
        # Show a message box
        messagebox.showinfo("Success", "Prompt saved to styles.csv")
        get_style_names()
    else:
        messagebox.showinfo("Failed", "'Save As' left blank.")


def write_row_to_csv(csv_file_path, row_dict):
    with open(csv_file_path, 'a', newline='') as csvfile:
        fieldnames = ['name', 'prompt', 'negative_prompt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(row_dict)


def open_png_metadata():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png")])
    if not file_path:
        return  # If no file selected, do nothing
    metadata = parse_png_info(file_path)
    for key, value in metadata.items():
        text_boxes[key].delete(1.0, tk.END)
        text_boxes[key].insert(tk.END, value)

    # Load the image
    img = Image.open(file_path)

    # Resize the image if necessary to fit in the image_label
    max_size = 220
    width, height = img.size
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Create a PhotoImage object
    img_tk = ImageTk.PhotoImage(img)

    # Set the image of the image_label
    image_label.config(image=img_tk)
    image_label.image = img_tk
    image_label.grid(row=0, column=6, rowspan=5)


# Define the function to parse PNG metadata
def parse_png_info(file_path):
    keys = ['Prompt:', 'Negative prompt:', 'Steps:']
    with Image.open(file_path) as img:
        if img.format != "PNG":
            raise ValueError("File is not a PNG image")
        metadata = img.info
        dictionary = metadata.copy()
        for key in keys:
            if key not in dictionary.keys():
                dictionary[key] = f"Not available"

        # Separate PNG data by keys
        parameters = str("Prompt: " + dictionary['parameters'].replace('\n', ' '))
        chunks = []
        start_index = 0

        for i in range(len(keys)):
            word = keys[i]
            index = parameters.find(word, start_index)
            if index != -1:
                start_index = index + len(word)
                next_word_index = parameters.find(keys[i + 1], start_index) if i < len(keys) - 1 else len(parameters)
                chunks.append(parameters[start_index:next_word_index].strip())
                start_index = next_word_index

        # Add remaining text
        if start_index < len(parameters):
            chunks.append(parameters[start_index:].strip())

        dictionary = dict(zip(KEY, chunks))
        dictionary['Other'] = f"Steps: {dictionary['Other']}"
        dictionary.pop('Steps', {})

        return dictionary


# Create a dictionary to hold the text boxes for each key
text_boxes = {}
for i, key in enumerate(KEY):
    # Create a label for the key
    label = tk.Label(root, text=key, anchor='e')
    label.grid(row=i, column=1, sticky='w')

    # Create a text box for the value
    text_box = tk.Text(root, height=3, width=80, wrap='word')
    text_box.grid(row=i, column=2, columnspan=2)

    # Add scrollbars to the text box
    scrollbar = tk.Scrollbar(root, command=text_box.yview)
    scrollbar.grid(row=i, column=4, sticky='e')
    text_box.config(yscrollcommand=scrollbar.set)

    text_boxes[key] = text_box

# Create a label to display the loaded image
image_label = tk.Label(root)
image_label.grid(row=1, column=5, rowspan=4)

# Create a button to load an image
button = tk.Button(root, text="Load Image", command=lambda: open_png_metadata())
button.grid(row=4, column=1)

# # Create a text field to save the prompt
save_field = tk.Text(root, height=1, width=20)
save_field.grid(row=4, column=2, columnspan=2, sticky='w')

# Create a button to save the prompt
save_button = tk.Button(root, text="Save Prompt", command=save_button)
save_button.grid(row=4, column=2, sticky='e')

# Create the dropdown menu
style_names = get_style_names()
dropdown_label = tk.Label(root, text="Select a prompt:")
dropdown_label.grid(row=5, column=1, sticky='w')
dropdown_var = tk.StringVar(root)
dropdown_var.set(style_names[0])
dropdown_menu = tk.OptionMenu(root, dropdown_var, *style_names, command=update_text_widgets)
dropdown_menu.grid(row=5, column=2, sticky='w')

# Delete style
delete_style_button = tk.Button(root, text="Delete Selected Prompt", command=delete_style_button)
delete_style_button.grid(row=5, column=2, sticky='e')

root.mainloop()
