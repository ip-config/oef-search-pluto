import argparse

from england_map_webserver.src.python.lib import EnglandMapWebserver

def main():
    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--http_port",        required=True, type=int, help="which port to run the HTTP interface on.")

    args = parser.parse_args()

    app = EnglandMapWebserver.EnglandMapWebserver(args)
    app.run(args)

if __name__ == '__main__':
    main()
