import os
import optparse
import sys
import time
sys.path.append('../')
from getUser import inituser, username, uid, workdir # here you can find username, inituser, uid, workdir

usage           = "python3 analyzer_submitter.py -f <fill_number> -r <runs_list>" # --dryrun if you want to test the script without submitting jobs, --cleaning if you want Noisy Strips cleaning
parser          = optparse.OptionParser(usage)
parser.add_option("-f", "--fill",           dest="fill",            type=int,                                   help="Fill number")
parser.add_option("-r", "--runs",           dest="runs",            type=str,                                   help="Runs")
parser.add_option("-n", "--cleaning",       dest="cleaning",        default=False,      action="store_true",    help="Default do not clean noisy strips")
parser.add_option("-d", "--dryrun",         dest="dryrun",          default=False,      action="store_true",    help="Default do not run")
(opt, args)     = parser.parse_args()


fill            = opt.fill
runs            = list(map(int, opt.runs.split(",")))
cleaning        = opt.cleaning
dryrun          = opt.dryrun
if cleaning:
    cleaning_suffix     = "_withNoisyStripsCleaning"
else:
    cleaning_suffix     = "_noNoisyStripsCleaning"

os.popen("cp /tmp/x509up_u" + str(uid) + " /afs/cern.ch/user/" + inituser + "/" + username + "/private/x509up")

def sub_writer(run_folder, log_folder, fill, runs, detector_region):
    f = open(run_folder+"condor.sub", "w")
    f.write("Proxy_filename          = x509up\n")
    f.write("Proxy_path              = /afs/cern.ch/user/" + inituser + "/" + username + "/private/$(Proxy_filename)\n")
    f.write("universe                = vanilla\n")
    f.write("x509userproxy           = $(Proxy_path)\n")
    f.write("use_x509userproxy       = true\n")
    # f.write("should_transfer_files   = YES\n")
    # f.write("when_to_transfer_output = ON_EXIT\n")
    f.write("transfer_input_files    = $(Proxy_path)\n")
    # f.write("transfer_output_remaps  = \""+outname+"_Skim.root=root://eosuser.cern.ch///eos/user/"+inituser + "/" + username+"/DarkMatter/topcandidate_file/"+dat_name+"_Skim.root\"\n")
    # f.write('requirements            = (TARGET.OpSysAndVer =?= "CentOS7")\n')
    f.write("+JobFlavour             = \"testmatch\"\n") # options are espresso = 20 minutes, microcentury = 1 hour, longlunch = 2 hours, workday = 8 hours, tomorrow = 1 day, testmatch = 3 days, nextweek = 1 week
    f.write('+JobTag                 = "'+str(fill)+"_"+"_".join(map(str, runs))+"_"+str(detector_region)+'"\n')
    f.write("executable              = "+run_folder+"runner.sh\n")
    f.write("arguments               = \n")
    #f.write("input                   = input.txt\n")
    f.write("output                  = "+log_folder+"output/analyzer_"+str(fill)+"_"+"_".join(map(str, runs))+"_"+str(detector_region)+".out\n")
    f.write("error                   = "+log_folder+"error/analyzer_"+str(fill)+"_"+"_".join(map(str, runs))+"_"+str(detector_region)+".err\n")
    f.write("log                     = "+log_folder+"log/analyzer_"+str(fill)+"_"+"_".join(map(str, runs))+"_"+str(detector_region)+".log\n")
    f.write("queue\n")
    f.close()

def runner_writer(run_folder, fill, runs, detector_region, collidingFile, outJson_path, noisyStripsFile):
    f = open(run_folder+"runner.sh", "w")
    f.write("#!/usr/bin/bash\n")
    f.write("cd /afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/\n")
    if noisyStripsFile is not None:
        f.write("python3 analyzer.py "+f"-f {fill} -r {','.join(map(str, runs))} -d {detector_region} -c {collidingFile} -o {outJson_path} -n {noisyStripsFile}"+"\n")
    else:
        f.write("python3 analyzer.py "+f"-f {fill} -r {','.join(map(str, runs))} -d {detector_region} -c {collidingFile} -o {outJson_path}"+"\n")


