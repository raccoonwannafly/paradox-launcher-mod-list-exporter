import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import os
import re

class ModExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paradox Mod List Extractor")
        self.root.geometry("600x500")

        # Data storage
        self.enabled_mods_paths = []
        self.mod_folder_path = ""
        self.extracted_mods = [] # List of tuples (Name, ID)

        # --- GUI Layout ---

        # Top Frame: Controls
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10)

        self.btn_load = tk.Button(top_frame, text="1. Load dlc_load.json", command=self.load_json, width=20, bg="#dddddd")
        self.btn_load.pack(side=tk.LEFT, padx=5)

        self.lbl_status = tk.Label(top_frame, text="Waiting for file...", fg="gray")
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        # Middle Frame: Results
        text_frame = tk.Frame(root)
        text_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.result_area = scrolledtext.ScrolledText(text_frame, state='disabled', font=("Consolas", 10))
        self.result_area.pack(expand=True, fill=tk.BOTH)

        # Bottom Frame: Export
        bottom_frame = tk.Frame(root, pady=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10)

        self.btn_export = tk.Button(bottom_frame, text="Export List to Text File", command=self.export_list, state=tk.DISABLED, bg="#4CAF50", fg="white")
        self.btn_export.pack(side=tk.RIGHT, padx=5)

    def log(self, message):
        """Helper to write to the text area"""
        self.result_area.config(state='normal')
        self.result_area.insert(tk.END, message + "\n")
        self.result_area.see(tk.END)
        self.result_area.config(state='disabled')

    def clear_log(self):
        self.result_area.config(state='normal')
        self.result_area.delete(1.0, tk.END)
        self.result_area.config(state='disabled')

    def load_json(self):
        file_path = filedialog.askopenfilename(
            title="Select dlc_load.json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        self.clear_log()
        self.log(f"Processing: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.enabled_mods_paths = data.get("enabled_mods", [])
            
            count = len(self.enabled_mods_paths)
            self.log(f"Found {count} enabled mods in JSON.")
            self.lbl_status.config(text=f"Loaded {count} mods", fg="blue")
            
            # Attempt to auto-detect mod directory
            # Usually dlc_load.json is in .../Paradox Interactive/GameName/
            # And mods are in .../Paradox Interactive/GameName/mod/
            game_root = os.path.dirname(file_path)
            potential_mod_dir = os.path.join(game_root, "mod")

            if os.path.exists(potential_mod_dir):
                self.mod_folder_path = potential_mod_dir
                self.log(f"Auto-detected mod directory: {self.mod_folder_path}")
                self.process_mods()
            else:
                self.log("Could not auto-detect 'mod' folder.")
                messagebox.showinfo("Locate Mod Folder", "I couldn't find the 'mod' folder automatically.\nPlease select your 'mod' folder manually.")
                self.manual_select_mod_folder()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse JSON: {e}")

    def manual_select_mod_folder(self):
        folder = filedialog.askdirectory(title="Select your Paradox 'mod' folder")
        if folder:
            self.mod_folder_path = folder
            self.process_mods()
        else:
            self.log("Operation cancelled. Cannot extract names without mod folder.")

    def get_mod_name(self, mod_file_path):
        """Reads a .mod file and extracts name="X" """
        if not os.path.exists(mod_file_path):
            return None
        
        try:
            with open(mod_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Regex to find name="Something"
                # Matches name="Something" or name = "Something"
                match = re.search(r'name\s*=\s*"(.*?)"', content)
                if match:
                    return match.group(1)
        except:
            return None
        return None

    def process_mods(self):
        self.log("\n--- Extracting Names ---\n")
        self.extracted_mods = []

        for rel_path in self.enabled_mods_paths:
            # rel_path is like "mod/12345.mod"
            # We need to strip "mod/" if it exists to get the filename
            filename = os.path.basename(rel_path)
            
            # Full path on disk
            full_path = os.path.join(self.mod_folder_path, filename)
            
            name = self.get_mod_name(full_path)
            
            if name:
                self.extracted_mods.append(name)
                self.log(f"[OK] {name}")
            else:
                self.extracted_mods.append(f"Unknown Mod ({filename})")
                self.log(f"[MISSING] Could not read name for {filename}")

        self.btn_export.config(state=tk.NORMAL)
        self.log(f"\nDone! Extracted {len(self.extracted_mods)} names.")

    def export_list(self):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Save Mod List"
        )
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    # Write simple list
                    f.write("Enabled Mods List:\n")
                    f.write("==================\n")
                    for mod in self.extracted_mods:
                        f.write(f"{mod}\n")
                messagebox.showinfo("Success", "Mod list saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModExtractorApp(root)
    root.mainloop()