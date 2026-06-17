from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.utils import platform
from kivy.metrics import dp, sp
import random, time
from typing import Optional, Dict

if platform not in ('android', 'ios'):
    Window.size = (360, 640)

BG = (0.15, 0.15, 0.15, 1)
BTN = (0.96, 0.35, 0.4, 1)
PURPLE = (0.36, 0.28, 0.67, 1)
PADLOCK_BTN = (0.25, 0.25, 0.35, 1)
PADLOCK_SELECTED = (0.36, 0.28, 0.67, 1)

class RoundedButton(Button):
    def __init__(self, **kwargs):
        bg = kwargs.pop('bg_color', None)
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.base_color = bg if bg is not None else BTN
        self.pressed_color = tuple(min(1, channel + 0.08) for channel in self.base_color[:3]) + (self.base_color[3],)
        with self.canvas.before:  # type: ignore
            self.bg_color = Color(*self.base_color)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(15)])
        self.bind(pos=self._update_rect, size=self._update_rect, state=self._update_state)  # type: ignore
    
    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_state(self, *args):
        self.bg_color.rgba = self.pressed_color if self.state == 'down' else self.base_color

class CircleButton(Button):
    def __init__(self, **kwargs):
        bg = kwargs.pop('bg_color', None)
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.base_color = bg if bg is not None else BTN
        self.pressed_color = tuple(min(1, channel + 0.08) for channel in self.base_color[:3]) + (self.base_color[3],)
        with self.canvas.before:  # type: ignore
            self.bg_color = Color(*self.base_color)
            self.bg_circle = Ellipse(size=self.size, pos=self.pos)
        self.bind(pos=self._update_circle, size=self._update_circle, state=self._update_state)  # type: ignore
    
    def _update_circle(self, *args):
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size

    def _update_state(self, *args):
        self.bg_color.rgba = self.pressed_color if self.state == 'down' else self.base_color

class TransparentButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (0.9, 0.9, 0.9, 1)

class CombinationLockDial(BoxLayout):
    def __init__(self, initial_value=0, on_change=None, **kwargs):
        super().__init__(orientation='vertical', size_hint=(1, 1), spacing=dp(5), **kwargs)
        self.on_change = on_change
        self.value = initial_value

        up_btn = RoundedButton(text='+', size_hint=(1, 0.25), font_size=sp(24), bg_color=PADLOCK_BTN)
        up_btn.bind(on_press=self.increment)  # type: ignore
        self.add_widget(up_btn)

        self.display = Label(text=str(initial_value), font_size=sp(32), bold=True, color=PADLOCK_SELECTED, size_hint=(1, 0.5))
        self.add_widget(self.display)

        down_btn = RoundedButton(text='-', size_hint=(1, 0.25), font_size=sp(24), bg_color=PADLOCK_BTN)
        down_btn.bind(on_press=self.decrement)  # type: ignore
        self.add_widget(down_btn)
    
    def increment(self, *args):
        self.value = (self.value + 1) % 10
        self.display.text = str(self.value)
        if self.on_change:
            self.on_change(self.value)
    
    def decrement(self, *args):
        self.value = (self.value - 1) % 10
        self.display.text = str(self.value)
        if self.on_change:
            self.on_change(self.value)

