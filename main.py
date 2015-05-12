__author__ = 'lucascostanzo'
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SwapTransition
from kivy.uix.floatlayout import FloatLayout


class TelaInicial(Screen):
    pass
class BuscaParty(Screen):
    pass
class NovaParty(Screen):
    pass
class Screen4(Screen):
    pass
class MyScreenManager(ScreenManager):
    pass


root = Builder.load_string('''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
MyScreenManager:
    transition: FadeTransition()
    TelaInicial:
    BuscaParty:
    NovaParty:
    Screen4:

<TelaInicial>:
    name:"first"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0, 1, .6, .8
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text:"Party Share"
            font_size: 90
            pos_hint: {'center_x':.5, 'y': .36}
        Button:
            text: 'Buscar Party'
            size_hint: .7, .2
            pos_hint: {'center_x':.5, 'y': .5}
            on_release: root.manager.current= "second"
        Button:
            text: "Nova Party"
            size_hint: .3, .3
            pos_hint: {'center_x':.5, 'y': .1}
            on_release: root.manager.current= "third"

<BuscaParty>:
    name:"second"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0, 1, .6, .8
            Rectangle:
                pos: self.pos
                size: self.size
        FloatLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, .7
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint: (.8, .908)
            pos_hint: {"center_x": .5}

        TextInput:
            text: "Buscar"
            font_size: 30
            size_hint: (.8, .08)
            pos_hint: {'center_x':.5, 'y': .91}
        Button:
            text: "Voltar"
            size_hint: .2, .2
            pos_hint: {'left_x':.5, 'top_y': .6}
            on_release: root.manager.current= "first"


<NovaParty>:
    name:"third"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0, 1, .6, .8
            Rectangle:
                pos: self.pos
                size: self.size
        GridLayout:
            size_hint_y: None
            height: 300
            pos_hint: {'center_x':.5, 'center_y': .5}
            cols: 2
            Label:
                text: "Nome da Party"
                font_size: 30
            TextInput:
                id: my_textinput
                multiline: False
                font_size: 30
            Label:
                text: "Senha"
                font_size: 30
            TextInput:
                font_size: 30
                password: True
                multiline: False
            Label:
                text: "Confirmar Senha"
                font_size: 30
            TextInput:
                password: True
                multiline: False
                font_size: 30
        Label:
            text:"Criar Party"
            font_size: 95
            pos_hint: {'center_x':.5, 'y': .4}
        Button:
            text: "Voltar"
            size_hint: .2, .2
            pos_hint: {'left_x':.5, 'top_y': .6}
            on_release: root.manager.current= "first"
        Button:
            text: "Avancar"
            size_hint: .2, .2
            pos_hint: {'center_x':.5, 'top_y': .6}
            on_release: root.manager.current= "forth"


<Screen4>:
    name: "forth"
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0, 1, .6, .8
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: my_label
            text: my_textinput.text
            font_size: 83
            pos_hint: {"center_x": .5, "y": .43}
        FloatLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, .7
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint: (.8, .85)
            pos_hint: {"center_x": .5}


''')

class MainApp(App):
    def build(self):
        return root

if __name__ == '__main__':
    MainApp().run()
