import numpy as np
import tkinter.filedialog
import tkinter as tk
from tkinter import ttk
import os, sys
sys.path.append(os.path.dirname(__file__))

from bias_names import BIAS_NAMES

class sliderGui():
    
    def __init__(self, model=None):
        
        self.model=None
        self.flag_loading_config=True
        
        map_file_path = os.path.join(os.path.dirname(__file__), "linear_fine_coarse_bias_map.npy")
        print(map_file_path)
        self.top_folder_path = "/".join(map_file_path.split("/")[:-2]) + "/"
        sys.path.append(self.top_folder_path)
        
        try:
            import dynapse1utils as ut
            self.utils = ut
        except ImportError:
            print("Failed to import Dynapse1Utils")
    
        
        self.linear_bias_map = np.load(map_file_path)
        
        self.main = tk.Tk()
        self.main.geometry("800x800+100+50")
        self.main.title("Samna bias gui")
        self.main.grid_rowconfigure(0, weight=1)
        self.main.columnconfigure(0, weight=1)
        self.frame_main = tk.Frame(self.main)
        self.frame_main.grid(sticky='news')
        
        self.slider_vars = {}
        self.spinbox_vars = {}
        
        self.sliders = {}
        self.spinboxes = {}
        
        self.label_vars = {}
        
        create_core_bias_block(self)
        
        self.model=model
        
        if self.model is None:
            print("WARNING: Gui running in debug mode!")
        else:
            config = self.model.get_configuration()
            
            for chip_id in range(4):
                for core_id in range(4):
                    self.param_group = config.chips[chip_id].cores[core_id].parameter_group
                                
                    for bias_name in BIAS_NAMES:
                        
                        value = self.param_group.get_linear_parameter(bias_name)
                        # print("Setting " + bias_name + " to " + str(value))
                        self.spinbox_vars[bias_name+":C%dC%d" %(chip_id, core_id)].set(value)
        
        
        self.flag_loading_config = False
        
        self.main.after(50, self.update_biases)
        self.main.mainloop()
        
    def slider_callback(self, var_name, idx, mode):
        
        var_name=var_name.split(':')[1]+":"+var_name.split(':')[2]
        bias_name=var_name.split(':')[0]
        chip_id=int(var_name.split(':')[1][1])
        core_id=int(var_name.split(':')[1][3])
        value = int(self.slider_vars[var_name].get())
        linear = int(self.linear_bias_map[value,2])
        coarse = int(self.linear_bias_map[value,0])
        fine = int(self.linear_bias_map[value,1])
        
        
        if self.spinbox_vars[var_name].get() != linear and self.flag_loading_config == False:
            self.spinbox_vars[var_name].set(linear)
            self.label_vars[var_name].set(str("(%d, %d)" % (coarse, fine)))
        
        # print(var_name, coarse, fine, linear)
        
        if self.model is not None and self.flag_loading_config == False:
            config = self.model.get_configuration()
            param_group = config.chips[chip_id].cores[core_id].parameter_group
            param_group.param_map[bias_name].fine_value = fine
            param_group.param_map[bias_name].coarse_value = coarse
            
            self.model.update_parameter_group(
                param_group, chip_id, core_id)
                    
    def spinbox_callback(self, var_name, idx, mode):
        
        var_name=var_name.split(':')[1]+":"+var_name.split(':')[2]
        linear = int(self.spinbox_vars[var_name].get())
        
        idx = (np.abs(self.linear_bias_map[:,2] - linear)).argmin()
        if self.slider_vars[var_name].get() != idx:
            self.slider_vars[var_name].set(idx)
        
        # print("spin callback")
        
        # for slider, spinbox in zip(self.scales, self.spinboxes):
        #     spinbox
        
    def _save_biases_to_file(self, filename : str):
        config = self.model.get_configuration()
        self.utils.save_parameters2txt_file(config, filename)
        print("Biases saved to: " + filename)

    def _load_biases_from_file(self, filename : str):
        self.utils.set_parameters_in_txt_file(self.model, filename)
        print("Biases loaded from: " + filename)
        
    def update_biases(self):
        
        self.flag_loading_config = True
        
        # print("Updating biases...")
        
        if self.model is None:
            print("WARNING: Gui running in debug mode!")
        else:
            config = self.model.get_configuration()
            
            for chip_id in range(4):
                for core_id in range(4):
                    self.param_group = config.chips[chip_id].cores[core_id].parameter_group
                                
                    for bias_name in BIAS_NAMES:
                        
                        value = self.param_group.get_linear_parameter(bias_name)
                        # print("Setting " + bias_name + " to " + str(value))
                        self.spinbox_vars[bias_name+":C%dC%d" %(chip_id, core_id)].set(value)
                        
        self.flag_loading_config = False
        
        self.main.after(500, self.update_biases)





