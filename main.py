import logging, os
import gui.gui as gui

logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s: %(message)s'
    )

logging.getLogger('asyncio').setLevel(logging.WARNING) # Suppress epoll

from config import MOD_SCAN_DIRS
# import temp

def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    w = gui.MainWindow()
    w.show()

    gui.app.exec()

    # asyncio.run(temp.main())


if __name__ == "__main__":
    main()
