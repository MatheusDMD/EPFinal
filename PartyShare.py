__author__ = 'PartyShare Team'


from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, GraphicException
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

import ctypes, os, sys
libcef_so = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcef.so')
if os.path.exists(libcef_so):
    # Import local module
    ctypes.CDLL(libcef_so, ctypes.RTLD_GLOBAL)
    if 0x02070000 <= sys.hexversion < 0x03000000:
        import cefpython_py27 as cefpython
    else:
        raise Exception("Unsupported python version: %s" % sys.version)
else:
    # Import from package
    from cefpython3 import cefpython

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SwapTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from apiclient.discovery import build
from apiclient.errors import HttpError

from firebase import firebase
import time

import urllib
import unicodedata
import editdistance

FIREBASE_URL = "https://party-share.firebaseio.com/"
fb = firebase.FirebaseApplication(FIREBASE_URL, None)

"""result = fb.get('party-share')"""



def envia_party(nome_party):
    fb.put("/", "%s"%nome_party, nome_party)

def envia_musica(music, url, senha):
    l = fb.get("/", "%s"%nome_party)
    if l == "%s"%nome_party:
        music = unicodedata.normalize('NFKD', music).encode('ascii','ignore')
        music = urllib.quote(music)
        print(l)
        lista = [l]
        lista.append(senha)
        lista.append({music: url[0]})
        print(lista)
        fb.put("/", "%s"%nome_party, lista)
    else:
        lista=l
        music = unicodedata.normalize('NFKD', music).encode('ascii','ignore')
        music = urllib.quote(music)
        lista.append({music: url[0]})
        print(lista)
        fb.put("/", "%s"%nome_party, lista)

def retoma_musicas(nome_party):
    musicas = fb.get("/", "%s"%nome_party)
    musicas = musicas[2::]
    musicas_lista2 = []
    musicas_lista = []
    print musicas
    for i in range(len(musicas)):
        musicas_lista.append(musicas[i].keys())
    for i in range(len(musicas_lista)):
        x = urllib.unquote(musicas_lista[i][0])
        musicas_lista2.append(x)
    return musicas_lista2

def retoma_url(nome_party):
    musicas = fb.get("/", "%s"%nome_party)
    musicas = musicas[2::]
    url_lista2 = []
    url_lista = []
    print musicas
    for i in range(len(musicas)):
        url_lista.append(musicas[i].values())
    for i in range(len(url_lista)):
        x = urllib.unquote(url_lista[i][0])
        url_lista2.append(x)
    return url_lista2

def retoma_festas():
    festas = fb.get("/","/")
    festas = festas.keys()
    return festas

def retoma_senhas(festa):
    senhas = fb.get("/","/")
    senhas = senhas[festa][1]
    return senhas

pesquisa=[]
contador_url = 0
nome_party = "Default"
senha = "Default"
musica = "Default"
URL = "Default"
TudoCerto="Defaut"

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyCpyMCAtFe31vFsPL0biclQp1RDxLQnVPI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube(pesquisa):
    videos = []
    channels = []
    playlists = []
    def youtube_search(options):
      youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)

      # Call the search.list method to retrieve results matching the specified
      # query term.
      search_response = youtube.search().list(
        q=options["q"],
        part="id,snippet",
        maxResults=options["max_results"]
      ).execute()



      # Add each result to the appropriate list, and then display the lists of
      # matching videos, channels, and playlists.
      for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
          videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                     search_result["id"]["videoId"]))
        elif search_result["id"]["kind"] == "youtube#channel":
          channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                       search_result["id"]["channelId"]))
        elif search_result["id"]["kind"] == "youtube#playlist":
          playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                        search_result["id"]["playlistId"]))


      print "Videos:\n", "\n".join(videos), "\n"
      print "Channels:\n", "\n".join(channels), "\n"
      print "Playlists:\n", "\n".join(playlists), "\n"


    if __name__ == "__main__":
      d={"q":pesquisa[0],"max_results":5}

      try:
        youtube_search(d)
      except HttpError, e:
        print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
    return videos









