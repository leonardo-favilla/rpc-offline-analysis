
class fillInfo:
    def __init__(self, fill=None, runs=None, totalLumi=None, file_folders=None):
        self.fill           = fill
        self.runs           = runs
        self.totalLumi      = totalLumi #pb-1
        self.file_folders   = file_folders


################## Fills Information ##################

# Fill 9606 #
fill_9606               = fillInfo()
fill_9606.fill          = 9606
fill_9606.runs          = [380466, 380470]
fill_9606.totalLumi     = {
                            380466: 220.282, 
                            380470: 531.633,
                            }
fill_9606.file_folders  = [
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill9606_Run380466To380470_NanoAOD_v4/250207_160241/0000/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill9606_Run380466To380470_NanoAOD_v4/250207_160241/0001/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill9606_Run380466To380470_NanoAOD_v4/250207_160241/0002/"
                            ]

# Fill 10623 #
fill_10623               = fillInfo()
fill_10623.fill          = 10623
fill_10623.runs          = [392046,392052,392071]
fill_10623.totalLumi     = {
                            392046: 13.383,
                            392052: 23.083,
                            392071: 53.568,
                            }
fill_10623.file_folders  = [
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10623_Run392030To392071_NanoAOD_v1/250524_124413/0000/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10623_Run392030To392071_NanoAOD_v1/250524_124413/0001/"
                            ]

# Fill 10640 #
fill_10640               = fillInfo()
fill_10640.fill          = 10640
fill_10640.runs          = [392220,392221]
fill_10640.totalLumi     = {
                            392220: 73.959,
                            392221: 143.674,    
                            }
fill_10640.file_folders  = [
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10640_Run392219To392222_NanoAOD_v1/250524_142451/0000/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10640_Run392219To392222_NanoAOD_v1/250524_142451/0001/"
                            ]

# Fill 10645 #
fill_10645               = fillInfo()
fill_10645.fill          = 10645
fill_10645.runs          = [392295,392296]
fill_10645.totalLumi     = {
                            392295: 170.426,
                            392296: 199.442,    
                            }
fill_10645.file_folders  = [
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10645_Run392293To392296_NanoAOD_v1/250524_135901/0000/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10645_Run392293To392296_NanoAOD_v1/250524_135901/0001/"
                            ]

# Fill 10649 #
fill_10649               = fillInfo()
fill_10649.fill          = 10649
fill_10649.runs          = [392358, 392360, 392361, 392363]
fill_10649.totalLumi     = {
                            392358: 52.146,
                            392360: 81.514,
                            392361: 127.260,
                            392363: 315.235,
                            }
fill_10649.file_folders  = [
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10649_Run392358To392363_NanoAOD_v1/250524_135917/0000/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10649_Run392358To392363_NanoAOD_v1/250524_135917/0001/"
                            ]

# Fill 10665 #
fill_10665               = fillInfo()
fill_10665.fill          = 10665
fill_10665.runs          = [392524, 392526]
fill_10665.totalLumi     = {
                            392524: 169.367,
                            392526: 644.047,
                            }
fill_10665.file_folders  = [
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10665_Run392524To392526_NanoAOD_v1/250526_111154/0000/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10665_Run392524To392526_NanoAOD_v1/250526_111154/0001/",
                            "/eos/cms/store/group/upgrade/GEM/NanoAOD/ZeroBias/crab_ZeroBias_Run3_Fill10665_Run392524To392526_NanoAOD_v1/250526_111154/0002/",
                            ]

# Fill 10671 #
fill_10671               = fillInfo()
fill_10671.fill          = 10671
fill_10671.runs          = [392642]
fill_10671.totalLumi     = {
                            392642: 826.564,
                            }
fill_10671.file_folders  = None
fill_10671.files         = [
                            "/eos/cms/store/group/dpg_muon/MuonDPGNtuples/ntuples/ZeroBias/2025/Automation/ntuple_10671.root",
                            ]





###########################
### Dictionary of fills ###
###########################
fillsDict = {
                9606:   fill_9606,
                10623:  fill_10623,
                10640:  fill_10640,
                10645:  fill_10645,
                10649:  fill_10649,
                10665:  fill_10665,
                10671:  fill_10671,
                }