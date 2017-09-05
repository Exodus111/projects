from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import *

class Conversation(FloatLayout):
    top_manager = ObjectProperty()
    bottom_manager = ObjectProperty()
    top_panel = ObjectProperty()
    bottom_panel = ObjectProperty()
    top_text = StringProperty()
    bottom_buttons = ListProperty()
    open_close = BooleanProperty(False)
    question_big = ObjectProperty()

    def set_size(self, size):
        self.size = size

    def add_text_to_panels(self, top_text, question_list=[]):
        self.top_text = top_text
        for n, q in enumerate(question_list):
            question = Question(question_text="{}. {}".format(n+1, q), on_release=lambda x: self.question_picked(x))
            self.bottom_panel.add_widget(question)

    def clear_text(self):
        self.top_text = ""
        self.bottom_panel.clear_widgets()

    def question_picked(self, button):
        self.question_big.text = button.question_text
        self.bottom_manager.current = "question_big"

    def question_selected(self):
        """
            This method is called when the player selects a question.
            This needs to call something in a parent widget.
        """
        pass

    def drop_panels(self):
        self.open_close = not self.open_close
        if self.open_close:
            self.top_manager.current = "top_panel"
            self.bottom_manager.current = "bottom_panel"
        else:
            self.top_manager.current = "None"
            self.bottom_manager.current = "None"

class Question(Button):
    question_text = StringProperty()