class BrowserLayout(BoxLayout):

    def __init__(self, **kwargs):
        super(BrowserLayout, self).__init__(**kwargs)



class CefBrowser(Widget):
    '''Represent a browser widget for kivy, which can be used like a normal widget.
    '''
    def __init__(self, start_url='http://www.youtube.com', **kwargs):
        super(CefBrowser, self).__init__(**kwargs)

        self.start_url = start_url

        #Workaround for flexible size:
        #start browser when the height has changed (done by layout)
        #This has to be done like this because I wasn't able to change the texture size
        #until runtime without core-dump.
        self.bind(size = self.size_changed)


    def size_changed(self, *kwargs):
        '''When the height of the cefbrowser widget got changed, create the browser
        '''
        if self.height != 100:
            self.start_cef(self.start_url)


    def _cef_mes(self, *kwargs):
        '''Get called every frame.
        '''
        cefpython.MessageLoopWork()


    def _update_rect(self, *kwargs):
        '''Get called whenever the texture got updated.
        => we need to reset the texture for the rectangle
        '''
        self.rect.texture = self.texture


    def start_cef(self, start_url='http://google.com'):
        '''Starts CEF.
        '''
        # create texture & add it to canvas
        self.texture = Texture.create(size=self.size, colorfmt='rgba', bufferfmt='ubyte')
        self.texture.flip_vertical()
        with self.canvas:
            Color(1, 1, 1)
            self.rect = Rectangle(size=self.size, texture=self.texture)

        #configure cef
        cefpython.g_debug = True
        settings = {"log_severity": cefpython.LOGSEVERITY_INFO,
                #"log_file": GetApplicationPath("debug.log"),
                "release_dcheck_enabled": True, # Enable only when debugging.
                # This directories must be set on Linux
                "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
                "resources_dir_path": cefpython.GetModuleDirectory(),
                "browser_subprocess_path": "%s/%s" % (cefpython.GetModuleDirectory(), "subprocess")}

        #start idle
        Clock.schedule_interval(self._cef_mes, 0)

        #init CEF
        cefpython.Initialize(settings)

        #WindowInfo offscreen flag
        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsOffscreen(0)

        #Create Broswer and naviagte to empty page <= OnPaint won't get called yet
        browserSettings = {}
        # The render handler callbacks are not yet set, thus an
        # error report will be thrown in the console (when release
        # DCHECKS are enabled), however don't worry, it is harmless.
        # This is happening because calling GetViewRect will return
        # false. That's why it is initially navigating to "about:blank".
        # Later, a real url will be loaded using the LoadUrl() method
        # and the GetViewRect will be called again. This time the render
        # handler callbacks will be available, it will work fine from
        # this point.
        # --
        # Do not use "about:blank" as navigateUrl - this will cause
        # the GoBack() and GoForward() methods to not work.
        # --
        # TODO: get rid of the hard-coded path. Use the __file__ variable
        #       to get the current directory. Using a path to a non-existent
        #       local html file seems to not cause any problems, so it can
        #       stay for a moment.
        self.browser = cefpython.CreateBrowserSync(windowInfo, browserSettings,
                navigateUrl="file:///home/czarek/cefpython/cefpython/cef3/linux/binaries_64bit/empty2.html")

        #set focus
        self.browser.SendFocusEvent(True)

        #Create RenderHandler (in ClientHandler)
        CH = ClientHandler(self.texture, self)
        self.browser.SetClientHandler(CH)

        #Call WasResized() => force cef to call GetViewRect() and OnPaint afterwards
        self.browser.WasResized()

        # Load desired start URL
        # TODO: let the local html file "empty.html" to finish loading,
        #       call the LoadUrl() method with a 100ms delay. In the
        #       empty.html you could add a "Loading.." text, this would
        #       event useful, user would see some message instead of the
        #       blank page. Sometimes the lag can cause the website to
        #       load for a few seconds and user would be seeing only a
        #       white screen and wonder of what is happening. The other
        #       solution would be to change the mouse cursor to loading
        #       state - but this won't work in touch screen devices? As
        #       there is no cursor there. In wxpython there is the
        #       wx.CallLater() method, is there anything similar in Kivy?
        self.browser.GetMainFrame().LoadUrl(start_url)

        #Clock.schedule_interval(self.press_key, 5)


    def go_forward(self):
        '''Going to forward in browser history
        '''
        global contador_url
        print "go forward"
        url = retoma_url(nome_party)
        self.browser.GetMainFrame().LoadUrl("https://www.youtube.com/watch?v=%s"%url[contador_url])
        contador_url+=1


    def go_back(self):
        '''Going back in browser history
        '''
        print "go back"
        self.browser.GoBack()


