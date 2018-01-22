from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import os

search=""
url=""
ti1 = TextInput(id="search")

def WidgetScreen():
    layout = GridLayout()
    layout.rows = 3
    layout.cols = 2
    layout.padding = 10
    layout.spacing = 10
    lbl1 = Label(text="Search Term")
    lbl2 = Label(text="URL")
    ti2 = TextInput(id=url)
    btn = Button(text='Search')
    btn.bind(on_press=callback)
    layout.add_widget(lbl1)
    layout.add_widget(lbl2)
    layout.add_widget(ti1)
    layout.add_widget(ti2)
    layout.add_widget(btn)
    return layout

def callback(instance):
    prompt = "python Queuer.py --searchterm \""+str(ti1.text)+"\""
    print(prompt)
    os.system(prompt)


class MyApp(App):

    def build(self):
        return WidgetScreen()


if __name__ == '__main__':
    MyApp().run()
