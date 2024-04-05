import sys
import queue
import tkinter as tk
import ttkbootstrap as ttk
import tkinter.scrolledtext as tkscrolled
from ttkbootstrap.dialogs.dialogs import Messagebox, MessageDialog
from tkinter import filedialog
from .markdown import SimpleMarkdownText
from .config import *
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .ui import App


class FfmpegErrorPage(ttk.Frame):
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(self, text=ffmpeg_missing_text, font=("Helvetica", 24)).pack(pady=20, padx=20)
        ttk.Button(self, text="Exit", command=self.exit, width=20, style="TButton").pack(pady=40, padx=10)

    def exit(self):
        sys.exit(1)


class ApiKeyPage(ttk.Frame):
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(self, text="Set OpenAI Api Key", font=("Helvetica", 24)).pack(pady=20, padx=20)
        self.api_key_entry = ttk.Entry(self)
        self.api_key_entry.pack()
        ttk.Button(self, text="Set", command=self.save_api_key, width=20, style="TButton").pack(pady=40, padx=10)
        ttk.Label(self, text=api_key_label_text).pack(pady=10, padx=5)
        self.master: 'App' = master

    def save_api_key(self):
        api_key = self.api_key_entry.get()
        if api_key is None or api_key == "":
            return
        try:
            self.master.summarize.set_api_key(api_key)
        except Exception as e:
            Messagebox.show_error(f"Error: {str(e)}", "Failed to set OpenAI api key", alert=True, width=200)
            return
        self.master.switch_frame(UploadRecordingPage)


class UploadRecordingPage(ttk.Frame):
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(self, text="Select Recording", font=("Helvetica", 24)).pack(pady=10)
        self.selector_btn = ttk.Button(self, text="Select File", command=self.select_file)
        self.selector_btn.pack(pady=10)
        self.language_var = tk.StringVar()
        ttk.Label(self, text="Recording Language").pack(padx=10, pady=5)
        ls = ttk.OptionMenu(self, self.language_var, "English", *whisper_languages.keys())
        ls.pack(padx=10, pady=5)
        ttk.Label(self, text=select_video_label_text).pack(pady=10, padx=5)
        self.spinner = tk.Label(self, text="", font=("Helvetica", 14))
        self.spinner.pack(pady=5, padx=5)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)
        self.progress['value'] = 0
        self.master: 'App' = master
        self.file_path = ""

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            md = MessageDialog(
                f"Extracting transcript of file:\n{file_path}\nLanguage: {self.language_var.get()}",
                title="Confirm Selection",
                buttons=['Confirm:success', 'Cancel:secondary'],
                parent=self,
            )
            md.show()
            if md.result == "Confirm":
                self.file_confirmed(file_path)

    def file_confirmed(self, file_path: str):
        self.file_path = file_path
        self.selector_btn["state"] = "disabled"
        self.progress['value'] = 5
        self.master.language = self.language_var.get()
        # signature: convert(file_path, language=sel_lan, chunk=secs | default])
        task_item = ("convert", (self.file_path,), {"language": whisper_languages[self.master.language]})
        self.master.task_queue.put(task_item)
        self.after(200, lambda: self.process_queue(0))

    def process_queue(self, counter):
        spinner = ['|', '/', '-', '\\']
        self.spinner.config(text=f"Processing {spinner[counter % len(spinner)]}")
        try:
            result = self.master.result_queue.get_nowait()
        except queue.Empty:
            self.after(200, lambda: self.process_queue(counter + 1))
            return
        if isinstance(result, int):
            self.progress['value'] = result
            self.after(200, lambda: self.process_queue(counter + 1))
        elif isinstance(result, str):
            self.master.transcript = result
            self.master.switch_frame(SummarisePage)
        else:
            self.progress['value'] = 0
            self.selector_btn["state"] = "normal"
            self.spinner.config(text="")
            self.file_path = ""
            if isinstance(result, Exception):
                Messagebox.show_error(f"Creating Transcript of {self.file_path} failed.\nError: {result}", "Failed to create transcript", alert=True,
                              width=200)
            else:
                Messagebox.show_error(f"Creating Transcript of {self.file_path} failed.\nError: Internal Server Error",
                                      "Failed to create transcript",
                                      alert=True,
                                      width=200)


