import customtkinter as ctk
from .Page_base_model import Page_BM
from .Theme import *
from .utils import hvr_clr_g
from .Widgits import C_Widgits
from .Theme import *
import os
from PIL import Image
import numpy as np
from tkinter import filedialog as fd

# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class Workspace(Page_BM):
    def __init__(self, window, THEFrame, parent):
        super().__init__(window, parent)
        self.menu_page_frame = THEFrame
        self.frame = self.Scrollable_frame # Parent of all children in this page
        self.frame.configure(fg_color = (hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.mode = ctk.get_appearance_mode()
        self.openable = True
        self.pages_path = ""
        self.icon_names = ["_d_s", "_d", "_l_s", "_l"]
        self.icon_path = None

        self.ws_label = ctk.CTkLabel(self.frame, text="New Page", font=(FONT_B, 40))
        self.ws_label.pack(fill="x", padx=20, pady=20)

        self.c_wgts = C_Widgits(self, self.frame)
        
        self.first_sec     =    self.c_wgts.section()
        self.f_page_name   =    self.c_wgts.section_unit(self.first_sec, title="Page Name", widget="entry", default="Pick a name")
        self.f_parent_type =    self.c_wgts.section_unit(self.first_sec, title="Parent Type", widget="combobox", values=["Panel Frame", "Section Frame"], )
        self.icon_path_btn =    self.c_wgts.section_unit(self.first_sec, title="Icon Path", widget="button", default="Pick an icon", command= self.get_icon_path)
        self.f_confirmation=    self.c_wgts.section_unit(self.first_sec, title="", widget="button", default="Create Page", command= self.create_page)
        

    def on_start(self):
        self.tool_menu()
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")

    def on_pick(self):
        self.tools_f.place(relx=0.5, rely=0.5, anchor="center")

    def on_update(self):
        pass

    def tool_menu(self):
        self.tool_p_f = self.menu_page_frame.apps_frame
        self.tools_f = ctk.CTkFrame(self.tool_p_f, fg_color="transparent")

    def get_icon_path(self):
        filetypes = ( ('images', '*.png'), ('All files', '*.*') )
        f = fd.askopenfile(filetypes=filetypes, title="Pick an icon")
        self.icon_path = f.name if f else None

    def create_page(self):
        file_name = self.f_page_name.gval()         # get field data (page name)
        if not (file_name == "" or self.icon_path == None):

            with open (os.path.join(os.path.dirname(__file__), "Page_EX_Code.py"), 'r') as file:    # open the example code file
                data = file.read()
            #######################################################################
            data = data.replace("CUNAME__C", file_name)  
            
            module_names = [file[:-3] for file in os.listdir(self.pages_path) if file.endswith('.py') and file != '__init__.py']       # replace the class name with the page name
            data = data.replace('"PAGE_Num__": 0', f'"PAGE_Num__": {len(module_names)+1}')                                             # replace the class name with the page name
            
            #######################################################################
            with open (os.path.join(self.pages_path, f"{file_name}.py"), 'w') as file:              # create a new file with the page name
                file.write(data)

            self.change_pixel_color(file_name) # get the image path from the dialog box, and the target color from Theme file

            self.menu_page_frame.new_page_constructor(file_name)        # Calling a func in the tab page frame to add the new page to the application
        
    def change_pixel_color(self, file_name):
        # Open the image and convert it to RGBA mode
        img = Image.open(self.icon_path).convert("RGBA")

        # Convert the image to a NumPy array
        img_array = np.array(img)

        for i in self.icon_names:
            # Apply the target color to non-transparent pixels
            img_array[img_array[..., 3] != 0, :3] = ICONS[i]

            # Create a new image from the modified array
            modified_img = Image.fromarray(img_array, "RGBA")

            # Save the modified image
            modified_img.save(os.path.join(os.path.dirname(self.pages_path), "Images", f"{file_name.lower()}{i}.png"))
            
    