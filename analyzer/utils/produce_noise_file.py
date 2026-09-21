import os
import json
from openGeomFile import openGeomFile



inFolderPath        = "/eos/user/f/fcarneva/public/10855"
outNoiseFilePath    = "/eos/user/f/fcarneva/public/10855/All_Dead_and_Noisy_strips_ID.txt"
df                  = openGeomFile("RPCGeometry.out")
regions             = [
                        ("EndcapMinus4","RE-4"),
                        ("EndcapMinus3","RE-3"),
                        ("EndcapMinus2","RE-2"),
                        ("EndcapMinus1","RE-1"),
                        ("EndcapPlus1","RE+1"),
                        ("EndcapPlus2","RE+2"),
                        ("EndcapPlus3","RE+3"),
                        ("EndcapPlus4","RE+4"),
                        ("WheelMinus2","W-2"),
                        ("WheelMinus1","W-1"),
                        ("WheelPlus0","W+0"),
                        ("WheelPlus1","W+1"),
                        ("WheelPlus2","W+2")
                        ]

inJsonFilePath_list = [f"{inFolderPath}/{reg}/{reg_tag}/rates/active_areas.json" for reg,reg_tag in regions]

with open(outNoiseFilePath, "w") as outNoiseFile:
    for i,inJsonFilePath in enumerate(inJsonFilePath_list):
        with open(inJsonFilePath, "r") as inJsonFile:
            inJson            = json.load(inJsonFile)
            chamberTag_list   = list(inJson.keys())
            rawId_list        = []
            for chamberTag in chamberTag_list:
                try:
                    rawId         = int(df[df["rpc_name"] == chamberTag]["RPC_Id"].values[0])
                    rawId_list.append(rawId)
                except IndexError:
                    print(f"Chamber tag {chamberTag} NOT found in geometry file. Skipping this chamber.")
            for chamberTag,rawId in zip(chamberTag_list,rawId_list):
                dead_strip_list  = [s.split("_")[1] for s in inJson[chamberTag]["dead_strips"]]
                noisy_strip_list = [s.split("_")[1] for s in inJson[chamberTag]["noisy_strips"]]
                diff_noisy_strip_list = [s.split("_")[1] for s in inJson[chamberTag]["diff_noisy_strips"]]
                line             = ",".join([str(rawId)] + dead_strip_list + noisy_strip_list + diff_noisy_strip_list)
                outNoiseFile.write(line + "\n")