class ClientHandler:

    def __init__(self, texture, parent):
        self.texture = texture
        self.parent = parent


    def OnPaint(self, browser, paintElementType, dirtyRects, buffer, width, height):
        print "OnPaint()"
        if paintElementType != cefpython.PET_VIEW:
            print "Popups aren't implemented yet"
            return

        #update buffer
        buffer = buffer.GetString(mode="bgra", origin="top-left")

        #update texture of canvas rectangle
        self.texture.blit_buffer(buffer, colorfmt='bgra', bufferfmt='ubyte')
        self.parent._update_rect()

        return True


    def GetViewRect(self, browser, rect):
        print "GetViewRect()"
        width, height = self.texture.size
        rect.append(0)
        rect.append(0)
        rect.append(width)
        rect.append(height)
        print width
        print height
        return True









class TelaInicial(Screen):
    pass
class BuscaParty(Screen):
    pass
class NovaParty(Screen):
    pass
class Screen4(Screen):
    pass
class Screen5(Screen):
    pass
class Screen6(Screen):
    pass
class Screen7(Screen):
    pass
class Screen8(Screen):
    pass
class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(MyScreenManager, self).__init__(**kwargs)
        self.valor = "Texto teste"
        self.password = "password teste"
        self.password2 = "conferir senha"
        self.plot_musicas = ""
        self.videos0 = "default"
        self.videos1 = "default"
        self.videos2 = "default"
        self.videos3 = "default"
        self.videos4 = "default"

    def altera(self):
        self.password = self.screens[2].ids["my_password"].text
        self.password2 = self.screens[2].ids["my_password2"].text
        global nome_party
        global senha
        if self.password == self.password2:
            self.valor = self.screens[2].ids["my_textinput"].text
            self.screens[3].ids["my_label"].text = self.valor
            senha = self.password
            nome_party = self.valor
            envia_party(nome_party)
            root.current = "forth"

        else:
            content = Button(text = "senhas diferentes")
            popup = Popup(title = "teste popup", content = content, auto_dismiss = False, size_hint = (.3, .3), pos_hint = {"center_x":.5, "center_y":.5})
            self.screens[2].ids["nova_party"].add_widget(popup)
            content.bind(on_press=popup.dismiss)

    def musica(self):
        self.nome_da_musica = self.screens[4].ids["musica"].text
        pesquisa.insert(0, self.nome_da_musica)
        videos = youtube(pesquisa)

        b0 = self.screens[5].ids["0"]
        b1 = self.screens[5].ids["1"]
        b2 = self.screens[5].ids["2"]
        b3 = self.screens[5].ids["3"]
        b4 = self.screens[5].ids["4"]
        b0.text = videos[0]
        b1.text = videos[1]
        b2.text = videos[2]
        b3.text = videos[3]
        b4.text = videos[4]

    def add_musica0(self):
        global senha
        global musica
        global URL
        x = self.screens[5].ids["0"].text.split("(")
        y = x[-1].split(")")
        musica = x[0]
        URL = y
        envia_musica(musica,URL, senha)
        print(musica, URL, senha)

    def add_musica1(self):
        global senha
        global musica
        global URL
        x = self.screens[5].ids["1"].text.split("(")
        y = x[-1].split(")")
        musica = x[0]
        URL = y
        envia_musica(musica,URL, senha)
        print(musica, URL)

    def add_musica2(self):
        global senha
        global musica
        global URL
        x = self.screens[5].ids["2"].text.split("(")
        y = x[-1].split(")")
        musica = x[0]
        URL = y
        envia_musica(musica,URL, senha)
        print(musica, URL)

    def add_musica3(self):
        global senha
        global musica
        global URL
        x = self.screens[5].ids["3"].text.split("(")
        y = x[-1].split(")")
        musica = x[0]
        URL = y
        envia_musica(musica,URL, senha)
        print(musica, URL)

    def add_musica4(self):
        global senha
        global musica
        global URL
        x = self.screens[5].ids["4"].text.split("(")
        y = x[-1].split(")")
        musica = x[0]
        URL = y
        envia_musica(musica,URL, senha)
        print(musica, URL)

    def buscar_festas(self):
        minha_busca = self.screens[1].ids["minha_busca"].text
        festas = retoma_festas()
        x = 0
        for i in festas:
            if editdistance.eval(minha_busca, i)<3:
                self.screens[1].ids["%d"%x].text = i
                x += 1

    def entrar_festa0(self):
        global TudoCerto
        if self.screens[1].ids["0"].text != "":
            TudoCerto = self.screens[1].ids["0"].text

    def entrar_festa1(self):
        global TudoCerto
        if self.screens[1].ids["1"].text != "":
            TudoCerto = self.screens[1].ids["1"].text

    def entrar_festa2(self):
        global TudoCerto
        if self.screens[1].ids["2"].text != "":
            TudoCerto = self.screens[1].ids["2"].text

    def entrar_festa3(self):
        global TudoCerto
        if self.screens[1].ids["3"].text != "":
            TudoCerto = self.screens[1].ids["3"].text

    def entrar_festa4(self):
        global TudoCerto
        if self.screens[1].ids["4"].text != "":
            TudoCerto = self.screens[1].ids["4"].text

    def tudo_certo(self):
        global TudoCerto
        global nome_party
        if self.screens[6].ids["password3"].text == retoma_senhas(TudoCerto):
            root.current = "forth"
            self.valor = TudoCerto
            nome_party = TudoCerto
            self.screens[3].ids["my_label"].text = self.valor
        else:
            content = Button(text = "Senha Incorreta")
            popup = Popup(title = "teste popup", content = content, auto_dismiss = False, size_hint = (.3, .3), pos_hint = {"center_x":.5, "center_y":.5})
            content.bind(on_press=popup.dismiss)
            self.screens[6].ids["confere_senha"].add_widget(popup)

    def plota_musicas(self):
        global nome_party
        self.plot_musicas = retoma_musicas(nome_party)
        self.screens[3].ids["plot"].clear_widgets()
        for i in range(len(self.plot_musicas)):
            l = Label(text = self.plot_musicas[i], pos_hint = {"center_x": 0.5, "center_y": .9-.05*i})
            self.screens[3].ids["plot"].add_widget(l)
        SV = ScrollView(size_hint=(None, None), size=(400, 400))
        self.screens[3].ids["plot"].add_widget(SV)











