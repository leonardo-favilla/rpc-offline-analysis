import ROOT
from math import sqrt
import json




def lhc_scheme(collidingFile):
    '''
    this function reads the colliding scheme from a .txt file and returns the list of bunches divided into:
    - all bunches
    - colliding bunches
    - prebeam bunches
    - abort bunches
    - non-colliding bunches
    '''
    with open(collidingFile, "r") as f:
        lines      = f.readlines()

    ntot           = 3564
    bxIDs          = list(range(ntot)) # bunches go from 0 to 3563
    bxID_coll      = [int(bx.replace("\n","")) for bx in lines]
    bxID_prebeam   = list(range(bxID_coll[0]))
    bxID_abort     = list(range(bxID_coll[-1]+1, ntot))
    bxID_noncoll   = list(set(bxIDs) - set(bxID_coll) - set(bxID_prebeam) - set(bxID_abort))

    nbx_prebeam    = len(bxID_prebeam)
    nbx_coll       = len(bxID_coll)
    nbx_noncoll    = len(bxID_noncoll)
    nbx_abort      = len(bxID_abort)

    return bxIDs, bxID_coll, bxID_prebeam, bxID_abort, bxID_noncoll





def calculateRates_regions(partial_results_inJson, rawIds, regions, bx_window_width, lumi_bins):
    dt          = 25e-9 # 25 ns
    hist_rates  = {}
    rates       = {}
    fits        = {}
    fitResults  = {}

    for reg in regions:
        #########################
        ### RATES CALCULATION ###
        #########################
        hist_rechits        = ROOT.TH1F(f"hist_rechits_{reg}", f"hist_rechits_{reg}", len(lumi_bins), 0, 25000)
        hist_events         = ROOT.TH1F(f"hist_events_{reg}", f"hist_events_{reg}", len(lumi_bins), 0, 25000)

        nRecHits                       = [sum(nRecHits_inLumiBin) for nRecHits_inLumiBin in list(zip(*[partial_results_inJson["nRecHits"][reg][rawId] for rawId in rawIds]))]
        totalArea                      = sum([partial_results_inJson["Aeff"][rawId] for rawId in rawIds])
        
        if reg == "Total":
            nEvents                    = partial_results_inJson["nEvents"][reg]
            k                          = bx_window_width * dt * totalArea
        else:
            nEvents                    = partial_results_inJson[f"nEvents_{bx_window_width}bx"][reg]
            k                          = 1 * dt * totalArea



        for (l, u), nRecHit, nEvent in zip(lumi_bins, nRecHits, nEvents):
            if l < 9000:
                continue
            bin_center = (l + u) / 2
            bin_num    = hist_events.FindBin(bin_center)
            hist_rechits.SetBinContent(bin_num, nRecHit)
            hist_rechits.SetBinError(bin_num, ROOT.TMath.Sqrt(nRecHit))
            hist_events.SetBinContent(bin_num, nEvent)
            hist_events.SetBinError(bin_num, ROOT.TMath.Sqrt(nEvent))

        hist_rechits.Divide(hist_events)
        hist_rechits.Scale(1./k)

        # save rates into dict #
        hist_rates[reg] = hist_rechits
        rates[reg]      = [[hist_rechits.GetBinContent(i),hist_rechits.GetBinError(i)] for i in range(1, hist_rechits.GetNbinsX()+1)]

        ############
        ### FITS ###
        ############
        if hist_rates[reg].GetEntries():
            fit_tmp          = ROOT.TF1(f"rate_{reg}_fit","pol1", 9000, 21000) # pol1: y = p0 + p1*x
            fitResult_tmp    = hist_rates[reg].Fit(fit_tmp, "SM0Q")
            p0               = fit_tmp.GetParameter(0)
            p1               = fit_tmp.GetParameter(1)
            p0_error         = fit_tmp.GetParError(0)
            p1_error         = fit_tmp.GetParError(1)
            chi2             = fitResult_tmp.Chi2()
            ndf              = fitResult_tmp.Ndf()
            covMatrix        = [[fitResult_tmp.GetCovarianceMatrix()(0,0), fitResult_tmp.GetCovarianceMatrix()(0,1)],
                                [fitResult_tmp.GetCovarianceMatrix()(1,0), fitResult_tmp.GetCovarianceMatrix()(1,1)]]
        else:
            fit_tmp          = None
            p0               = None
            p1               = None
            p0_error         = None
            p1_error         = None
            chi2             = None
            ndf              = None
            covMatrix        = None


        # save fit functions into dict #
        fits[reg]                      = fit_tmp
        fitResults[reg]                = {}
        fitResults[reg]["p0"]          = p0 
        fitResults[reg]["p1"]          = p1 
        fitResults[reg]["p0_error"]    = p0_error 
        fitResults[reg]["p1_error"]    = p1_error 
        fitResults[reg]["chi2"]        = chi2
        fitResults[reg]["ndf"]         = ndf
        fitResults[reg]["covMatrix"]   = covMatrix

    return hist_rates, rates, fits, fitResults





