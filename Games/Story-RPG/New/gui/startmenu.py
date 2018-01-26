from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.properties import *

from tools.tools import *
from tools.fbofloatlayout import FboFloatLayout

class StartMenu(ScreenManager):
    button_new = ObjectProperty()
    button_load = ObjectProperty()
    button_about = ObjectProperty()
    button_options = ObjectProperty()
    button_quit = ObjectProperty()
    gamesize = ListProperty([0,0])
    resolutions = ListProperty([(1024, 960),
    							(1366, 768),
    							(1290, 1080)])

    def setup(self, gamesize):
        self.current = "active"
        self.gamesize = gamesize
        for call in ("new", "load", "about", "options", "quit"):
        	eval("self.button_{}.bind(on_release=self._on_{})".format(call, call))

    def disable_buttons(self):
    	for but in self.children:
    		if but.name == "gui_button":
	    		but.disabled = True

    def enable_buttons(self, *_):
    	for but in self.children:
    		if but.name == "gui_button":
    			but.disabled = False

    def _on_new(self, *_):
    	self.current = "inactive"
    	Clock.schedule_once(lambda *x: self.parent.start_new_game(), 2)
    	Clock.schedule_once(lambda *x: self.parent.menu_on_off(), 2.1)

    def _on_load(self, *_):
    	print("Load Pressed")

    def _on_about(self, *_):
    	about = About(size_hint=(None, None), size=(self.size[0]+200, self.size[1]+100))
    	about.gamecenter = (self.gamesize[0]/2, self.gamesize[1]/2) 
    	self.parent.add_widget(about)
    	self.disable_buttons()

    def remove_about(self):
    	for child in self.parent.children:
    		if child.name == "about":
    			self.parent.remove_widget(child)
    			self.enable_buttons()

    def _on_options(self, *_):
    	dsize = self.size
    	dpos = (int((self.gamesize[0]/2)-(dsize[0]/2)), int((self.gamesize[1]/2)-(dsize[1]*.8)))

    	dpdown = DropDown(pos=dpos, size=dsize)
    	for r in self.resolutions:
    		b = ResButton(text="{},{}".format(r[0], r[1]),
    			size_hint=(None,None),
    			size=self.button_new.size)
    		b.bind(on_release=self.change_resolution)
    		dpdown.add_widget(b)
    	dpdown.bind(on_dismiss=self.enable_buttons)
    	self.parent.add_widget(dpdown)
    	self.disable_buttons()

    def _on_quit(self, *_):
    	print("App Stop failed!")

    def change_resolution(self, e):
    	res = e.text
    	res = [int(i) for i in res.split(",")]
    	self.parent.change_resolution(res)
    	e.parent.parent.dismiss()


class About(ButtonBehavior, Widget):
	textlist = ListProperty(["About the Game", 
							 "[Name of Author] Wrote, Coded and Designed the game.",
							 "[Name of Artist] Designed and drew all the art."])
	gamecenter = ListProperty([0,0])

	def on_press(self, *_):
		self.parent.startmenu.remove_about()

	def test_borders_of_widget(self):
		with self.canvas:
			Color(rgba=(1.,1.,1.,.5))
			Rectangle(pos=self.pos, size=self.size)

class ResButton(Button):
	pass

class InGameMenu(FboFloatLayout):
    button_save = ObjectProperty()
    button_load = ObjectProperty()
    button_options = ObjectProperty()
    button_quit = ObjectProperty()
    gamesize = ListProperty([0,0])

    def setup(self, gamesize):
        self.alpha = 0.
        self.gamesize = gamesize
        for call in ("save", "load", "options", "quit"):
            eval("self.button_{}.bind(on_release=self._on_{})".format(call, call))
        self.disable_buttons()

    def disable_buttons(self):
        self.button_save.disabled = True
        self.button_load.disabled = True
        self.button_options.disabled = True
        self.button_quit.disabled = True

    def enable_buttons(self, *_):
        self.button_save.disabled = False
        self.button_load.disabled = False
        self.button_options.disabled = False
        self.button_quit.disabled = False

    def _on_save(self, *_):
    	print("Save Pressed")

    def _on_load(self, *_):
    	print("Load Pressed")

    def _on_options(self, *_):
    	print("Options Pressed")

    def _on_quit(self, *_):
    	print("App Stop failed!")

class ClassPopup(Popup):
    master = ObjectProperty()
    book_title = StringProperty()
    book_text = StringProperty()

class ClassMenu(FboFloatLayout):
    button1 = ObjectProperty()
    button2 = ObjectProperty()
    button3 = ObjectProperty()
    menu = ObjectProperty()
    book_text = StringProperty("Select one of the Books to read.")
    book_dict = DictProperty(load_json("data/class_book_text.json"))
    gamesize = ListProperty([0,0])
    menu_size = ListProperty([100, 100])
    imagedict = DictProperty({
        "button1":{"normal":"images/gui/books/book1/book1_normal.png", 
                   "hover":"images/gui/books/book1/book1_hover.png", 
                   "clicked":"images/gui/books/book1/book1_clicked.png"},

        "button2":{"normal":"images/gui/books/book2/book2_normal.png", 
                   "hover":"images/gui/books/book2/book2_hover.png", 
                   "clicked":"images/gui/books/book2/book2_clicked.png"}, 

        "button3":{"normal":"images/gui/books/book3/book3_normal.png", 
                   "hover":"images/gui/books/book3/book3_hover.png", 
                   "clicked":"images/gui/books/book3/book3_clicked.png"}})

    def setup(self, gamesize):
        self.alpha = 0.
        self.gamesize = gamesize
        w, h, = gamesize
        self.menu_size[0] = (int(w*0.8))
        self.menu_size[1] = (int(h*0.65))
        self.toggle_buttons(True)

    def toggle_buttons(self, truefalse):
        self.button1.disabled = truefalse
        self.button2.disabled = truefalse
        self.button3.disabled = truefalse

    def check_for_hover(self, mousepos):
        x,y = mousepos
        x1, y1 = self.menu.pos
        mousepos = (x-x1, y-y1) 
        for button in (self.button1, self.button2, self.button3):
            if button.collide_point(*mousepos):
                button.background_normal = self.imagedict[button.name]["hover"]
                self.book_text = self.book_dict[button.name]["title"]
            else:
                if button.background_normal == self.imagedict[button.name]["hover"]:
                    button.background_normal = self.imagedict[button.name]["normal"]
                    self.book_text = "Select one of the Books to read."

    def button_clicked(self, button):
        popup = ClassPopup()
        popup.book_title = self.book_dict[button.name]["title"]
        popup.book_text = self.book_dict[button.name]["text"]
        popup.master = self
        popup.open()

    def book_chosen(self, title):
        self.parent.parent.events.flags["flag_"+title] = True
        self.parent.parent.toggle_classmenu()




