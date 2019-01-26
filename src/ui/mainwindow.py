import tkinter as tk
from tkinter import filedialog

class MainWindow(tk.Frame):

  def __init__(self, root = None):
    self._root = root
    if self._root is None:
      self._root = tk.Tk()
    tk.Frame.__init__(self, self._root)
    self.init_ui()
    self.pack()
    self.generate_function = None

  def init_ui(self):
    self.label_input = tk.Label(self, text="Input Directory or File")
    self.label_input.pack()
    self.text_input = tk.Text(self, height=1)
    self.text_input.pack()
    self.button_input = tk.Button(self, text="open", command=self.select_input)
    self.button_input.pack()

    self.label_output = tk.Label(self, text="CustomSongs directory")
    self.label_output.pack()
    self.text_output = tk.Text(self, height=1)
    self.text_output.pack()
    self.button_input = tk.Button(self, text="open", command=self.select_output)
    self.button_input.pack()

    self.button_generate = tk.Button(self, text="generate", command=self.on_generate)
    self.button_generate.pack()

    self.label_msgs = tk.Label(self, text="")
    self.label_msgs.pack()


  def select_input(self):
    inp = self.text_input.get('1.0', tk.END).strip()
    path = filedialog.askopenfilename(initialdir = inp, title = "Select song", filetypes = (("ogg","*.ogg"),("all files","*.*")))
    if path is not None and len(path) > 0:
      self.text_input.delete('1.0', tk.END)
      self.text_input.insert(tk.END, path)

  def select_output(self):
    outp = self.text_output.get('1.0', tk.END).strip()
    path = filedialog.askdirectory(initialdir = outp, title = "Select CustomSongs dir")
    if path is not None and len(path) > 0:
      self.text_output.delete('1.0', tk.END)
      self.text_output.insert(tk.END, path)

  def on_generate(self):
    if self.generate_function is not None:
      inp = self.text_input.get('1.0', tk.END).strip()
      outp = self.text_output.get('1.0', tk.END).strip()
      self.button_generate['state'] = tk.DISABLED
      msgs = self.generate_function(inp, outp)
      self.button_generate['state'] = tk.NORMAL
      self.label_msgs['text'] = ''
      for msg in msgs:
        self.label_msgs['text'] += msg + '\n'