root = Builder.load_string('''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
MyScreenManager:
    transition: FadeTransition()
    TelaInicial:
    BuscaParty:
    NovaParty:
    Screen4:
    Screen5:
    Screen6:
    Screen7:
    Screen8:

<TelaInicial>:
    name:"first"
    FloatLayout:
        canvas.before:
            Color:
                rgba: .0, .55, .7, 1
            Rectangle:
                pos: self.pos
                size: self.size
#        Label:
#           text:"Party Share"
#           font_size: 100
#           font_name: 'DroidSans'
#           bold: True
#           italic: True
#           pos_hint: {'center_x':.5, 'y': .36}
        Image:
            source: "logo.png"
            size_hint: .5, .5
            pos_hint: {"center_x": .5, "center_y": .7}
            allow_stretch: True
        Button:
            text:
            size_hint: .22, .3
            pos_hint: {'center_x':.3, 'y': .1}
            on_release: root.manager.current= "second"
            background_color: (.5, 0, .5, 0)
            Image:
                source: "botao porta.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 200, 200
        Button:
            text:
            size_hint: .22, .3
            pos_hint: {'center_x':.7, 'y': .1}
            on_release: root.manager.current= "third"
            background_color: (.5, 0, .5, 0)
            Image:
                source: "Botao +.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 200,200

<BuscaParty>:
    name:"second"
    FloatLayout:
        canvas.before:
            Color:
                rgba: .0, .55, .7, 1
            Rectangle:
                pos: self.pos
                size: self.size
        FloatLayout:
            canvas.before:
                Color:
                    rgba: 1, 1, 1, .4
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint: (.8, .908)
            pos_hint: {"center_x": .5}

            Button:
                id: 0
                text: " "
                font_size: 50
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .8}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.current= "seventh"
                on_release: root.manager.entrar_festa0()
                background_color: (.5, 0, .5, .4)


            Button:
                id: 1
                text: " "
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .6}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.entrar_festa1()

            Button:
                id: 2
                text:
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .4}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.entrar_festa2()
            Button:
                id: 3
                text: " "
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .2}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.entrar_festa3()
            Button:
                id: 4
                text: " "
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .0}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.entrar_festa4()

        TextInput:
            id: minha_busca
            multiline: False
            text: "Buscar"
            font_size: 30
            size_hint: (.8, .08)
            pos_hint: {'center_x':.5, 'y': .91}
        Button:
            text: "Voltar"
            size_hint: .13, .18
            pos_hint: {'center_x':.1, 'center_y': .1}
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.current= "first"
            Image:
                source: "botao voltar.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 115, 115
        Button:
            size_hint: .13, .18
            pos_hint: {'center_x':.9, 'center_y': .1}
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.buscar_festas()

            Image:
                source: "Botao.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 115, 115



<NovaParty>:
    name:"third"
    FloatLayout:
        id: nova_party
        canvas.before:
            Color:
                rgba: .0, .55, .7, 1
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
                id: my_password
                font_size: 30
                password: True
                multiline: False
            Label:
                text: "Confirmar Senha"
                font_size: 30
            TextInput:
                id: my_password2
                password: True
                multiline: False
                font_size: 30
                #on_text: root.manager.altera()
        Label:
            text:"Criar Party"
            font_size: 95
            pos_hint: {'center_x':.5, 'y': .4}
        Button:
            text: "Voltar"
            size_hint: .13, .18
            pos_hint: {'center_x':.1, 'center_y': .12}
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.current= "first"
            Image:
                source: "botao voltar.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 120, 120
        Button:
            text: "Voltar"
            size_hint: .13, .18
            pos_hint: {'center_x':.9, 'center_y': .12}
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.altera()
            Image:
                source: "Botao ok.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 120, 120


<Screen4>:
    name: "forth"
    FloatLayout:
        canvas.before:
            Color:
                rgba: .0, .55, .7, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: my_label
            text: root.manager.valor
            font_size: 83
            pos_hint: {"center_x": .5, "y": .43}
        FloatLayout:
            id: plot
            canvas.before:
                Color:
                    rgba: 1, 1, 1, .4
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint: (.8, .85)
            pos_hint: {"center_x": .5}

        Button:
            size_hint: .13, .18
            font_size: 30
            pos_hint: {'center_x':.9, 'center_y': .3}
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.current = "fifth"
            Image:
                source: "Botao +.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 120, 120
        Button:
            text:
            size_hint: .13, .18
            font_size: 30
            pos_hint: {'center_x':.9, 'center_y': .1}
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.plota_musicas()
            Image:
                source: "botao atualizar.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 120, 120
        Button:
            text: "cef"
            size_hint: .13, .18
            font_size: 30
            pos_hint: {'center_x':.9, 'center_y': .7}
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.current = "cefpython"
            Image:
                source: "play.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 120, 120
        Button:
            text:
            size_hint: .13, .18
            font_size: 30
            pos_hint: {'center_x':.9, 'center_y': .5}
            background_color: (.5, 0, .5, 0)
            on_release: cefpython.Shutdown()
            Image:
                source: "pause.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
                size: 120, 120
<Screen5>
    name:"fifth"
    FloatLayout:
        canvas.before:
            Color:
                rgba: .0, .55, .7, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Adicionar"
            pos_hint:{"center_x": .37, "center_y": .65}
            font_size: 100

        TextInput:
            id: musica
            multiline: False
            text: "Buscar"
            font_size: 30
            size_hint: (.65, .08)
            pos_hint: {'center_x':.425, 'center_y': .5}
        Button:
            size_hint: .13, .18
            pos_hint: {'center_x':.85, 'center_y': .5}
            on_press: root.manager.musica()
            background_color: (.5, 0, .5, 0)
            on_release: root.manager.current = "six"
            Image:
                source: "Botao.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True
<Screen6>
    name:"six"
    FloatLayout:
        canvas.before:
            Color:
                rgba: .0, .55, .7, 1
            Rectangle:
                pos: self.pos
                size: self.size
        FloatLayout:
            id: tela_das_musicas
            canvas.before:
                Color:
                    rgba: 1, 1, 1, .4
                Rectangle:
                    pos: self.pos
                    size: self.size
            size_hint: (.8, .908)
            pos_hint: {"center_x": .5}

            Button:
                id: 0
                text: "default"
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .8}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.add_musica0()
                on_release: root.manager.current = "forth"

            Button:
                id: 1
                text: "default"
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .6}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.add_musica1()
                on_release: root.manager.current = "forth"

            Button:
                id: 2
                text: "default"
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .4}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.add_musica2()
                on_release: root.manager.current = "forth"

            Button:
                id: 3
                text: "default"
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .2}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.add_musica3()
                on_release: root.manager.current = "forth"

            Button:
                id: 4
                text: "default"
                size_hint: 1, .2
                pos_hint: {'center_x':.5, 'y': .0}
                background_color: (.5, 0, .5, .4)
                on_release: root.manager.add_musica4()
                on_release: root.manager.current = "forth"

        Label:
            text: "Musicas"
            font_size: 30
            size_hint: (.8, .08)
            pos_hint: {'center_x':.5, 'y': .91}

<Screen7>
    name:"seventh"
    FloatLayout:
        id: confere_senha
        canvas.before:
            Color:
                rgba: .0, .55, .7, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "Senha"
            pos_hint:{"center_x": .27, "center_y": .65}
            font_size: 100
        TextInput:
            id: password3
            multiline: False
            password: True
            text:
            font_size: 30
            size_hint: (.65, .08)
            pos_hint: {'center_x':.425, 'center_y': .5}
        Button:
            text: "Continuar"
            size_hint: .13, .18
            pos_hint: {'center_x':.85, 'center_y': .5}
            background_color: (.5, 0, .5, 0)
            on_press: root.manager.plota_musicas()
            on_press: root.manager.tudo_certo()
            Image:
                source: "Botao ok.png"
                size_hint: [1,1]
                center_x: self.parent.center_x
                center_y: self.parent.center_y
                allow_stretch: True

<Screen8>:
    name: "cefpython"
    BrowserLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            width: 80
            Button:
                background_color: (.0, .55, .7, 1)
                text: "Back"
                on_press: root.manager.current = "forth"
                Image:
                    source: "logo.png"
                    size_hint: [1,1]
                    center_x: self.parent.center_x
                    center_y: self.parent.center_y
                    allow_stretch: True
                    size: 100, 100
            Button:
                background_color: (.0, .55, .7, 1)
                text: "Forward"
                on_press: browser.go_forward()
                Image:
                    source: "botao avancar.png"
                    size_hint: [1,1]
                    center_x: self.parent.center_x
                    center_y: self.parent.center_y
                    allow_stretch: True
                    size: 100, 100
        CefBrowser:
            id: browser






''')
class CefBrowserApp(App):
    def build(self):
        return BrowserLayout()
class MainApp(App):
    def build(self):
        return root

if __name__ == '__main__':
    MainApp().run()
    CefBrowserApp().run()
    cefpython.Shutdown()