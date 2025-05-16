import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, colorchooser, simpledialog, ttk
from tkinter.ttk import Style, Notebook
import pandas as pd
import json
import cssutils
from bs4 import BeautifulSoup
import re
import os

class QuizApp:
    def __init__(self, root):
        self.root = root
        root.title("Quiz Editor")
        root.geometry("1200x700")
        style = Style()
        style.theme_use("clam")

        self.notebook = Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.categories = []
        self.questions = {}
        self.current_category = None
        self.current_question_index = None
        self.general_id = ""
        self.quiz_id = ""
        self.loading_question = False  # Flag to prevent unnecessary saving during loading

        self.create_main_tab()
        self.create_fast_tab()
        self.create_export_tab()

    def create_main_tab(self):
        main_frame = tk.Frame(self.notebook)
        self.notebook.add(main_frame, text="Categories and Questions")

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        category_frame = tk.Frame(left_frame)
        category_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(category_frame, text="Categories").pack()
        self.category_listbox = tk.Listbox(category_frame, height=10, width=40)
        self.category_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.category_listbox.bind('<<ListboxSelect>>', self.load_category)

        category_button_frame = tk.Frame(category_frame)
        category_button_frame.pack(fill=tk.X)
        tk.Button(category_button_frame, text="Add Category", command=self.add_category).pack(side=tk.LEFT, padx=5)
        tk.Button(category_button_frame, text="Remove Category", command=self.remove_category).pack(side=tk.LEFT, padx=5)
        tk.Button(category_button_frame, text="Upload Excel", command=self.upload_file).pack(side=tk.LEFT, padx=5)
        tk.Button(category_button_frame, text="Save as Excel", command=self.save_to_excel).pack(side=tk.LEFT, padx=5)

        tk.Label(left_frame, text="Questions").pack()
        self.question_listbox = tk.Listbox(left_frame, width=40)
        self.question_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.question_listbox.bind('<<ListboxSelect>>', self.load_question)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(right_frame, text="Question").pack()
        self.question_text = scrolledtext.ScrolledText(right_frame, height=5, width=60)
        self.question_text.pack(fill=tk.X, expand=True, pady=5)
        self.question_text.bind('<<Modified>>', self.on_content_modified)

        tk.Label(right_frame, text="Answers").pack()
        self.answers_frame = tk.Frame(right_frame)
        self.answers_frame.pack(fill=tk.X, expand=True, pady=5)
        self.answer_widgets = []
        self.add_answer()

        tk.Label(right_frame, text="Correct Answer Index").pack()
        self.correct_answer_index = tk.Entry(right_frame)
        self.correct_answer_index.pack(fill=tk.X, expand=True, pady=5)
        self.correct_answer_index.bind('<KeyRelease>', self.on_content_modified)

        tk.Label(right_frame, text="Notes").pack()
        self.notes_text = scrolledtext.ScrolledText(right_frame, height=3, width=60)
        self.notes_text.pack(fill=tk.X, expand=True, pady=5)
        self.notes_text.bind('<<Modified>>', self.on_content_modified)

        tk.Label(right_frame, text="Keywords").pack()
        self.keywords_text = tk.Entry(right_frame)
        self.keywords_text.pack(fill=tk.X, expand=True, pady=5)
        self.keywords_text.bind('<KeyRelease>', self.on_content_modified)

        tk.Label(right_frame, text="Tags").pack()
        self.tags_text = tk.Entry(right_frame)
        self.tags_text.pack(fill=tk.X, expand=True, pady=5)
        self.tags_text.bind('<KeyRelease>', self.on_content_modified)

        button_frame = tk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="Add Image", command=self.add_image_main_tab).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Color Text", command=self.color_text).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Highlight Text", command=self.highlight_text).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Add Answer", command=self.add_answer).pack(side=tk.LEFT, padx=5)

    def create_fast_tab(self):
        fast_frame = tk.Frame(self.notebook)
        self.notebook.add(fast_frame, text="Fast")

        # Split the fast_frame into left and right frames
        left_frame = tk.Frame(fast_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(fast_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons at the top of the left frame
        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="Add Image Entry", command=self.add_image_entry_set).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Add Note Entry", command=self.add_note_entry_set).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Bulk Add Notes", command=self.bulk_add_notes).pack(side=tk.LEFT, padx=5)

        # Left frame content
        # Create a canvas and scrollbar for the fast tab
        canvas = tk.Canvas(left_frame)
        scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
        self.fast_content_frame = tk.Frame(canvas)

        self.fast_content_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.fast_content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # List to hold all image entry sets
        self.image_entry_sets = []
        self.add_image_entry_set()

        # List to hold all note entry sets
        self.note_entry_sets = []

        # Right frame content - Log table
        tk.Label(right_frame, text="Image Log").pack()
        self.log_frame = tk.Frame(right_frame)
        self.log_frame.pack(fill=tk.BOTH, expand=True)

        # Header for the log table
        headers = ["Q No.", "Type", "Choice No.", "Image Path", "Action"]
        for idx, header in enumerate(headers):
            label = tk.Label(self.log_frame, text=header, relief=tk.RIDGE, width=12)
            label.grid(row=0, column=idx, sticky="nsew")

        self.log_entries = []

    def add_image_entry_set(self):
        frame = tk.Frame(self.fast_content_frame, bd=2, relief=tk.RIDGE, padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Label(frame, text="Question Number:").grid(row=0, column=0, sticky="w")
        question_number_entry = tk.Entry(frame, width=10)
        question_number_entry.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(frame, text="Type:").grid(row=0, column=2, sticky="w")
        type_var = tk.StringVar(value='q')
        type_menu = ttk.Combobox(frame, textvariable=type_var, values=['q', 'c', 'n'], width=5)
        type_menu.grid(row=0, column=3, sticky="w", padx=5)

        choice_number_entry = None

        def on_type_change(event=None):
            nonlocal choice_number_entry
            if type_var.get() == 'c':
                if not choice_number_entry:
                    tk.Label(frame, text="Choice Number:").grid(row=0, column=4, sticky="w")
                    choice_number_entry = tk.Entry(frame, width=10)
                    choice_number_entry.grid(row=0, column=5, sticky="w", padx=5)
            else:
                if choice_number_entry:
                    label = frame.grid_slaves(row=0, column=4)[0]
                    label.destroy()
                    choice_number_entry.destroy()
                    choice_number_entry = None

        type_menu.bind('<<ComboboxSelected>>', on_type_change)

        add_image_button = tk.Button(frame, text="Add Image", command=lambda: self.add_image_fast_tab(question_number_entry, type_var, choice_number_entry))
        add_image_button.grid(row=0, column=6, sticky="w", padx=5)

        self.image_entry_sets.append({
            'frame': frame,
            'question_number_entry': question_number_entry,
            'type_var': type_var,
            'choice_number_entry': choice_number_entry
        })

    def add_note_entry_set(self):
        frame = tk.Frame(self.fast_content_frame, bd=2, relief=tk.RIDGE, padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        tk.Label(frame, text="Question Number:").grid(row=0, column=0, sticky="w")
        question_number_entry = tk.Entry(frame, width=10)
        question_number_entry.grid(row=0, column=1, sticky="w", padx=5)

        add_note_button = tk.Button(frame, text="Add Note", command=lambda: self.add_note_fast_tab(question_number_entry))
        add_note_button.grid(row=0, column=2, sticky="w", padx=5)

        self.note_entry_sets.append({
            'frame': frame,
            'question_number_entry': question_number_entry,
        })

    def create_export_tab(self):
        export_frame = tk.Frame(self.notebook)
        self.notebook.add(export_frame, text="Export")
        
        tk.Label(export_frame, text="General ID:").pack(pady=5)
        self.general_id_entry = tk.Entry(export_frame)
        self.general_id_entry.pack(pady=5)
        
        tk.Label(export_frame, text="Quiz ID:").pack(pady=5)
        self.quiz_id_entry = tk.Entry(export_frame)
        self.quiz_id_entry.pack(pady=5)
        
        tk.Button(export_frame, text="Export to JS", command=self.export_to_js).pack(pady=20)

    def add_category(self):
        category = simpledialog.askstring("Add Category", "Enter new category name:")
        if category and category not in self.categories:
            self.categories.append(category)
            self.questions[category] = []
            self.category_listbox.insert(tk.END, category)

    def remove_category(self):
        selection = self.category_listbox.curselection()
        if selection:
            category = self.categories[selection[0]]
            del self.questions[category]
            self.categories.remove(category)
            self.category_listbox.delete(selection)
            self.question_listbox.delete(0, tk.END)
            self.current_category = None
            self.current_question_index = None

    def add_answer(self):
        new_answer_text = scrolledtext.ScrolledText(self.answers_frame, height=2, width=60)
        new_answer_text.pack(fill=tk.X, expand=True, pady=2)
        new_answer_text.bind('<<Modified>>', self.on_content_modified)
        self.answer_widgets.append(new_answer_text)

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            self.load_excel(file_path)

    def load_excel(self, file_path):
        df = pd.read_excel(file_path)
        self.categories = list(df['category'].unique())
        self.questions = {}
        unique_id = 1

        for category in self.categories:
            category_questions = df[df['category'] == category].to_dict('records')
            for question in category_questions:
                question['unique_id'] = unique_id
                unique_id += 1
                question['keywords'] = str(question.get('keywords', '')).split(',')
                question['tags'] = str(question.get('tags', '')).split(',')
                answers = [str(question.get(f'answer{j}', '')) for j in range(1, 7) if pd.notna(question.get(f'answer{j}', None))]
                question['answers'] = answers
                if 'answerindex' in question and pd.notna(question['answerindex']):
                    question['answerindex'] = str(int(question['answerindex']) - 1)
                else:
                    question['answerindex'] = '0'

            self.questions[category] = category_questions

        self.category_listbox.delete(0, tk.END)
        for category in self.categories:
            self.category_listbox.insert(tk.END, category)

    def load_category(self, evt):
        if self.current_category is not None and self.current_question_index is not None:
            self.save_current_question()

        selection = self.category_listbox.curselection()
        if selection:
            self.current_category = self.categories[selection[0]]
            self.current_question_index = None
            self.question_listbox.delete(0, tk.END)
            for question in self.questions[self.current_category]:
                self.question_listbox.insert(tk.END, question['questiontext'])

    def load_question(self, evt=None):
        if self.current_category is not None and self.current_question_index is not None:
            self.save_current_question()

        if evt:
            selection = self.question_listbox.curselection()
            if selection:
                self.current_question_index = selection[0]
        if self.current_question_index is not None:
            self.loading_question = True  # Start loading
            question_data = self.questions[self.current_category][self.current_question_index]

            self.question_text.delete('1.0', tk.END)
            self.question_text.insert(tk.END, question_data['questiontext'])
            self.question_text.edit_modified(False)

            for widget in self.answer_widgets:
                widget.pack_forget()
                widget.destroy()
            self.answer_widgets.clear()

            for answer in question_data.get('answers', []):
                self.add_answer()
                self.answer_widgets[-1].insert(tk.END, answer)
                self.answer_widgets[-1].edit_modified(False)

            self.correct_answer_index.delete(0, tk.END)
            self.correct_answer_index.insert(tk.END, str(int(question_data.get('answerindex', '0')) + 1))

            self.notes_text.delete('1.0', tk.END)
            self.notes_text.insert(tk.END, question_data.get('note', ''))
            self.notes_text.edit_modified(False)

            self.keywords_text.delete(0, tk.END)
            self.keywords_text.insert(tk.END, ', '.join(question_data.get('keywords', [])))

            self.tags_text.delete(0, tk.END)
            self.tags_text.insert(tk.END, ', '.join(question_data.get('tags', [])))

            self.loading_question = False  # Finish loading

    def save_current_question(self):
        if self.current_category is not None and self.current_question_index is not None:
            question_data = self.questions[self.current_category][self.current_question_index]
            question_data['questiontext'] = self.question_text.get("1.0", tk.END).strip()
            question_data['note'] = self.notes_text.get("1.0", tk.END).strip()
            question_data['answers'] = [answer_text.get("1.0", tk.END).strip() for answer_text in self.answer_widgets]
            try:
                question_data['answerindex'] = str(int(self.correct_answer_index.get()) - 1)
            except ValueError:
                question_data['answerindex'] = '0'
            question_data['keywords'] = [k.strip() for k in self.keywords_text.get().split(',')]
            question_data['tags'] = [t.strip() for t in self.tags_text.get().split(',')]

    def on_content_modified(self, event=None):
        if self.loading_question:
            return
        widget = event.widget
        if hasattr(widget, 'edit_modified') and widget.edit_modified():
            self.save_current_question()
            widget.edit_modified(False)

    def add_image_main_tab(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_paths:
            base_dir = os.getcwd()
            for file_path in file_paths:
                relative_path = os.path.relpath(file_path, base_dir)
                relative_path = relative_path.replace('\\', '/')
                img_tag = f'$$IMG$${relative_path}$$/IMG$$'
                try:
                    widget = self.root.focus_get()
                    if isinstance(widget, scrolledtext.ScrolledText) or isinstance(widget, tk.Entry):
                        widget.insert(tk.INSERT, img_tag)
                        if isinstance(widget, scrolledtext.ScrolledText):
                            widget.edit_modified(True)
                        else:
                            self.on_content_modified()
                            # For Entry widgets, manually trigger save
                            self.save_current_question()
                        self.show_temporary_message("Image added successfully.")
                except AttributeError:
                    pass

    def color_text(self):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            self.apply_style_to_selection(f'<span style="color:{color_code}">', '</span>')

    def highlight_text(self):
        highlight_color = colorchooser.askcolor(title="Choose highlight color")[1]
        if highlight_color:
            self.apply_style_to_selection(f'<span style="background-color:{highlight_color}">', '</span>')

    def insert_at_cursor(self, text):
        try:
            self.root.focus_get().insert(tk.INSERT, text)
        except AttributeError:
            pass

    def apply_style_to_selection(self, start_tag, end_tag):
        try:
            widget = self.root.focus_get()
            if isinstance(widget, scrolledtext.ScrolledText):
                selected_text = widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                widget.insert(tk.INSERT, f'{start_tag}{selected_text}{end_tag}')
                widget.edit_modified(True)
        except tk.TclError:
            messagebox.showinfo("Error", "No text selected")

    def export_to_js(self):
        self.save_current_question()
        self.general_id = self.general_id_entry.get()
        self.quiz_id = self.quiz_id_entry.get()
        
        data = []

        for category in self.categories:
            for question_data in self.questions[category]:
                question_id = question_data['unique_id']
                question_text = question_data['questiontext']
                question_text = self.process_html(question_text)
                correct_answers = [int(question_data['answerindex'])] if question_data.get('answerindex') else []
                note_text = question_data.get('note', '')
                note_text = self.process_html(note_text)
                keywords = question_data.get('keywords', [])
                tags = question_data.get('tags', [])

                question_item = {
                    "id": f"{self.general_id}_{self.quiz_id}_{question_id}",
                    "generalId": self.general_id,
                    "quizId": self.quiz_id,
                    "category": category,
                    "text": self.format_text_for_js(question_text),
                    "choices": [self.format_text_for_js(self.process_html(a)) for a in question_data['answers']],
                    "correctAnswers": correct_answers,
                    "keywords": [k.strip() for k in keywords],
                    "tags": [t.strip() for t in tags],
                    "note": self.format_text_for_js(note_text),
                    "userAnswer": [],
                    "showingNote": False
                }
                data.append(question_item)

        filename = f"{self.general_id}-{self.quiz_id}.js"
        directory = filedialog.askdirectory()
        if directory:
            file_path = os.path.join(directory, filename)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write("// questions.js\n\n")
                file.write(f"window.generalId = \"{self.general_id}\";\n")
                file.write(f"window.quizId = \"{self.quiz_id}\";\n\n")
                file.write(f"window.initialQuestions = {json.dumps(data, indent=2, ensure_ascii=False)};\n\n")
                file.write("if (!window.allQuestions) window.allQuestions = [];\n")
                file.write("window.allQuestions = window.allQuestions.concat(window.initialQuestions);\n")
            messagebox.showinfo("Success", f"Quiz exported to JS successfully as {filename}")
        else:
            messagebox.showinfo("Cancelled", "Export cancelled.")

    def format_text_for_js(self, text):
        text = text.replace('\n', '<br>')
        text = text.replace('$$IMG$$', '<img src="').replace('$$/IMG$$', '">')
        text = re.sub(r'data-dir="(.*?)"', r'dir="\1"', text)
        text = re.sub(r'data-align="(.*?)"', r'align="\1"', text)
        return text

    def parse_css(self, css_text):
        css_rules = {}
        parser = cssutils.CSSParser()
        sheet = parser.parseString(css_text)
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                selector = rule.selectorText
                # Skip selectors with pseudo-elements
                if '::' in selector:
                    continue
                styles = {prop.name: prop.value for prop in rule.style}
                css_rules[selector] = styles
        return css_rules

    def apply_styles(self, tag, styles):
        current_style = tag.get('style', '')
        style_dict = cssutils.parseStyle(current_style)
        for prop, value in styles.items():
            style_dict[prop] = value
        tag['style'] = style_dict.cssText

    def process_html(self, input_html):
        soup = BeautifulSoup(input_html, 'html.parser')
        style_tags = soup.find_all('style')
        css_rules = {}
        for style_tag in style_tags:
            css_text = style_tag.string
            if css_text:
                css_rules.update(self.parse_css(css_text))

        for selector, styles in css_rules.items():
            elements = soup.select(selector)
            for element in elements:
                self.apply_styles(element, styles)

        for tag in soup.find_all(True):
            if 'dir' in tag.attrs:
                tag['data-dir'] = tag['dir']
            if 'align' in tag.attrs:
                tag['data-align'] = tag['align']

        for tag in soup(['head', 'meta', 'title', 'link', 'script', 'style']):
            tag.decompose()

        body_contents = soup.body.contents if soup.body else soup.contents

        output_html = ''.join(str(content) for content in body_contents)

        return output_html

    def save_to_excel(self):
        self.save_current_question()
        data_list = []
        for category in self.categories:
            for question in self.questions[category]:
                question_data = {}
                question_data['category'] = category
                question_data['questiontext'] = question.get('questiontext', '')
                question_data['note'] = question.get('note', '')
                question_data['keywords'] = ', '.join(question.get('keywords', []))
                question_data['tags'] = ', '.join(question.get('tags', []))
                question_data['answerindex'] = str(int(question.get('answerindex', '0')) + 1)
                # Add answers
                answers = question.get('answers', [])
                for i, answer in enumerate(answers):
                    question_data[f'answer{i+1}'] = answer
                data_list.append(question_data)
        df = pd.DataFrame(data_list)
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Success", f"Quiz saved to Excel successfully as {file_path}")

    def get_question_by_global_number(self, number):
        counter = 1
        for category in self.categories:
            questions_in_category = self.questions[category]
            for idx, question in enumerate(questions_in_category):
                if counter == number:
                    return category, idx
                counter += 1
        return None, None  # Number not found

    def add_image_fast_tab(self, question_number_entry, type_var, choice_number_entry):
        try:
            question_number = int(question_number_entry.get())
            field_type = type_var.get()
            choice_number = int(choice_number_entry.get()) if choice_number_entry and choice_number_entry.get() else None
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")
            return

        category, idx = self.get_question_by_global_number(question_number)
        if category is None:
            messagebox.showerror("Error", "Question number not found.")
            return

        # Save any unsaved changes in the main tab
        if self.current_category == category and self.current_question_index == idx:
            self.save_current_question()

        file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_paths:
            base_dir = os.getcwd()
            question_data = self.questions[category][idx]
            for file_path in file_paths:
                relative_path = os.path.relpath(file_path, base_dir)
                relative_path = relative_path.replace('\\', '/')
                img_tag = f'$$IMG$${relative_path}$$/IMG$$'

                if field_type == 'q':
                    question_data['questiontext'] += img_tag
                elif field_type == 'n':
                    if 'note' in question_data:
                        question_data['note'] += img_tag
                    else:
                        question_data['note'] = img_tag
                elif field_type == 'c':
                    if choice_number is None or choice_number < 1 or choice_number > len(question_data['answers']):
                        messagebox.showerror("Error", "Invalid choice number.")
                        return
                    question_data['answers'][choice_number - 1] += img_tag
                else:
                    messagebox.showerror("Error", "Invalid type selected.")
                    return

                # Log the addition in the log table
                self.add_log_entry(question_number, field_type, choice_number, relative_path, category, idx, img_tag)

            # Update the question in main tab if it's loaded
            if self.current_category == category and self.current_question_index == idx:
                self.load_question()

            self.show_temporary_message("Image(s) added successfully.")

    def add_note_fast_tab(self, question_number_entry):
        try:
            question_number = int(question_number_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid question number.")
            return

        category, idx = self.get_question_by_global_number(question_number)
        if category is None:
            messagebox.showerror("Error", "Question number not found.")
            return

        # Save any unsaved changes in the main tab
        if self.current_category == category and self.current_question_index == idx:
            self.save_current_question()

        # Open a new window for note entry
        note_window = tk.Toplevel(self.root)
        note_window.title("Add Note")

        tk.Label(note_window, text="Enter Note:").pack(pady=5)
        note_text_widget = scrolledtext.ScrolledText(note_window, width=80, height=20)
        note_text_widget.pack(padx=10, pady=5)
        # Optionally pre-fill the existing note
        existing_note = self.questions[category][idx].get('note', '')
        note_text_widget.insert("1.0", existing_note)

        def save_note():
            note_text = note_text_widget.get("1.0", tk.END).strip()
            self.add_note_to_question(category, idx, note_text)
            note_window.destroy()
            self.show_temporary_message("Note added successfully.")

        # Binding Enter key to save_note function
        def on_return_key(event):
            save_note()
            return 'break'  # Prevent default behavior

        note_text_widget.bind('<Return>', on_return_key)

        tk.Button(note_window, text="Save Note", command=save_note).pack(pady=10)

    def add_note_to_question(self, category, idx, note_text, append=False):
        question_data = self.questions[category][idx]

        if append and 'note' in question_data:
            question_data['note'] += note_text
        else:
            question_data['note'] = note_text

        # Update the question in main tab if it's loaded
        if self.current_category == category and self.current_question_index == idx:
            self.load_question()

    def bulk_add_notes(self):
        # Ask the user to select files
        file_paths = filedialog.askopenfilenames(filetypes=[("Text Files", "*.txt;*.rtf;*.html;*.htm")])
        if not file_paths:
            return

        # Ask the user to input the question number range
        range_window = tk.Toplevel(self.root)
        range_window.title("Select Question Range")

        tk.Label(range_window, text="Start Question Number:").grid(row=0, column=0, padx=5, pady=5)
        start_number_entry = tk.Entry(range_window)
        start_number_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(range_window, text="End Question Number:").grid(row=1, column=0, padx=5, pady=5)
        end_number_entry = tk.Entry(range_window)
        end_number_entry.grid(row=1, column=1, padx=5, pady=5)

        def add_notes():
            try:
                start_number = int(start_number_entry.get())
                end_number = int(end_number_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid question numbers.")
                return

            if end_number < start_number:
                messagebox.showerror("Error", "End number must be greater than or equal to start number.")
                return

            num_questions = end_number - start_number + 1
            num_files = len(file_paths)

            if num_questions != num_files:
                messagebox.showerror("Error", "Number of selected files does not match the number of questions in the range.")
                return

            # Proceed to add notes
            question_number = start_number
            for file_path in file_paths:
                category, idx = self.get_question_by_global_number(question_number)
                if category is None:
                    messagebox.showerror("Error", f"Question number {question_number} not found.")
                    return

                # Read the file content
                with open(file_path, 'r', encoding='utf-8') as file:
                    note_text = file.read()

                # Save any unsaved changes in the main tab
                if self.current_category == category and self.current_question_index == idx:
                    self.save_current_question()

                # Append the note to the question
                self.add_note_to_question(category, idx, note_text, append=True)  # Set append=True

                question_number += 1

            range_window.destroy()
            self.show_temporary_message("Notes added successfully.")

        tk.Button(range_window, text="Add Notes", command=add_notes).grid(row=2, column=0, columnspan=2, padx=5, pady=10)

    def add_log_entry(self, q_number, field_type, choice_number, image_path, category, idx, img_tag):
        row = len(self.log_entries) + 1

        # Question Number
        q_label = tk.Label(self.log_frame, text=str(q_number), relief=tk.RIDGE)
        q_label.grid(row=row, column=0, sticky="nsew")

        # Type
        type_label = tk.Label(self.log_frame, text=field_type, relief=tk.RIDGE)
        type_label.grid(row=row, column=1, sticky="nsew")

        # Choice Number
        choice_label = tk.Label(self.log_frame, text=str(choice_number) if choice_number else "", relief=tk.RIDGE)
        choice_label.grid(row=row, column=2, sticky="nsew")

        # Image Path
        path_label = tk.Label(self.log_frame, text=image_path, relief=tk.RIDGE, wraplength=150)
        path_label.grid(row=row, column=3, sticky="nsew")

        # Delete Button
        delete_button = tk.Button(self.log_frame, text="X", command=lambda: self.delete_image_log_entry(entry))
        delete_button.grid(row=row, column=4, sticky="nsew")

        entry = {
            'row': row,
            'q_number': q_number,
            'field_type': field_type,
            'choice_number': choice_number,
            'image_path': image_path,
            'category': category,
            'idx': idx,
            'img_tag': img_tag,
            'widgets': [q_label, type_label, choice_label, path_label, delete_button]
        }

        self.log_entries.append(entry)

    def delete_image_log_entry(self, entry):
        question_data = self.questions[entry['category']][entry['idx']]
        img_tag = entry['img_tag']

        if entry['field_type'] == 'q':
            question_data['questiontext'] = question_data['questiontext'].replace(img_tag, '')
        elif entry['field_type'] == 'n':
            question_data['note'] = question_data['note'].replace(img_tag, '')
        elif entry['field_type'] == 'c':
            idx = entry['choice_number'] - 1
            question_data['answers'][idx] = question_data['answers'][idx].replace(img_tag, '')

        # Remove the log entry widgets
        for widget in entry['widgets']:
            widget.destroy()

        # Remove entry from log_entries list
        self.log_entries.remove(entry)

        # Update the subsequent rows in the log table
        for e in self.log_entries:
            if e['row'] > entry['row']:
                e['row'] -= 1
                for widget in e['widgets']:
                    r, c = widget.grid_info()['row'], widget.grid_info()['column']
                    widget.grid(row=r-1, column=c)

        # Update the question in main tab if it's loaded
        if self.current_category == entry['category'] and self.current_question_index == entry['idx']:
            self.load_question()

        self.show_temporary_message("Image removed successfully.")

    def show_temporary_message(self, message):
        notification = tk.Label(self.root, text=message, bg="lightgreen")
        notification.place(relx=0.5, rely=0.5, anchor='center')
        self.root.after(2000, notification.destroy)  # Destroy after 2 seconds

    def get_global_question_number(self, category, idx):
        counter = 1
        for cat in self.categories:
            questions_in_category = self.questions[cat]
            for i, question in enumerate(questions_in_category):
                if cat == category and i == idx:
                    return counter
                counter += 1
        return None


root = tk.Tk()
app = QuizApp(root)
root.mainloop()