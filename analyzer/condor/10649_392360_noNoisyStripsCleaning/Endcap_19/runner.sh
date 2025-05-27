#!/usr/bin/bash
cd /afs/cern.ch/user/l/lfavilla/RPC/analyzer/
python3 analyzer.py -f 10649 -r 392360 -d Endcap_19 -c /afs/cern.ch/user/l/lfavilla/RPC/analyzer/utils/lhc_schemes/Fill_10649/colliding_10649.txt -o /eos/user/l/lfavilla/RPC/common-tuples-results/10649/392360/partial_results/partial_results_10649_392360_Endcap_19_noNoisyStripsCleaning.json
