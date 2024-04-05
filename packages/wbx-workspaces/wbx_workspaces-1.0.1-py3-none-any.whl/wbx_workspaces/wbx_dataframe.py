import pandas as pd 
pd.set_option('display.max_colwidth', 120)
import wbx_workspaces.wbx_utils as wbx_utils 
from wbx_workspaces.wbx import WbxRequest as Wbxr
import json as json
from pprint import pprint

ut=wbx_utils.UtilsTrc()
wbxr=Wbxr()

# populates df with data obj based cols list of fields
#
def update_df_data(df,  data, cols):    
    if 'items' in data:
        for item in data['items']:
            ut.trace(3, f"Processing item {item}")
            new_row={}
            for f in cols:
                itemdata = item['data']
                if f in itemdata :
                    new_row[f]=itemdata[f]
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        ut.trace(3, f"no items in {data}")
    return(df)

class workspacesDF:

    cols = {'capacity':[],'displayName':[],'id':[]}

    def __init__(self, locationId="", orgId=""):
        mycols=self.cols
        self.df = pd.DataFrame(mycols)
        self.locationId=locationId
        self.add_list(locationId, orgId)

    def add_list(self, locationId="", orgId=""):
        #
        # process options
        params="?"
        if (locationId):
            params=f"{params}locationId={locationId}"
        #
        # get row data
        self.jsonList = wbxr.get_wbx_data(f"workspaces", f"{params}")
        # pprint(self.jsonList)
        #
        # build DF 
        if 'items' in self.jsonList:
            for item in self.jsonList['items']:
                ut.trace(3, f"Processing item {item}")
                new_row={}
                for f in self.cols:
                    if f in item:
                        new_row[f]=item[f]
                self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            ut.trace(3, f"Error listing workspaces")
        
    def print(self, csvFile=""):
        df=self.df
        print(df.loc[:, ~df.columns.isin([''])])
        if csvFile:
            df.to_csv(csvFile, index=False)
            ut.trace(2, f"{csvFile} written.")

class locationsDF:

    cols = {'name':[],'id':[]}

    def __init__(self, orgId=""):
        
        mycols=self.cols
        self.df = pd.DataFrame(mycols)
        self.add_list(orgId)

    def add_list(self, orgId=""):
        params=""
        if (orgId):
            params=f"?OrgId={orgId}"
        #
        # get row data
        self.jsonList = wbxr.get_wbx_data(f"locations", f"{params}")
        #
        # build DF
        if 'items' in self.jsonList:
            for item in self.jsonList['items']:
                ut.trace(3, f"Processing item {item}")
                new_row={}
                for f in self.cols:
                    if f in item:
                        new_row[f]=item[f]
                self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            ut.trace(3, f"Error listing workspaces")
        
    def print(self, csvFile=""):
        df=self.df
        print(df.loc[:, ~df.columns.isin([''])])
        if csvFile:
            df.to_csv(csvFile, index=False)
            ut.trace(2, f"{csvFile} written.")

class metricsDF :

    frm = wbx_utils.midnight_iso_ms(1)
    to = wbx_utils.midnight_iso_ms(0)  

    def __init__(self, workspace_id, metric):    

        self.metric=metric
        self.workspace_id=workspace_id
        
        match metric:
            case 'peopleCount':
                self.endpoint="workspaceMetrics"
                self.params=f"&metricName={metric}&from={self.frm}"
                cols = {'start':[], 'end':[], 'mean':[]}
                self.df = pd.DataFrame(cols)


            case 'timeUsed':
                self.endpoint="workspaceDurationMetrics"
                self.params=f"&metricName={metric}&from={self.frm}"
                cols = {'start':[], 'end':[], 'duration':[]}
                self.df = pd.DataFrame(cols)
            
            case _ :
                print(f"Error metric {metric} not expected ")
    
        self.add_list(workspace_id)

    def add_list(self, workspace_id):
        self.jsonList = wbxr.get_wbx_data(f"{self.endpoint}?workspaceId={workspace_id}{self.params}")

    def write_to_file(self):
        if (self.jsonList): 
            file_name=f"{self.metric}_{self.workspace_id}_{self.frm}.json"
            with open(file_name, "w") as jsfile:
                jsfile.write(json.dumps(self.jsonList['items'], indent=2))
                print(f"Created {file_name}")
        else:
            print(f"No {self.metric} data for {self.workspace_id}")




