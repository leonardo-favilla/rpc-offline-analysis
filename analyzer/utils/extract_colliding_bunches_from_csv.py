import pandas as pd

# Load the .csv file containing bunches information
inFile       = "./lhc_schemes/Fill_10649/lhc_scheme_10649.csv"
outFile      = "./lhc_schemes/Fill_10649/colliding_10649.txt"
df           = pd.read_csv(inFile, header=0)

# Select only colliding bunches
df_colliding        = df[df["peak_lumi"]>=1]
colliding_bunches   = df_colliding["bunch_number"].values
# Save colliding bunches to a .txt file
with open(outFile, "w") as f:
    for bunch in colliding_bunches:
        f.write(str(bunch)+"\n")

# Print some information
print(df.columns)
print(f"total number of bunches {len(df)} ---> number of colliding bunches {len(df_colliding)}\n")
print("Colliding bunches:")
print(df_colliding)
print(f"Colliding bunches saved to: {outFile}")
