import tkinter as tk
from enum import Enum
from PIL import Image, ImageTk
from pandas import DataFrame
from pathlib import Path
from tkinter import filedialog, messagebox

class VisualTheme(Enum):
    DARK_MODE = 0
    LIGHT_MODE = 1

class DisappearingTextApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        
        self.BG_COLOR: str = "white"
        
        self.changes_id: str = ""
        self.visual_theme: Enum = VisualTheme.LIGHT_MODE
        self.timer_duration = 3 * 60
        
        
        self.geometry("500x500")
        # self.resizable(width=False,height=False)
        self.title("Disappearing Text Writing App")
        self.config(padx=10, pady=10, bg=self.BG_COLOR)
        
        self.gray_crescent_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(Path("images/gray-crescent-moon.png").as_posix()).resize(size=(30,30)))
        self.black_crescent_image: ImageTk.PhotoImage = ImageTk.PhotoImage(Image.open(Path("images/black-crescent-moon.png").as_posix()).resize(size=(30,30)))
        
        self.__set_up_widgets()
        
        self.mainloop()
    
    def __set_up_widgets(self) -> None:
        self.moon_icon = tk.Button(image=self.gray_crescent_image, borderwidth=0, bg="white", command=self.change_theme)
        self.moon_icon.grid(column=1,row=1, sticky="NW", pady=5)
        
        self.moon_icon.bind("<Enter>", lambda _: self.moon_icon.config(image=self.black_crescent_image))
        self.moon_icon.bind("<Leave>", lambda _: self.moon_icon.config(image=self.gray_crescent_image))
        
        self.text_widget = tk.Text(width=60, height=28, bd=0, fg="gray", 
                                   highlightbackground="black", highlightcolor="black", highlightthickness=2)
        self.__add_default_text()
        self.text_widget.grid(column=1, columnspan=2, row=2, sticky="we", padx=0)
        
        self.text_widget.bind("<FocusIn>", lambda _: self.__clear_default_text())
        self.text_widget.bind("<FocusOut>", lambda _: self.__add_default_text())
        self.text_widget.bind("<Key>", self.detect_changes)
        self.text_widget.bind("<Control-a>", lambda _: "break")
        self.text_widget.bind("<Control-c>", lambda _: "break")
        self.text_widget.bind("<Control-v>", lambda _: "break")
        
        self.timer_label = tk.Label(text="05:30", bg="white", font=("Helvetica", 16, "bold"))
        self.timer_label.grid(column=2, row=1, sticky="NE", pady=5)
        
        self.__start_timer(self.timer_duration)
        
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(1, weight=1, minsize=50)
        self.rowconfigure(2, weight=1)
        
    
    def __clear_default_text(self) -> None:
        if self.text_widget.get(1.0,"1.end") == "Start typing...":
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.config(fg="black")
    
    def __add_default_text(self):
        if not self.text_widget.get(1.0,"1.end"):
            self.text_widget.insert(1.0, "Start typing...")
            self.text_widget.config(fg="gray")
    
    def __start_timer(self, count: int) -> None:
        self.timer_id = self.after(1000, self.__start_timer, count - 1)
        
        minutes: str = str(count // 60)
        seconds: str = str(count % 60)
        
        if int(minutes) < 10:
            minutes = "0" + minutes
        
        if int(seconds) < 10:
            seconds = "0" + seconds
        
        self.timer_label.configure(text = f"{minutes}:{seconds}")
                
        if count == 0:
            self.after_cancel(self.timer_id)
            self.save_changes()
            return       
    
    def detect_changes(self, event) -> None:
        
        if self.changes_id:
            self.text_widget.config(fg="black")
            self.after_cancel(self.changes_id)
        
        if event.char:
            self.process_changes(seconds=5)
    
    def process_changes(self, seconds) -> None:
        
        if seconds == 0:
            self.text_widget.delete("1.0", tk.END)
            self.after_cancel(self.timer_id)
            self.__start_timer(self.timer_duration)
            return
        elif seconds == 1:
            self.text_widget.config(fg="#e64c66")
            self.update_idletasks()
        elif seconds == 2:
            self.text_widget.config(fg="#730013")
            
        self.changes_id = self.after(1000, lambda: self.process_changes(seconds - 1))
    
    def save_changes(self) -> None:
        FILETYPES = (
            ("Text documents (*.txt)", "*.txt"),
            ("All files (*.*)", "*.*")
        )
        
        user_text = self.text_widget.get("1.0", "end-1c")
        
        filepath = filedialog.asksaveasfilename(filetypes=FILETYPES, defaultextension=".txt")
        filepath = Path(filepath).as_posix()
        
        try:
            with open(filepath, mode="w") as file:
                file.write(user_text)
        except Exception as error:
            messagebox.showerror(title="Error while writing to file", message=f"ERROR: {error}.\nYour text will be copied to the clipboard instead.")
            DataFrame([f"{user_text}"]).to_clipboard(index=False, header=False, excel=False)
        else:
            messagebox.showinfo(title="Success", message=f"Writing to {filepath} was successful.")
        self.destroy()
    
    def change_theme(self):
        match self.visual_theme:
            case VisualTheme.LIGHT_MODE:
                self.config(bg="black")
                self.moon_icon.config(bg='black')
                self.timer_label.config(bg='black', fg='white')
                self.text_widget.config(highlightbackground='gray', highlightcolor='gray')
                
                self.visual_theme = VisualTheme.DARK_MODE
            case VisualTheme.DARK_MODE:
                self.config(bg="white")
                self.moon_icon.config(bg='white')
                self.timer_label.config(bg='white', fg='black')
                self.text_widget.config(highlightbackground='black', highlightcolor='black')
                
                self.visual_theme = VisualTheme.LIGHT_MODE
            case _:
                messagebox.showerror(title='Error', message=f'Visual theme is not one of LIGHT_MODE or DARK_MODE')
        
        
    
            