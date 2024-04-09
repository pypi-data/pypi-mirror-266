# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder

class HelloWorldApp(App):
    def change_label_text(self):
        self.root.ids.my_label.text = "Button clicked!"

def sayhello():
    HelloWorldApp().run()

if __name__ == '__main__':
    sayhello()
