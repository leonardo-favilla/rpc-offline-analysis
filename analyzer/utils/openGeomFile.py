import pandas as pd
def openGeomFile(GeometryFile_path):
    data_barrel = []
    data_endcap = []

    columns_barrel = ["RPC_Id", "rpc_name", "slength", "swidth", "nStrips", "stripArea", "eta", "phi", "distR"]
    columns_endcap = ["RPC_Id", "rpc_name", "slength", "swidth", "nStrips", "stripArea", "eta", "phi", "distR", "Rmin", "Rmax"]

    nrows = 0
    with open(GeometryFile_path, "r") as file:
        for index, line in enumerate(file):
            if index == 0:  # Skip the first row
                continue
            nrows += 1
            parts  = line.split()
            
            if "W" in parts[1]:
                RPC_Id,rpc_name,slength,swidth,nStrips,stripArea,eta,phi,distR           = int(parts[0]),parts[1],float(parts[3]),float(parts[5]),int(parts[7]),float(parts[9]),float(parts[11]),float(parts[13]),float(parts[15])
                data_barrel.append([RPC_Id,rpc_name,slength,swidth,nStrips,stripArea,eta,phi,distR])
            elif "RE" in parts[1]:
                RPC_Id,rpc_name,slength,swidth,nStrips,stripArea,eta,phi,distR,Rmin,Rmax = int(parts[0]),parts[1],float(parts[3]),float(parts[5]),int(parts[7]),float(parts[9]),float(parts[11]),float(parts[13]),float(parts[15]),float(parts[17]),float(parts[19])
                data_endcap.append([RPC_Id,rpc_name,slength,swidth,nStrips,stripArea,eta,phi,distR,Rmin,Rmax])
        
            

    df_geometry_barrel = pd.DataFrame(data_barrel, columns=columns_barrel)
    df_geometry_endcap = pd.DataFrame(data_endcap, columns=columns_endcap)
    df_geometry        = pd.concat([df_geometry_barrel, df_geometry_endcap], ignore_index=True)
    rawId_barrel_list  = df_geometry_barrel["RPC_Id"].unique().tolist()
    rawId_endcap_list  = df_geometry_endcap["RPC_Id"].unique().tolist()
    rawId_list         = df_geometry["RPC_Id"].unique().tolist()


    # print(f"Number of rolls in BARREL: {len(df_geometry_barrel)}")
    # print(f"Number of rolls in ENDCAP: {len(df_geometry_endcap)}")
    # print(f"Number of rolls in TOTAL:  {len(df_geometry)}")

    return df_geometry