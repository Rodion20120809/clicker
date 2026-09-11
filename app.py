import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy import platform
from kivy.properties import NumericProperty, StringProperty  # ДОДАНО: властивість для теми
from kivy.clock import Clock
from kivy.animation import Animation  # Модуль для анімацій
from kivy.core.audio import SoundLoader  # ДОДАНО: завантаження музики та звукових ефектів

# Розмір вікна
if platform != 'android':
    Window.size = (450, 900)


class Fish(Image):
    hp_current = 0
    timer_hide = None
    timer_show = None

    def on_kv_post(self, base_widget):
        self.GAME_SCREEN = self.parent.parent
        return super().on_kv_post(base_widget)

    def new_fish(self, *args):
        self.source = 'assets/images/fish_01.png'
        self.hp_current = 10
        self.show_fish()

    def show_fish(self, *args):
        # Плавна поява риби за 0.2 секунди
        Animation.cancel_all(self)
        anim = Animation(opacity=1, duration=0.2)
        anim.start(self)

        time_visible = random.uniform(0.5, 2)
        self.timer_hide = Clock.schedule_once(self.hide_fish, time_visible)

    def hide_fish(self, *args):
        # Плавне зникання риби за 0.2 секунди
        Animation.cancel_all(self)
        anim = Animation(opacity=0, duration=0.2)
        anim.start(self)

        time_hidden = random.uniform(1.0, 3.0)
        self.timer_show = Clock.schedule_once(self.show_fish, time_hidden)

    def stop_timers(self):
        if self.timer_hide:
            self.timer_hide.cancel()
        if self.timer_show:
            self.timer_show.cancel()

    def defeated(self):
        Animation.cancel_all(self)
        # Швидке згасання при остаточному програші риби
        anim = Animation(opacity=0, duration=0.15)
        anim.start(self)
        self.stop_timers()

    # КЛІК ПО РИБІ
    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) or not self.opacity:
            return super().on_touch_down(touch)

        self.hp_current -= 1
        self.GAME_SCREEN.score += 1
        app.play_fish_sound()  # ДОДАНО: звук влучання по рибі

        # Анімація пульсації: миттєве зменшення і повернення розміру
        anim_click = (
            Animation(size_hint=(0.85, 0.55), duration=0.1) +
            Animation(size_hint=(1, 0.65), duration=0.1)
        )
        anim_click.start(self)

        if self.hp_current <= 0:
            self.defeated()
            Clock.schedule_once(self.GAME_SCREEN.level_complete, 0.5)
        else:
            self.stop_timers()
            # Чекаємо 0.1с, поки відпрацює анімація уколу, і ховаємо рибу
            Clock.schedule_once(self.hide_fish, 0.2)

        return True


class MenuScreen(Screen):
    def go_game(self, *args):
        self.manager.current = "game"

    def go_settings(self, *args):
        self.manager.current = "settings"

    def exit_app(self, *args):
        app.stop()


class GameScreen(Screen):
    score = NumericProperty(0)

    def on_pre_enter(self, *args):
        self.score = 0
        self.ids.level_complete.opacity = 0
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        self.start_game()
        return super().on_enter(*args)

    def start_game(self):
        self.ids.fish.new_fish()

    def level_complete(self, *args):
        # Плавна поява привітання про проходження рівня
        anim = Animation(opacity=1, duration=0.4)
        anim.start(self.ids.level_complete)

    def go_menu(self, *args):
        self.manager.current = "menu"

    # КЛІК ПО ЕКРАНУ
    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.ids.fish.hp_current > 0:
            self.score = max(0, self.score - 1)
            self.ids.fish.hp_current += 1
        return True


class SettingsScreen(Screen):
    def go_menu(self, *args):
        self.manager.current = "menu"


class ClickerApp(App):
    # ДОДАНО: поточна тема; її значення читає файл clicker.kv.
    theme = StringProperty("light")

    # ДОДАНО: звуки завантажуються один раз після запуску застосунку.
    def on_start(self):
        self.button_sound = SoundLoader.load("assets/sounds/Menu Selection Click.wav")
        self.fish_sound = SoundLoader.load("assets/sounds/Menu Selection Click.wav")
        self.music_sound = None
        self.play_music("Path to Lake Land.ogg")  # ДОДАНО: запускаємо перший трек зі списку нижче.

    # ДОДАНО: змінює кольорову тему без перезапуску застосунку.
    def set_theme(self, theme):
        self.theme = theme

    # ДОДАНО: відтворює короткий звук натискання кнопки.
    def play_button_sound(self):
        if self.button_sound:
            self.button_sound.stop()
            self.button_sound.play()

    # ДОДАНО: відтворює короткий звук влучання по рибі.
    def play_fish_sound(self):
        if self.fish_sound:
            self.fish_sound.stop()
            self.fish_sound.play()

    # ДОДАНО: зупиняє попередній трек та запускає вибраний фоновий трек.
    def play_music(self, track_name):
        if self.music_sound:
            self.music_sound.stop()

        # ДОДАНО: точні назви двох фонових треків у папці assets/sounds.
        self.music_sound = SoundLoader.load("assets/sounds/"+track_name)
        if self.music_sound:
            self.music_sound.loop = True
            self.music_sound.volume = 0.4
            self.music_sound.play()

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


app = ClickerApp()
app.run()
