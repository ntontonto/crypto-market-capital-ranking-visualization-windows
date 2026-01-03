
from datetime import datetime

class VideoMetadataGenerator:
    def __init__(self, input_data):
        self.data = input_data
        self.as_of = input_data.get("asOf", "").split("T")[0]
        # Support both keys for backward compatibility or schema variance
        self.top_movers = input_data.get("weekly_top_movers") or input_data.get("today_top_movers", {})
        self.gainers = self.top_movers.get("gainers", [])
        self.losers = self.top_movers.get("losers", [])

    def get_title(self) -> str:
        """
        Generates a title focusing on the top gainer.
        Format: Crypto Ranking {Date}: {TopGainer} (+{Pct}%) 🚀 #Shorts
        """
        if not self.gainers:
            return f"Crypto Market Ranking {self.as_of} 🚀 #Shorts"

        top_gainer = self.gainers[0]
        symbol = top_gainer.get("symbol", "").upper()
        # Use change_7d_pct as it is available in weekly_top_movers
        change_pct = top_gainer.get("change_7d_pct") or top_gainer.get("price_change_percentage_24h", 0)
        
        return f"Crypto Ranking {self.as_of}: {symbol} (+{change_pct:.1f}%) 🚀 #Shorts"

    def get_description(self) -> str:
        """
        Generates a description with top gainers/losers summary.
        """
        lines = []
        lines.append(f"Daily Crypto Market Ranking & Analysis for {self.as_of}.")
        lines.append("Top market cap movers and trends visualized.")
        lines.append("")
        
        if self.gainers:
            lines.append("🚀 Top Gainers (7d):")
            for item in self.gainers[:3]:
                sym = item.get('symbol', '').upper()
                pct = item.get("change_7d_pct") or item.get("price_change_percentage_24h", 0)
                lines.append(f"- {sym}: +{pct:.1f}%")
            lines.append("")

        if self.losers:
            lines.append("📉 Top Losers (7d):")
            for item in self.losers[:3]:
                sym = item.get('symbol', '').upper()
                pct = item.get("change_7d_pct") or item.get("price_change_percentage_24h", 0)
                lines.append(f"- {sym}: {pct:.1f}%")
            lines.append("")

        lines.append("#Crypto #Bitcoin #Ethereum #Altcoins #MarketAnalysis #Web3 #Blockchain")
        
        # Add dynamic tags based on top coins
        dynamic_tags = [f"#{item.get('symbol', '').upper()}" for item in self.gainers[:3]]
        if dynamic_tags:
            lines.append(" ".join(dynamic_tags))
            
        return "\n".join(lines)

    def get_tags(self) -> list:
        """
        Returns a list of tags.
        """
        tags = ["crypto", "bitcoin", "ethereum", "market cap", "ranking", "animation", "manim", "investing", "finance"]
        
        # Add top 3 gainers
        for item in self.gainers[:3]:
            sym = item.get('symbol', '')
            if sym:
                tags.append(sym)
                tags.append(f"{sym} price")
        
        return tags
