#include "ROOT/RVec.hxx"


ROOT::RVec<int> ids_rpcRecHit_rawId(ROOT::RVec<int> rpcRecHit_rawId, int rawId) // Return the indices of RecHits involving a specific rawId in a single event
{
    ROOT::RVec<int> ids;
    for (int i = 0; i<rpcRecHit_rawId.size(); i++)
    {
        if(rpcRecHit_rawId[i]==rawId) 
        {
            ids.push_back(i);
        }
    }
    return ids;
}


ROOT::RVec<int> rpcRechHit_isNoisy(ROOT::RVec<int> ids_rpcRecHit_rawId, ROOT::RVec<int> rpcRecHit_firstClusterStrip, ROOT::RVec<int> rpcRecHit_clusterSize, ROOT::RVec<int> noisy_strips_rvec) // Return an array of 0 and 1 with the same length of "ids_rpcRecHit_rawId", where 1 means that the RecHit is noisy
{
    ROOT::RVec<int> isNoisy     = {};
    for (int i = 0; i<ids_rpcRecHit_rawId.size(); i++)
    {
        int idx                 = ids_rpcRecHit_rawId[i];
        int firstClusterStrip   = rpcRecHit_firstClusterStrip[i];
        int clusterSize         = rpcRecHit_clusterSize[i];
        int lastClusterStrip    = firstClusterStrip + clusterSize - 1;
        int isNoisy_            = 0;
        for (int strip = firstClusterStrip; strip <= lastClusterStrip; strip++)
        {
            if (std::find(noisy_strips_rvec.begin(), noisy_strips_rvec.end(), strip) != noisy_strips_rvec.end())
            {
                isNoisy_ = 1;
                break;
            }
        }
        isNoisy.push_back(isNoisy_);
    }
    return isNoisy;
}


int n_rpcRecHit_rawId(ROOT::RVec<int> ids_rpcRecHit_rawId, ROOT::RVec<int> rpcRechHit_isNoisy) // Count number of occurrancies of RecHits involving a specific rawId in a single event
{
    int n       = ids_rpcRecHit_rawId.size();
    int n_noisy = ROOT::VecOps::Sum(rpcRechHit_isNoisy);

    return n-n_noisy;
}


int n_rpcRecHit_rawId_SchemeRegion(ROOT::RVec<int> ids_rpcRecHit_rawId, ROOT::RVec<int> rpcRechHit_isNoisy, ROOT::RVec<int> rpcRecHit_SchemeRegion, int SchemeRegion) // Count number of occurrancies of RecHits involving a specific rawId in a single event and in a specific lhc scheme region
{
    int n = 0;
    for (int i = 0; i<ids_rpcRecHit_rawId.size(); i++)
    {
        int idx     = ids_rpcRecHit_rawId[i];
        int isNoisy = rpcRechHit_isNoisy[i];
        if (isNoisy==1)
        {
            continue;
        }
        if (rpcRecHit_SchemeRegion[idx]==SchemeRegion)
        {
            n+=1;
        }
    }
    return n;
}

// int n_rpcRecHit_rawId_SchemeRegion(ROOT::RVec<int> rpcRecHit_rawId, int rawId, ROOT::RVec<int> rpcRecHit_SchemeRegion, int SchemeRegion) // Count number of occurrancies of RecHits involving a specific rawId in a single event and in a specific lhc scheme region
// {
//     int n = 0;
//     for (int i = 0; i<rpcRecHit_rawId.size(); i++)
//     {
//         if(rpcRecHit_rawId[i]==rawId)
//         {
//             if(rpcRecHit_SchemeRegion[i]==SchemeRegion)
//             {
//                 n+=1;
//             }
//         }
//     }
//     return n;
// }

ROOT::RVec<int> bx_rawId(ROOT::RVec<int> rpcRecHit_rawId, ROOT::RVec<int> rpcRecHit_bx, int rawId) // Return the bx of RecHits involving a specific rawId in a single event
{
    ROOT::RVec<int> bx_rawId;
    for (int i = 0; i<rpcRecHit_rawId.size(); i++)
    {
        if(rpcRecHit_rawId[i]==rawId)
        {
            bx_rawId.push_back(rpcRecHit_bx[i]);
        }
    }
    return bx_rawId;
}


ROOT::RVec<int> rpcRecHit_bxReal(int bunchCrossing, ROOT::RVec<int> rpcRecHit_bx) // Return the real bx of RecHits in a single event
{
    ROOT::RVec<int> bxReal;
    for (int i = 0; i<rpcRecHit_bx.size(); i++)
    {
        bxReal.push_back(bunchCrossing+rpcRecHit_bx[i]);
    }
    return bxReal;
}


ROOT::RVec<int> rpcRecHit_SchemeRegion(ROOT::RVec<int> rpcRecHit_bxReal, ROOT::RVec<int> collidingBunches) // Return the filling scheme region associated to each rpcRecHit in a single event
{
    ROOT::RVec<int> region;
    for (int i = 0; i<rpcRecHit_bxReal.size(); i++)
    {
        int bx = rpcRecHit_bxReal[i];
        if (std::find(collidingBunches.begin(), collidingBunches.end(), bx) != collidingBunches.end())
        {
            region.push_back(1);  // Colliding
        } 
        else if (bx < collidingBunches[0])
        {  
            region.push_back(3);  // PreBeam
        } 
        else if (bx > collidingBunches[collidingBunches.size() - 1])
        {  
            region.push_back(4);  // BeamAbort
        } 
        else
        {
            region.push_back(2);  // NonColliding
        }
    }
    return region;
}


int nEvents_SchemeRegion(int bunchCrossing, int bx_window_width, ROOT::RVec<int> collidingBunches, int SchemeRegion) // Count number of events in a single bx window with a specific lhc scheme region
{
    int nEvents = 0;
    ROOT::RVec<int> bx_window;
    if (bx_window_width == 5)
    {
        bx_window = {-2, -1, 0, 1, 2};
    }
    else if (bx_window_width == 8)
    {
        bx_window = {-3, -2, -1, 0, 1, 2, 3, 4};
    }

    for (int i = 0; i < bx_window.size(); i++)
    {
        int bxReal = bunchCrossing + bx_window[i];
        if (std::find(collidingBunches.begin(), collidingBunches.end(), bxReal) != collidingBunches.end())
        {
            if (SchemeRegion == 1)
            {
                nEvents += 1;
            }
        }
        else if (bxReal < collidingBunches[0])
        {
            if (SchemeRegion == 3)
            {
                nEvents += 1;
            }
        }
        else if (bxReal > collidingBunches[collidingBunches.size() - 1])
        {
            if (SchemeRegion == 4)
            {
                nEvents += 1;
            }
        }
        else
        {
            if (SchemeRegion == 2)
            {
                nEvents += 1;
            }
        }

    }
    return nEvents;
}