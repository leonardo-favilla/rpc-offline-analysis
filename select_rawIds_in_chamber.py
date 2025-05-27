def select_rawIds_in_chamber(df_geometry, chamber):
    # select the rawIds for the chamber #
    if chamber in df_geometry["rpc_name"].unique().tolist(): # here we check if the chamber is a single roll
        rawIds                              = list(map(str, df_geometry[df_geometry["rpc_name"].str.startswith(chamber)]["RPC_Id"].unique().tolist()))
    else:                                                    # here we enter only if the chamber is a multi roll (OR if it does NOT exists in the geometry file so need to be carefull)
        combination                         = chamber.split("_")
        rpcNamesMatchedToChamber            = []
        for name in list(df_geometry["rpc_name"]):
            matches                         = []
            for part in combination:
                matching_condition_1        = part in name.split("_")
                matching_condition_2        = any((tag.startswith(part)) and not (tag.startswith("CH")) for tag in name.split("_"))
                matching_condition          = matching_condition_1 or matching_condition_2
                matches.append(matching_condition)
            rpcNameMatched                  = all(matches)
            
            if rpcNameMatched:
                # print(name, matching_condition_1, matching_condition_2)
                rpcNamesMatchedToChamber.append(name)
        nrpcNamesMatchedToChamber           = len(rpcNamesMatchedToChamber)
        rawIds                              = list(map(str, df_geometry[df_geometry["rpc_name"].apply(lambda name: name in rpcNamesMatchedToChamber)]["RPC_Id"].unique().tolist()))

    return rawIds