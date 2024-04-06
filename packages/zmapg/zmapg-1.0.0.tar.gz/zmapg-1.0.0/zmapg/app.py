import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
from ttkthemes import ThemedStyle
import threading
import time
import shutil  # Import shutil module for checking executables

class ZMapUI:

    def __init__(self, master):
        self.master = master
        master.title("ZMap UI")
        master.configure(bg="#1e1e1e")  # Set main window background color
        master.resizable(False, False)  # Disable window resizing

        # Check if ZMap is installed
        if not shutil.which('zmap'):
            tk.messagebox.showerror("ZMap Not Found", "ZMap is not installed on your system. Please install ZMap first.")
            master.destroy()  # Close the application
            return

        # Apply dark theme
        style = ThemedStyle(master)
        style.set_theme("equilux")

        # Prompt for sudo password
        subprocess.Popen(['sudo', '-v'])

        # Create menu
        self.menu_bar = tk.Menu(master, bg="black", fg="white", activebackground="gray", activeforeground="white")
        self.master.config(menu=self.menu_bar)
        
        # Add "File" menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False, bg="black", fg="white", activebackground="gray", activeforeground="white")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command=master.quit)

        # Add "Help" menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=False, bg="black", fg="white", activebackground="gray", activeforeground="white")
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About Developer", command=self.show_about_developer)

        # First row
        self.target_label = ttk.Label(master, text="Target IP:")
        self.target_entry = ttk.Entry(master)
        self.subnet_label = ttk.Label(master, text="Subnet:")
        self.subnet_combo = ttk.Combobox(master, values=["/23", "/24", "/22", "/16", "/8"])
        self.target_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.target_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.subnet_label.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.subnet_combo.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        # Second row
        self.scan_button = ttk.Button(master, text="Scan", command=self.start_scan)
        self.port_label = ttk.Label(master, text="Port Number:")
        self.port_entry = ttk.Entry(master)
        self.scan_button.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.port_label.grid(row=1, column=2, padx=10, pady=5, sticky="e")
        self.port_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

        # Third row
        self.results_label = ttk.Label(master, text="Results:")
        self.results_label.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="w")
        self.results_text = tk.Text(master, height=10)
        self.results_text.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        # Last row
        self.export_all_button = ttk.Button(master, text="Export All", command=self.export_all)
        self.export_all_button.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        # Taskbar
        self.progressbar = ttk.Progressbar(master, orient="horizontal", mode="indeterminate")
        self.progressbar.grid(row=5, column=0, columnspan=4, padx=10, pady=1, sticky="ew")

    def start_scan(self):
        # Check if port, target, and subnet are provided
        target_ip = self.target_entry.get()
        subnet = self.subnet_combo.get()
        port_number = self.port_entry.get()

        if not target_ip or not subnet or not port_number:
            # Display alert popup
            tk.messagebox.showwarning("Missing Information", "Please fill in all fields (Target IP, Subnet, Port Number) before starting the scan.")
            return

        self.progressbar.start()
        threading.Thread(target=self.scan).start()

    def scan(self):
        target_ip = self.target_entry.get()
        subnet = self.subnet_combo.get()
        port_number = self.port_entry.get()

        # Construct ZMap command
        zmap_command = f"sudo zmap -p {port_number} {target_ip}{subnet}"

        # Execute ZMap command
        try:
            output = subprocess.check_output(zmap_command, shell=True, universal_newlines=True)
            self.results_text.insert(tk.END, output)
        except subprocess.CalledProcessError as e:
            self.results_text.insert(tk.END, f"Error: {e.output}")

        # Stop progress bar after scanning is finished
        self.progressbar.stop()

    def export_selected(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")])
            if file_path:
                # Placeholder for export logic
                print("Exporting selected IPs to:", file_path)
        except Exception as e:
            print("Error occurred during export:", e)

    def export_all(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")])
            if file_path:
                with open(file_path, 'w') as file:
                    file.write(self.results_text.get("1.0", tk.END))
                print("Exporting all IPs to:", file_path)
        except Exception as e:
            print("Error occurred during export:", e)


    def show_about_developer(self):
        # Placeholder for showing information about the developer
        about_text = "Developer: @atiilla\nGithub: github.com/atiilla\nVersion: 1.0"
        tk.messagebox.showinfo("About Developer", about_text)

def main():
    root = tk.Tk()
    app = ZMapUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