def create_core_bias_block(gui):
    
    notebook = ttk.Notebook(gui.frame_main)
    gui.frame_main.grid_rowconfigure(0, weight=1)
    gui.frame_main.grid_rowconfigure(1, weight=100)
    gui.frame_main.grid_columnconfigure(0, weight=1)
    gui.frame_main.grid_columnconfigure(1, weight=5)
    gui.frame_main.grid_columnconfigure(2, weight=100)
    
    bias_filename = tk.StringVar(value="BIAS FILE: None", name="Label: bias filename")
    
    def open_file_dialog():
        filename = tk.filedialog.askopenfilename(title="Load Biases")
        bias_filename.set("BIAS FILE: " + filename)
        gui._load_biases_from_file(filename)
        
    def save_file_dialog():
        filename = tk.filedialog.asksaveasfilename(title="Save Biases")
        bias_filename.set("BIAS FILE: " + filename)
        gui._save_biases_to_file(filename)
    
    bias_filename_label = ttk.Label(gui.frame_main, textvariable=bias_filename)
    btn_save = ttk.Button(gui.frame_main, text = "Save biases", command=save_file_dialog)
    btn_load = ttk.Button(gui.frame_main, text = "Load biases", command=open_file_dialog)
    
    btn_load.grid(row=0, column=1, sticky='nw', ipady=6, ipadx=6)
    btn_save.grid(row=0, column=0, sticky='nw', ipady=6, ipadx=6)
    bias_filename_label.grid(row=0, column=2, columnspan=2, sticky='nw', ipady=6, ipadx=6)
    notebook.grid(row=1, column=0, columnspan=3, sticky='nesw')
    
    chip_frames = [ttk.Frame(notebook, width=800, height=800) for chip_id in range(4)]
    
    for chip_id in range(4):
        for core_id in range(4):
        
            frame_canvas = tk.Frame(chip_frames[chip_id])
            chip_frames[chip_id].grid_columnconfigure(core_id, weight=1)
            chip_frames[chip_id].grid_rowconfigure(0, weight=1)
            frame_canvas.grid(row=0, column=core_id, sticky='nsew')
            frame_canvas.grid_rowconfigure(0, weight=2)
            frame_canvas.grid_columnconfigure(0, weight=2)
            frame_canvas.grid_propagate(True)
            
            canvas_core = tk.Canvas(frame_canvas)
            canvas_core.grid(row=0, column=0, sticky='nsew')
            
            scroll_bar = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas_core.yview)
            scroll_bar.grid(row=0, column=1, sticky='nes')
            canvas_core.configure(yscrollcommand=scroll_bar.set)
            
            frame_core = tk.Frame(canvas_core)
            canvas_core.create_window(0, 0, window=frame_core, anchor='nw')
            
            for bias_name in BIAS_NAMES:
                create_single_bias_block(gui, frame_core, bias_name+":C"+str(chip_id)+"C"+str(core_id))
            
            frame_core.update_idletasks()
            
            frame_canvas.config(width=200,
                            height=2000)
            canvas_core.config(scrollregion=canvas_core.bbox("all"))
    
    for chip_id in range(4):
        notebook.add(chip_frames[chip_id], text= "Chip " + str(chip_id))

def create_single_bias_block(gui, parent, bias_name):
    
    var_slider = tk.IntVar(value=0, name="Slider:"+bias_name)
    var_slider.trace_add("write", gui.slider_callback)
    var_spinbox = tk.IntVar(value=0, name="Spinbox:"+bias_name)
    var_spinbox.trace_add("write", gui.spinbox_callback)
    var_label = tk.StringVar(value="(0, 0)", name="Label:"+bias_name)
    
    slider = tk.Scale(parent, from_=0, to_=len(gui.linear_bias_map)-1,
                                    orient=tk.HORIZONTAL,
                                    variable = var_slider,
                                    # command = gui.slider_command,
                                    length = 180,
                                    showvalue=0,
                                    label=bias_name.split(":")[0])
    
    spinbox = ttk.Spinbox(parent, from_=0, to_=2400000000, textvariable = var_spinbox, width = 10)
    
    label = tk.Label(parent, textvariable=var_label)
    
    gui.slider_vars[bias_name] = var_slider
    gui.spinbox_vars[bias_name] = var_spinbox
    gui.label_vars[bias_name] =  var_label
    gui.sliders[bias_name] = slider
    gui.spinboxes[bias_name] = spinbox
    
    slider.pack(fill = "both", expand=True)
    spinbox.pack(fill = "both", expand=True)
    label.pack(fill = "both", expand=True)
    
    # return var_slider, var_spinbox, slider, spinbox

def run_gui(model):
    
    gui = sliderGui(model)


def run_threaded_gui(model):
    
    import threading
    
    gui_thread = threading.Thread(target=run_gui,args=(model,))
    gui_thread.start()
    
    
        
if __name__ == '__main__':
    
    # import threading
    
    gui = sliderGui()
    # model = None
    # t1 = threading.Thread(target=run_gui, args=(model,))
    # t1.start()