def calculateRates_backgrounds(fitRatesRegions, fitResultsRegions, colliding_scheme_txt):
    # get colliding scheme #
    bxIDs, bxID_coll, bxID_prebeam, bxID_abort, bxID_noncoll = lhc_scheme(colliding_scheme_txt)
    ntot               = len(bxIDs)
    nbx_prebeam        = len(bxID_prebeam)
    nbx_coll           = len(bxID_coll)
    nbx_noncoll        = len(bxID_noncoll)
    nbx_abort          = len(bxID_abort)


    #########################
    ### RATES CALCULATION ###
    #########################
    funcs              = {}
    funcs_parameters   = {}
    funcs["Inclusive"] = ROOT.TF1("func_Inclusive", "pol1", 9000, 21000)
    funcs["Delayed"]   = ROOT.TF1("func_Delayed", "pol1", 9000, 21000)
    funcs["Prompt"]    = ROOT.TF1("func_Prompt", "pol1", 9000, 21000)

    # INCLUSIVE #
    funcs["Inclusive"].SetParameter(0,(nbx_prebeam*fitRatesRegions["PreBeam"].GetParameter(0) + nbx_coll*fitRatesRegions["Colliding"].GetParameter(0) + nbx_noncoll*fitRatesRegions["NonColliding"].GetParameter(0) + nbx_abort*fitRatesRegions["BeamAbort"].GetParameter(0))/ntot)
    funcs["Inclusive"].SetParameter(1,(nbx_prebeam*fitRatesRegions["PreBeam"].GetParameter(1) + nbx_coll*fitRatesRegions["Colliding"].GetParameter(1) + nbx_noncoll*fitRatesRegions["NonColliding"].GetParameter(1) + nbx_abort*fitRatesRegions["BeamAbort"].GetParameter(1))/ntot)
    
    # DELAYED #
    funcs["Delayed"].SetParameter(0,(nbx_prebeam*fitRatesRegions["PreBeam"].GetParameter(0) + nbx_noncoll*fitRatesRegions["NonColliding"].GetParameter(0) + nbx_abort*fitRatesRegions["BeamAbort"].GetParameter(0))/(ntot-nbx_coll))
    funcs["Delayed"].SetParameter(1,(nbx_prebeam*fitRatesRegions["PreBeam"].GetParameter(1) + nbx_noncoll*fitRatesRegions["NonColliding"].GetParameter(1) + nbx_abort*fitRatesRegions["BeamAbort"].GetParameter(1))/(ntot-nbx_coll))
    
    # PROMPT #
    funcs["Prompt"].SetParameter(0,fitRatesRegions["Colliding"].GetParameter(0) - funcs["Delayed"].GetParameter(0))    
    funcs["Prompt"].SetParameter(1,fitRatesRegions["Colliding"].GetParameter(1) - funcs["Delayed"].GetParameter(1))    


    ######################
    # ERRORS CALCULATION #
    ######################
    funcs_parameters["Inclusive"] = {}
    funcs_parameters["Delayed"]   = {}
    funcs_parameters["Prompt"]    = {}


    # INCLUSIVE #
    funcs_parameters["Inclusive"]["p0"]        = funcs["Inclusive"].GetParameter(0)
    funcs_parameters["Inclusive"]["p1"]        = funcs["Inclusive"].GetParameter(1)
    funcs_parameters["Inclusive"]["p0_error"]  = sqrt(((nbx_prebeam**2)*fitResultsRegions["PreBeam"]["p0_error"]**2 + (nbx_coll**2)*fitResultsRegions["Colliding"]["p0_error"]**2 + (nbx_noncoll**2)*fitResultsRegions["NonColliding"]["p0_error"]**2 + (nbx_abort**2)*fitResultsRegions["BeamAbort"]["p0_error"]**2)/(ntot**2))
    funcs_parameters["Inclusive"]["p1_error"]  = sqrt(((nbx_prebeam**2)*fitResultsRegions["PreBeam"]["p1_error"]**2 + (nbx_coll**2)*fitResultsRegions["Colliding"]["p1_error"]**2 + (nbx_noncoll**2)*fitResultsRegions["NonColliding"]["p1_error"]**2 + (nbx_abort**2)*fitResultsRegions["BeamAbort"]["p1_error"]**2)/(ntot**2))
    funcs_parameters["Inclusive"]["cov_p0p1"]  = ((nbx_prebeam**2)*fitResultsRegions["PreBeam"]["covMatrix"][0][1] + (nbx_coll**2)*fitResultsRegions["Colliding"]["covMatrix"][0][1] + (nbx_noncoll**2)*fitResultsRegions["NonColliding"]["covMatrix"][0][1] + (nbx_abort**2)*fitResultsRegions["BeamAbort"]["covMatrix"][0][1])/(ntot**2)
    funcs_parameters["Inclusive"]["covMatrix"] = [
                                                                        [funcs_parameters["Inclusive"]["p0_error"]**2, funcs_parameters["Inclusive"]["cov_p0p1"]],
                                                                        [funcs_parameters["Inclusive"]["cov_p0p1"], funcs_parameters["Inclusive"]["p1_error"]**2]
                                                                    ]
    # DELAYED #
    funcs_parameters["Delayed"]["p0"]          = funcs["Delayed"].GetParameter(0)
    funcs_parameters["Delayed"]["p1"]          = funcs["Delayed"].GetParameter(1)
    funcs_parameters["Delayed"]["p0_error"]    = sqrt(((nbx_prebeam**2)*fitResultsRegions["PreBeam"]["p0_error"]**2 + (nbx_noncoll**2)*fitResultsRegions["NonColliding"]["p0_error"]**2 + (nbx_abort**2)*fitResultsRegions["BeamAbort"]["p0_error"]**2)/(ntot**2))
    funcs_parameters["Delayed"]["p1_error"]    = sqrt(((nbx_prebeam**2)*fitResultsRegions["PreBeam"]["p1_error"]**2 + (nbx_noncoll**2)*fitResultsRegions["NonColliding"]["p1_error"]**2 + (nbx_abort**2)*fitResultsRegions["BeamAbort"]["p1_error"]**2)/(ntot**2))
    funcs_parameters["Delayed"]["cov_p0p1"]    = ((nbx_prebeam**2)*fitResultsRegions["PreBeam"]["covMatrix"][0][1] + (nbx_noncoll**2)*fitResultsRegions["NonColliding"]["covMatrix"][0][1] + (nbx_abort**2)*fitResultsRegions["BeamAbort"]["covMatrix"][0][1])/(ntot**2)
    funcs_parameters["Delayed"]["covMatrix"]   = [
                                                                        [funcs_parameters["Delayed"]["p0_error"]**2, funcs_parameters["Delayed"]["cov_p0p1"]],
                                                                        [funcs_parameters["Delayed"]["cov_p0p1"], funcs_parameters["Delayed"]["p1_error"]**2]
                                                                    ]
    # PROMPT #
    funcs_parameters["Prompt"]["p0"]           = funcs["Prompt"].GetParameter(0)
    funcs_parameters["Prompt"]["p1"]           = funcs["Prompt"].GetParameter(1)
    funcs_parameters["Prompt"]["p0_error"]     = sqrt(fitResultsRegions["Colliding"]["p0_error"]**2 + funcs_parameters["Delayed"]["p0_error"]**2)
    funcs_parameters["Prompt"]["p1_error"]     = sqrt(fitResultsRegions["Colliding"]["p1_error"]**2 + funcs_parameters["Delayed"]["p1_error"]**2)
    funcs_parameters["Prompt"]["cov_p0p1"]     = fitResultsRegions["Colliding"]["covMatrix"][0][1] + funcs_parameters["Delayed"]["cov_p0p1"]
    funcs_parameters["Prompt"]["covMatrix"]    = [
                                                                        [funcs_parameters["Prompt"]["p0_error"]**2, funcs_parameters["Prompt"]["cov_p0p1"]],
                                                                        [funcs_parameters["Prompt"]["cov_p0p1"], funcs_parameters["Prompt"]["p1_error"]**2]
                                                                    ]


    return funcs, funcs_parameters