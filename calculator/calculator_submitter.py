import os
import optparse
import sys
import time
sys.path.append('../')
from getUser import inituser, username, uid, workdir # here you can find username, inituser, uid, workdir

usage           = "python3 calculator_submitter.py -f <fill_number> -r <runs_list>" # --dryrun if you want to test the script without submitting jobs, --cleaning if you want Noisy Strips cleaning
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

def sub_writer(run_folder, log_folder, fill, runs):
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
    f.write("+JobFlavour             = \"tomorrow\"\n") # options are espresso = 20 minutes, microcentury = 1 hour, longlunch = 2 hours, workday = 8 hours, tomorrow = 1 day, testmatch = 3 days, nextweek = 1 week
    f.write('+JobTag                 = "'+str(fill)+"_"+"_".join(map(str, runs))+'"\n')
    f.write("executable              = "+run_folder+"runner.sh\n")
    f.write("arguments               = \n")
    #f.write("input                   = input.txt\n")
    f.write("output                  = "+log_folder+"output/calculator_"+str(fill)+"_"+"_".join(map(str, runs))+".out\n")
    f.write("error                   = "+log_folder+"error/calculator_"+str(fill)+"_"+"_".join(map(str, runs))+".err\n")
    f.write("log                     = "+log_folder+"log/calculator_"+str(fill)+"_"+"_".join(map(str, runs))+".log\n")
    f.write("queue\n")
    f.close()

def runner_writer(run_folder, fill, runs, cleaning):
    f = open(run_folder+"runner.sh", "w")
    f.write("#!/usr/bin/bash\n")
    f.write("cd /afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/calculator/\n")
    if cleaning:
        f.write("python3 calculator_runner.py "+f"-f {fill} -r {','.join(map(str, runs))} --cleaning"+"\n")
    else:
        f.write("python3 calculator_runner.py "+f"-f {fill} -r {','.join(map(str, runs))}"+"\n")


condor_folder           = "/afs/cern.ch/" + workdir + "/" + inituser + "/" + username + "/rpc-offline-analysis/calculator/condor/"
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
run_folder              = condor_subfolder
if not os.path.exists(run_folder):
    os.makedirs(run_folder)
    print(f"Creating run folder:        {run_folder}")

runner_writer(run_folder, fill, runs, cleaning)
sub_writer(run_folder, log_folder, fill, runs)
if not dryrun:
    os.popen("condor_submit " + run_folder + "condor.sub")