condor_folder           = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/analyzer/condor/"
condor_subfolder        = condor_folder + str(fill) + "_" + "_".join((map(str, runs))) + cleaning_suffix + "/"
log_folder              = condor_subfolder + "condor/"
if not os.path.exists(condor_folder):
    os.makedirs(condor_folder)
    print(f"Creating condor folder:     {condor_folder}")
if not os.path.exists(condor_subfolder):
    os.makedirs(condor_subfolder)
    print(f"Creating condor subfolder:  {condor_subfolder}")
if not os.path.exists(log_folder):
    os.makedirs(log_folder)
    print(f"Creating log folder:        {log_folder}")
if not os.path.exists(log_folder+"output/"):
    os.makedirs(log_folder+"output/")
if not os.path.exists(log_folder+"error/"):
    os.makedirs(log_folder+"error/")
if not os.path.exists(log_folder+"log/"):
    os.makedirs(log_folder+"log/")



if not os.path.exists("/tmp/x509up_u" + str(uid)):
    print("Please run voms command")
    exit()


######## LAUNCH CONDOR ########
collidingFile        = f"/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + f"/rpc-offline-analysis/analyzer/utils/lhc_schemes/Fill_{fill}/colliding_{fill}.txt"
if cleaning:
    # noisyStripsFile  = f"/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + f"/rpc-offline-analysis/analyzer/utils/noisy_files/Fill_{fill}/All_Noisy_strips_ID.txt"
    noisyStripsFile  = f"/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + f"/rpc-offline-analysis/analyzer/utils/noisy_files/Fill_{fill}/All_Dead_and_Noisy_strips_ID.txt"
    print(f"Cleaning noisy strips using: {noisyStripsFile}")
else:
    noisyStripsFile  = None
    print("No noisy strips cleaning")

detector_regions = [
                    "Barrel_0",
                    "Barrel_1",
                    "Barrel_2",
                    "Barrel_3",
                    "Barrel_4",
                    "Barrel_5",
                    "Barrel_6",
                    "Barrel_7",
                    "Barrel_8",
                    "Barrel_9",

                    "Endcap_0",
                    "Endcap_1",
                    "Endcap_2",
                    "Endcap_3",
                    "Endcap_4",
                    "Endcap_5",
                    "Endcap_6",
                    "Endcap_7",
                    "Endcap_8",
                    "Endcap_9",
                    "Endcap_10",
                    "Endcap_11",
                    "Endcap_12",
                    "Endcap_13",
                    "Endcap_14",
                    "Endcap_15",
                    "Endcap_16",
                    "Endcap_17",
                    "Endcap_18",
                    "Endcap_19",
                    "Endcap_20",
                    "Endcap_21",
                    "Endcap_22",
                    "Endcap_23"
                    ]

for detector_region in detector_regions:
    outFolder_path          = "/eos/user/l/lfavilla/rpc-offline-analysis/common-tuples-results/"+str(fill)+"/"
    outSubFolder_path       = outFolder_path+"_".join((map(str, runs)))+"/"
    outSubSubFolder_path    = outSubFolder_path+"partial_results/"
    outJson_path            = outSubSubFolder_path+f"partial_results_{fill}_{'_'.join((map(str, runs)))}_{detector_region}{cleaning_suffix}.json"
    run_folder              = condor_subfolder + detector_region + "/"
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)
        print(f"Creating run folder:        {run_folder}")
    if not os.path.exists(outFolder_path):
        os.makedirs(outFolder_path)
        print(f"Creating out folder:        {outFolder_path}")
    if not os.path.exists(outSubFolder_path):
        os.makedirs(outSubFolder_path)
        print(f"Creating out subfolder:     {outSubFolder_path}")
    if not os.path.exists(outSubSubFolder_path):
        os.makedirs(outSubSubFolder_path)
        print(f"Creating out sub-subfolder: {outSubSubFolder_path}")



    runner_writer(run_folder, fill, runs, detector_region, collidingFile, outJson_path, noisyStripsFile)
    sub_writer(run_folder, log_folder, fill, runs, detector_region)
    if not dryrun:
        os.popen("condor_submit " + run_folder + "condor.sub")
    time.sleep(2)