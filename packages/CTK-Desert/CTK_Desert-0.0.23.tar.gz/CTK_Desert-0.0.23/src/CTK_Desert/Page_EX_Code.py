import customtkinter as ctk
from CTK_Desert.Page_base_model import Page_BM
from CTK_Desert.Theme import *
from CTK_Desert.utils import hvr_clr_g

# don't ever pack the frame, it will be packed in the Tab_Page_Frame.py
class CUNAME__C(Page_BM):
    def __init__(self, window, THEFrame, parent):
        super().__init__(window, parent)
        self.menu_page_frame = THEFrame
        self.frame = self.Scrollable_frame # Parent of all children in this page
        self.frame.configure(fg_color = (hvr_clr_g(LIGHT_MODE["background"], "l"), hvr_clr_g(DARK_MODE["background"], "d")))
        self.mode = ctk.get_appearance_mode()

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

