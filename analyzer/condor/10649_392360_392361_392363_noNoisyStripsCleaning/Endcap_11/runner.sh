#!/usr/bin/bash
cd /afs/cern.ch/user/l/lfavilla/RPC/analyzer/
python3 analyzer.py -f 10649 -r 392360,392361,392363 -d Endcap_11 -c /afs/cern.ch/user/l/lfavilla/RPC/analyzer/utils/lhc_schemes/Fill_10649/colliding_10649.txt -o /eos/user/l/lfavilla/RPC/common-tuples-results/10649/392360_392361_392363/partial_results/partial_results_10649_392360_392361_392363_Endcap_11_noNoisyStripsCleaning.json
