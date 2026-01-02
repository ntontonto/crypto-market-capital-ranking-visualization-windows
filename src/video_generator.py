from manim import *
import json
import datetime
import numpy as np
import math

# Configure for Vertical 9:16
config.pixel_height = 1920
config.pixel_width = 1080
config.frame_height = 16.0
config.frame_width = 9.0

class CryptoRankingShorts(Scene):
    def construct(self):
        # Configuration
        self.camera.background_color = "#1e1e1e"
        self.camera.frame_height = 16
        self.camera.frame_width = 9
        
        # Load Data
        try:
            with open("current_input.json", "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = self._get_dummy_data() # This implies _get_dummy_data() should exist. It doesn't in original.
            # For now, let's make it return an empty dict if not found, or handle it.
            # Based on the original code, it would return. Let's keep that behavior for now.
            print("Error: current_input.json not found. Run main.py first.")
            return

        # Scene 1: Ranking Chart (Dynamic Line Graph)
        self.render_ranking_chart(duration=35)
        
        # Scene 2: Top Movers
        self.clear() # Clear chart
        self.render_movers(duration=15)
        
        # Scene 3: Dominance
        self.clear()
        self.render_dominance(duration=10)

    def _get_dummy_data(self):
        # Placeholder for dummy data if file not found
        # This method was introduced in the provided `construct` body,
        # but not defined elsewhere. Adding a basic placeholder.
        print("Using dummy data as current_input.json was not found.")
        return {
            "top10_7d": [
                {"date": "2023-01-01", "items": [{"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "market_cap": 500e9}]},
                {"date": "2023-01-02", "items": [{"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin", "market_cap": 510e9}]},
            ],
            "today_top_movers": {},
            "dominance": {"series": []}
        }

    def render_ranking_chart(self, duration=35):
        # 1. Processing Data
        top_data = self.data.get("top10_7d", [])
        if not top_data:
            return

        # Pivot data: coin_id -> list of (day_index, market_cap)
        # We need to handle that a coin might not be in the top 10 on some days.
        # But for smooth lines, we ideally need data for all days if possible.
        # Since our fetcher gets history for top 30, the 'top10_7d' in input.json 
        # is structured as "Top 10 of that day". 
        # If a coin drops out of top 10, it disappears from this list.
        # Ideally we should have passed the full history of top coins in input.json.
        # Assuming the fetcher does the job, we'll connect points we have.
        
        coin_series = {}
        all_mcaps = []
        days = []
        
        for day_idx, day_entry in enumerate(top_data):
            date_str = day_entry.get('date', f"Day {day_idx}")
            # Shorten date for axis labels "12-27"
            try:
                # Validate date format but store full string
                datetime.datetime.strptime(date_str, "%Y-%m-%d")
                days.append(date_str)
            except:
                days.append(str(day_idx))
                
            for item in day_entry.get('items', []):
                cid = item['id']
                mcap = item['market_cap']
                symbol = item['symbol'].upper()
                
                if cid not in coin_series:
                    coin_series[cid] = {
                        "color": self._get_coin_color(symbol),
                        "symbol": symbol,
                        "data": []
                    }
                coin_series[cid]["data"].append((day_idx, mcap))
                all_mcaps.append(mcap)

        # 2. Setup Axes (Logarithmic Y)
        # 2. Setup Axes
        # Calculate Y-Range (Growth Rate)
        # We need to normalize current series to start=100
        # Check global min/max of normalized data
        
        details_map = {} # cid -> {coords: [[d, val], ...], color, symbol}
        all_y_values = []
        
        for cid, info in coin_series.items():
            raw_data = info['data']
            if not raw_data:
                continue
            
            # Find start value (first data point)
            # Assuming raw_data is sorted by date index 0..6
            start_val = raw_data[0][1]
            if start_val <= 0:
                continue # Can't normalize
                
            normalized_coords = []
            for day_i, mc in raw_data:
                norm_val = (mc / start_val) * 100.0
                normalized_coords.append([day_i, norm_val])
                all_y_values.append(norm_val)
                
            details_map[cid] = {
                "coords": normalized_coords,
                "color": info['color'],
                "symbol": info['symbol']
            }
            
        # Filter Top 5 and Bottom 5 Growth
        # Sort by final value (last day's normalized value)
        sorted_cids = sorted(details_map.keys(), key=lambda c: details_map[c]['coords'][-1][1], reverse=True)
        
        selected_cids = []
        if len(sorted_cids) <= 10:
            selected_cids = sorted_cids
        else:
            # Top 5
            selected_cids.extend(sorted_cids[:5])
            # Bottom 5 (reversed order for chart logic? No just standard list)
            # Ensure no duplicates if list is small (handled by <= 10 check)
            selected_cids.extend(sorted_cids[-5:])
            
        # Filter details_map
        details_map = {k: details_map[k] for k in selected_cids}
        
        # Re-calculate y-range based on selected coins only?
        # Or keep global context? Global context is better so we see they are outliers?
        # User asked to "only show", usually meaningful if axes scale to them.
        # Let's re-calculate Y-range for clarity.
        
        all_y_values = []
        for d in details_map.values():
            for _, val in d['coords']:
                all_y_values.append(val)
            
        if not all_y_values:
            y_min, y_max = 90, 110
        else:
            y_min = min(all_y_values)
            y_max = max(all_y_values)
            y_min = math.floor(y_min / 5) * 5 - 5
            y_max = math.ceil(y_max / 5) * 5 + 5
            
        axes = Axes(
            x_range=[0, 6, 1],
            y_range=[y_min, y_max, (y_max - y_min) / 5],
            x_length=9,
            y_length=12,
            axis_config={"color": "#444444"},
            tips=False
        ).to_edge(DOWN, buff=2.0)
        
        x_labels = VGroup()
        if len(days) == 7:
            for i, d_str in enumerate(days):
                dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                lab = Text(dt.strftime("%m/%d"), font_size=20, color=GRAY).next_to(axes.c2p(i, y_min), DOWN, buff=0.2)
                x_labels.add(lab)
                
        y_labels = VGroup()
        if (y_max - y_min) > 0:
            y_step = (y_max - y_min) / 5
            y_steps = np.arange(y_min, y_max + 0.001, y_step)
            for val in y_steps:
                lab = Text(f"{int(val)}", font_size=24, color=GRAY).next_to(axes.c2p(0, val), LEFT, buff=0.2)
                y_labels.add(lab)

        # Baseline at 100
        baseline = DashedLine(
            start=axes.c2p(0, 100),
            end=axes.c2p(6, 100),
            color=GRAY,
            stroke_opacity=0.5
        )

        title_str = "Market Cap Growth"
        if len(days) >= 2:
            try:
                start_d = datetime.datetime.strptime(top_data[0]['date'], "%Y-%m-%d").strftime("%m/%d")
                end_d = datetime.datetime.strptime(top_data[-1]['date'], "%Y-%m-%d").strftime("%m/%d")
                title_str += f" ({start_d} - {end_d})"
            except:
                title_str += " (7 Days)"
                
        title = Text(title_str, font_size=36, weight=BOLD).to_edge(UP, buff=1.0)
        
        self.play(
            FadeIn(axes),
            FadeIn(x_labels),
            FadeIn(y_labels),
            Create(baseline),
            Write(title),
            run_time=2
        )

        # 3. Animation
        time_tracker = ValueTracker(0)

        lines_group = VGroup()
        labels_group = VGroup()
        
        coin_mobjects = {} 

        for cid, details in details_map.items():
            coords = details['coords']
            color = details['color']
            sym = details['symbol']
            
            if len(coords) < 2:
                continue 
                
            line = VMobject(color=color, stroke_width=4)
            full_points = [axes.c2p(x, y) for x, y in coords]
            line.set_points_as_corners(full_points)
            
            label_container = VGroup()
            dot = Dot(color=color, radius=0.1)
            
            # Label: SYM (+13.5%)
            # We use a VGroup for text parts to keep them aligned
            sym_text = Text(sym, font_size=24, weight=BOLD, color=color)
            
            # Decimal Number for dynamic percentage
            # We want "(+13.5%)" format. 
            # DecimalNumber handles the number and sign.
            # We add parentheses manually?
            # Creating a custom updater for the whole label string is easier for formatting "(...)"
            
            # Let's use DecimalNumber for smooth number animation, and static braces.
            # Layout: Dot | Sym | ( | Num | % | )
            
            qt_open = Text("(", font_size=20, color=color)
            # Use Text instead of DecimalNumber to avoid LaTeX dependency
            pct_num = Text("+0.0", font_size=20, color=color) 
            pct_sym = Text("%)", font_size=20, color=color) # combine % and )
            
            # Alignment
            sym_text.next_to(dot, RIGHT, buff=0.1)
            qt_open.next_to(sym_text, RIGHT, buff=0.15)
            pct_num.next_to(qt_open, RIGHT, buff=0.05)
            pct_sym.next_to(pct_num, RIGHT, buff=0.05)
            
            # Add updaters to keep relative positions
            # When pct_num changes width (e.g. 9.9 -> 10.0), following elements should shift?
            # We can use add_updater on the group or individual items.
            # Simplest is to re-arrange in the line updater.
            
            label_container.add(dot, sym_text, qt_open, pct_num, pct_sym)
            
            coin_mobjects[cid] = {
                "line_full": line, 
                "line_shown": VMobject(color=color, stroke_width=4), 
                "label": label_container,
                "pct_num": pct_num, # Refernece to update value
                "label_parts": [sym_text, qt_open, pct_num, pct_sym], # For re-alignment
                "data_points": coords 
            }
            
            lines_group.add(coin_mobjects[cid]["line_shown"])
            labels_group.add(label_container)
            
        # Add Groups to Scene
        # IMPORTANT: lines_group must be in the scene for its updater to run!
        self.add(lines_group, labels_group)

        # Setup Updaters
        def update_lines(mob):
            t = time_tracker.get_value()
            
            for cid, objs in coin_mobjects.items():
                # full_line = objs["line_full"] # Not needed here
                shown_line = objs["line_shown"]
                label = objs["label"]
                points = objs["data_points"]
                pct_num = objs["pct_num"]
                parts = objs["label_parts"] # sym, (, num, %)
                
                # If t < first point x, or no points, hide
                if not points or t < points[0][0]:
                    shown_line.set_points([])
                    label.set_opacity(0)
                    continue
                
                label.set_opacity(1)
                
                # Filter points strictly in the past
                past_points = [p for p in points if p[0] <= t]
                
                if not past_points:
                    shown_line.set_points([])
                    label.set_opacity(0)
                    continue
                
                # Build points list
                current_poly_points = [axes.c2p(p[0], p[1]) for p in past_points]
                current_val = past_points[-1][1] # Default to last known point
                
                last_p = past_points[-1]
                idx_last = points.index(last_p)
                
                # Interpolate if we are not exactly at the end and there is a next point
                if idx_last < len(points) - 1:
                    next_p = points[idx_last + 1]
                    
                    # Prevent division by zero if delta x is 0 (shouldn't happen with days)
                    dx = next_p[0] - last_p[0]
                    if dx > 0:
                        alpha = (t - last_p[0]) / dx
                        # Clamp alpha
                        alpha = max(0, min(1, alpha))
                        
                        current_y = last_p[1] + (next_p[1] - last_p[1]) * alpha
                        current_val = current_y # Real interpolated value
                        
                        new_tip = axes.c2p(t, current_y)
                        current_poly_points.append(new_tip)
                
                if len(current_poly_points) > 0:
                    shown_line.set_points_as_corners(current_poly_points)
                    tip_pos = current_poly_points[-1]
                    
                    # Update Value
                    pct_val = current_val - 100
                    # Create new text object
                    new_text = Text(f"{pct_val:+.1f}", font_size=20, color=objs['line_shown'].get_color())
                    # Position it relative to others?
                    # Since we are using become(), position might reset or needs setting.
                    # Actually become() adopts the position of the new mobject, which is default.
                    # We need to manually match position? 
                    # Better to update, then just let the layout alignment code below handle it.
                    pct_num.become(new_text)
                    
                    # Re-align Label Parts
                    # parts: [sym, (, num, %)]
                    # dot is label[0]
                    dot = label[0]
                    dot.move_to(tip_pos)
                    
                    parts[0].next_to(dot, RIGHT, buff=0.1)
                    parts[1].next_to(parts[0], RIGHT, buff=0.15)
                    pct_num.next_to(parts[1], RIGHT, buff=0.05) # Need to explicitly re-align pct_num
                    parts[3].next_to(pct_num, RIGHT, buff=0.05) # Text

        # Attach updater
        lines_group.add_updater(update_lines)
        
        # Animate
        self.play(
            time_tracker.animate.set_value(6),
            run_time=duration - 5,
            rate_func=linear
        )
        
        lines_group.remove_updater(update_lines)
        self.wait(3)

    def _get_coin_color(self, symbol):
        colors = {
            "BTC": "#F7931A", # Bitcoin Orange
            "ETH": "#627EEA", # Ethereum Blue
            "USDT": "#26A17B", # Tether Green
            "BNB": "#F3BA2F", # Binance Yellow
            "SOL": "#14F195", # Solana Green
            "XRP": "#FFFFFF", # XRP Black/Grey -> Maybe use White/Silver for dark bg
            "USDC": "#2775CA", # USDC Blue
            "ADA": "#0033AD", # Cardano
            "DOGE": "#C2A633", # Doge
            "AVAX": "#E84142", # Avalanche
        }
        return colors.get(symbol, WHITE) # Default

    def render_movers(self, duration):
        # Prefer weekly_top_movers, fallback to today_top_movers
        weekly_data = self.data.get("weekly_top_movers")
        daily_data = self.data.get("today_top_movers")
        
        if weekly_data and weekly_data.get("gainers"):
            movers = weekly_data
            title_text = "7 Days Top Movers"
            pct_key = "change_7d_pct"
            print(f"DEBUG: Using Weekly Movers: {len(movers.get('gainers', []))} gainers")
        else:
            movers = daily_data or {}
            title_text = "24h Top Movers"
            pct_key = "change_24h_pct"
            print(f"DEBUG: Using Daily Movers: {len(movers.get('gainers', []))} gainers")
            
        gainers = movers.get("gainers", [])
        losers = movers.get("losers", [])
        
        # Title
        title = Text(title_text, font_size=48, color=GOLD).to_edge(UP, buff=1.5)
        self.play(Write(title))
        
        # Layout
        # Gainers on Left, Losers on Right
        # Or top/bottom? Left/Right is better for vertical video?
        # Actually vertical video is narrow. Maybe Gainers Top, Losers Bottom?
        # Let's do Gainers (Green) followed by Losers (Red) list.
        
        # Helper to create row
        def create_row(item, is_gainer):
            color = GREEN if is_gainer else RED
            sym = item['name'] # or symbol
            price = item['price']
            pct = item[pct_key]
            
            row = VGroup()
            # Symbol
            t_sym = Text(sym, font_size=32, weight=BOLD)
            # Price
            if price > 1.0:
                p_str = f"${price:,.2f}"
            else:
                p_str = f"${price:.4f}"
            t_price = Text(p_str, font_size=24, color=GRAY)
            # Pct
            sign = "+" if pct > 0 else ""
            t_pct = Text(f"{sign}{pct:.1f}%", font_size=32, color=color)
            
            # Use columns?
            # 3 columns: Sym (Left), Price (Center), Pct (Right)
            # Adjust for vertical width (1080px is plenty)
            
            row.add(t_sym, t_price, t_pct)
            row.arrange(RIGHT, buff=0.5)
            return row

        # Gainers Group
        g_group = VGroup()
        if gainers:
            head = Text("Gainers", font_size=36, color=GREEN).to_edge(LEFT, buff=1.0)
            g_group.add(head)
            for item in gainers[:3]:
                r = create_row(item, True)
                g_group.add(r)
            g_group.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
            g_group.to_edge(LEFT, buff=1.0).shift(UP * 1.0)
            
        # Losers Group
        l_group = VGroup()
        if losers:
            head = Text("Losers", font_size=36, color=RED).to_edge(LEFT, buff=1.0)
            l_group.add(head)
            for item in losers[:3]:
                r = create_row(item, False)
                l_group.add(r)
            l_group.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
            # Position below gainers
            if gainers:
                l_group.next_to(g_group, DOWN, buff=1.0)
            else:
                l_group.to_edge(LEFT, buff=1.0)
                
        # Animation
        if gainers:
            self.play(FadeIn(g_group, shift=RIGHT))
        if losers:
            self.play(FadeIn(l_group, shift=RIGHT))
        # Wait remaining time
        # We used ~ 6 * 0.8 = 4.8s + startup 1s = ~6s.
        # Total duration 15s.
        self.wait(duration - 6)

    def render_dominance(self, duration):
        # Data: dominance.series (list of {date, btc_pct, eth_pct, stable_pct})
        series = self.data.get("dominance", {}).get("series", [])
        if not series:
            return
            
        current = series[-1]
        start = series[0]
        
        # Calculate Deltas
        btc_delta = current['btc_pct'] - start['btc_pct']
        eth_delta = current['eth_pct'] - start['eth_pct']
        stable_delta = current['stable_pct'] - start['stable_pct']
        
        # Title
        title = Text("Market Dominance", font_size=48, color=BLUE).to_edge(UP, buff=2.0)
        self.play(FadeIn(title))
        
        # Lines
        # BTC
        btc_line = self._create_dom_line("Bitcoin", current['btc_pct'], btc_delta, ORANGE)
        btc_line.shift(UP * 0.5)
        
        # ETH
        eth_line = self._create_dom_line("Ethereum", current['eth_pct'], eth_delta, PURPLE)
        eth_line.next_to(btc_line, DOWN, buff=1.0)
        
        # Stable
        stable_line = self._create_dom_line("Stablecoins", current['stable_pct'], stable_delta, GREEN)
        stable_line.next_to(eth_line, DOWN, buff=1.0)
        
        self.play(
            FadeIn(btc_line, shift=RIGHT),
            FadeIn(eth_line, shift=RIGHT),
            FadeIn(stable_line, shift=RIGHT),
            run_time=2
        )
        
        self.wait(duration - 3)

    def _create_dom_line(self, label, value, delta, color):
        grp = VGroup()
        name = Text(label, font_size=36, color=WHITE, weight=BOLD)
        
        val_str = f"{value:.1f}%"
        val = Text(val_str, font_size=36, color=color)
        
        # Delta
        sign = "+" if delta >= 0 else ""
        delta_str = f"({sign}{delta:.1f}pt)"
        d_color = GREEN if delta >= 0 else RED
        d_val = Text(delta_str, font_size=24, color=d_color)
        
        # Layout: Name ..... Value (Delta)
        # Fixed width layout
        name.move_to(LEFT * 2)
        val.move_to(RIGHT * 1)
        d_val.next_to(val, RIGHT, buff=0.2)
        
        grp.add(name, val, d_val)
        return grp
