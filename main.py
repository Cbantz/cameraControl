import pyqtgraph as pg
from organizer import Organizer



def start_application():
    # Start Qt app
    app = pg.mkQApp("Main Window")
    print(f"app created: {app}")

    global org
    org = Organizer()
    org.connect_to_window()

    # Display Widget as new Window
    win = org.window

    win.show()

    app.exec()

def closeEvent(event):
    for thread in org:
        thread.quit()
        thread.wait()

    event.accept()

if __name__ == "__main__":
    start_application()