# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
class HelloWorldApp(App):
    pass

def sayhello():
    HelloWorldApp().run()

if __name__ == '__main__':
    sayhello()
