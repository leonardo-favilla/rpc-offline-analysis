#!/usr/bin/bash
cd /afs/cern.ch/user/l/lfavilla/RPC/analyzer/condor/9606_380470/Endcap_7/
python3 /afs/cern.ch/user/l/lfavilla/RPC/analyzer/analyzer.py -f 9606 -r 380470 -d Endcap_7 -c /eos/user/l/lfavilla/SWAN_projects/RPC/common-tuples/lhc_schemes/Fill_9606/colliding_9606.txt -o /eos/user/l/lfavilla/RPC/common-tuples-results/9606/380470/partial_results_9606_380470_Endcap_7.json
