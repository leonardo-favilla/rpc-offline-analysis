#!/usr/bin/bash
cd /afs/cern.ch/user/l/lfavilla/RPC/analyzer/
python3 analyzer.py -f 9606 -r 380466 -d Endcap_8 -c /afs/cern.ch/user/l/lfavilla/RPC/analyzer/utils/lhc_schemes/Fill_9606/colliding_9606.txt -o /eos/user/l/lfavilla/RPC/common-tuples-results/9606/380466/partial_results/partial_results_9606_380466_Endcap_8_withNoisyStripsCleaning.json -n /afs/cern.ch/user/l/lfavilla/RPC/analyzer/utils/noisy_files/Fill_9606/All_Noisy_strips_ID.txt
