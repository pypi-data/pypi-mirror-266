
import sys
import time
import argparse

import cozmoai


def parse_args():
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose")
    args = parser.parse_args()
    return args


def main():
    
    args = parse_args()     

    try:
        with cozmoai.connect(
                log_level="DEBUG" if args.verbose else "INFO",
                protocol_log_level="INFO",
                robot_log_level="INFO") as cli:
            brain = cozmoai.brain.Brain(cli)
            brain.start()
            while True:
                try:
                    time.sleep(1.0)
                except KeyboardInterrupt:
                    break
            brain.stop()
    except Exception as e:
        print("error: {}".format(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
