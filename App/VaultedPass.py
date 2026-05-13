from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
import random, time

Window.size = (360, 640)

BG = (0.15, 0.15, 0.15, 1)
BTN = (0.96, 0.35, 0.4, 1)
PURPLE = (0.36, 0.28, 0.67, 1)
PADLOCK_BTN = (0.25, 0.25, 0.35, 1)
PADLOCK_SELECTED = (0.36, 0.28, 0.67, 1)

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = BTN
        with self.canvas.before:  # type: ignore
            self.bg_color = Color(*BTN)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[25])
        self.bind(pos=self._update_rect, size=self._update_rect)  # type: ignore
    
    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

class CircleButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = BTN
        with self.canvas.before:  # type: ignore
            self.bg_color = Color(*BTN)
            self.bg_circle = Ellipse(size=self.size, pos=self.pos)
        self.bind(pos=self._update_circle, size=self._update_circle)  # type: ignore
    
    def _update_circle(self, *args):
        self.bg_circle.pos = self.pos
        self.bg_circle.size = self.size

class TransparentButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = (0.9, 0.9, 0.9, 1)

class CombinationLockDial(BoxLayout):
    def __init__(self, initial_value=0, on_change=None, **kwargs):
        super().__init__(orientation='vertical', size_hint=(1, 1), spacing=5, **kwargs)
        self.on_change = on_change
        self.value = initial_value
        
        # Up button
        up_btn = Button(text='▲', size_hint=(1, 0.15), font_size=18, background_color=PADLOCK_BTN, background_normal='')
        up_btn.bind(on_press=self.increment)  # type: ignore
        self.add_widget(up_btn)
        
        # Display value
        self.display = Label(text=str(initial_value), font_size=32, bold=True, color=PADLOCK_SELECTED, size_hint=(1, 0.4))
        self.add_widget(self.display)
        
        # Down button
        down_btn = Button(text='▼', size_hint=(1, 0.15), font_size=18, background_color=PADLOCK_BTN, background_normal='')
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
        root = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        # Logo area
        logo_box = BoxLayout(size_hint=(1, 0.15), padding=10)
        logo_label = Label(text='🔒 Vaulted Pass™', font_size=24, bold=True, color=PURPLE)
        logo_box.add_widget(logo_label)
        root.add_widget(logo_box)
        
        # Title
        root.add_widget(Label(text='Sign In', font_size=26, bold=True, size_hint=(1, 0.08), color=(1, 1, 1, 1)))
        root.add_widget(Label(text='Hi there! Nice to see you again', font_size=13, size_hint=(1, 0.06), color=(0.8, 0.8, 0.8, 1)))
        
        # Best times leaderboard
        root.add_widget(Label(text='Best Times:', font_size=12, bold=True, size_hint=(1, 0.04), color=(0.9, 0.9, 0.9, 1)))
        self.leaderboard = Label(text='', font_size=10, size_hint=(1, 0.12), color=(0.8, 0.8, 0.8, 1))
        root.add_widget(self.leaderboard)
        
        # PIN input
        root.add_widget(Label(text='Enter PIN:', size_hint=(1, 0.06), font_size=13, color=(0.9, 0.9, 0.9, 1)))
        self.pwd = TextInput(hint_text='Apenas números', multiline=False, input_filter='int', size_hint=(1, 0.12), font_size=20, background_color=(0.25, 0.25, 0.25, 1), foreground_color=(0.9, 0.9, 0.9, 1))
        root.add_widget(self.pwd)
        
        # Mode selection
        root.add_widget(Label(text='Choose variation:', size_hint=(1, 0.06), font_size=13, color=(0.9, 0.9, 0.9, 1)))
        self.mode = Spinner(text='Standard Keyboard', values=('Standard Keyboard','Scrambled Keyboard','Standard PadLock','Scrambled PadLock'), size_hint=(1, 0.1), font_size=12)
        root.add_widget(self.mode)
        
        # Error label
        self.error_label = Label(text='', font_size=11, color=(1, 0, 0, 1), size_hint=(1, 0.06))
        root.add_widget(self.error_label)
        
        # Start button
        btn = RoundedButton(text='Compare', size_hint=(1, 0.12))
        btn.bind(on_press=self.start)  # type: ignore
        root.add_widget(btn)
        
        self.add_widget(root)
    
    def update_leaderboard(self):
        best_times = self.manager.best_times
        leaderboard_text = ''
        modes = [
            ('standard', 'Std Keyboard'),
            ('scrambled', 'Scr Keyboard'),
            ('padlock', 'Std PadLock'),
            ('padlock_random', 'Scr PadLock')
        ]
        for mode_key, mode_name in modes:
            if mode_key in best_times and best_times[mode_key] is not None:
                leaderboard_text += f'{mode_name}: {best_times[mode_key]:.2f}s\n'
        self.leaderboard.text = leaderboard_text if leaderboard_text else 'No times yet'

    def start(self, *_):
        if not self.pwd.text:
            self.error_label.text = 'Please enter a PIN'
            return
        if len(self.pwd.text) < 4:
            self.error_label.text = 'PIN must have at least 4 digits'
            return
        self.error_label.text = ''
        
        # Map display names to internal names
        mode_map = {
            'Standard Keyboard': 'standard',
            'Scrambled Keyboard': 'scrambled',
            'Standard PadLock': 'padlock',
            'Scrambled PadLock': 'padlock_random'
        }
        internal_mode = mode_map.get(self.mode.text, 'standard')
        
        test = self.manager.get_screen('test')
        test.setup(self.pwd.text, internal_mode)
        self.manager.current = 'test'

class TestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        
        # Logo
        logo_box = BoxLayout(size_hint=(1, 0.08), padding=5)
        logo_label = Label(text='◉', font_size=24, color=(1, 1, 1, 1))
        logo_box.add_widget(logo_label)
        self.layout.add_widget(logo_box)
        
        # Title
        self.layout.add_widget(Label(text='Sign In', font_size=24, bold=True, size_hint=(1, 0.08), color=(1, 1, 1, 1)))
        
        # Timer
        self.timer = Label(text='Time: 0.00 s', size_hint=(1, 0.08), font_size=18, bold=True, color=PURPLE)
        self.layout.add_widget(self.timer)
        
        # Input area
        self.input_area = BoxLayout()
        self.layout.add_widget(self.input_area)
        
        self.add_widget(self.layout)
        self.event = None

    def setup(self, pwd, mode):
        self.password = pwd
        self.mode = mode
        self.entered = ''
        self.start_time = None
        if self.event: self.event.cancel()
        self.timer.text = 'Time: 0.00 s'
        self.input_area.clear_widgets()

        if mode in ('standard', 'scrambled'):
            nums = [str(i) for i in range(10)]
            if mode == 'scrambled': random.shuffle(nums)
            
            # Create 3x3 grid layout + 0 in center at bottom
            grid = GridLayout(cols=3, spacing=10, padding=10, size_hint=(1, 1))
            
            # Add 1-9
            for n in nums[1:10]:
                b = CircleButton(text=n, font_size=28, bold=True)
                b.bind(on_press=self.press)  # type: ignore
                grid.add_widget(b)
            
            # Add bottom row with 0 in center
            grid.add_widget(Label())  # Empty left
            b = CircleButton(text=nums[0], font_size=28, bold=True)  # 0 in center
            b.bind(on_press=self.press)  # type: ignore
            grid.add_widget(b)
            b = TransparentButton(text='←', font_size=24)  # Backspace no background
            b.bind(on_press=self.backspace)  # type: ignore
            grid.add_widget(b)
            
            self.input_area.add_widget(grid)
        else:
            # PadLock mode with combination lock dials
            dial_container = GridLayout(cols=4, spacing=12, padding=20, size_hint=(1, 0.7))
            self.dials = []
            
            for i in range(len(pwd)):
                val = random.randint(0, 9) if mode == 'padlock_random' else 0
                dial = CombinationLockDial(initial_value=val, on_change=self.start_timer)
                dial_container.add_widget(dial)
                self.dials.append(dial)
            
            confirm = RoundedButton(text='Sign in', size_hint=(1, 0.2), bold=True)
            confirm.bind(on_press=self.confirm)  # type: ignore
            
            wrap = BoxLayout(orientation='vertical', spacing=10)
            wrap.add_widget(dial_container)
            wrap.add_widget(confirm)
            self.input_area.add_widget(wrap)

    def start_timer(self, *args):
        if self.start_time is None:
            self.start_time = time.time()
            self.event = Clock.schedule_interval(self.update_timer, 0.05)

    def update_timer(self, dt):
        if self.start_time is not None:
            self.timer.text = f'Time: {time.time() - self.start_time:.2f} s'

    def press(self, btn):
        self.start_timer()
        self.entered += btn.text
        if len(self.entered) == len(self.password): self.finish()

    def backspace(self, btn):
        if self.entered:
            self.entered = self.entered[:-1]

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
        root = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Logo
        logo_box = BoxLayout(size_hint=(1, 0.1), padding=5)
        logo_label = Label(text='◉', font_size=32, color=(1, 1, 1, 1))
        logo_box.add_widget(logo_label)
        root.add_widget(logo_box)
        
        # Title
        root.add_widget(Label(text='Result', font_size=26, bold=True, size_hint=(1, 0.1), color=(1, 1, 1, 1)))
        
        # Result label
        self.label = Label(font_size=18, size_hint=(1, 0.5))
        root.add_widget(self.label)
        
        # Back button
        btn = RoundedButton(text='Back to Menu', size_hint=(1, 0.15), bold=True)
        btn.bind(on_press=self.go_back)  # type: ignore
        root.add_widget(btn)
        
        self.add_widget(root)

    def set_result(self, t, correct, mode):
        status = 'CORRECT ✓' if correct else 'INCORRECT ✗'
        status_color = '[color=00aa00]' if correct else '[color=ff0000]'
        mode_display = self._get_mode_name(mode)
        self.label.text = f'[b]Variation:[/b] {mode_display}\n\n[b]Final Time:[/b] {t:.2f}s\n\n[b]{status_color}{status}[/color][/b]'
        self.label.markup = True
        
        # Update best times if correct
        if correct:
            if mode not in self.manager.best_times or self.manager.best_times[mode] is None or t < self.manager.best_times[mode]:
                self.manager.best_times[mode] = t
    
    def _get_mode_name(self, mode):
        names = {
            'standard': 'Standard Keyboard',
            'scrambled': 'Scrambled Keyboard',
            'padlock': 'Standard PadLock',
            'padlock_random': 'Scrambled PadLock'
        }
        return names.get(mode, mode)
    
    def go_back(self, *_):
        setup_screen = self.manager.get_screen('setup')
        setup_screen.update_leaderboard()
        self.manager.current = 'setup'

class AppMain(App):
    def build(self):
        Window.clearcolor = BG
        sm = ScreenManager()
        sm.best_times = {
            'standard': None,
            'scrambled': None,
            'padlock': None,
            'padlock_random': None
        }
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(TestScreen(name='test'))
        sm.add_widget(ResultScreen(name='result'))
        return sm

AppMain().run()
