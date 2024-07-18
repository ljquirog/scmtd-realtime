from template import *
import sys

# add cmd line instructions to readme

if __name__ == "__main__":
    route_id = sys.argv[1]
    stop_id = sys.argv[2]    
    filename = sys.argv[3]    
    
    results_df = generate_realtime(route_id, stop_id)
    generate_csv(results_df, filename)