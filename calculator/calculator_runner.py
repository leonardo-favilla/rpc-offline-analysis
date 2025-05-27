import sys
sys.path.append('../')
import subprocess
from analyzer.utils.openGeomFile import openGeomFile
from tqdm import tqdm
import time
import shutil
from getUser import inituser, username, uid, workdir

fill                    = 9606
runs                    = "380470"
GeometryFile_path       = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/utils/RPCGeometry.out"



def print_progress_bar(iteration, total, chamber, length=50):
    terminal_width  = shutil.get_terminal_size((80, 20)).columns
    percent         = 100 * (iteration / float(total))
    filled_len      = int(length * iteration // total)
    bar             = '#' * filled_len + '-' * (length - filled_len)

    line            = f'\rProgress: |{bar}| {percent:6.2f}% - chamber: {chamber}'
    padded_line = line.ljust(terminal_width)
    sys.stdout.write(padded_line)
    sys.stdout.flush()


### Load Geometry File ###
df_geometry             = openGeomFile(GeometryFile_path)
# BARREL #
wheels                  = ["W-2", "W-1", "W+0", "W+1", "W+2"]
stations                = ["RB1in", "RB1out", "RB2in", "RB2out", "RB3", "RB4"]
sectors                 = [f"S{str(i).zfill(2)}" for i in range(1,13)]
betaparts1              = ["Backward", "Middle", "Forward"] # RB2in Wheels -1,0,+1 and RB2out Wheels -2,+2 have 3 eta partitions
betaparts2              = ["Backward",  "Forward"]          # all the others have only 2 eta partitions
# ENDCAP #
disks                   = ["RE-4", "RE-3", "RE-2", "RE-1", "RE+1", "RE+2", "RE+3", "RE+4"]
rings                   = ["R2", "R3"]
echambers               = [f"CH{str(i).zfill(2)}" for i in range(1, 37)]
eetaparts               = ["A", "B", "C"]

# chambers                        = ["W-2_RB4+_S01_Backward"]
chambers_singleRoll             = df_geometry["rpc_name"].unique().tolist()
chambers_multiRoll_Barrel       = []
chambers_multiRoll_Endcap       = []
for w in wheels:
    for s in stations:
        if ((s=="RB2in") and (w in ["W-1", "W+0", "W+1"])) or ((s=="RB2out") and (w in ["W-2", "W+2"])): # RB2in Wheels -1,0,+1 and RB2out Wheels -2,+2 have 3 eta partitions
            betaparts           = betaparts1
        else:                                                                                            # all the others have only 2 eta partitions
            betaparts           = betaparts2
        
        chambers_multiRoll_Barrel.append("_".join([w,s]))
        for sec in sectors:
            chambers_multiRoll_Barrel.append("_".join([w,s,sec]))
    
        for etapart in betaparts:
            chambers_multiRoll_Barrel.append("_".join([w,s,etapart]))
            
for d in disks:
    for r in rings:
        chambers_multiRoll_Endcap.append("_".join([d,r]))
        for ch in echambers:
            chambers_multiRoll_Endcap.append("_".join([d,r,ch]))
        for etapart in eetaparts:
            chambers_multiRoll_Endcap.append("_".join([d,r,etapart]))



# Run the calculator.py script for each chamber #
if False:
    t0 = time.time()
    print(f"Analyzing SINGLE roll chambers:                     {len(chambers_singleRoll)}")
    print(f"Starting at:                                        {time.strftime('%H:%M:%S', time.localtime(t0))}")
    for i, chamber in enumerate(chambers_singleRoll):
        print_progress_bar(i, len(chambers_singleRoll), chamber)
        result = subprocess.run(["python3", "calculator.py", "-f", str(fill), "-r", runs, "-c", chamber], text=True, capture_output=True)
    tf = time.time()
    print(f" Time elapsed to analyze SINGLE roll chambers:       {tf-t0}")

if False:
    t0 = time.time()
    print(f"Analyzing MULTI roll BARREL chambers:               {len(chambers_multiRoll_Barrel)}")
    print(f"Starting at:                                        {time.strftime('%H:%M:%S', time.localtime(t0))}")
    for i, chamber in enumerate(chambers_multiRoll_Barrel):
        print_progress_bar(i, len(chambers_multiRoll_Barrel), chamber)
        result = subprocess.run(["python3", "calculator.py", "-f", str(fill), "-r", runs, "-c", chamber], text=True, capture_output=True)
    tf = time.time()
    print(f" Time elapsed to analyze MULTI roll BARREL chambers: {tf-t0}")

if True:
    t0 = time.time()
    print(f"Analyzing MULTI roll ENDCAP chambers:               {len(chambers_multiRoll_Endcap)}")
    print(f"Starting at:                                        {time.strftime('%H:%M:%S', time.localtime(t0))}")
    for i, chamber in enumerate(chambers_multiRoll_Endcap):
        print_progress_bar(i, len(chambers_multiRoll_Endcap), chamber)
        result = subprocess.run(["python3", "calculator.py", "-f", str(fill), "-r", runs, "-c", chamber], text=True, capture_output=True)
    tf = time.time()
    print(f" Time elapsed to analyze MULTI roll ENDCAP chambers: {tf-t0}")



# print("\n\n")
# print("Output:", result.stdout)
# print("Errors:", result.stderr)
