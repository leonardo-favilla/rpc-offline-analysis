import os
import json
import optparse

usage                   = "python3 join_partials.py -f <fill_number> -r <runs_list>"
parser                  = optparse.OptionParser(usage)
parser.add_option("-f", "--fill",       dest="fill",                                                        type=int,   help="Fill number")
parser.add_option("-r", "--runs",       dest="runs",                                                        type=str,   help="Runs list, in the form run1,run2,run3")
parser.add_option(      "--cleaning",   dest="cleaning",            action="store_true", default=False,                 help="Apply noisy strips cleaning (default: False)")
(opt, args)             = parser.parse_args()
fill                    = opt.fill
runs                    = opt.runs
cleaning                = opt.cleaning
if cleaning:
    cleaning_suffix     = "_withNoisyStripsCleaning"
else:
    cleaning_suffix     = "_noNoisyStripsCleaning"

partial_results_folder  = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill}/{'_'.join(runs.split(','))}/partial_results/"
outJson_path            = f"/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/{fill}/{'_'.join(runs.split(','))}/partial_results_{fill}_{'_'.join(runs.split(','))}{cleaning_suffix}.json"

def join_partials(partial_results_folder):
    backgrounds             = ["Total", "Colliding", "NonColliding", "PreBeam", "BeamAbort"]
    partial_results_files   = [f"{partial_results_folder}{file}" for file in os.listdir(partial_results_folder) if (".json" in file) and (cleaning_suffix in file)]
    partial_results         = []

    ### Load partial results to join ###
    for path in partial_results_files:
        with open(path, "r") as f:
            partial_results.append(json.load(f))

    print(len(partial_results_files))
    # print(len(partial_results))

    ### Join partial results ###
    joined_results                      = {}
    joined_results["nEvents"]           = partial_results[0]["nEvents"]
    joined_results["nEvents_5bx"]       = partial_results[0]["nEvents_5bx"]
    joined_results["nEvents_8bx"]       = partial_results[0]["nEvents_8bx"]
    joined_results["nRecHits"]          = {}
    for bkg in backgrounds:
        joined_results["nRecHits"][bkg] = {}
    joined_results["Aeff"]              = {}


    for partial_result in partial_results:
        for bkg in backgrounds:
            joined_results["nRecHits"][bkg].update(partial_result["nRecHits"][bkg])
        joined_results["Aeff"].update(partial_result["Aeff"])


    return joined_results
    
    
    

outJson = join_partials(partial_results_folder)
with open(outJson_path, "w") as f:
    json.dump(outJson, f, indent=4)
print(f"Partial results joined and saved to: {outJson_path}")