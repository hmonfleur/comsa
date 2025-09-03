from pprint import pprint
import yaml
from pathlib import Path
from argparse import ArgumentParser
from numpy import average
import pandas as pd

def get_all_services(data):
    retval = [ svc for app in data.keys() for svc in data[app]["all_services"] ] 
    return retval

def compute_average_service_tangling(data):
    retval = average([ float(value) for app in data.keys() for value in data[app]["tangling"].values() ])
    return retval
    

# COMMAND LINE ARGUMENT PARSER
argument_parser = ArgumentParser(
        prog = 'tangling analysis',
        description = 'Analyses files resulting from comsa-type-tangling')

argument_parser.add_argument("source_folder", type=str, help="Directory containing files to analyse.")
argument_parser.add_argument("results_folder", type=str, help="Folder to save results.")
args = vars(argument_parser.parse_args())

data = {}
results = {}
folder = Path(args["source_folder"])
for file in folder.iterdir():
    if file.is_file():  # skip subdirectories
        with open(file, "r", encoding="utf-8") as f:
            data[file.name.split(".")[0]] = yaml.safe_load(f)

print("---")
print("APPS")
pprint(list(data.keys()))
print("---")
print("APPS NB")
pprint(len(data.keys()))
print("---")
print("DATA ENTRIES")
pprint(list(data[list(data.keys())[0]].keys()))
print("---")

# ARCHITECTURE BY APP
type_concern_arch_nb_app = { app:data[app]["architecture_nb_by_type"] for app in data }

