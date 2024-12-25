

import tkinter as tk
from tkinter import messagebox

from Constants import *
import configparser

# Example dictionary
default_settings  = {'Max P': 100, 'MaxDistortionHight': 0.2, 'DistortionGridSize': 1, 'Test Parm3': 10, 'Test Parm5': 3, 'Test Parm7': 20}

def load_settings(file_path, default_settings):
    """Load settings from an .ini file, updating the defaults with the file's values."""
    config = configparser.ConfigParser()
    config.read(file_path)

    # Start with default settings
    settings = default_settings.copy()

    # Update with values from the file
    if "Settings" in config:
        for key, value in config["Settings"].items():
            if key in settings:  # Only update keys that exist in the default dictionary
                try:
                    if isinstance(settings[key], int):
                        settings[key] = int(value)
                    elif isinstance(settings[key], float):
                        settings[key] = float(value)
                    else:
                        settings[key] = value  # Keep as string
                except ValueError:
                    print(f"Warning: Invalid value for '{key}' in {file_path}. Using default.")

    return settings

def save_settings(file_path, settings):
    """Save the dictionary back to the .ini file."""
    config = configparser.ConfigParser()
    config["Settings"] = {key: str(value) for key, value in settings.items()}
    with open(file_path, "w") as configfile:
        config.write(configfile)

def create_table_window():
    def confirm_changes():
        """Update the dictionary with the values from the text boxes and save to file."""
        for key, entry in entry_widgets.items():
            try:
                # Convert to the appropriate type based on the original value
                if isinstance(settings[key], int):
                    settings[key] = int(entry.get())
                elif isinstance(settings[key], float):
                    settings[key] = float(entry.get())
                else:
                    settings[key] = entry.get()  # Keep as string
            except ValueError:
                messagebox.showerror("Error", f"Invalid value for '{key}'. Please enter a valid {type(settings[key]).__name__}.")
                return
        save_settings("settings.ini", settings)
        messagebox.showinfo("Success", "Settings updated and saved successfully!")
        root.destroy()  # Close the window after confirmation

    root = tk.Tk()
    root.title("Settings Table")

    # Create a dictionary to store Entry widgets for easy access
    entry_widgets = {}

    # Add labels and text boxes for each key-value pair
    for row, (key, value) in enumerate(settings.items()):
        tk.Label(root, text=key).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        # Create an entry widget with the current value
        entry = tk.Entry(root, width=20)
        entry.insert(0, str(value))
        entry.grid(row=row, column=1, padx=10, pady=5)
        
        # Store the entry widget for later access
        entry_widgets[key] = entry

    # Add a confirmation button
    confirm_button = tk.Button(root, text="Confirm", command=confirm_changes)
    confirm_button.grid(row=len(settings), column=0, columnspan=2, pady=10)

    root.mainloop()


settings = load_settings("settings.ini", default_settings)
