import yfinance as yf
import pandas as pd
from datetime import datetime

# Liste des actifs a surveiller pour le rapport quotidien
assets = ["AAPL", "MSFT", "TSLA", "EURUSD=X", "GC=F"]

def generate_daily_report():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"--- RAPPORT FINANCIER AUTOMATIQUE DU {now} ---"
    print(header)
    
    # Creation d'un petit fichier texte pour garder une trace sur le serveur
    with open("daily_performance.log", "a") as f:
        f.write(f"\n{header}\n")
        
        for asset in assets:
            try:
                # Recuperation des donnees du jour
                ticker = yf.Ticker(asset)
                data = ticker.history(period="2d")
                
                if len(data) >= 2:
                    price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2]
                    change = ((price - prev_price) / prev_price) * 100
                    
                    status = "HAUSSE" if change > 0 else "BAISSE"
                    report_line = f"Actif: {asset:10} | Prix: {price:10.2f} | Var: {change:6.2f}% | [{status}]"
                    
                    print(report_line)
                    f.write(report_line + "\n")
            except Exception as e:
                error_msg = f"Erreur pour {asset}: {e}"
                print(error_msg)
                f.write(error_msg + "\n")
        
        f.write("-" * 50 + "\n")

if __name__ == "__main__":
    generate_daily_report()