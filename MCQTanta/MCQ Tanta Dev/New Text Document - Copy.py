import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import shutil
import subprocess
import tempfile
import threading
import queue

# --- Configuration ---
DEFAULT_APP_NAME = "MyWebApp"
DEFAULT_PACKAGE_ID = "com.example.mywebapp"
DEFAULT_OUTPUT_APK_NAME = "app-debug.apk"
CORDOVA_COMMAND = "cordova" # or the full path if not in PATH

class AppConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("HTML to APK Converter")
        master.geometry("700x550")

        self.html_folder_var = tk.StringVar()
        self.app_name_var = tk.StringVar(value=DEFAULT_APP_NAME)
        self.package_id_var = tk.StringVar(value=DEFAULT_PACKAGE_ID)
        self.output_apk_name_var = tk.StringVar(value=DEFAULT_OUTPUT_APK_NAME)
        self.output_dir_var = tk.StringVar(value=".")

        self.build_queue = queue.Queue()

        # --- UI Elements ---
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # HTML Folder
        ttk.Label(main_frame, text="HTML Folder (with index.html):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.html_folder_entry = ttk.Entry(main_frame, textvariable=self.html_folder_var, width=50)
        self.html_folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(main_frame, text="Browse...", command=self.browse_html_folder).grid(row=0, column=2, padx=5, pady=2)

        # App Name
        ttk.Label(main_frame, text="App Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.app_name_entry = ttk.Entry(main_frame, textvariable=self.app_name_var, width=50)
        self.app_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        # Package ID
        ttk.Label(main_frame, text="Package ID (e.g., com.company.app):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.package_id_entry = ttk.Entry(main_frame, textvariable=self.package_id_var, width=50)
        self.package_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        # Output APK Name
        ttk.Label(main_frame, text="Output APK Name:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.output_apk_name_entry = ttk.Entry(main_frame, textvariable=self.output_apk_name_var, width=50)
        self.output_apk_name_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)

        # Output Directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.output_dir_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(main_frame, text="Browse...", command=self.browse_output_dir).grid(row=4, column=2, padx=5, pady=2)

        # Generate Button
        self.generate_button = ttk.Button(main_frame, text="Generate APK", command=self.start_build_process)
        self.generate_button.grid(row=5, column=0, columnspan=3, pady=10)

        # Log Area
        ttk.Label(main_frame, text="Build Log:").grid(row=6, column=0, sticky=tk.W, pady=(10,0))
        self.log_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, width=80)
        self.log_area.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.log_area.configure(state='disabled') # Read-only

        main_frame.columnconfigure(1, weight=1) # Allow entry fields to expand
        main_frame.rowconfigure(7, weight=1) # Allow log area to expand

        self.check_prerequisites()
        self.master.after(100, self.process_queue)


    def check_prerequisites(self):
        if shutil.which(CORDOVA_COMMAND) is None:
            self.log_message(f"ERROR: '{CORDOVA_COMMAND}' command not found. "
                             "Please ensure Cordova CLI is installed and in your system PATH.\n"
                             "You also need Node.js, JDK, and Android SDK properly configured.", "error")
            messagebox.showerror("Prerequisite Missing",
                                 f"'{CORDOVA_COMMAND}' command not found. "
                                 "Please install Cordova CLI and ensure it's in your PATH. "
                                 "Also check Node.js, JDK, and Android SDK setup.")
            self.generate_button.config(state=tk.DISABLED)
        else:
            self.log_message("Cordova CLI found. Ensure JDK and Android SDK are also configured.", "info")

    def log_message(self, message, level="info"):
        self.log_area.configure(state='normal')
        if level == "error":
            self.log_area.insert(tk.END, f"ERROR: {message}\n", "error_tag")
        elif level == "warning":
            self.log_area.insert(tk.END, f"WARNING: {message}\n", "warning_tag")
        elif level == "success":
            self.log_area.insert(tk.END, f"SUCCESS: {message}\n", "success_tag")
        else:
            self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END) # Scroll to the end
        self.log_area.configure(state='disabled')
        self.log_area.tag_config("error_tag", foreground="red")
        self.log_area.tag_config("warning_tag", foreground="orange")
        self.log_area.tag_config("success_tag", foreground="green")


    def browse_html_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.html_folder_var.set(folder_selected)

    def browse_output_dir(self):
        dir_selected = filedialog.askdirectory()
        if dir_selected:
            self.output_dir_var.set(dir_selected)

    def process_queue(self):
        try:
            while True:
                message, level = self.build_queue.get_nowait()
                self.log_message(message, level)
        except queue.Empty:
            pass
        self.master.after(100, self.process_queue) # Check queue periodically

    def start_build_process(self):
        html_folder = self.html_folder_var.get()
        app_name = self.app_name_var.get()
        package_id = self.package_id_var.get()
        output_apk_name = self.output_apk_name_var.get()
        output_dir = self.output_dir_var.get()

        if not html_folder or not os.path.isdir(html_folder):
            messagebox.showerror("Error", "Please select a valid HTML folder.")
            return
        if not os.path.exists(os.path.join(html_folder, "index.html")):
            messagebox.showerror("Error", "'index.html' not found in the selected HTML folder.")
            return
        if not app_name or not package_id or not output_apk_name or not output_dir:
            messagebox.showerror("Error", "All fields must be filled.")
            return
        if not output_apk_name.lower().endswith(".apk"):
            output_apk_name += ".apk"
            self.output_apk_name_var.set(output_apk_name)


        self.log_area.configure(state='normal')
        self.log_area.delete('1.0', tk.END) # Clear previous logs
        self.log_area.configure(state='disabled')

        self.log_message("Starting APK generation process...", "info")
        self.generate_button.config(state=tk.DISABLED)

        # Run build in a separate thread to keep GUI responsive
        build_thread = threading.Thread(target=self._build_apk_thread,
                                        args=(html_folder, app_name, package_id, output_apk_name, output_dir),
                                        daemon=True)
        build_thread.start()

    def _run_command_in_thread(self, cmd_list, working_dir=None, error_message="Command failed"):
        self.build_queue.put((f"\nRunning: {' '.join(cmd_list)}" + (f" in {working_dir}" if working_dir else ""), "info"))
        try:
            process = subprocess.Popen(cmd_list, cwd=working_dir,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, encoding='utf-8', errors='replace',
                                       shell=os.name == 'nt') # shell=True on Windows for cordova.cmd

            # Stream stdout
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    if line.strip(): # Avoid empty lines cluttering the log too much
                        self.build_queue.put((line.strip(), "info"))
                process.stdout.close()

            # Stream stderr
            stderr_output = []
            if process.stderr:
                for line in iter(process.stderr.readline, ''):
                    if line.strip():
                        stderr_output.append(line.strip())
                        self.build_queue.put((line.strip(), "warning")) # Treat stderr as warning initially
                process.stderr.close()

            process.wait() # Wait for the process to complete

            if process.returncode != 0:
                # If there was significant stderr, ensure it's marked as an error
                if stderr_output:
                    self.build_queue.put(("\n--- STDERR ---", "error"))
                    for line in stderr_output:
                         self.build_queue.put((line, "error"))
                self.build_queue.put((f"{error_message}. Exit code: {process.returncode}", "error"))
                raise RuntimeError(f"{error_message}. Exit code: {process.returncode}")
            else:
                self.build_queue.put(("Command successful.", "info"))
            return True
        except FileNotFoundError:
            self.build_queue.put((f"ERROR: Command '{cmd_list[0]}' not found. Is it installed and in your PATH?", "error"))
            raise
        except Exception as e:
            self.build_queue.put((f"An error occurred: {e}", "error"))
            raise

    def _build_apk_thread(self, html_folder_abs, app_name, package_id, output_apk_name, output_dir_abs):
        final_apk_path = os.path.join(os.path.abspath(output_dir_abs), output_apk_name)

        self.build_queue.put((f"HTML Source: {html_folder_abs}", "info"))
        self.build_queue.put((f"App Name: {app_name}", "info"))
        self.build_queue.put((f"Package ID: {package_id}", "info"))
        self.build_queue.put((f"Output APK: {final_apk_path}", "info"))

        with tempfile.TemporaryDirectory(prefix="cordova_build_") as temp_build_dir:
            self.build_queue.put((f"Using temporary build directory: {temp_build_dir}", "info"))
            cordova_project_path = os.path.join(temp_build_dir, "MyCordovaApp")

            try:
                # 1. Create Cordova Project
                self._run_command_in_thread(
                    [CORDOVA_COMMAND, "create", cordova_project_path, package_id, app_name],
                    working_dir=temp_build_dir,
                    error_message="Failed to create Cordova project"
                )

                # 2. Add Android Platform
                self._run_command_in_thread(
                    [CORDOVA_COMMAND, "platform", "add", "android"],
                    working_dir=cordova_project_path,
                    error_message="Failed to add Android platform"
                )

                # 3. Replace default www content
                cordova_www_path = os.path.join(cordova_project_path, "www")
                self.build_queue.put((f"Removing default Cordova www folder: {cordova_www_path}", "info"))
                shutil.rmtree(cordova_www_path)
                self.build_queue.put((f"Copying your HTML content from {html_folder_abs} to {cordova_www_path}", "info"))
                shutil.copytree(html_folder_abs, cordova_www_path)

                # (Optional) Modify config.xml
                config_xml_path = os.path.join(cordova_project_path, "config.xml")
                try:
                    with open(config_xml_path, 'r+', encoding='utf-8') as f:
                        config_content = f.read()
                        if '<allow-navigation href="*" />' not in config_content:
                            config_content = config_content.replace(
                                '</widget>',
                                '    <allow-navigation href="*" />\n</widget>'
                            )
                        if '<preference name="InspectableWebview" value="true" />' not in config_content:
                             config_content = config_content.replace(
                                '</widget>',
                                '    <preference name="InspectableWebview" value="true" />\n</widget>'
                            )
                        f.seek(0)
                        f.write(config_content)
                        f.truncate()
                    self.build_queue.put(("Updated config.xml for navigation and WebView inspection.", "info"))
                except Exception as e:
                    self.build_queue.put((f"Warning: Could not modify config.xml: {e}", "warning"))

                # 4. Build Android (debug APK by default)
                self._run_command_in_thread(
                    [CORDOVA_COMMAND, "build", "android"],
                    working_dir=cordova_project_path,
                    error_message="Failed to build Android APK"
                )

                # 5. Locate and copy the APK
                apk_potential_paths = [
                    os.path.join(cordova_project_path, "platforms", "android", "app", "build", "outputs", "apk", "debug", "app-debug.apk"),
                    os.path.join(cordova_project_path, "platforms", "android", "build", "outputs", "apk", "app-debug.apk"), # Older Cordova
                ]
                built_apk_path = None
                for path_option in apk_potential_paths:
                    if os.path.exists(path_option):
                        built_apk_path = path_option
                        break
                
                if not built_apk_path:
                    self.build_queue.put(("Error: Could not find the built APK. Build output might have changed.", "error"))
                    self.build_queue.put((f"Look for .apk files under: {os.path.join(cordova_project_path, 'platforms', 'android')}", "info"))
                    raise RuntimeError("APK not found after build.")

                self.build_queue.put((f"APK built successfully at: {built_apk_path}", "info"))
                os.makedirs(os.path.abspath(output_dir_abs), exist_ok=True)
                shutil.copy(built_apk_path, final_apk_path)
                self.build_queue.put((f"APK copied to: {final_apk_path}", "success"))
                self.build_queue.put(("\n--- APK Generation Complete ---", "success"))
                self.build_queue.put(("You can now install this APK on an Android device or emulator.", "info"))
                self.build_queue.put(("Note: This is a DEBUG build. For Play Store, you'll need a release build with signing.", "info"))

            except Exception as e:
                self.build_queue.put((f"BUILD FAILED: {e}", "error"))
            finally:
                self.build_queue.put((f"Temporary build directory {temp_build_dir} will be cleaned up.", "info"))
                self.master.after(0, lambda: self.generate_button.config(state=tk.NORMAL)) # Re-enable button in main thread

if __name__ == "__main__":
    root = tk.Tk()
    app = AppConverterGUI(root)
    root.mainloop()