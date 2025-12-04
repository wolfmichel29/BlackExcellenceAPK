import os
import json
import random
from datetime import date

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import StringProperty, NumericProperty, ListProperty

Window.size = (900, 600)


class WelcomeScreen(Screen):
    pass


class GameScreen(Screen):
    player_name = StringProperty("Player")
    chapter_title = StringProperty("")
    question_text = StringProperty("")
    option1_text = StringProperty("")
    option2_text = StringProperty("")
    option3_text = StringProperty("")
    option4_text = StringProperty("")
    feedback_text = StringProperty("")
    coins_text = StringProperty("0")
    progress_text = StringProperty("")
    progress_value = NumericProperty(0)
    progress_max = NumericProperty(1)
    xp_text = StringProperty("0")

    # per-chapter theme
    bg_source = StringProperty("")
    accent_color = ListProperty([0.12, 0.04, 0.25, 1])
    banner_color = ListProperty([0.15, 0.02, 0.25, 1])
    button_color = ListProperty([0.2, 0.9, 0.9, 1])
    button_down_color = ListProperty([0.9, 0.6, 0.2, 1])

    def animate_coins(self):
        label = self.ids.coin_label
        Animation(font_size=30, d=0.12) + Animation(font_size=20, d=0.12)


class ChapterEndScreen(Screen):
    chapter_title = StringProperty("")
    chapter_result = StringProperty("")
    chapter_accuracy = StringProperty("")
    coins_text = StringProperty("0")
    overall_progress = StringProperty("")


class EndScreen(Screen):
    result_title = StringProperty("Game Complete")
    result_summary = StringProperty("")
    coins_text = StringProperty("0")
    chapter_message = StringProperty("")
    high_score_text = StringProperty("")


class ProfileScreen(Screen):
    profile_summary = StringProperty("")
    stats_text = StringProperty("")


class SkinsScreen(Screen):
    info_text = StringProperty("")
    active_skin_name = StringProperty("")
    coin_balance_text = StringProperty("")


class DailyResultScreen(Screen):
    result_text = StringProperty("")
    streak_text = StringProperty("")
    coins_text = StringProperty("0")


class RewardPopup(ModalView):
    reward_text = StringProperty("")