for app in list(type_concern_arch_nb_app.values()):
    to_remove = set()
    app["RestartConcern"] = 0
    for concern in list(app.keys()):
        if concern != "ImageConcern" and "Image" in concern:
            if "ImageConcern" not in app:
                app["ImageConcern"] = 0
            app["ImageConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "DeployConcern" and "Deploy" in concern:
            if "DeployConcern" not in app:
                app["DeployConcern"] = 0
            app["DeployConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "BuildConcern" and "Build" in concern:
            if "BuildConcern" not in app:
                app["BuildConcern"] = 0
            app["BuildConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "RestartConcern" and "Restart" in concern:
            if "RestartConcern" not in app:
                app["RestartConcern"] = 0
            app["RestartConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "ClusterConcern" and "Cluster" in concern:
            if "ClusterConcern" not in app:
                app["ClusterConcern"] = 0
            app["ClusterConcern"] += app[concern]
            to_remove.add(concern)
    for concern in to_remove:
        del app[concern]


df = pd.DataFrame.from_dict(type_concern_arch_nb_app)
resultpath = Path(args["results_folder"])
resultpath.mkdir(exist_ok=True)
resultpath = resultpath.joinpath("type_concern_arch_nb_app.csv")
df.reset_index(inplace=True)
df.rename(columns={"index": "App"}, inplace=True)
sum_row = df.apply(pd.to_numeric, errors="coerce").sum(axis=0)
df.loc["Sum"] = sum_row
df = df.sort_index(
    axis=1,
    key=lambda s: s.astype(str).str.strip().str.casefold()
)
df.to_csv(resultpath, sep="&", index=False)


# POLICIES BY APP
type_concern_policies_nb_app = { app:data[app]["policies_nb_by_type"] for app in data }

for app in list(type_concern_policies_nb_app.values()):
    to_remove = set()
    app["RestartConcern"] = 0
    for concern in list(app.keys()):
        if concern != "ImageConcern" and "Image" in concern:
            if "ImageConcern" not in app:
                app["ImageConcern"] = 0
            app["ImageConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "DeployConcern" and "Deploy" in concern:
            if "DeployConcern" not in app:
                app["DeployConcern"] = 0
            app["DeployConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "BuildConcern" and "Build" in concern:
            if "BuildConcern" not in app:
                app["BuildConcern"] = 0
            app["BuildConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "RestartConcern" and "Restart" in concern:
            if "RestartConcern" not in app:
                app["RestartConcern"] = 0
            app["RestartConcern"] += app[concern]
            to_remove.add(concern)
        if concern != "ClusterConcern" and "Cluster" in concern:
            if "ClusterConcern" not in app:
                app["ClusterConcern"] = 0
            app["ClusterConcern"] += app[concern]
            to_remove.add(concern)
    for concern in to_remove:
        del app[concern]

df = pd.DataFrame.from_dict(type_concern_policies_nb_app)

# prepare output path
resultpath = Path(args["results_folder"])
resultpath.mkdir(exist_ok=True)
resultpath = resultpath.joinpath("type_concern_policies_nb_app.csv")

# reset and rename index
df.reset_index(inplace=True)
df.rename(columns={"index": "App"}, inplace=True)

# ---- SUM COLUMN (row totals) ----
# sum across all columns except 'App' and an existing 'RowSum' (safe on re-runs)
cols_to_sum = [c for c in df.columns if c not in ("App", "RowSum")]
numeric_view = df[cols_to_sum].apply(pd.to_numeric, errors="coerce")
df["RowSum"] = numeric_view.sum(axis=1)

# ---- SUM ROW (column totals, incl. grand total in RowSum) ----
sum_row_full = numeric_view.sum().to_dict()
sum_row_full["App"] = "Sum"
sum_row_full["RowSum"] = numeric_view.sum(axis=1).sum()  # grand total
df = pd.concat([df, pd.DataFrame([sum_row_full])], ignore_index=True)

# optional: sort columns alphabetically (case-insensitive)
df = df.sort_index(
    axis=1,
    key=lambda s: s.astype(str).str.strip().str.casefold()
)

# move RowSum to the end
if "RowSum" in df.columns:
    cols = [c for c in df.columns if c != "RowSum"] + ["RowSum"]
    df = df[cols]

# save
df.to_csv(resultpath, sep="&", index=False)


# POLICIES PRESENCE GLOBAL
policies_dataset_presence = {}
for app in data:
    for concern in data[app]["policies_nb_by_type"]:
        if concern not in policies_dataset_presence:
            policies_dataset_presence[concern] = 0
        policies_dataset_presence[concern] +=1

to_remove = set()
policies_dataset_presence["RestartConcern"] = 0
for concern in list(policies_dataset_presence.keys()):
    if concern != "ImageConcern" and "Image" in concern:
        if "ImageConcern" not in policies_dataset_presence:
            policies_dataset_presence["ImageConcern"] = 0
        policies_dataset_presence["ImageConcern"] += policies_dataset_presence[concern]
        to_remove.add(concern)
    if concern != "DeployConcern" and "Deploy" in concern:
        if "DeployConcern" not in policies_dataset_presence:
            policies_dataset_presence["DeployConcern"] = 0
        policies_dataset_presence["DeployConcern"] += policies_dataset_presence[concern]
        to_remove.add(concern)
    if concern != "BuildConcern" and "Build" in concern:
        if "BuildConcern" not in policies_dataset_presence:
            policies_dataset_presence["BuildConcern"] = 0
        policies_dataset_presence["BuildConcern"] += policies_dataset_presence[concern]
        to_remove.add(concern)
    if concern != "RestartConcern" and "Restart" in concern:
        if "RestartConcern" not in policies_dataset_presence:
            policies_dataset_presence["RestartConcern"] = 0
        policies_dataset_presence["RestartConcern"] += policies_dataset_presence[concern]
        to_remove.add(concern)
    if concern != "ClusterConcern" and "Cluster" in concern:
        if "ClusterConcern" not in policies_dataset_presence:
            policies_dataset_presence["ClusterConcern"] = 0
        policies_dataset_presence["ClusterConcern"] += policies_dataset_presence[concern]
        to_remove.add(concern)
for concern in to_remove:
    del policies_dataset_presence[concern]


for concern in policies_dataset_presence:
    policies_dataset_presence[concern] = (policies_dataset_presence[concern]/len(data))*100


df = pd.DataFrame.from_dict(policies_dataset_presence, orient="index")
df = df.sort_values(by=0, ascending=False)
resultpath = Path(args["results_folder"])
resultpath.mkdir(exist_ok=True)
resultpath = resultpath.joinpath("policies_dataset_presence.csv")
df.to_csv(resultpath, sep="&", index=True)
#
#arch_dataset_presence = {}
#for app in data:
#    for concern in data[app]["architecture_nb_by_type"]:
#        if concern not in arch_dataset_presence:
#            arch_dataset_presence[concern] = 0
#        arch_dataset_presence[concern] +=1
#for concern in arch_dataset_presence:
#    arch_dataset_presence[concern] = (arch_dataset_presence[concern]/len(data))*100
#
#
#df = pd.DataFrame.from_dict(arch_dataset_presence, orient="index")
#df = df.sort_values(by=0, ascending=False)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("arch_dataset_presence.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
#policies_scattering_by_app = { app:{concern_type: data[app]["concern_scattering_by_type"][concern_type]  for concern_type in set(data[app]["policies_concerns"].values())} for app in data}
#df = pd.DataFrame.from_dict(policies_scattering_by_app)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("policies_scattering_by_app.csv")
#df.reset_index(inplace=True)
#df.rename(columns={"index": "App"}, inplace=True)
#sum_row = df.apply(pd.to_numeric, errors="coerce").sum(axis=0)
#df.loc["Sum"] = sum_row
#df = df.sort_index(
#    axis=1,
#    key=lambda s: s.astype(str).str.strip().str.casefold()
#)
#df.to_csv(resultpath, sep="&", index=False)
#
#
#architecture_scattering_by_app = { app:{concern_type: round(data[app]["concern_scattering_by_type"][concern_type]*100,2)  for concern_type in set(data[app]["architecture_concerns"].values())} for app in data}
#df = pd.DataFrame.from_dict(architecture_scattering_by_app)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("architecture_scattering_by_app.csv")
#df.reset_index(inplace=True)
#df.rename(columns={"index": "App"}, inplace=True)
#sum_row = df.apply(pd.to_numeric, errors="coerce").sum(axis=0)
#df.loc["Sum"] = sum_row
#df = df.sort_index(
#    axis=1,
#    key=lambda s: s.astype(str).str.strip().str.casefold()
#)
#df.to_csv(resultpath, sep="&", index=False)
#
#average_policies_scattering_by_type = {}
#for app in data.values():
#    for concern in set(app["policies_concerns"].values()):
#        if concern not in average_policies_scattering_by_type:
#            average_policies_scattering_by_type[concern] = []
#        average_policies_scattering_by_type[concern].append(app["concern_scattering_by_type"][concern])
#to_remove = set()
#for concern in average_policies_scattering_by_type:
#    if concern != "ImageConcern" and "Image" in concern:
#        average_policies_scattering_by_type["ImageConcern"].extend(average_policies_scattering_by_type[concern])
#        to_remove.add(concern)
#for concern in average_policies_scattering_by_type:
#    if concern != "DeployConcern" and "Deploy" in concern:
#        average_policies_scattering_by_type["DeployConcern"].extend(average_policies_scattering_by_type[concern])
#        to_remove.add(concern)
#for concern in average_policies_scattering_by_type:
#    if concern != "BuildConcern" and "Build" in concern:
#        average_policies_scattering_by_type["BuildConcern"].extend(average_policies_scattering_by_type[concern])
#        to_remove.add(concern)
#average_policies_scattering_by_type["RestartConcern"] = []
#for concern in average_policies_scattering_by_type:
#    if concern != "RestartConcern" and "Restart" in concern:
#        average_policies_scattering_by_type["RestartConcern"].extend(average_policies_scattering_by_type[concern])
#        to_remove.add(concern)
#for concern in average_policies_scattering_by_type:
#    if concern != "ClusterConcern" and "Cluster" in concern:
#        average_policies_scattering_by_type["ClusterConcern"].extend(average_policies_scattering_by_type[concern])
#        to_remove.add(concern)
#for k,v in average_policies_scattering_by_type.items():
#    if len(v)<2:
#        to_remove.add(k)
#for concern in to_remove:
#    del average_policies_scattering_by_type[concern]
#for concern in average_policies_scattering_by_type:
#    tmp = average_policies_scattering_by_type[concern]
#    average_policies_scattering_by_type[concern] = round((average(tmp))*100, 2)
#
#df = pd.DataFrame.from_dict(average_policies_scattering_by_type, orient="index")
#df = df.sort_values(by=0, ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("average_policies_scattering_by_type.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
#average_architecture_scattering_by_type = {}
#for app in data.values():
#    for concern in set(app["architecture_concerns"].values()):
#        if concern not in average_architecture_scattering_by_type:
#            average_architecture_scattering_by_type[concern] = []
#        average_architecture_scattering_by_type[concern].append(app["concern_scattering_by_type"][concern])
#for concern in average_architecture_scattering_by_type:
#    tmp = average_architecture_scattering_by_type[concern]
#    average_architecture_scattering_by_type[concern] = round((average(tmp))*100, 2)
#
#df = pd.DataFrame.from_dict(average_architecture_scattering_by_type, orient="index")
#df = df.sort_values(by=0, ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("average_architecture_scattering_by_type.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
#business_service_proportion =  {n:round((app["business_service_nb"]/app["services_nb"])*100,2) for n,app in data.items()}
#infrastructure_service_proportion = {n:round((app["infrastructure_services_nb"]/app["services_nb"])*100,2) for n,app in data.items()}
#proportions_all = sorted([(n, business_service_proportion[n], infrastructure_service_proportion[n], data[n]["services_nb"]) for n in data], key=lambda x: x[1])
#average_business_proportion = average([ x[1] for x in proportions_all ])
#average_infrastructure_proportion = average( [ x[2] for x in proportions_all ] )
#average_service_nb = average( [ x[3] for x in proportions_all ] )
#proportions_all.append(("AVERAGE", average_business_proportion, average_infrastructure_proportion, average_service_nb) )
#
#df = pd.DataFrame(proportions_all, columns=["APP", "Business", "Infrastructure", "n_svc"])
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("proportion_business_infrastructure.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
## BUSINESS SERVICES ARCHITECTURE PATTERN PROPORTION
#business_architecture_repartition = dict()
#business_architecture_repartition["nb"] = 0
#business_architecture_repartition["concerns"] = {}
#business_architecture_repartition["proportion"] = {}
#
#for app in data.values():
#    for k,v in app["strict_architecture_by_service"].items():
#        if k in app["business_services"]:
#            business_architecture_repartition["nb"] += 1
#            for concern_type in set(v.values()):
#                if concern_type not in business_architecture_repartition["concerns"]:
#                    business_architecture_repartition["concerns"][concern_type] =  0
#                business_architecture_repartition["concerns"][concern_type] += 1
#
#for k,v in business_architecture_repartition["concerns"].items():
#    business_architecture_repartition["proportion"][k] = (v/business_architecture_repartition["nb"])*100
#    
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in business_architecture_repartition["proportion"].items() ], key = lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("business_service_arch_repartition.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
## BUSINESS SERVICES POLICIES PATTERN PROPORTION
#business_policies_repartition = dict()
#business_policies_repartition["nb"] = 0
#business_policies_repartition["concerns"] = {}
#business_policies_repartition["proportion"] = {}
#
#for app in data.values():
#    for k,v in app["strict_policies_by_service"].items():
#        if k in app["business_services"]:
#            business_policies_repartition["nb"] += 1
#            for concern_type in set(v.values()):
#                if concern_type not in business_policies_repartition["concerns"]:
#                    business_policies_repartition["concerns"][concern_type] =  0
#                business_policies_repartition["concerns"][concern_type] += 1
#
#
#to_remove = set()
#business_policies_repartition["concerns"]["RestartConcern"] = 0
#for concern in list(business_policies_repartition["concerns"].keys()):
#    if concern != "ImageConcern" and "Image" in concern:
#        if "ImageConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["ImageConcern"] = 0
#        business_policies_repartition["concerns"]["ImageConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "DeployConcern" and "Deploy" in concern:
#        if "DeployConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["DeployConcern"] = 0
#        business_policies_repartition["concerns"]["DeployConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "BuildConcern" and "Build" in concern:
#        if "BuildConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["BuildConcern"] = 0
#        business_policies_repartition["concerns"]["BuildConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "RestartConcern" and "Restart" in concern:
#        if "RestartConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["RestartConcern"] = 0
#        business_policies_repartition["concerns"]["RestartConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "ClusterConcern" and "Cluster" in concern:
#        if "ClusterConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["ClusterConcern"] = 0
#        business_policies_repartition["concerns"]["ClusterConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#for concern in to_remove:
#    del business_policies_repartition["concerns"][concern]
#
#for k,v in business_policies_repartition["concerns"].items():
#    business_policies_repartition["proportion"][k] = (v/business_policies_repartition["nb"])*100
#
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in business_policies_repartition["proportion"].items()], key= lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("business_service_policies_repartition.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
#
### BUSINESS SERVICES ARCHITECTURE PATTERN PROPORTION APP LESS THAN 15
#business_architecture_repartition = dict()
#business_architecture_repartition["nb"] = 0
#business_architecture_repartition["concerns"] = {}
#business_architecture_repartition["proportion"] = {}
#
#for app in data.values():
#    if app["services_nb"] <= 15:
#        for k,v in app["strict_architecture_by_service"].items():
#                if k in app["business_services"]:
#                    business_architecture_repartition["nb"] += 1
#                    for concern_type in set(v.values()):
#                        if concern_type not in business_architecture_repartition["concerns"]:
#                            business_architecture_repartition["concerns"][concern_type] =  0
#                        business_architecture_repartition["concerns"][concern_type] += 1
#
#for k,v in business_architecture_repartition["concerns"].items():
#    business_architecture_repartition["proportion"][k] = (v/business_architecture_repartition["nb"])*100
#    
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in business_architecture_repartition["proportion"].items() ], key = lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("business_service_arch_repartition_inf15.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
## BUSINESS SERVICES POLICIES PATTERN PROPORTION LESS THAN 15 
#business_policies_repartition = dict()
#business_policies_repartition["nb"] = 0
#business_policies_repartition["concerns"] = {}
#business_policies_repartition["proportion"] = {}
#
#for app in data.values():
#    if app["services_nb"] <= 15:
#        for k,v in app["strict_policies_by_service"].items():
#            if k in app["business_services"]:
#                business_policies_repartition["nb"] += 1
#                for concern_type in set(v.values()):
#                    if concern_type not in business_policies_repartition["concerns"]:
#                        business_policies_repartition["concerns"][concern_type] =  0
#                    business_policies_repartition["concerns"][concern_type] += 1
#
#to_remove = set()
#business_policies_repartition["concerns"]["RestartConcern"] = 0
#for concern in list(business_policies_repartition["concerns"].keys()):
#    if concern != "ImageConcern" and "Image" in concern:
#        if "ImageConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["ImageConcern"] = 0
#        business_policies_repartition["concerns"]["ImageConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "DeployConcern" and "Deploy" in concern:
#        if "DeployConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["DeployConcern"] = 0
#        business_policies_repartition["concerns"]["DeployConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "BuildConcern" and "Build" in concern:
#        if "BuildConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["BuildConcern"] = 0
#        business_policies_repartition["concerns"]["BuildConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "RestartConcern" and "Restart" in concern:
#        if "RestartConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["RestartConcern"] = 0
#        business_policies_repartition["concerns"]["RestartConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "ClusterConcern" and "Cluster" in concern:
#        if "ClusterConcern" not in business_policies_repartition["concerns"]:
#            business_policies_repartition["concerns"]["ClusterConcern"] = 0
#        business_policies_repartition["concerns"]["ClusterConcern"] += business_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#for concern in to_remove:
#    del business_policies_repartition["concerns"][concern]
#
#
#for k,v in business_policies_repartition["concerns"].items():
#    business_policies_repartition["proportion"][k] = (v/business_policies_repartition["nb"])*100
#
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in business_policies_repartition["proportion"].items()], key= lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("business_service_policies_repartition_inf15.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
#
### INFRASTRUCTURE SERVICES ARCHITECTURE PATTERN PROPORTION APP LESS THAN 15
#infrastructure_architecture_repartition = dict()
#infrastructure_architecture_repartition["nb"] = 0
#infrastructure_architecture_repartition["concerns"] = {}
#infrastructure_architecture_repartition["proportion"] = {}
#
#for app in data.values():
#    if app["services_nb"] <= 15:
#        for k,v in app["strict_architecture_by_service"].items():
#                if k in app["infrastructure_services"]:
#                    infrastructure_architecture_repartition["nb"] += 1
#                    for concern_type in set(v.values()):
#                        if concern_type not in infrastructure_architecture_repartition["concerns"]:
#                            infrastructure_architecture_repartition["concerns"][concern_type] =  0
#                        infrastructure_architecture_repartition["concerns"][concern_type] += 1
#
#for k,v in infrastructure_architecture_repartition["concerns"].items():
#    infrastructure_architecture_repartition["proportion"][k] = (v/infrastructure_architecture_repartition["nb"])*100
#    
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in infrastructure_architecture_repartition["proportion"].items() ], key = lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("infrastructure_service_arch_repartition_inf15.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
## INFRASTRUCTURE SERVICES POLICIES PATTERN PROPORTION LESS THAN 15 
#infrastructure_policies_repartition = dict()
#infrastructure_policies_repartition["nb"] = 0
#infrastructure_policies_repartition["concerns"] = {}
#infrastructure_policies_repartition["proportion"] = {}
#
#for app in data.values():
#    if app["services_nb"] <= 15:
#        for k,v in app["strict_policies_by_service"].items():
#            if k in app["infrastructure_services"]:
#                infrastructure_policies_repartition["nb"] += 1
#                for concern_type in set(v.values()):
#                    if concern_type not in infrastructure_policies_repartition["concerns"]:
#                        infrastructure_policies_repartition["concerns"][concern_type] =  0
#                    infrastructure_policies_repartition["concerns"][concern_type] += 1
#
#to_remove = set()
#infrastructure_policies_repartition["concerns"]["RestartConcern"] = 0
#for concern in list(infrastructure_policies_repartition["concerns"].keys()):
#    if concern != "ImageConcern" and "Image" in concern:
#        if "ImageConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["ImageConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["ImageConcern"] += 1
#        to_remove.add(concern)
#    if concern != "DeployConcern" and "Deploy" in concern:
#        if "DeployConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["DeployConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["DeployConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "BuildConcern" and "Build" in concern:
#        if "BuildConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["BuildConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["BuildConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "RestartConcern" and "Restart" in concern:
#        if "RestartConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["RestartConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["RestartConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "ClusterConcern" and "Cluster" in concern:
#        if "ClusterConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["ClusterConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["ClusterConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#for concern in to_remove:
#    del infrastructure_policies_repartition["concerns"][concern]
#
#
#for k,v in infrastructure_policies_repartition["concerns"].items():
#    infrastructure_policies_repartition["proportion"][k] = (v/infrastructure_policies_repartition["nb"])*100
#
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in infrastructure_policies_repartition["proportion"].items()], key= lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("infrastructure_service_policies_repartition_inf15.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
#
### INFRASTRUCTURE SERVICES ARCHITECTURE PATTERN PROPORTION APP 
#infrastructure_architecture_repartition = dict()
#infrastructure_architecture_repartition["nb"] = 0
#infrastructure_architecture_repartition["concerns"] = {}
#infrastructure_architecture_repartition["proportion"] = {}
#
#for app in data.values():
#    for k,v in app["strict_architecture_by_service"].items():
#            if k in app["infrastructure_services"]:
#                infrastructure_architecture_repartition["nb"] += 1
#                for concern_type in set(v.values()):
#                    if concern_type not in infrastructure_architecture_repartition["concerns"]:
#                        infrastructure_architecture_repartition["concerns"][concern_type] =  0
#                    infrastructure_architecture_repartition["concerns"][concern_type] += 1
#
#for k,v in infrastructure_architecture_repartition["concerns"].items():
#    infrastructure_architecture_repartition["proportion"][k] = (v/infrastructure_architecture_repartition["nb"])*100
#    
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in infrastructure_architecture_repartition["proportion"].items() ], key = lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("infrastructure_service_arch_repartition.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
## INFRASTRUCTURE SERVICES POLICIES PATTERN PROPORTION
#infrastructure_policies_repartition = dict()
#infrastructure_policies_repartition["nb"] = 0
#infrastructure_policies_repartition["concerns"] = {}
#infrastructure_policies_repartition["proportion"] = {}
#
#for app in data.values():
#    for k,v in app["strict_policies_by_service"].items():
#        if k in app["infrastructure_services"]:
#            infrastructure_policies_repartition["nb"] += 1
#            for concern_type in set(v.values()):
#                if concern_type not in infrastructure_policies_repartition["concerns"]:
#                    infrastructure_policies_repartition["concerns"][concern_type] =  0
#                infrastructure_policies_repartition["concerns"][concern_type] += 1
#
#to_remove = set()
#infrastructure_policies_repartition["concerns"]["RestartConcern"] = 0
#for concern in list(infrastructure_policies_repartition["concerns"].keys()):
#    if concern != "ImageConcern" and "Image" in concern:
#        if "ImageConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["ImageConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["ImageConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "DeployConcern" and "Deploy" in concern:
#        if "DeployConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["DeployConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["DeployConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "BuildConcern" and "Build" in concern:
#        if "BuildConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["BuildConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["BuildConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "RestartConcern" and "Restart" in concern:
#        if "RestartConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["RestartConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["RestartConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "ClusterConcern" and "Cluster" in concern:
#        if "ClusterConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["ClusterConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["ClusterConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#for concern in to_remove:
#    del infrastructure_policies_repartition["concerns"][concern]
#
#
#for k,v in infrastructure_policies_repartition["concerns"].items():
#    infrastructure_policies_repartition["proportion"][k] = (v/infrastructure_policies_repartition["nb"])*100
#
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in infrastructure_policies_repartition["proportion"].items()], key= lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("infrastructure_service_policies_repartition.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
#
### ALL SERVICES ARCHITECTURE PATTERN PROPORTION APP 
#infrastructure_architecture_repartition = dict()
#infrastructure_architecture_repartition["nb"] = 0
#infrastructure_architecture_repartition["concerns"] = {}
#infrastructure_architecture_repartition["proportion"] = {}
#
#for app in data.values():
#    for k,v in app["strict_architecture_by_service"].items():
#        infrastructure_architecture_repartition["nb"] += 1
#        for concern_type in set(v.values()):
#            if concern_type not in infrastructure_architecture_repartition["concerns"]:
#                infrastructure_architecture_repartition["concerns"][concern_type] =  0
#            infrastructure_architecture_repartition["concerns"][concern_type] += 1
#
#for k,v in infrastructure_architecture_repartition["concerns"].items():
#    infrastructure_architecture_repartition["proportion"][k] = (v/infrastructure_architecture_repartition["nb"])*100
#    
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in infrastructure_architecture_repartition["proportion"].items() ], key = lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("all_service_arch_repartition.csv")
#df.to_csv(resultpath, sep="&", index=True)
#
## INFRASTRUCTURE SERVICES POLICIES PATTERN PROPORTION
#infrastructure_policies_repartition = dict()
#infrastructure_policies_repartition["nb"] = 0
#infrastructure_policies_repartition["concerns"] = {}
#infrastructure_policies_repartition["proportion"] = {}
#
#for app in data.values():
#    for k,v in app["strict_policies_by_service"].items():
#        infrastructure_policies_repartition["nb"] += 1
#        for concern_type in set(v.values()):
#            if concern_type not in infrastructure_policies_repartition["concerns"]:
#                infrastructure_policies_repartition["concerns"][concern_type] =  0
#            infrastructure_policies_repartition["concerns"][concern_type] += 1
#
#to_remove = set()
#infrastructure_policies_repartition["concerns"]["RestartConcern"] = 0
#for concern in list(infrastructure_policies_repartition["concerns"].keys()):
#    if concern != "ImageConcern" and "Image" in concern:
#        if "ImageConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["ImageConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["ImageConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "DeployConcern" and "Deploy" in concern:
#        if "DeployConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["DeployConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["DeployConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "BuildConcern" and "Build" in concern:
#        if "BuildConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["BuildConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["BuildConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "RestartConcern" and "Restart" in concern:
#        if "RestartConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["RestartConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["RestartConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#    if concern != "ClusterConcern" and "Cluster" in concern:
#        if "ClusterConcern" not in infrastructure_policies_repartition["concerns"]:
#            infrastructure_policies_repartition["concerns"]["ClusterConcern"] = 0
#        infrastructure_policies_repartition["concerns"]["ClusterConcern"] += infrastructure_policies_repartition["concerns"][concern]
#        to_remove.add(concern)
#for concern in to_remove:
#    del infrastructure_policies_repartition["concerns"][concern]
#
#
#for k,v in infrastructure_policies_repartition["concerns"].items():
#    infrastructure_policies_repartition["proportion"][k] = (v/infrastructure_policies_repartition["nb"])*100
#
#df = pd.DataFrame(sorted([ (k,round(v,2)) for (k,v) in infrastructure_policies_repartition["proportion"].items()], key= lambda x: x[1]), columns=["Concern", "%"])
#df = df.sort_values(by="%", ascending=False)
#print(df)
#resultpath = Path(args["results_folder"])
#resultpath.mkdir(exist_ok=True)
#resultpath = resultpath.joinpath("all_service_policies_repartition.csv")
#df.to_csv(resultpath, sep="&", index=True)
