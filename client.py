import socket
import threading
import select

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config
from kivy.uix.textinput import TextInput
from kivy.properties import NumericProperty

Builder.load_string("""
#:import C kivy.utils.get_color_from_hex
#:import RiseInTransition kivy.uix.screenmanager.RiseInTransition

<BoxLayout>:
    padding: 10
    spacing: 10

<GridLayout>:
    rows: 2
    cols: 2
    spacing: 10
    row_default_height: 90
    row_force_default: True

<Label>:
    font_size: 25

<Button>:
    font_size: 30
    height: 90
    size_hint: (1, None)
    border: (2, 2, 2, 2)

<TextInput>:
    font_size: 30
    multiline: False
    padding: [10, 0.5 * (self.height - self.line_height)]

<ScrollView>:
    canvas.before:
        Color:
            rgb: 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<ChatLabel@Label>:
    color: C('#101010')
    text_size: (self.width, None)
    halign: 'left'
    valign: 'top'
    padding: (0, 0)
    size_hint: (1, None)
    height: self.texture_size[1]
    markup: True

<RootWidget>:
    transition: RiseInTransition()

    Screen:
        name: 'username'
        BoxLayout:
            orientation: 'vertical'
            GridLayout:
                Label:
                    text: 'Nickname:'
                    halign: 'left'
                    size_hint: (0.4, 1)
                CustomInput:
                    id: nickname
            Button:
                text: 'Connect'
                on_press: app.connect()

    Screen:
        name: 'chatroom'
        BoxLayout:
            orientation: 'vertical'
            ScrollView:
                ChatLabel:
                    id: chat_logs
                    text: ''
            BoxLayout:
                height: 90
                orientation: 'horizontal'
                padding: 0
                size_hint: (1, None)
                CustomInput:
                    id: message
                    on_text_validate: app.sending()
                Button:
                    text: 'Send'
                    on_press: app.sending()
                    size_hint: (0.3, 1)
""")

class CustomInput(TextInput):
    max_chars = NumericProperty(20)
    def insert_text(self, substring, from_undo=False):
        if not from_undo and (len(self.text)+len(substring) > self.max_chars):
            return
        super(CustomInput, self).insert_text(substring, from_undo)

class RootWidget(ScreenManager):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

class ChatApp(App):
    def build(self):
        self.exiting = False
        return RootWidget()

    def recv_loop(self, connection):
        while True:
            if self.exiting:
                return
            readable, writable, errored = select.select([connection], [], [connection], 0.1)
            if readable or errored:
                message = connection.recv(1024)
                text = message.decode('utf-8', 'ignore')
                if not message:
                    print(">Disconnected")
                    return
                print(text)
                self.root.ids.chat_logs.text += ('{}\n'.format(text))

    def connect(self):
        self.nick = self.root.ids.nickname.text

        self.sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('127.0.0.1', 9999)

        print(">Connecting to server")
        self.sckt.connect(('127.0.0.1', 9999))

        print(">Starting receiving thread")
        threading.Thread(target=self.recv_loop, args=[self.sckt]).start()

        self.root.current = 'chatroom'

    def sending(self):
        msg = self.root.ids.message.text
        phasetwo = self.nick + ': ' + msg
        tosend = phasetwo.encode('utf-8', 'ignore')
        self.sckt.send(tosend)
        self.root.ids.message.text = ''

    def on_stop(self):
        self.exiting = True
        self.sckt.close()
        exit()

if __name__ == '__main__':
    Config.set('graphics', 'height', '800')
    Config.set('graphics', 'width', '500')

    ChatApp().run()