class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(14))

        logo_box = BoxLayout(size_hint=(1, 0.1), padding=dp(5))
        logo_label = Label(text='Vaulted Pass™', font_size=sp(26), bold=True, color=PURPLE)
        logo_box.add_widget(logo_label)
        root.add_widget(logo_box)

        root.add_widget(Label(text='Iniciar Sessão', font_size=sp(22), bold=True, size_hint=(1, 0.06), color=(1, 1, 1, 1)))
        root.add_widget(Label(text='Olá! Bom ver-te novamente!', font_size=sp(14), size_hint=(1, 0.05), color=(0.8, 0.8, 0.8, 1)))

        root.add_widget(Label(text='Melhores Tempos:', font_size=sp(14), bold=True, size_hint=(1, 0.04), color=(0.9, 0.9, 0.9, 1)))
        self.leaderboard = Label(text='', font_size=sp(13), size_hint=(1, 0.15), color=(0.8, 0.8, 0.8, 1))
        root.add_widget(self.leaderboard)

        root.add_widget(Label(text='Enter PIN:', size_hint=(1, 0.05), font_size=sp(14), color=(0.9, 0.9, 0.9, 1)))
        self.pwd = TextInput(hint_text='Apenas números', multiline=False, input_filter='int', size_hint=(1, 0.08), font_size=sp(18), background_color=(0.25, 0.25, 0.25, 1), foreground_color=(0.9, 0.9, 0.9, 1))
        root.add_widget(self.pwd)

        root.add_widget(Label(text='Escolher variação:', size_hint=(1, 0.05), font_size=sp(14), color=(0.9, 0.9, 0.9, 1)))
        
        self.mode = Spinner(
            text='Teclado Padrão', 
            values=('Teclado Padrão', 'Teclado Embaralhado', 'Cadeado Padrão', 'Cadeado Embaralhado'), 
            size_hint=(1, 0.08), 
            font_size=sp(14)
        )
        self.mode.bind(text=self._on_spinner_change) # type: ignore
        
        # SOLUÇÃO AQUI: Força a limpeza inicial logo ao carregar a interface pela primeira vez
        self._on_spinner_change(self.mode, self.mode.text)
        
        root.add_widget(self.mode)

        self.error_label = Label(text='', font_size=sp(13), color=(1, 0, 0, 1), size_hint=(1, 0.05))
        root.add_widget(self.error_label)

        btn = RoundedButton(text='Comparar', size_hint=(1, 0.1), font_size=sp(16))
        btn.bind(on_press=self.start)  # type: ignore
        root.add_widget(btn)
        
        self.add_widget(root)

    def _on_spinner_change(self, spinner, text):
        all_options = ['Teclado Padrão', 'Teclado Embaralhado', 'Cadeado Padrão', 'Cadeado Embaralhado']
        if text in all_options:
            all_options.remove(text)
        spinner.values = all_options
    
    def update_leaderboard(self):
        best_times = self.manager.best_times
        leaderboard_text = ''
        modes = [
            ('standard', 'Teclado Padrão'),
            ('scrambled', 'Teclado Embaralhado'),
            ('padlock', 'Cadeado Padrão'),
            ('padlock_random', 'Cadeado Embaralhado')
        ]
        for mode_key, mode_name in modes:
            if mode_key in best_times and best_times[mode_key] is not None:
                leaderboard_text += f'{mode_name}: {best_times[mode_key]:.2f}s\n'
        self.leaderboard.text = leaderboard_text if leaderboard_text else 'Ainda sem tempos'

    def start(self, *_):
        if not self.pwd.text:
            self.error_label.text = 'Por favor, introduza um PIN'
            return
        if len(self.pwd.text) < 4:
            self.error_label.text = 'O PIN deve ter pelo menos 4 dígitos'
            return
        self.error_label.text = ''
        
        mode_map = {
            'Teclado Padrão': 'standard',
            'Teclado Embaralhado': 'scrambled',
            'Cadeado Padrão': 'padlock',
            'Cadeado Embaralhado': 'padlock_random'
        }
        internal_mode = mode_map.get(self.mode.text, 'standard')
        
        test = self.manager.get_screen('test')
        test.setup(self.pwd.text, internal_mode)
        self.manager.current = 'test'

class TestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        logo_box = BoxLayout(size_hint=(1, 0.06), padding=dp(5))
        logo_icon = Label(text='*', font_size=sp(24), color=(1, 1, 1, 1))
        logo_box.add_widget(logo_icon)
        self.layout.add_widget(logo_box)

        self.layout.add_widget(Label(text='Iniciar Sessão', font_size=sp(22), bold=True, size_hint=(1, 0.06), color=(1, 1, 1, 1)))

        self.timer = Label(text='Tempo: 0.00 s', size_hint=(1, 0.06), font_size=sp(18), bold=True, color=PURPLE)
        self.layout.add_widget(self.timer)

        self.logo_label = Label(text='', font_size=sp(24), color=(1, 1, 1, 1), size_hint=(1, 0.06))
        self.layout.add_widget(self.logo_label)

        self.input_area = BoxLayout(size_hint=(1, 0.69))
        self.layout.add_widget(self.input_area)

        self.add_widget(self.layout)
        self.event = None

    def setup(self, pwd, mode):
        self.password = pwd
        self.mode = mode
        self.entered = ''
        self.start_time = time.time()
        if self.event: self.event.cancel()
        self.timer.text = 'Time: 0.00 s'
        
        self.logo_label.text = ''
        if mode in ('standard', 'scrambled'):
            self.logo_label.opacity = 1
        else:
            self.logo_label.opacity = 0

        self.input_area.clear_widgets()
        self.event = Clock.schedule_interval(self.update_timer, 0.05)

        if mode in ('standard', 'scrambled'):
            nums = [str(i) for i in range(10)]
            if mode == 'scrambled': random.shuffle(nums)

            keyboard_wrapper = BoxLayout(orientation='vertical', size_hint=(1, 1))
            
            grid = GridLayout(cols=3, spacing=dp(12), padding=dp(10), size_hint=(1, None), height=dp(320))
            grid.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

            for n in nums[1:10]:
                b = CircleButton(text=n, font_size=sp(24), bold=True)
                b.bind(on_press=self.press)  # type: ignore
                grid.add_widget(b)

            grid.add_widget(Label())
            b = CircleButton(text=nums[0], font_size=sp(24), bold=True)
            b.bind(on_press=self.press)  # type: ignore
            grid.add_widget(b)
            
            b = TransparentButton(text='Del', font_size=sp(18))
            b.bind(on_press=self.backspace)  # type: ignore
            grid.add_widget(b)

            keyboard_wrapper.add_widget(grid)
            self.input_area.add_widget(keyboard_wrapper)
        else:
            dial_container = GridLayout(cols=4, spacing=dp(10), padding=dp(10), size_hint=(1, None), height=dp(240))
            self.dials = []

            for i in range(len(pwd)):
                val = random.randint(0, 9) if mode == 'padlock_random' else 0
                dial = CombinationLockDial(initial_value=val, on_change=self.start_timer)
                dial_container.add_widget(dial)
                self.dials.append(dial)

            confirm = RoundedButton(text='Entrar', size_hint=(1, None), height=dp(48), bold=True, font_size=sp(16))
            confirm.bind(on_press=self.confirm)  # type: ignore

            wrap = BoxLayout(orientation='vertical', spacing=dp(15), size_hint=(1, 1))
            wrap.add_widget(dial_container)
            wrap.add_widget(confirm)
            self.input_area.add_widget(wrap)

    def start_timer(self, *args):
        if self.start_time is None:
            self.start_time = time.time()
        if self.event is None:
            self.event = Clock.schedule_interval(self.update_timer, 0.05)

    def update_timer(self, dt):
        if self.start_time is not None:
            self.timer.text = f'Time: {time.time() - self.start_time:.2f} s'

    def press(self, btn):
        self.start_timer()
        self.entered += btn.text
        
        if self.mode in ('standard', 'scrambled'):
            self.logo_label.text = '* ' * len(self.entered)
            
        if len(self.entered) == len(self.password): 
            self.finish()

    def backspace(self, btn):
        if self.entered:
            self.entered = self.entered[:-1]
            if self.entered:
                self.logo_label.text = '* ' * len(self.entered)
            else:
                self.logo_label.text = ''

    def update_slider_label(self, inst, val, lbl):
        self.start_timer()
        lbl.text = str(int(val))

    def confirm(self, *_):
        self.entered = ''.join(str(dial.value) for dial in self.dials)
        self.finish()

    def finish(self):
        if self.event: self.event.cancel()
        elapsed = time.time() - self.start_time if self.start_time else 0
        result = self.manager.get_screen('result')
        result.set_result(elapsed, self.entered == self.password, self.mode)
        self.manager.current = 'result'

class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))

        logo_box = BoxLayout(size_hint=(1, 0.1), padding=dp(5))
        logo_label = Label(text='*', font_size=sp(32), color=(1, 1, 1, 1))
        logo_box.add_widget(logo_label)
        root.add_widget(logo_box)

        root.add_widget(Label(text='Resultado', font_size=sp(26), bold=True, size_hint=(1, 0.1), color=(1, 1, 1, 1)))

        self.label = Label(font_size=sp(18), size_hint=(1, 0.5))
        root.add_widget(self.label)

        btn = RoundedButton(text='Voltar ao Menu', size_hint=(1, None), height=dp(50), bold=True, font_size=sp(16))
        btn.bind(on_press=self.go_back)  # type: ignore
        root.add_widget(btn)
        
        self.add_widget(root)

    def set_result(self, t, correct, mode):
        status = 'CORRETO ✓' if correct else 'INCORRETO ✗'
        status_color = '[color=00aa00]' if correct else '[color=ff0000]'
        mode_display = self._get_mode_name(mode)
        self.label.text = f'[b]Variação:[/b] {mode_display}\n\n[b]Tempo Final:[/b] {t:.2f}s\n\n[b]{status_color}{status}[/color][/b]'
        self.label.markup = True

        if correct:
            if mode not in self.manager.best_times or self.manager.best_times[mode] is None or t < self.manager.best_times[mode]:
                self.manager.best_times[mode] = t
    
    def _get_mode_name(self, mode):
        names = {
            'standard': 'Teclado Padrão',
            'scrambled': 'Teclado Embaralhado',
            'padlock': 'Cadeado Padrão',
            'padlock_random': 'Cadeado Embaralhado'
        }
        return names.get(mode, mode)
    
    def go_back(self, *_):
        setup_screen = self.manager.get_screen('setup')
        setup_screen.update_leaderboard()
        self.manager.current = 'setup'

class AppMain(App):
    def build(self):
        self.title = 'Vaulted Pass™'
        Window.clearcolor = BG
        sm = ScreenManager()
        sm.best_times: Dict[str, Optional[float]] = {  # type: ignore
            'standard': None,
            'scrambled': None,
            'padlock': None,
            'padlock_random': None
        }
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(TestScreen(name='test'))
        sm.add_widget(ResultScreen(name='result'))
        return sm

if __name__ == '__main__':
    AppMain().run()