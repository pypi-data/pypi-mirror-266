import textwrap
from PIL import Image
import customtkinter as ctk
from .Theme import *
from .utils import hvr_clr_g

class C_Widgits():
    def __init__(self, page_class, parent):
        self.page = page_class
        self.parent = parent
        self.c = 1 # multiplier for y padding
        
    def section(self, Title=None):
        section_frame = ctk.CTkFrame(self.parent, fg_color= "transparent")

        if Title != "" and Title != None:
            section_label = ctk.CTkLabel(section_frame, text=f"{Title}", font=(FONT_B, 25), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="w")
            section_label.pack(side="top", fill="x", padx=20)

        ops_frame = ctk.CTkFrame(section_frame, fg_color= "transparent")
        ops_frame.pack(fill="x", padx=20, pady=10)

        section_frame.pack(fill="x", pady=10)
        return ops_frame
    
###############################################################################################################################################################################################

    def section_unit(self, section, title : str = "", widget : str =None, command: callable =None, values : list =None, default : str =None):
        """
        Adds a unit to a section with specified parameters.

        Parameters:
        - section (ctk.Frame): The parent widget to which the unit will be added.
        - title (str, optional): The title of the unit.
        - widget (str, optional): The type of widget to be used in the unit. 
            - Supported values: "combobox", "button", "checkbox", "entry", "switch".
        - command (callable, optional): The command to be executed when the widget is interacted with.
        - values (list, optional): A list of values to populate a combobox widget.
        - default: The default value for the widget.
            - treated as the text for a button widget.

        Returns:
        - ctk.Frame: The frame containing the unit.

        You can get the value of the widget using the gval method of the returned frame.
        """
                
        unit_parent = section
        unit_frame = ctk.CTkFrame(unit_parent, fg_color= "transparent")

        unit_label = ctk.CTkLabel(unit_frame, text=f"{title}", font=(FONT, 20))
        unit_label.pack(side="left", fill="x", padx=20, pady=10)

        if widget == "combobox" or widget == "ComboBox":
            unit_option = ctk.CTkComboBox(unit_frame, font=(FONT, 15), values = values, dropdown_font=(FONT, 15), state="readonly", command=command)
            unit_option.set(f"{default}")
            unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if widget == "button" or widget == "Button":
            unit_option = ctk.CTkButton(unit_frame, text=f"{'' if default == None else default}", font=(FONT, 15), command=command, fg_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), hover_color=(hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)))
            unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if widget == "checkbox" or widget == "CheckBox":
            unit_option = ctk.CTkCheckBox(unit_frame, text="", command=command, fg_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), hover_color=(hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)), onvalue=True, offvalue=False,)
            if default != None:
                unit_option.configure(variable=default) 
            unit_option.pack(side="right", fill="x", pady=10)

        if widget == "entry" or widget == "Entry":
            unit_option = ctk.CTkEntry(unit_frame, font=(FONT, 15), fg_color="transparent", placeholder_text=f"{default}", placeholder_text_color=(LIGHT_MODE["text"], DARK_MODE["text"]))
            # unit_option.insert(0, f"{default}")
            unit_option.pack(side="right", fill="x", padx=20, pady=10)

        if widget == "switch" or widget == "Switch":
            unit_option = ctk.CTkSwitch(unit_frame, command=command, fg_color=(hvr_clr_g(LIGHT_MODE["background"], "l", 85), hvr_clr_g(DARK_MODE["background"], "d", 85)), progress_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), onvalue=True, offvalue=False, text="", bg_color="transparent", border_color="transparent")
            if default != None:
                unit_option.configure(variable=default) 
            unit_option.pack(side="right", fill="x", pady=10)

        unit_frame.pack(fill="x")

        def gval():
            if widget != None:
                return unit_option.get()
            return None
        unit_frame.gval = gval

        try:
            self.page.update_size_BM()
        except:
            pass
        return unit_frame
    
###############################################################################################################################################################################################

    def add_tab(self, section, text=None, image=None, size=None, image_size=250): # (frame >> frame_template, image input is of a normal image)
        if image != None:        
            im = Image.open(image)
            w, h = im.size[0],im.size[1]
            r = w/h
            s = (image_size, int(image_size/r))
            im_ctk = ctk.CTkImage(im, size=s)
                    
        if size == "l":
            self.large(section, text, im_ctk)
        elif size == "s":
            self.small(section, text, im_ctk)
        try:
            self.page.update_size_BM()
        except:
            pass

    # Type num 1 (Ready to use)
    def Label_func(self, parent_f):          
        l_widget = ctk.CTkLabel(parent_f, text="No Recent projects", font=(FONT, 20), fg_color="transparent", text_color=(LIGHT_MODE["text"], DARK_MODE["text"]), anchor="center")
        l_widget.pack(fill="x", padx=20, pady=10*self.c, expand=True)

    # Type num 2 (Not done yet)
    def large(self, parent_f, text, image):  
        tab_cont = ctk.CTkFrame(parent_f, fg_color="transparent", height=300, width=self.parent.winfo_width())

        tabs_f = ctk.CTkButton(tab_cont, fg_color=(LIGHT_MODE["primary"], DARK_MODE["primary"]), height=400, width=350, 
                               text=f"{text}", image=image, compound="top", )
        tabs_f.pack(padx=20, pady=10*self.c)
        
        tab_cont.pack(expand=True, fill="both")

    # Type num 3 (Ready to use)
    def small(self, parent_f, text, image):  
        tab_cont = ctk.CTkFrame(parent_f, fg_color="transparent", height=300, width=self.parent.winfo_width())

        tab_img = ctk.CTkButton(tab_cont, fg_color="transparent", text="", image=image, hover_color=(hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        tab_img.pack(padx=20, pady=10*self.c, side="left")

        tab_cont.update()
        tit_f   = ctk.CTkFrame(tab_cont, fg_color="transparent",)
        newtext = textwrap.shorten(text, 50)
        tab_tit = ctk.CTkLabel(tit_f, fg_color="transparent", text=f"{newtext}", font=(FONT, 20), anchor="w")
        tab_tit.pack(fill = "both", expand = True)
        tit_f.pack(pady=10*self.c, fill = "x", expand = True, side="left")

        add_btn = ctk.CTkButton(tab_cont, width=30, height=30, text="+", font=(FONT_B, 30),  
                                fg_color=(LIGHT_MODE["accent"], DARK_MODE["accent"]), 
                                hover_color=(hvr_clr_g(LIGHT_MODE["accent"], "l", 20), hvr_clr_g(DARK_MODE["accent"], "d", 20)), 
                                command= lambda : None)                 # command= lambda num = self.image_count.queue[0]: self.add_image_btn_command(num) #
        add_btn.place(relx=0.975, rely=0.5, anchor="e")

        tab_cont.pack(expand=True, fill="both", pady=10)

        White_line = ctk.CTkFrame(parent_f, fg_color=(DARK_MODE["background"], LIGHT_MODE["background"]), height=2)
        White_line.pack(fill="x", expand=True, padx = 20)


