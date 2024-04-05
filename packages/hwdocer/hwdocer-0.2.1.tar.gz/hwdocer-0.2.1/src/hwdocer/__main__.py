import sys

from .hwdocer import HwDocer

def main():
    obj = HwDocer(sys.argv)
    obj.run()
    
if __name__ == "__main__":
    main()