class AdventureApp(App):
    def build(self):
        self.title = "Black Excellence Word Adventure"

        # runtime state
        self.player_name = "Player"
        self.coins = 0
        self.score = 0
        self.chapter_index = 0
        self.question_index = 0
        self.is_locked = False

        base_dir = os.path.dirname(__file__)
        self.coin_image = os.path.join(base_dir, "images", "coin.png")


        # --- Per-chapter themes (T1: hard switch) ---
        CHAPTER_THEMES = [
            # 1) Black Movies & Cinema
            {
                "bg_image": os.path.join(base_dir, "images", "default_bg.jpg"),
                "music": os.path.join(base_dir, "audio", "cinema_synthwave.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "ping_soft.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_low.wav"),
                "accent_color": [0.20, 0.01, 0.12, 1],
                "banner_color": [0.45, 0.00, 0.20, 1],
                "button_color": [1.00, 0.23, 0.66, 1],
                "button_down_color": [1.00, 0.60, 0.30, 1],
            },
            # 2) Black Scientists & Inventors
            {
                "bg_image": os.path.join(base_dir, "images", "ch2_science.jpg"),
                "music": os.path.join(base_dir, "audio", "tech_glow_loop.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "ping_science.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_error.wav"),
                "accent_color": [0.03, 0.05, 0.18, 1],
                "banner_color": [0.00, 0.24, 0.40, 1],
                "button_color": [0.30, 0.80, 1.00, 1],
                "button_down_color": [0.10, 0.50, 0.90, 1],
            },
            # 3) Black History & Civil Rights
            {
                "bg_image": os.path.join(base_dir, "images", "ch3_history.jpg"),
                "music": os.path.join(base_dir, "audio", "heritage_ambient.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "chime_victory.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_warning.wav"),
                "accent_color": [0.10, 0.04, 0.16, 1],
                "banner_color": [0.25, 0.10, 0.30, 1],
                "button_color": [0.83, 0.71, 0.22, 1],
                "button_down_color": [0.98, 0.82, 0.30, 1],
            },
            # 4) Black Sports Legends
            {
                "bg_image": os.path.join(base_dir, "images", "ch4_sports.jpg"),
                "music": os.path.join(base_dir, "audio", "sports_energy.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "click_score.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_fast.wav"),
                "accent_color": [0.00, 0.10, 0.05, 1],
                "banner_color": [0.00, 0.30, 0.15, 1],
                "button_color": [0.00, 1.00, 0.50, 1],
                "button_down_color": [0.20, 0.80, 0.40, 1],
            },
            # 5) Black Innovation & Technology
            {
                "bg_image": os.path.join(base_dir, "images", "ch5_tech.jpg"),
                "music": os.path.join(base_dir, "audio", "cyberpulse_loop.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "ping_digital.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_glitch.wav"),
                "accent_color": [0.08, 0.02, 0.16, 1],
                "banner_color": [0.18, 0.00, 0.35, 1],
                "button_color": [0.61, 0.35, 1.00, 1],
                "button_down_color": [0.80, 0.55, 1.00, 1],
            },
            # 6) Black Music & Culture
            {
                "bg_image": os.path.join(base_dir, "images", "ch6_music.jpg"),
                "music": os.path.join(base_dir, "audio", "neon_groove.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "ping_beat.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_flat.wav"),
                "accent_color": [0.16, 0.06, 0.03, 1],
                "banner_color": [0.25, 0.08, 0.02, 1],
                "button_color": [1.00, 0.44, 0.26, 1],
                "button_down_color": [1.00, 0.65, 0.30, 1],
            },
            # 7) Black Art, Fashion & Design
            {
                "bg_image": os.path.join(base_dir, "images", "ch7_art.jpg"),
                "music": os.path.join(base_dir, "audio", "studio_ambient.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "chime_soft.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_low2.wav"),
                "accent_color": [0.02, 0.12, 0.16, 1],
                "banner_color": [0.00, 0.30, 0.40, 1],
                "button_color": [0.00, 0.83, 1.00, 1],
                "button_down_color": [0.20, 0.95, 1.00, 1],
            },
            # 8) Black Literature & Storytelling
            {
                "bg_image": os.path.join(base_dir, "images", "ch8_literature.jpg"),
                "music": os.path.join(base_dir, "audio", "literary_ethereal.mp3"),
                "sfx_correct": os.path.join(base_dir, "audio", "ping_glass.wav"),
                "sfx_wrong": os.path.join(base_dir, "audio", "buzz_soft.wav"),
                "accent_color": [0.06, 0.06, 0.16, 1],
                "banner_color": [0.17, 0.19, 0.40, 1],
                "button_color": [0.62, 0.70, 0.96, 1],
                "button_down_color": [0.83, 0.88, 0.98, 1],
            },
        ]

        # --- Skins (Option 1: tint on top of chapter themes) ---
        SKINS = {
            "default": {
                "display_name": "Default Neon",
                "cost": 0,
                "banner_tint": [0, 0, 0, 0],
                "accent_tint": [0, 0, 0, 0],
                "button_tint": [0, 0, 0, 0],
            },
            "electric_blue": {
                "display_name": "Electric Blue",
                "cost": 60,
                "banner_tint": [0.0, 0.1, 0.2, 0],
                "accent_tint": [0.0, 0.1, 0.2, 0],
                "button_tint": [0.0, 0.2, 0.4, 0],
            },
            "hot_pink": {
                "display_name": "Hot Pink Arcade",
                "cost": 75,
                "banner_tint": [0.1, 0.0, 0.1, 0],
                "accent_tint": [0.1, 0.0, 0.1, 0],
                "button_tint": [0.2, 0.0, 0.2, 0],
            },
            "royal_gold": {
                "display_name": "Royal Gold",
                "cost": 100,
                "banner_tint": [0.1, 0.1, 0.0, 0],
                "accent_tint": [0.05, 0.05, 0.0, 0],
                "button_tint": [0.15, 0.12, 0.0, 0],
            },
        }
        self.SKINS = SKINS

        # ✅ Load chapters from JSON file instead of Python
        self.chapters = self.load_questions()

        # attach themes by index
        for i, ch in enumerate(self.chapters):
            if i < len(CHAPTER_THEMES):
                ch["theme"] = CHAPTER_THEMES[i]

        # total questions assumes 10 per chapter in adventure mode
        self.total_questions_per_chapter = 10
        self.total_questions = len(self.chapters) * self.total_questions_per_chapter
        self.chapter_scores = [0 for _ in self.chapters]

        # persistent scores
        self.score_file = os.path.join(base_dir, "scores.json")
        self.scores = self.load_scores()

        # runtime theme / mode
        self.bg_music = None
        self.snd_correct = None
        self.snd_wrong = None
        self.sound_cache = {}
        self.active_theme_index = None
        self.mode = "adventure"         # "adventure" or "daily"
        self.daily_questions = []       # list of (chapter_idx, question_idx)
        self.daily_index = 0
        self.xp = 0

        Builder.load_file("adventure.kv")

        sm = ScreenManager(transition=FadeTransition(duration=0.25))
        sm.add_widget(WelcomeScreen(name="welcome"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(ChapterEndScreen(name="chapter_end"))
        sm.add_widget(EndScreen(name="end"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(SkinsScreen(name="skins"))
        sm.add_widget(DailyResultScreen(name="daily_end"))


        self.sm = sm

        return sm


    #------------------------------------
    #-----LOAD QUESTION FUNCTION---------
    #------------------------------------

    def load_questions(self):
        with open("questions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["chapters"]

    # -------- scores --------
    def load_scores(self):
        default = {
            "best_score": 0,
            "best_accuracy": 0.0,
            "total_coins_earned": 0,      # lifetime earned
            "coin_balance": 0,            # spendable coins for skins
            "highest_chapter_completed": 1,
            "total_correct_all_time": 0,
            "total_questions_all_time": 0,
            "max_coins_single_run": 0,
            "daily_streak": 0,
            "last_daily_date": "",
            "skins_unlocked": ["default"],
            "active_skin": "default",
        }
        if not os.path.exists(self.score_file):
            return default
        try:
            with open(self.score_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k, v in default.items():
                data.setdefault(k, v)
            return data
        except Exception:
            return default

    def save_scores(self):
        try:
            with open(self.score_file, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=4)
        except Exception:
            pass

    def update_scores(self, final_score, accuracy, total_coins):
        # adventure-mode final only
        if final_score > self.scores.get("best_score", 0):
            self.scores["best_score"] = final_score
        if accuracy > self.scores.get("best_accuracy", 0.0):
            self.scores["best_accuracy"] = accuracy

        self.scores["total_coins_earned"] = (
            self.scores.get("total_coins_earned", 0) + total_coins
        )
        self.scores["coin_balance"] = (
            self.scores.get("coin_balance", 0) + total_coins
        )

        self.scores["highest_chapter_completed"] = max(
            self.scores.get("highest_chapter_completed", 1),
            len(self.chapters),
        )

        self.scores["total_correct_all_time"] = (
            self.scores.get("total_correct_all_time", 0) + final_score
        )
        self.scores["total_questions_all_time"] = (
            self.scores.get("total_questions_all_time", 0) + self.total_questions
        )
        self.scores["max_coins_single_run"] = max(
            self.scores.get("max_coins_single_run", 0),
            total_coins,
        )

        self.save_scores()

    # -------- helpers for skins / questions --------
    def get_active_skin(self):
        name = self.scores.get("active_skin", "default")
        return self.SKINS.get(name, self.SKINS["default"])

    def get_all_question_refs(self):
        refs = []
        for ci, ch in enumerate(self.chapters):
            for qi, _ in enumerate(ch["questions"]):
                refs.append((ci, qi))
        return refs

    def group_by_difficulty(self, questions):
        groups = {"easy": [], "medium": [], "hard": []}
        for q in questions:
            difficulty = q.get("difficulty", "easy")
            earned_coins, earned_xp = self.get_reward(difficulty)

        return groups

    # -------- audio / theme --------
    def load_sound(self, path):
        if not path:
            return None
        if path in self.sound_cache:
            return self.sound_cache[path]
        if not os.path.exists(path):
            return None
        snd = SoundLoader.load(path)
        self.sound_cache[path] = snd
        return snd

    def apply_chapter_theme(self):
        if not self.chapters:
            return
        idx = self.chapter_index

        chapter = self.chapters[idx]
        theme = chapter.get("theme", {})
        self.active_theme_index = idx

        game = self.sm.get_screen("game")

        # base colors from chapter
        banner = theme.get("banner_color", game.banner_color)
        accent = theme.get("accent_color", game.accent_color)
        button = theme.get("button_color", game.button_color)
        button_down = theme.get("button_down_color", game.button_down_color)

        # apply skin tint on top (Option 1: keep chapter identity)
        skin = self.get_active_skin()

        def add_color(c, t):
            return [max(0, min(1, c[i] + t[i])) for i in range(4)]

        banner = add_color(banner, skin["banner_tint"])
        accent = add_color(accent, skin["accent_tint"])
        button = add_color(button, skin["button_tint"])
        button_down = [min(1, x * 0.85) for x in button]

        game.banner_color = banner
        game.accent_color = accent
        game.button_color = button
        game.button_down_color = button_down

        if theme.get("bg_image"):
            game.bg_source = theme["bg_image"]

        music_path = theme.get("music")
        if music_path:
            if self.bg_music:
                self.bg_music.stop()
            self.bg_music = self.load_sound(music_path)
            if self.bg_music:
                try:
                    self.bg_music.loop = True
                except Exception:
                    pass
                self.bg_music.volume = 0.4
                self.bg_music.play()

        self.snd_correct = self.load_sound(theme.get("sfx_correct"))
        self.snd_wrong = self.load_sound(theme.get("sfx_wrong"))

    def play_correct_sound(self):
        if self.snd_correct:
            self.snd_correct.stop()
            self.snd_correct.play()

    def play_wrong_sound(self):
        if self.snd_wrong:
            self.snd_wrong.stop()
            self.snd_wrong.play()

    def show_achievement(self, title):
        popup = ModalView(size_hint=(None, None), size=(420, 220))
        lbl = Label(text=f"[b]Achievement Unlocked![/b]\n{title}",
                    markup=True, halign="center", valign="middle")
        lbl.bind(size=lambda *_: setattr(lbl, 'text_size', lbl.size))
        popup.add_widget(lbl)
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)

    def show_reward_popup(self, coins):
        popup = Factory.RewardPopup()
        popup.reward_text = f"[b]+{coins} Coins[/b]"

        # Start tiny + invisible
        popup.size = (300, 185)
        popup.opacity = 0
        popup.open()

        # Animate to full size with bounce
        anim_in = (
                Animation(opacity=1, d=0.15) &
                Animation(size=(420, 260), d=0.35, t="out_back")
        )
        anim_in.start(popup)

        # Auto-dismiss with shrink
        def hide(dt):
            anim_out = (
                    Animation(opacity=0, d=0.2) &
                    Animation(size=(280, 160), d=0.2)
            )
            anim_out.bind(on_complete=lambda *_: popup.dismiss())
            anim_out.start(popup)

        Clock.schedule_once(hide, 1.6)

        # Auto-dismiss with SAFE animation
        def hide(dt):
            anim_out = Animation(opacity=0, d=0.2)
            anim_out.bind(on_complete=lambda *_: popup.dismiss())
            anim_out.start(popup)

        Clock.schedule_once(hide, 1.6)

        # Auto-dismiss after 1.6 seconds with fade out
        def hide(dt):
            anim_out = Animation(opacity=0, d=0.2)

            def _dismiss(*_args):
                popup.dismiss()

            anim_out.bind(on_complete=_dismiss)
            anim_out.start(popup)

        Clock.schedule_once(hide, 1.6)

    def build_daily_pool(self):
        pool = []
        for ci, ch in enumerate(self.chapters):
            for level in ch["questions"]:
                for q in ch["questions"][level]:
                    pool.append((ci, level, q))
        random.shuffle(pool)
        return pool[:5]

    def validate_questions(self):
        for ch in self.chapters:
            for diff in ["easy", "medium", "hard"]:
                for q in ch["questions"][diff]:
                    assert "prompt" in q
                    assert len(q["options"]) == 4
                    assert isinstance(q["answer"], int)

    # -------- fun facts popup --------


    # -------- game flow --------
    def reset_state(self):
        self.coins = 0
        self.score = 0
        self.chapter_index = 0
        self.question_index = 0
        self.is_locked = False
        self.chapter_scores = [0 for _ in self.chapters]
        self.active_theme_index = None

        # XP reset (if you added XP tracking)
        self.xp = 0
        game = self.sm.get_screen("game")
        game.player_name = self.player_name
        game.progress_value = 0
        game.coins_text = "0"
        game.feedback_text = ""
        game.progress_text = ""
        if hasattr(game, "xp_text"):
            game.xp_text = "0"

        # ---- Build 10-question sets per chapter for this run ----
        # Each chapter: random subset of its questions, max 10.
        self.chapter_question_sets = []
        for ch in self.chapters:
            pool = ch["questions"][:]  # copy full list
            random.shuffle(pool)  # shuffle in-place
            self.chapter_question_sets.append(pool[:10])  # take first 10

    def start_game(self):
        welcome = self.sm.get_screen("welcome")
        name_input = welcome.ids.get("name_input")
        entered_name = name_input.text.strip() if name_input else ""
        self.player_name = entered_name if entered_name else "Player"

        self.mode = "adventure"
        self.reset_state()
        self.sm.current = "game"
        self.show_question()

    def start_daily_challenge(self):
        # daily mode: 5 random questions across all chapters
        self.mode = "daily"
        self.reset_state()
        all_refs = self.get_all_question_refs()
        random.shuffle(all_refs)
        self.daily_questions = all_refs[:5]
        self.daily_index = 0
        self.sm.current = "game"
        self.show_question()

    def get_current_question(self):
        # DAILY MODE: uses daily_questions index into full chapters list
        if self.mode == "daily":
            ci, qi = self.daily_questions[self.daily_index]
            return self.chapters[ci]["questions"][qi]

        # ADVENTURE MODE: use the prebuilt 10-question set for this chapter
        chapter_questions = self.chapter_question_sets[self.chapter_index]

        if self.question_index >= len(chapter_questions):
            # Safety: clamp to last question instead of crashing
            return chapter_questions[-1]

        return chapter_questions[self.question_index]

    def current_question_number(self):
        if self.mode == "daily":
            return self.daily_index + 1

        # Adventure mode: count questions based on 10-question sets
        n = 0
        for i, _ in enumerate(self.chapters):
            if i < self.chapter_index:
                n += len(self.chapter_question_sets[i])
        return n + self.question_index + 1

    def show_question(self):
        game = self.sm.get_screen("game")

        # ----- mode-specific flow -----
        if self.mode == "daily":
            if not self.daily_questions or self.daily_index >= len(self.daily_questions):
                self.finish_daily()
                return

            ci, qi = self.daily_questions[self.daily_index]
            self.chapter_index = ci  # theme follows the chapter of the question
            chapter = self.chapters[ci]

        else:
            # adventure mode
            if self.chapter_index >= len(self.chapters):
                self.finish_game()
                return

            chapter = self.chapters[self.chapter_index]
            chapter_questions = self.chapter_question_sets[self.chapter_index]

            # if we've exhausted the 10 for this chapter, move on
            if self.question_index >= len(chapter_questions):
                self.finish_chapter()
                return

        # ----- apply theme based on current chapter -----
        self.apply_chapter_theme()

        # ----- get question -----
        if self.mode == "daily":
            ci, qi = self.daily_questions[self.daily_index]
            q = self.chapters[ci]["questions"][qi]
        else:
            chapter_questions = self.chapter_question_sets[self.chapter_index]
            q = chapter_questions[self.question_index]

        game.chapter_title = chapter["title"]
        game.question_text = q["prompt"]

        # shuffle answers visually but keep index mapping
        options = list(q["options"])
        indices = list(range(len(options)))
        random.shuffle(indices)
        game._option_map = indices

        game.option1_text = options[indices[0]]
        game.option2_text = options[indices[1]]
        game.option3_text = options[indices[2]]
        game.option4_text = options[indices[3]]

        # ----- progress / HUD -----
        question_number = self.current_question_number()
        if self.mode == "daily":
            total = len(self.daily_questions)
            game.progress_max = total
            game.progress_text = f"Daily Question {question_number} of {total}"
        else:
            game.progress_max = self.total_questions
            game.progress_text = f"Question {question_number} of {self.total_questions}"

        game.progress_value = question_number
        game.coins_text = str(self.coins)
        if hasattr(game, "xp_text"):
            game.xp_text = str(getattr(self, "xp", 0))

        if self.mode == "adventure":
            if self.question_index == 0 and question_number != 1:
                game.feedback_text = (
                    f"[b]New Chapter:[/b] {chapter['title']} — Your knowledge is getting better!"
                )
            else:
                if not game.feedback_text.startswith("[b]New Chapter"):
                    game.feedback_text = ""
        else:
            if not game.feedback_text.startswith("[b]Fun Fact"):
                game.feedback_text = ""

        # ----- animations -----
        qlbl = game.ids.get("question_lbl")
        if qlbl:
            qlbl.opacity = 0
            Animation(opacity=1, d=0.25).start(qlbl)

        for opt_id in ("opt1", "opt2", "opt3", "opt4"):
            btn = game.ids.get(opt_id)
            if btn:
                btn.opacity = 0
                btn.y -= 10
                Animation(opacity=1, y=btn.y + 10, d=0.25).start(btn)

        self.is_locked = False

    def check_achievements(self):
        unlocks = []

        if self.score == 5:
            unlocks.append("First 5 Correct")
        if self.score == 10:
            unlocks.append("Rising Scholar")
        if self.coins >= 100:
            unlocks.append("Coin Collector")
        if self.chapter_index == len(self.chapters) - 1:
            unlocks.append("Chapter Master")

        for title in unlocks:
            self.show_achievement(title)

    def on_answer(self, visual_index, button_widget):
        if self.is_locked:
            return
        self.is_locked = True

        self.animate_button_pulse(button_widget)
        Clock.schedule_once(lambda dt: self._process_answer(visual_index), 0.15)

    def _process_answer(self, visual_index):
        game = self.sm.get_screen("game")
        q = self.get_current_question()
        game.xp_text = str(self.xp)

        original_index = game._option_map[visual_index]
        correct_index = q["correct_index"]

        #Change the amount of Coins.
        if original_index == correct_index:
            reward = 25
            xp_gain = q.get("xp", 10)

            self.score += 1
            self.coins += reward
            self.xp += xp_gain

            if self.mode == "adventure":
                self.chapter_scores[self.chapter_index] += 1

            game.feedback_text = "[color=00ffbf]Correct! +25 coins[/color]"
            self.play_correct_sound()
            self.check_achievements()

            self.show_reward_popup(reward)
            self.animate_coin_hud(reward)
            self.animate_coin_fly(reward)

            game.coins_text = str(self.coins)
            game.xp_text = str(self.xp)



        else:
            correct_word = q["options"][correct_index]
            game.feedback_text = (
                f"[color=ff6b6b]Not quite![/color] "
                f"Correct word: [b]{correct_word}[/b]"
            )
            self.play_wrong_sound()
            for opt_id in ("opt1", "opt2", "opt3", "opt4"):
                self._shake_widget(game.ids.get(opt_id))

        game.coins_text = str(self.coins)

        # show fun fact popup then move on
        # move directly to next question (Fun Facts removed)
        Clock.schedule_once(lambda dt: self._next_step(), 0.9)

    def get_daily_bonus(self):
        streak = self.scores.get("daily_streak", 1)
        return min(streak * 10, 100)  # cap at 100 bonus coins

    def get_reward(self, difficulty):
        rewards = {
            "easy": (15, 10),
            "medium": (25, 15),
            "hard": (50, 30)
        }
        return rewards.get(difficulty, (20, 10))

    def animate_coin_hud(self, gained):
        """Quick pop animation on the coins label when coins are earned."""
        game = self.sm.get_screen("game")
        lbl = game.ids.get("coins_lbl")
        if not lbl:
            return

        # Small size pop
        try:
            base_size = float(lbl.font_size)
        except Exception:
            base_size = 20.0

        pop_up = Animation(font_size=base_size * 1.25, d=0.10)
        pop_down = Animation(font_size=base_size, d=0.10)
        (pop_up + pop_down).start(lbl)

    def animate_coin_fly(self, amount):
        game = self.sm.get_screen("game")

        # Create floating coin text
        fly = Label(
            text=f"+{amount}",
            font_size=52,
            bold=True,
            color=(1, 0.9, 0.2, 1),
            size_hint=(None, None)
        )
        fly.texture_update()
        fly.size = fly.texture_size

        # Add to screen
        game.add_widget(fly)

        # Start near center/question box
        start_x = game.center_x - fly.width / 2
        start_y = game.center_y - 40
        fly.pos = (start_x, start_y)

        # Get target = coin label position
        coins_lbl = game.ids.get("coins_lbl")
        if coins_lbl:
            target_x, target_y = coins_lbl.to_window(*coins_lbl.center)
            target_x -= fly.width / 2
        else:
            target_x = game.width - 80
            target_y = game.height - 60

        # Animate fly → HUD
        anim = (
                Animation(pos=(target_x, target_y), d=0.6, t="out_quad") &
                Animation(opacity=0, d=0.6)
        )

        def cleanup(*_):
            game.remove_widget(fly)

        anim.bind(on_complete=cleanup)
        anim.start(fly)

    def _next_step(self):
        # ----- DAILY MODE -----
        if self.mode == "daily":
            if self.daily_index < len(self.daily_questions) - 1:
                self.daily_index += 1
                self.show_question()
            else:
                self.finish_daily()
            return

        # ----- ADVENTURE MODE -----
        chapter_questions = self.chapter_question_sets[self.chapter_index]

        if self.question_index < len(chapter_questions) - 1:
            self.question_index += 1
            self.show_question()
        else:
            # finished this chapter's 10 questions
            self.finish_chapter()

    def animate_button_pulse(self, widget):
        anim1 = Animation(opacity=0.6, d=0.08)
        anim2 = Animation(opacity=1.0, d=0.08)
        (anim1 + anim2).start(widget)

    def _shake_widget(self, widget):
        if not widget:
            return
        x = widget.x
        (Animation(x=x - 8, d=0.05) +
         Animation(x=x + 8, d=0.05) +
         Animation(x=x, d=0.05)).start(widget)

    def finish_chapter(self):
        chapter = self.chapters[self.chapter_index]
        chapter_title = chapter["title"]

        # use limited 10-question set
        chapter_questions = self.chapter_question_sets[self.chapter_index]
        chapter_total = len(chapter_questions)
        chapter_correct = self.chapter_scores[self.chapter_index]
        chapter_accuracy = (
            (chapter_correct / chapter_total) * 100.0 if chapter_total else 0.0
        )

        question_number = self.current_question_number()

        chapter_end = self.sm.get_screen("chapter_end")
        chapter_end.chapter_title = chapter_title
        chapter_end.chapter_result = (
            f"Correct in this chapter: [b]{chapter_correct}[/b] / {chapter_total}"
        )
        chapter_end.chapter_accuracy = f"Chapter accuracy: [b]{chapter_accuracy:.0f}%[/b]"
        chapter_end.coins_text = str(self.coins)
        chapter_end.overall_progress = (
            f"Overall progress: Question {question_number} of {self.total_questions}"
        )

        if self.chapter_index == len(self.chapters) - 1:
            self.finish_game()
        else:
            self.sm.current = "chapter_end"

    def continue_to_next_chapter(self):
        self.chapter_index += 1
        self.question_index = 0
        self.is_locked = False
        self.sm.current = "game"
        self.show_question()

    def back_to_welcome_from_chapter(self):
        self.reset_state()
        self.sm.current = "welcome"

    def finish_game(self):
        total_questions = self.total_questions or 1
        accuracy = (self.score / total_questions) * 100.0
        accuracy_str = f"{accuracy:.0f}%"

        end = self.sm.get_screen("end")
        end.result_title = "Black Excellence Word Adventure has been Completed!"
        end.result_summary = (
            f"[b]{self.player_name}[/b], you journeyed through all 8 chapters.\n\n"
            f"Correct answers: [b]{self.score}[/b] / {total_questions}\n"
            f"Accuracy: [b]{accuracy_str}[/b]"
        )
        end.coins_text = str(self.coins)
        end.chapter_message = (
            "You’ve cleared the entire Black Excellence Knowledge Adventure.\n"
            "Keep exploring, keep learning, keep shining."
        )

        self.update_scores(self.score, accuracy, self.coins)

        best_score = self.scores.get("best_score", 0)
        best_accuracy = self.scores.get("best_accuracy", 0.0)
        total_coins_earned = self.scores.get("total_coins_earned", 0)
        coin_balance = self.scores.get("coin_balance", 0)

        end.high_score_text = (
            f"[b]Best Score:[/b] {best_score}  |  "
            f"[b]Best Accuracy:[/b] {best_accuracy:.0f}%\n"
            f"[b]Total Coins Earned:[/b] {total_coins_earned}  |  "
            f"[b]Coin Balance:[/b] {coin_balance}"
        )

        self.sm.current = "end"

    def finish_daily(self):
        total = len(self.daily_questions) or 1
        accuracy = (self.score / total) * 100.0

        today_str = date.today().isoformat()
        last = self.scores.get("last_daily_date", "")

        if last == today_str:
            # already logged today; keep streak as-is
            pass
        else:
            if last:
                last_date = date.fromisoformat(last)
                delta = (date.today() - last_date).days
                if delta == 1:
                    self.scores["daily_streak"] = self.scores.get("daily_streak", 0) + 1
                else:
                    self.scores["daily_streak"] = 1
            else:
                self.scores["daily_streak"] = 1
            self.scores["last_daily_date"] = today_str

        # update coins & global stats
        self.scores["total_coins_earned"] = (
            self.scores.get("total_coins_earned", 0) + self.coins
        )
        self.scores["coin_balance"] = (
            self.scores.get("coin_balance", 0) + self.coins
        )
        self.scores["total_correct_all_time"] = (
            self.scores.get("total_correct_all_time", 0) + self.score
        )
        self.scores["total_questions_all_time"] = (
            self.scores.get("total_questions_all_time", 0) + total
        )
        self.scores["max_coins_single_run"] = max(
            self.scores.get("max_coins_single_run", 0),
            self.coins,
        )
        self.save_scores()

        scr = self.sm.get_screen("daily_end")
        scr.result_text = (
            f"Daily Challenge Complete!\n\n"
            f"Correct: {self.score} / {total}\n"
            f"Accuracy: {accuracy:.0f}%"
        )
        bonus = self.get_daily_bonus()
        self.coins += bonus
        self.scores["coin_balance"] += bonus

        scr.result_text += f"\n\nDaily Bonus: +{bonus} coins"

        scr.coins_text = str(self.coins)
        scr.streak_text = f"Current Daily Streak: {self.scores.get('daily_streak', 0)} days"

        self.sm.current = "daily_end"

    def open_profile(self):
        scr = self.sm.get_screen("profile")
        total_correct = self.scores.get("total_correct_all_time", 0)
        total_questions = self.scores.get("total_questions_all_time", 0)
        avg_acc = (total_correct / total_questions) * 100.0 if total_questions else 0.0
        best_score = self.scores.get("best_score", 0)
        best_acc = self.scores.get("best_accuracy", 0.0)
        total_coins_all = self.scores.get("total_coins_earned", 0)
        coin_balance = self.scores.get("coin_balance", 0)
        streak = self.scores.get("daily_streak", 0)

        scr.profile_summary = (
            f"Player: [b]{self.player_name}[/b]\n"
            f"Best Score: [b]{best_score}[/b]\n"
            f"Best Accuracy: [b]{best_acc:.0f}%[/b]"
        )
        scr.stats_text = (
            f"Total Correct (all time): {total_correct}\n"
            f"Total Questions Seen: {total_questions}\n"
            f"Average Accuracy: {avg_acc:.0f}%\n"
            f"Total Coins Earned: {total_coins_all}\n"
            f"Coin Balance: {coin_balance}\n"
            f"Daily Streak: {streak} days"
        )

        self.sm.current = "profile"

    def open_skins(self):
        scr = self.sm.get_screen("skins")
        unlocked = set(self.scores.get("skins_unlocked", ["default"]))
        active = self.scores.get("active_skin", "default")

        info_lines = []
        for key, data in self.SKINS.items():
            status = "[unlocked]" if key in unlocked else f"[cost: {data.get('cost', 0)}]"
            star = "★" if key == active else " "
            info_lines.append(f"{star} {data['display_name']}  {status}")
        scr.info_text = "\n".join(info_lines)
        scr.active_skin_name = self.SKINS.get(active, self.SKINS["default"])["display_name"]
        scr.coin_balance_text = f"Coin balance: {self.scores.get('coin_balance', 0)}"
        self.sm.current = "skins"

    def unlock_skin(self, skin_key):
        if skin_key not in self.SKINS:
            return

        unlocked = set(self.scores.get("skins_unlocked", ["default"]))
        if skin_key in unlocked:
            return  # already unlocked

        cost = self.SKINS[skin_key].get("cost", 0)
        balance = self.scores.get("coin_balance", 0)
        if balance < cost:
            # not enough coins
            return

        # deduct and unlock
        self.scores["coin_balance"] = balance - cost
        unlocked.add(skin_key)
        self.scores["skins_unlocked"] = list(unlocked)
        self.save_scores()
        self.open_skins()

    def set_active_skin(self, skin_key):
        unlocked = set(self.scores.get("skins_unlocked", ["default"]))
        if skin_key not in unlocked:
            return
        self.scores["active_skin"] = skin_key
        self.save_scores()
        self.open_skins()

    def play_again(self):
        # default: restart adventure mode
        self.mode = "adventure"
        self.reset_state()
        self.sm.current = "game"
        self.show_question()

    def quit_app(self):
        if self.bg_music:
            self.bg_music.stop()
        self.stop()


if __name__ == "__main__":
    AdventureApp().run()
