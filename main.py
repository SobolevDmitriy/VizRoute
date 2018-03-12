import platform
from vizRoute import VizRoute


def main():
    tg = VizRoute()
    tg.buildGraph()


if __name__ == '__main__':
    platform = platform.system()
    if platform != 'Linux':
        print("Only Linux supported")
        exit(0)
    else:
        main()