class SummarisePage(ttk.Frame):
    def __init__(self, master: 'App'):
        super().__init__(master)
        ttk.Label(self, text="Write a prompt to instruct GPT-4 to summarize the transcript", font=("Helvetica", 24)).pack(pady=10)
        self.prompt_entry = tkscrolled.ScrolledText(self, width=40, height=20, wrap="word")
        self.prompt_entry.pack(expand=True, fill="both")

        self.sum_btn = ttk.Button(self, text="Summarise", command=self.start_summarization, style="TButton")
        self.sum_btn.pack(pady=10)
        self.spinner = tk.Label(self, text="", font=("Helvetica", 14))
        self.spinner.pack(pady=5, padx=5)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)
        self.prompts = ttk.Text(self, width=40, height=20, wrap="word")
        self.prompts.insert(1.0, master.prompt_history + prompt_template_text)
        self.prompts.pack(expand=True, fill="both")
        self.prompts.configure(state="disabled", inactiveselectbackground=self.prompts.cget("selectbackground"))
        self.master: 'App' = master

    def start_summarization(self):
        input = self.prompt_entry.get("1.0", "end-1c")
        if input is None or len(input) == 0:
            return
        self.sum_btn["state"] = "disabled"
        self.master.prompt_history = input
        self.progress['value'] = 0
        # signature: summarize(prompt:str, language:str = "English")
        task_item = ("summarize", (input,), {"language": self.master.language})
        self.master.task_queue.put(task_item)
        self.after(200, lambda: self.process_queue(0))

    def process_queue(self, counter):
        spinner = ['|', '/', '-', '\\']
        self.spinner.config(text=f"Processing {spinner[counter % len(spinner)]}")
        try:
            result = self.master.result_queue.get_nowait()
        except queue.Empty:
            self.after(200, lambda: self.process_queue(counter + 1))
            self.progress["value"] = min(90, ((counter // 5) * 100) // 90)
            return
        if isinstance(result, str):
            self.master.result = result
            self.master.switch_frame(ShowSummaryPage)
        else:
            self.progress['value'] = 0
            self.sum_btn["state"] = "normal"
            self.spinner.config(text="")
            if isinstance(result, Exception):
                Messagebox.show_error(f"Error: {str(result)}", "Failed to create summary", alert=True, width=200)
            else:
                Messagebox.show_error(f"Internal Server Error: {type(result)} rxd from queue", "Failed to create summary", alert=True, width=200)
            self.master.switch_frame(SummarisePage)


class ShowSummaryPage(ttk.Frame):
    def __init__(self, master: 'App'):
        super().__init__(master)
        self.text = SimpleMarkdownText(master, width=45, height=22, font=tk.font.Font(family="Helvetica", size=12))
        self.text.pack(fill="both", expand=True)
        self.text.insert_markdown(master.result)
        buttons = ttk.Frame(self)
        buttons.pack(pady=10)
        ttk.Button(buttons, text="New Summary", command=self.back, style='Outline.TButton').pack(side="left", padx=5)
        self.clipboard_btn = ttk.Button(buttons, text="Copy to Clipboard", command=self.copy_to_clipboard, style="TButton")
        self.clipboard_btn.pack(side="left", padx=5)
        ttk.Button(buttons, text="Save to File", command=self.save_file, style="TButton").pack(padx=5)
        self.copied_label = tk.Label(self, text="")
        self.copied_label.pack(pady=10)
        self.master: 'App' = master

    def save_file(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension="md")
        if filename is None:
            return
        with open(filename, 'w', encoding='utf8') as f:
            f.write(self.master.result)
        Messagebox.ok(f"File {filename} Saved Successfully", width=200)
        self.text.pack_forget()
        self.master.switch_frame(SummarisePage)

    def copy_to_clipboard(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.master.result)
        self.copied_label.config(text="Text copied to clipboard!")
        self.after(2000, lambda: self.copied_label.config(text=""))

    def back(self):
        self.text.pack_forget()
        self.master.switch_frame(SummarisePage)
