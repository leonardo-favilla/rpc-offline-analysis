
class fillInfo:
    def __init__(self, fill=None, runs=None, totalLumi=None, file_folders=None):
        self.fill           = fill
        self.runs           = runs
        self.totalLumi      = totalLumi #pb-1
        self.file_folders   = file_folders



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




fillsDict = {
                9606:   fill_9606,
                10649:  fill_10649,
                }