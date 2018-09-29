import os
import tkinter as tk
from tkinter import filedialog, messagebox, IntVar
from PIL import ImageTk, Image

from Config import *
from Patcher import Patcher

class Viewer:
    def __init__(self):
        self.index = None
        self.image_on = None  # stores the image to show on gui
        self.database = []
        self.setup()

    def setup(self):
        self.root = tk.Tk()
        self.root.title("labelview")
        self.root.state("iconic")
        # self.root.resizable(width=False, height=False)  # cannot change window size
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.f = 0.8  # the fraction of image region
        self.b = 0.3  # the fraction of button region
        

        # left side control panel
        self.control = tk.Frame(self.root, width=self.w*(1-self.f), height=self.h)
        self.control.grid(row=0, column=0)

        # button control panel
        # open single file
        open_f = tk.Button(self.control, text="open file", command=self.load_file)
        open_f.grid(row=0, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)
        # load single csv/xml corresponding to wsi file
        load_l = tk.Button(self.control, text="load csv/xml", command=self.load_labels)
        load_l.grid(row=0, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)

        # open directory
        open_d = tk.Button(self.control, text="open dir", command=self.load_files)
        open_d.grid(row=1, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)
        # set csv/xml directory
        load_ld = tk.Button(self.control, text="load csv/xml dir", command=self.load_labels_dir)
        load_ld.grid(row=1, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)

        # display file count
        self.n_count = tk.Label(self.control, text=".kfb/.tif count")
        self.n_count.grid(row=2, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)

        # display fname
        self.fname = tk.Label(self.control, text="XXXX.kfb/.tif")
        self.fname.grid(row=3, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)
        # display lname
        self.lname = tk.Label(self.control, text="XXXX.csv/.xml")
        self.lname.grid(row=3, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)

        # previous
        prev_b = tk.Button(self.control, text="previous", command=lambda: self.update(step=-1))
        prev_b.grid(row=4, column=0, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)
        # next
        next_b = tk.Button(self.control, text="next", command=lambda: self.update(step=1))
        next_b.grid(row=4, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)

        # checkbox control panel
        # checkbox hint
        c_hint = tk.Label(self.control, text="choose classes here:")
        c_hint.grid(row=5, column=0, columnspan=2, sticky=tk.E, ipady=5, padx=10, pady=10)
        # add confirm button
        conform = tk.Button(self.control, text="confirm", command=lambda: self.update())
        conform.grid(row=5, column=2, columnspan=2, sticky=tk.EW, ipady=5, padx=10, pady=10)
        # add checkboxes
        self.checkboxes = []
        for i, class_i in enumerate(CLASSES):
            var = IntVar(value=1)
            chk = tk.Checkbutton(self.control, text=class_i, variable=var)
            if i < len(CLASSES)//2:
                chk.grid(row=6+i, column=1, columnspan=1, sticky=tk.W, ipady=5, padx=10, pady=2)
            else:
                chk.grid(row=6+i-len(CLASSES)//2, column=3, columnspan=1, sticky=tk.W, ipady=5, padx=10, pady=2)
            self.checkboxes.append(var)


        # right side image panel
        self.display = tk.Canvas(self.root, width=self.w*self.f, height=self.h)
        self.display.grid(row=0, column=1)


    def load_file(self):
        fname = filedialog.askopenfilename(filetypes=(("kfb files", "*.kfb"), ("tif files", "*.tif")))
        if not fname:
            messagebox.showinfo("warning", "no file choosed")
        else:
            self.index = 0
            del self.database
            self.database = []
            self.database.append({"basename":os.path.splitext(os.path.basename(fname))[0], "fname":fname, "lname":None})
            self.update_text()


    def load_files(self):
        file_dir = filedialog.askdirectory()
        if not file_dir:
            messagebox.showinfo("warning", "no directory choosed")
        else:
            self.index = None
            del self.database
            self.database = []
            fnames = os.listdir(file_dir)
            fnames.sort()
            for fname in fnames:
                if fname.endswith(".kfb") or fname.endswith(".tif"):
                    self.database.append({"basename":os.path.splitext(fname)[0], "fname":os.path.join(file_dir, fname), "lname":None})
            if not self.database:
                messagebox.showinfo("warning", "no kfb file exists")
            else:
                self.index = 0
                self.update_text()


    def load_labels(self):
        # if not self.database:
        #     messagebox.showinfo("error", "no kfb/tif file loaded")
        #     return
        lname = filedialog.askopenfilename(filetypes=(("csv files", "*.csv"), ("xml files", "*.xml")))
        if not lname:
            messagebox.showinfo("warning", "no file choosed")
        elif not self.database[self.index]["basename"] in os.path.basename(lname):
            messagebox.showinfo("warning", "label file does not match with kfb/tif file")
        else:
            self.database[self.index]["lname"] = lname
            self.update()


    def load_labels_dir(self):
        def nullify_lname():
            for item in self.database:
                item["lname"] = None
        def choose_matched():
            database_new = [item for item in self.database if item["lname"] is not None]
            del self.database
            self.database = database_new
            if self.database:
                self.index = 0
            else:
                self.index = None

        # if not self.database:
        #     messagebox.showinfo("error", "no kfb/tif file loaded")
        #     return
        file_dir = filedialog.askdirectory()
        if not file_dir:
            messagebox.showinfo("warning", "no directory choosed")
        else:
            nullify_lname()
            lnames = os.listdir(file_dir)
            lnames.sort()
            for lname in lnames:
                if lname.endswith(".csv") or lname.endswith(".xml"):
                    for i,item in enumerate(self.database):
                        if item["basename"] in os.path.basename(lname):
                            self.database[i]["lname"] = os.path.join(file_dir, lname)
                            break
            choose_matched()
            self.update()


    def load_thumbnail(self, i, classes):
        if i == len(self.database) or i < 0:
            messagebox.showinfo("warning", "already the end")
            return
        def resize(image, w, h):
            w0, h0 = image.size
            factor = min(w/w0, h/w0)
            return image.resize((int(w0*factor), int(h0*factor)))
        self.patcher = Patcher(self.database[i]["fname"], self.database[i]["lname"])
        image = self.patcher.patch_label(classes)
        image = ImageTk.PhotoImage(resize(image, self.w*self.f, self.h))
        self.image_on = image
        self.display.create_image(self.w*self.f/2, self.h*0.5, image=image)
        self.index = i


    def update_text(self):
        self.n_count.config(text="{} / {}".format(self.index+1, len(self.database)))
        self.fname.config(text=os.path.basename(self.database[self.index]["fname"]))
        if self.database[self.index]["lname"] is not None:
            self.lname.config(text=os.path.basename(self.database[self.index]["lname"]))
        else:
            self.lname.config(text="--------")


    def clear(self):
        self.n_count.config(text=".kfb/.tif count")
        self.fname.config(text=".kfb/.tif")
        self.lname.config(text=".csv/.xml")
        self.image_on = None
        self.database = []


    def update(self, step=0):
        if self.index is None:
            messagebox.showinfo("error", "there is no file/label matched")
            self.clear()
            return
        checked_classes = [CLASSES[i] for i,var in enumerate(self.checkboxes) if var.get()]
        self.load_thumbnail(self.index+step, checked_classes)
        self.update_text()


    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
