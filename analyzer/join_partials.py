import os
import json

partial_results_folder = "/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/9606/380470/partial_results/"
outJson_path           = "/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/9606/380470/partial_results_9606_380470_withNoisyStripsCleaning.json"

def join_partials(partial_results_folder):
    backgrounds             = ["Total", "Colliding", "NonColliding", "PreBeam", "BeamAbort"]
    partial_results_files   = [f"{partial_results_folder}{file}" for file in os.listdir(partial_results_folder) if (".json" in file) and ("withNoisyStripsCleaning" in file)]
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