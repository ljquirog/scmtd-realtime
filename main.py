from template import *
import sys

if __name__ == "__main__":
    route_id = sys.argv[1]
    stop_id = sys.argv[2]        
    generate_realtime(route_id, stop_id)