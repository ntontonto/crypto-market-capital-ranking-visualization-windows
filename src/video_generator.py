
from manim import *
import json
import datetime

class CryptoRankingShorts(Scene):
    def construct(self):
        # Configuration
        self.camera.background_color = "#1e1e1e"
        # 9:16 aspect ratio setup
        # Manim default height is 8.0 units. 
        # Width for 9:16 should be 8.0 * (9/16) = 4.5
        # However, Manim usually fits width to 14.22 (16:9).
        # We need to act as if we are in portrait. 
        # A common trick is to use a custom config or just build within a vertical frame.
        # But Manim Community supports setting pixel width/height in config.
        # We will assume the CLI command sets the resolution to 1080x1920 or similar.
        
        # Load Data
        # In a real run, we might pass data in via a temporary file or environment variable.
        # For simplicity, we'll read the latest cache file here or a specific passed file.
        # But wait, Scene classes are instantiated by Manim. Passing arguments is tricky.
        # Best practice: Read a standard "current_data.json" file that main.py prepared.
        
        try:
            with open("current_data.json", "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            # Fallback dummy data for testing render without main.py
            self.data = self._get_dummy_data()

        # --- SCENE A: Title (0-5s) ---
        title_group = self._create_title_scene()
        self.play(Write(title_group), run_time=2)
        self.wait(2)
        self.play(FadeOut(title_group, shift=UP))

        # --- SCENE B: Ranking (5-45s) ---
        # Page 1: 1-10
        self._show_ranking_page(self.data[:10], page_num=1)
        # Page 2: 11-20
        self._show_ranking_page(self.data[10:20], page_num=2)

        # --- SCENE C: Highlights (45-60s) ---
        self._show_highlights()

    def _create_title_scene(self):
        # Dynamic Date
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        title = Text("Crypto Market Cap", font_size=48, color=BLUE)
        subtitle = Text("Top 20 Ranking", font_size=60, weight=BOLD)
        date_text = Text(f"as of {date_str}", font_size=24, color=GRAY)
        
        title_group = VGroup(title, subtitle, date_text).arrange(DOWN, buff=0.5)
        return title_group

    def _show_ranking_page(self, page_data, page_num):
        # Header
        header = Text(f"Top {1 + (page_num-1)*10} - {page_num*10}", font_size=36, color=YELLOW)
        header.to_edge(UP, buff=1.0)
        self.play(FadeIn(header))
        
        rows = VGroup()
        for i, item in enumerate(page_data):
            rank = Text(f"#{item['rank']}", font_size=24, color=GRAY, width=0.8)
            symbol = Text(item['symbol'], font_size=24, weight=BOLD, width=1.2)
            
            price_val = item['price'] if item['price'] > 1 else f"{item['price']:.4f}"
            price = Text(f"${price_val}", font_size=24, color=WHITE, width=2.0).set_alignment_with_box_content(RIGHT)
            
            # Change color
            change_val = item['change_24h'] or 0
            c_color = GREEN if change_val >= 0 else RED
            change = Text(f"{change_val:.1f}%", font_size=24, color=c_color, width=1.2).set_alignment_with_box_content(RIGHT)
            
            row = VGroup(rank, symbol, price, change).arrange(RIGHT, buff=0.4)
            # Align row to left/center
            rows.add(row)

        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        rows.next_to(header, DOWN, buff=0.5)
        
        # Staggered animation
        self.play(
            LaggedStart(*[FadeIn(row, shift=RIGHT) for row in rows], lag_ratio=0.1), 
            run_time=3
        )
        self.wait(15) # Wait to read
        self.play(FadeOut(rows), FadeOut(header))

    def _show_highlights(self):
        # Sort data
        sorted_data = sorted(self.data, key=lambda x: x['change_24h'] or 0, reverse=True)
        top_gainers = sorted_data[:3]
        top_losers = sorted_data[-3:]
        
        title = Text("MOVERS (24h)", font_size=48, color=GOLD).to_edge(UP, buff=1.5)
        
        # Gainers
        g_label = Text("Top Gainers", font_size=32, color=GREEN).next_to(title, DOWN, buff=0.5)
        g_group = self._create_highlight_group(top_gainers, GREEN)
        g_group.next_to(g_label, DOWN, buff=0.3)
        
        # Losers
        l_label = Text("Top Losers", font_size=32, color=RED).next_to(g_group, DOWN, buff=0.8)
        l_group = self._create_highlight_group(top_losers, RED)
        l_group.next_to(l_label, DOWN, buff=0.3)
        
        group = VGroup(title, g_label, g_group, l_label, l_group)
        self.play(FadeIn(group, shift=UP))
        self.wait(10)

    def _create_highlight_group(self, items, color):
        grp = VGroup()
        for item in items:
            t = Text(f"{item['symbol']}   {item['change_24h']:.1f}%", font_size=36, color=color)
            grp.add(t)
        grp.arrange(DOWN, buff=0.2)
        return grp

    def _get_dummy_data(self):
        return [
            {"rank": i, "name": f"Coin{i}", "symbol": f"C{i}", "price": 100+i, "market_cap": 1000000, "change_24h": 5.5}
            for i in range(1, 21)
        ]
