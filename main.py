from threading import Thread
from bot import start_bot
from kiosk import App

if __name__ == "__main__":
    
    t = Thread(target=start_bot, daemon=True)
    t.start()

    App().mainloop()
