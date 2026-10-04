import yfinance as yf
from flask import Flask, jsonify
import threading, time, os
app = Flask(__name__)
last_signal = {"price": 0, "signal": "انتظار..."}
def get_rsi(p, n=14):
    d=p.diff()
    g=d.where(d>0,0).rolling(n).mean()
    l=-d.where(d<0,0).rolling(n).mean()
    rs=g/l
    return 100-(100/(1+rs))
def get_signal():
    try:
        data=yf.download("GC=F", period="2d", interval="5m", progress=False)
        c=data['Close']
        s20=c.rolling(20).mean().iloc[-1]
        s50=c.rolling(50).mean().iloc[-1]
        price=float(c.iloc[-1])
        rsi=float(get_rsi(c).iloc[-1])
        if price>s20 and float(s20)>float(s50) and rsi<70: sig="🟢 شراء قوي BUY"
        elif price<float(s20) and float(s20)<float(s50) and rsi>30: sig="🔴 بيع قوي SELL"
        elif rsi>70: sig="⚠️ تشبع شراء"
        elif rsi<30: sig="⚠️ تشبع بيع"
        else: sig="⏸️ انتظار"
        return {"price":round(price,2),"signal":sig,"rsi":round(rsi,2)}
    except: return None
def loop():
    global last_signal
    while True:
        r=get_signal()
        if r: last_signal=r
        time.sleep(300)
@app.route("/")
def home(): return jsonify(last_signal)
threading.Thread(target=loop, daemon=True).start()
if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.getenv("PORT",10000)))
