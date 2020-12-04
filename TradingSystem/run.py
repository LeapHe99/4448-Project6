from event import EventEngine
from engine import MainEngine
from mainwindow import MainWindow,create_qapp



def main():
    qapp = create_qapp('My Trading System')

    event_engine = EventEngine()
    # event_engine.start()
    main_engine = MainEngine(event_engine)
    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    qapp.exec()

if __name__ == "__main__":
    main()

