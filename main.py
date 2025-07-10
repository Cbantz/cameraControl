import pyqtgraph as pg
from organizer import Organizer



def start_application():
    # Start Qt app
    app = pg.mkQApp("Main Window")
    print(f"app created: {app}")

    global org
    org = Organizer()


    app.exec()



if __name__ == "__main__":
    start_application()