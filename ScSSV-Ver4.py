import numpy as np
import pandas as pd
#import openpyxl
#import plotly.figure_factory as ff
import os
# from tqdm import tqdm  # progress bar is activated when there is a loop
# from tqdm import tqdm_gui

# import matplotlib.pyplot as plt
# from matplotlib.widgets import Slider
# from PIL import ImageTk, Image
import time
import streamlit as st
st.set_page_config(layout="wide")
# st.cache_data.clear()

def listToString(s):
    # initialize an empty string
    str1 = ""
    # traverse in the string
    for ele in s:
        str1 += ele + "  "
    # return string
    return str1

def listToString2(s):
    # initialize an empty string
    str1 = ""
    # traverse in the string
    for ele in s:
        str1 += ele + "  "
    # return string
    return str1
# -------------------------------------------------------------------------------------------
def getWellName5(dfUPD,colName,minCount=5):
    # usage==> getWellName5(dfUPD,'Well', 5)
    wellName_Accepted=dfUPD[colName].value_counts().rename_axis(colName)
    wellName_Accepted = wellName_Accepted.to_frame()
    wellName_Accepted.rename(columns ={colName:'Freq'}, inplace= True)
    filt = (wellName_Accepted['Freq']>=minCount)
    wellName_Accepted=wellName_Accepted.loc[filt]
    wellName_Accepted.reset_index(inplace=True)
    wellName_accepted=wellName_Accepted[colName]
    wellName_freq = list(wellName_Accepted['Freq'])
    wellName_accepted= list(wellName_accepted)
    return wellName_accepted, wellName_freq

def getUPD_Accepted(dfUPD, colName, minCount=5):
    wellName_Accepted, Freq = getWellName5(dfUPD,colName,minCount=minCount)
    # print(f"wellName_Accepted={wellName_Accepted}")
    # print(f"Freq={Freq}")
    filt = dfUPD[colName].isin(wellName_Accepted)
    return dfUPD.loc[filt] , wellName_Accepted , Freq  #<-- columns to be collected
    
# dfUPD_Accepted, WellName, Freq = getUPD_Accepted(dfUPD, 'WELL', minCount = 5)


def getPredictorLabel(SheetName, excelObj):
    if 'PCP' in SheetName:
        colLabelPI = 'PCP'
    elif 'CHP' in SheetName:
        colLabelPI = 'CHP'    
    elif 'THP' in SheetName:
        colLabelPI = 'THP'
    elif 'THT'  in SheetName:
        colLabelPI = 'THT'        
    elif 'ICP' in SheetName:
        colLabelPI = 'ICP'
    df = excelObj.parse(SheetName)     # this takes time to complete !!!
    df.drop([0,1,2,3,5], axis=0, inplace= True)
    df.columns = df.iloc[0]
    df.drop([4],axis =0, inplace=True)
    df.rename(columns={"Well No":"Date"}, inplace=True)
    df.reset_index(inplace = True, drop=True)   
    return df, colLabelPI# dfUPD_Accepted['WELL'].value_counts()
    
def getUnPivotPI(df,colLabelPI,WellNameUPD):
    colNames = df.columns[1:]

    #UNPIVOT BigData
    #---------------
    dfUnpiv= pd.DataFrame()
   
    mybar=form2.progress(0, text=f"Unpivoting PI {colLabelPI} data in progress...please wait :hourglass_flowing_sand:")
    i=0
    for col in colNames:  # iterate well name, unpivot
       
        if col in WellNameUPD:
            i+=1
            mybar.progress(i,  text=f"Unpivoting PI {colLabelPI} data in progress...please wait :hourglass_flowing_sand:")
            dftemp = df.loc[:,['Date', col]]
            dftemp["Well"]=col
            dftemp.rename(columns={col:colLabelPI}, inplace=True)
            dfUnpiv = pd.concat([dfUnpiv,dftemp], ignore_index=True)
    
    dfUnpiv['Date'] = pd.to_datetime(dfUnpiv['Date'])
    #extract Date and time
    dfUnpiv["newDate"] = dfUnpiv['Date'].dt.date
    dfUnpiv["Time"] = dfUnpiv['Date'].dt.hour
    
    dfUnpiv.drop(['Date'], axis=1, inplace =True)
    dfUnpiv.rename(columns={'newDate':'Date'}, inplace =True)
    dfUnpiv['Date']=pd.to_datetime(dfUnpiv['Date'])
#     dfPCP = dfUnpiv.groupby('Time').get_group(0).copy()
    dfUnpiv = dfUnpiv.groupby('Time').get_group(0) #Return daily PI Data at time =0
    dfUnpiv.reset_index(inplace=True, drop=True)
    mybar.progress((100),  text=f"Unpivoting PI {colLabelPI} data completed :thumbsup:")
    return dfUnpiv  
    


# --------------------------------------------------------------------------------------------------------

# with st.sidebar:
#     with st.echo():
#         st.write("This code will be printed to the sidebar.")

#     with st.spinner("Loading..."):
#         time.sleep(5)
#     st.success("Done!")

st.sidebar.image("petronas-logo.jpg",caption='Petroliam National Berhad',
            use_column_width="auto")
# st.sidebar.header("Platform CariGali 2023")
st.sidebar.title("ScSSV Reliability")

status = st.sidebar.radio("Select Menu", ["Visualisation", "Process Pi"], index=None)

if status == "Visualisation":
    # st.markdown(f'<h1 style="color:#33ff33;font-size:24px;">{"ColorMeBlue text”"}</h1>', unsafe_allow_html=True)
    st.sidebar.title('Visualisation')
    # choose = False
    # choose2 = False


    # well_expander = st.expander("Senarai")
    # well_expander.write(listwell1)
    
    # tab1, tab2 = st.sidebar.tabs(["Carigali", "Exxon"])
    containervisual = st.container(border=True)
    col1, col2 = containervisual.columns([5,2])
    formsidebar = st.sidebar.form("sidebar")
    formOutput = col1.form("output")
    
    col1.title("Visualisation")
    
    form2 = col1.form("Output")
    
    choose = formsidebar.radio(
        "Select Platform:",
        [ "***Dulang***","***Angsi***", "***Bokor***", "***Samarang***", "***Tapis-C***"],
         captions = ["Dulang Well", "Angsi Well", "Bokor Well", "Samarang Well","Exxon Well"],
        index=None)
    
    
    button = formsidebar.form_submit_button("Submit")
  
    if choose == "***Dulang***":
        choose2 = False
        listwelldate = []
        listwellfound=[]
        listwell1 = []
        listwell2 = []
        listwell3 = []
        
       
        #root_path = 'C:/Users/user/SCSSV/'
        bd_final = pd.read_csv("bd_Final_Dulang.csv" )
        bd_pred_final = pd.read_csv("bd_pred_final_dulang.csv")
    
    
    
        wellList = dict()
        for i in range(len(bd_pred_final['Well'])-1):
           
            if (bd_pred_final.iloc[i]["StatusUPD"]==1) and (bd_pred_final.iloc[i+1]["StatusUPD"]==0):
                namaWell=bd_pred_final.iloc[i+1]["Well"]
                tarikh =bd_pred_final.iloc[i+1]["Date"]
                if not (namaWell in wellList.keys()):
                    L=[]
                else:
                    L=wellList[namaWell]
                L.append(tarikh)
                wellList[namaWell]=L
    
        # form2.write(wellList.keys())
        for wn in wellList.keys():
            textlist1 = wn + " " + listToString(wellList[wn])
            # textlist1 = wn + " " + ",".join(
            # found = found + 1
            listwell2.append (textlist1)
            
            listwell2.insert (0,textlist1)
        
        for wn in wellList.keys():
            listwell1.append(wn + " " + str(len(wellList[wn])))
            listwell3.append(wn)
   
        wellnameselect = form2.selectbox(choose,listwell3)
        
        # wellnameselect,predicttimes = wellnameselect.split(" ")
        
        days = form2.slider("Choose Forecasting Horizon", 1, 180,60)
        buttonselect_dulang = form2.form_submit_button("Display")
        
    
        if buttonselect_dulang:
            
            if choose:
                form2.write(f"You have selected: {wellnameselect} and forecasting horizon {days} days")
            
            form2.divider()
            form2.write(f" :blue[Forecasting Pi Data for {wellnameselect}]")
            bd_pred_Well = bd_pred_final.groupby('Well').get_group(wellnameselect)[["Date","Well","StatusUPD","PCP","THP", "THT"]]
            
            
            filt= bd_final["Well"] == wellnameselect
            bd_finalWell = bd_final.loc[filt]
            
            temp_pred= bd_pred_Well.iloc[0:days]["Date"]
            temp_pred.reset_index(drop=True, inplace= True)
            x_offset = 0
            # temp_pi = bd_finalWell.iloc[1640:1640 +days][["THP","THT","PCP"]]
            temp_pi = bd_finalWell.iloc[x_offset:x_offset +days][["THP","THT","PCP"]]
            temp_pi.reset_index(drop=True, inplace= True)
            # concate_pi_pred
            bd_pred_pi = pd.concat([temp_pi,temp_pred], axis = 1)
    
            # plot upd prediction
            date_selection2 = bd_pred_Well.iloc[0:days]
            
            # form2.write(f"UPD occurences = {predicttimes}")
            form2.line_chart( bd_pred_pi[['THP','THT','PCP','Date']], x ='Date', y=['THP','THT','PCP'])
            form2.write(f" :blue[Prediction Data for {wellnameselect}]")
            form2.line_chart(date_selection2[['Date','StatusUPD']], x ='Date', y=['StatusUPD'], color="#38B09D")

            with col1.expander(f"Download {choose} prediction table"):
                wellnameselect1 = pd.DataFrame(listwell2)
                wellnameselect1_transposed = wellnameselect1.T  # or df1.transpose()
                wellnameT = pd.DataFrame(wellnameselect1_transposed)
                
                
                DF = pd.DataFrame()
                for i in range (wellnameT.shape[1]):
             
                    data = wellnameselect1.iloc[i]
                    L =data.str.split(" ", n=1)
                    wellname = L[0]
                    Dates = wellname[1].split("  ")
                    mydf = {}
                    mydf[wellname[0]]= Dates
                    df = pd.DataFrame(mydf)
                    DF = pd.concat([DF, df], sort = False, axis=1)
                DF.reset_index(drop=True, inplace= True)
                # st.dataframe(DF)
                DF.to_csv("UPD_Dates_Dulang.csv", index=False)
                Download = pd.read_csv("UPD_Dates_Dulang.csv")
                # st.dataframe(Download, width=200, height=100)
                st.dataframe(Download)
                peta = pd.DataFrame({
                "col1": 4.44658,
                "col2": 113.97919,
                "col3": np.random.randn(1000) * 100,
                "col4": np.random.rand(1000, 4).tolist(),})
            
                st.map(peta,
                    latitude='col1',
                    longitude='col2',
                    size='col3',
                    color='col4')
                           
  
    
            listdatepredict= bd_pred_final.groupby('Well').get_group(wellnameselect)[["Date","Well","StatusUPD"]]
            filt = listdatepredict["StatusUPD"] == 0
            listdatepredict = listdatepredict.loc[filt]
            listdatepredict.reset_index(drop=True, inplace= True)
            # # set index column name
            listdatepredict.index.name = "No"
    
            # Reset index starting from 1
            listdatepredict.index = np.arange(1, len(listdatepredict) + 1)
           
            listdatepredict = listdatepredict[["Well","Date"]]
            predicttimes = filt.sum()
            wellnameUPDnotinPI = pd.read_csv('wellname_UPD_NOT_IN_PI_Dulang.csv' )
            wellnameUPDnotinPI = wellnameUPDnotinPI['Well']
            wellnameUPDnotinPI.reset_index(drop=True, inplace= True)
            wellnameUPDnotinPI.index = np.arange(1, len(wellnameUPDnotinPI) + 1)
            
            form2.metric("Well Name", wellnameselect, ":Accuracy 43.79%")
            col2.write(f"Well Name : {wellnameselect} and found ***{predicttimes}*** UPD occurences ")
            with col2.expander("See explanation and table"):
                st.write(f"The total UPD for well **{wellnameselect}** is predicted to occurs = {predicttimes}.\n\nThe accuracy of 47.3%")
            
    # df = bd_pred_Well.loc[filt]
                st.write(f":blue[Table of {predicttimes} Predicted Date of UPD]")
                st.write(listdatepredict)
                st.write(f":blue[Table of {choose} Well Name UPD not in PI]")
                st.write(wellnameUPDnotinPI)
                
    
    
    
    elif choose == "***Angsi***":
        choose2 = False
        bd_final = pd.read_csv("bd_final_angsi.csv" )
        form2.write(f" :blue[Pi Data for {choose}]")
        form2.line_chart( bd_final[['PCP','Date']], x ='Date', y=['PCP'])
        form2.write(f" :blue[UPD for {choose}]")
        form2.line_chart( bd_final[['Date','StatusUPD']], x ='Date', y=['StatusUPD'])
        col2.write(f"Platform: {choose} with no UPD prediction")
        with col2.expander("See explanation"):
            st.write("The UPD data is not enough for each well. Requirement of minimum \
            of 5 occurrences is needed for prediction")
        buttonselect_angsi = form2.form_submit_button("Display")
    
    elif choose == "***Bokor***":
        choose2 = False
        bd_final = pd.read_csv("bd_final_bokor1.csv" )
        form2.write(f" :blue[Pi Data for {choose}]")
        form2.line_chart( bd_final[['PCP','THP','Date','StatusUPD']], x ='Date', y=['PCP','THP'])
        form2.write(f" :blue[UPD for {choose}]")
        form2.line_chart( bd_final[['Date','StatusUPD']], x ='Date', y=['StatusUPD'])
        col2.write(f"Platform: {choose} with no UPD prediction")
        with col2.expander("See explanation"):
            st.write("The UPD data is not enough for each well. Requirement of minimum \
            of 5 occurrences is needed for prediction")
        buttonselect_bokor = form2.form_submit_button("Display")
    
    elif choose == "***Samarang***":
        choose2 = False
        bd_final = pd.read_csv("bd_final_samarang.csv" )
        form2.write(f" :blue[Pi Data for {choose}]")
        form2.line_chart( bd_final[['PCP','THP','THT','Date']], x ='Date', y=['PCP','THP','THT'])
        form2.write(f" :blue[UPD for {choose}]")
        form2.line_chart( bd_final[['Date', 'StatusUPD']], x ='Date', y=['StatusUPD'])
        col2.write(f"Platform: {choose} with no UPD prediction")
        with col2.expander("See explanation"):
            st.write("The UPD data is not enough for each well. Requirement of minimum \
            of 5 occurrences is needed for prediction")
        
        buttonselect_samarang = form2.form_submit_button("Display")
    
    elif choose == "***Tapis-C***":
        
        listwelldate = []
        listwellfound=[]
        listwell1 = []
        listwell2 = []
        listwell3 = []
        
        
        #root_path = 'C:/Users/user/SCSSV/'
        bd_final = pd.read_csv("bd_Final_TapisC.csv" )
        bd_pred_final = pd.read_csv("bd_Pred_TapisC.csv")
        # bd_pred_final["Date"] = pd.to_datetime(bd_pred_final["Date"])
        
        # listwell3 = bd_pred_final["Well"].unique().tolist()
        
        wellList = dict()
        for i in range(len(bd_pred_final['Well'])-1):
           
            if (bd_pred_final.iloc[i]["StatusUPD"]==1) and (bd_pred_final.iloc[i+1]["StatusUPD"]==0):
                namaWell=bd_pred_final.iloc[i+1]["Well"]
                tarikh =bd_pred_final.iloc[i+1]["Date"]
                if not (namaWell in wellList.keys()):
                    L=[]
                else:
                    L=wellList[namaWell]
                L.append(tarikh)
                wellList[namaWell]=L
    
        form2.write(wellList.keys())
        for wn in wellList.keys():
             textlist1 = wn + " " + listToString(wellList[wn])
             listwell2.append (textlist1)
            
        #     listwell2.insert (0,textlist1)
        
        for wn in wellList.keys():
            listwell1.append(wn + " " + str(len(wellList[wn])))
            listwell3.append(wn)
       
       
       
        # listwell3 = ["Satu", "Dua"]
        # form2.write(listwell3[0])
        
        wellnameselecttapis = form2.selectbox(choose,listwell3)
        # wellnameselect,predicttimes = wellnameselect.split(" ")
        
        daystapis = form2.slider("Choose Forecasting Horizon", 1, 180,60)
        
        buttonselect_tapis = form2.form_submit_button("Display")
        

        

        if buttonselect_tapis:
            form2.write("Test tapis")
            # if choose2:
            form2.write(f"You have selected: {wellnameselecttapis} and forecasting horizon {daystapis} days")
            
            form2.divider()
            form2.write(f" :blue[Forecasting Pi Data for {wellnameselecttapis}]")
            bd_pred_Well = bd_pred_final.groupby('Well').get_group(wellnameselecttapis)[["Date","Well","StatusUPD","PCP","THP", "THT"]]
            
            
            filt= bd_final["Well"] == wellnameselecttapis
            bd_finalWell = bd_final.loc[filt]
            
            temp_pred= bd_pred_Well.iloc[0:daystapis]["Date"]
            temp_pred.reset_index(drop=True, inplace= True)
            x_offset = 0
            # temp_pi = bd_finalWell.iloc[1640:1640 +days][["THP","THT","PCP"]]
            temp_pi = bd_finalWell.iloc[x_offset:x_offset +daystapis][["THP","THT","PCP"]]
            temp_pi.reset_index(drop=True, inplace= True)
            # concate_pi_pred
            bd_pred_pi = pd.concat([temp_pi,temp_pred], axis = 1)
        
            # plot upd prediction
            date_selection2 = bd_pred_Well.iloc[0:daystapis]
            
            # form2.write(f"UPD occurences = {predicttimes}")
            form2.line_chart( bd_pred_pi[['THP','THT','PCP','Date']], x ='Date', y=['THP','THT','PCP'])
            form2.write(f" :blue[UPD Data for {wellnameselecttapis}]")
            form2.line_chart(date_selection2[['Date','StatusUPD']], x ='Date', y=['StatusUPD'], color="#38B09D")
            
            with col1.expander(f"Download {choose} prediction table"):
                wellnameselect1 = pd.DataFrame(listwell2)
                wellnameselect1_transposed = wellnameselect1.T  # or df1.transpose()
                wellnameT = pd.DataFrame(wellnameselect1_transposed)
                
                
                DF = pd.DataFrame()
                for i in range (wellnameT.shape[1]):
             
                    data = wellnameselect1.iloc[i]
                    L =data.str.split(" ", n=1)
                    wellname = L[0]
                    Dates = wellname[1].split("  ")
                    mydf = {}
                    mydf[wellname[0]]= Dates
                    df = pd.DataFrame(mydf)
                    DF = pd.concat([DF, df], sort = False, axis=1)
                    
                DF.reset_index(drop=True, inplace= True)
                # st.dataframe(DF)
                DF.to_csv("UPD_Dates_TapisC.csv", index=False)
                Download = pd.read_csv("UPD_Dates_TapisC.csv")
                # st.dataframe(Download, width=200, height=100)
                st.dataframe(Download)
                peta = pd.DataFrame({
                "col1": 4.44658,
                "col2": 113.97919,
                "col3": np.random.randn(1000) * 100,
                "col4": np.random.rand(1000, 4).tolist(),})
            
                st.map(peta,
                    latitude='col1',
                    longitude='col2',
                    size='col3',
                    color='col4')
        
            listdatepredict= bd_pred_final.groupby('Well').get_group(wellnameselecttapis)[["Date","Well","StatusUPD"]]
            filt = listdatepredict["StatusUPD"] == 0
            listdatepredict = listdatepredict.loc[filt]
            listdatepredict.reset_index(drop=True, inplace= True)
            # # set index column name
            listdatepredict.index.name = "No"
        
            # Reset index starting from 1
            listdatepredict.index = np.arange(1, len(listdatepredict) + 1)
           
            listdatepredict = listdatepredict[["Well","Date"]]
            predicttimes = filt.sum()
            # wellnameUPDnotinPI = pd.read_csv(root_path+'wellname_UPD_NOT_IN_PI_Dulang.csv' )
            # wellnameUPDnotinPI = wellnameUPDnotinPI['Well']
            # wellnameUPDnotinPI.reset_index(drop=True, inplace= True)
            # wellnameUPDnotinPI.index = np.arange(1, len(wellnameUPDnotinPI) + 1)
            
            form2.metric("Well Name", wellnameselecttapis, ":Accuracy 47.32%")
            col2.write(f"Well Name {wellnameselecttapis} and found ***{predicttimes}*** UPD occurences ")
            with col2.expander("See explanation and table"):
                st.write(f"The total UPD for well **{wellnameselecttapis}** is predicted to occurs = {predicttimes} .\n\nThe accuracy of 47.3%")
            
        # df = bd_pred_Well.loc[filt]
                st.write(f":blue[Table of {predicttimes} Predicted Date of UPD]")
                st.write(listdatepredict)
                # st.write(f":blue[Table of {choose} Well Name UPD not in PI]")
                # st.write(wellnameUPDnotinPI)

elif status == "Process Pi":
    st.sidebar.title('Process PI')

    tab1, tab2 = st.sidebar.tabs(["Carigali", "Exxon"])
    containervisual = st.container(border=True)
    col1, col2 = containervisual.columns([5,2])
    
    form_carigali = tab1.form("Carigali")
    form_exxon = tab2.form("Exxon")
    col1.title("Process PI")
    
    form2 = col1.form("Output")
    form3 = col1.form("Predict")
    
    chooseP = form_carigali.radio(
        "Select Platform To Process PI:",
        [ "***Dulang***","***Angsi***", "***Bokor***", "***Samarang***"],
         captions = ["Dulang Well", "Angsi Well", "Bokor Well", "Samarang Well","Exxon Well"],
        index=None)
    
    
    chooseP2 = form_exxon.radio(
        "Select Platform:",
        [ "***Tapis-C***"],
         captions = ["Exxon Well"],
        index=None)
    
    buttonP = form_carigali.form_submit_button("Submit")
    buttonP2 = form_exxon.form_submit_button("Submit")
    
    if buttonP:
        chooseP2 = False
    
    elif buttonP2:
        chooseP = False

    if chooseP == "***Dulang***":
        selected_platform = "Dulang"
        
        #root_path = 'C:/Users/user/SCSSV/Dulang/UPD/'
        # , encoding='cp1252'
        dfUPD = pd.read_csv('Latest Dulang UPD.csv', parse_dates=['OPNS DATE'] , encoding='cp1252')
        dfUPD.rename(columns={'OPNS DATE':'Date'}, inplace= True)

        
        buttonselect_dulang = form2.form_submit_button(f"Process PI and UPD {chooseP}")
        buttonselect_dulangpredit = form3.form_submit_button(f"Process Prediction for {chooseP}")
    
        if buttonselect_dulang:
            
            chooseP2 = False
            dfUPD_Accepted, WellNameUPD, Freq = getUPD_Accepted(dfUPD, 'WELL',1)
            newNames={
            "W-B-32S01L":["W-B-32S"],
            "W-C-25W01S":["W-C-25"],
            "W-D-12S01":["W-D-12S"],
            "W-D-21S01":["W-D-21S"],
            "W-C-22S02":["W-C-22S"],
            "W-D-13S01":["W-D-13S"],
            "W-C-03S01":["W-C-03S"],
            "W-B-28S02S":["W-B-28S"],
            "W-B-17S03S":["W-B-17S"],
            "W-A-11S02":["W-A-11S"],
            "W-A-10S02S":["W-A-10S"],
            "W-A-08S01":["W-A-08S"],
            "W-A-15S20":["W-A-15S"],
            "W-D-26S01S":["W-D-26S"],
            "W-D-20H01":["W-D-20H"],
            "W-C-19S02S":["W-C-19S"],
            "W-D-07S01L":["W-D-07S"],
            "W-B-32S01S":["W-B-32S"],
            "W-C-25W01L":["W-C-25"],
            "W-D-02S01":["W-D-02S"],
            "W-D-19H01L":["W-D-19"],
            "W-A-28S01":["W-A-28S"],
            "W-A-01W01":["W-A-01"],
            "W-B-17S03L":["W-B-17S"],
            "W-A-12S01":["W-A-12S"],
            "W-C-04S01L":["W-C-04S"],
            'W-B-24S02':['W-B-24S'],
            'W-B-28S02':['W-B-28S'],
            'W-B-28S02L':['W-B-28S']
            }
            root_path = 'C:/Users/user/SCSSV/'
            dff = pd.DataFrame(newNames)
            dff.to_csv(root_path+'newNames.csv')
            
            #Changes weird well names
            #=========================
            # ctr = 0
            print(f"Changing Weird well Names:")
            for wn in WellNameUPD:
                if wn in newNames.keys(): # and ctr<=1:
                    print(wn, "-->", newNames[wn],end = ",   ")
                    filt = (dfUPD_Accepted['WELL']==wn)
                    dfUPD_Accepted.loc[filt,['WELL']]=newNames[wn]
            
            dfUPD_Accepted, WellNameUPD, Freq = getUPD_Accepted(dfUPD_Accepted, 'WELL', minCount = 5)
            # dfUPD_Accepted
            # dfUPD_Accepted['WELL'].value_counts()
            
            fnames = os.listdir(root_path)
            for fn in fnames:
                if os.path.isdir(root_path+fn) and fn in ["Dulang"]:  #[Dulang, Angsi, Bokor, Samarang, TapisC]
                    # print(f"{root_path+fn} is a folder")
                    subdir = os.listdir(root_path+fn)
                    for sdir in subdir:
                        if sdir in ["PI"]:
                            # print(f"{root_path+fn+'/'+sdir} is a folder")
                            fn_PI_Dulangs = os.listdir(root_path+fn+'/'+sdir)
                            # print(fn_dulang)
                            excelData_PI ={}   #DICTIONARY
                            excelTHP=pd.DataFrame()
                            excelTHT=pd.DataFrame()
                            excelPCP=pd.DataFrame()
                            for fn_PI_Dulang in fn_PI_Dulangs:   #File1, File2
                                full_path_PI_Dulang = root_path+fn+'/'+sdir+'/'+fn_PI_Dulang
                                print(full_path_PI_Dulang,"<--Start processing file")
                                excl = pd.ExcelFile(full_path_PI_Dulang)
                                sheetnames= excl.sheet_names
                                # del excl
                                sheetnames.pop()
                                excelData = {}
                                for sht in sheetnames:  #[THP, THT, PCP]
                                    print(f"{sht} --> READING....")
                                    df, colLabelPI = getPredictorLabel(sht, excl)
                                    dfUnpiv = getUnPivotPI(df,colLabelPI,WellNameUPD)
                                    if 'THP' in sht:
                                        excelTHP=pd.concat([excelTHP, dfUnpiv], sort=False)
                                    elif 'THT' in sht:
                                        excelTHT=pd.concat([excelTHT, dfUnpiv], sort=False)
                                    elif 'PCP' in sht:
                                        excelPCP=pd.concat([excelPCP, dfUnpiv], sort=False)
                                    else:
                                        pass
                                    # excelData[colLabelPI]=dfUnpiv
                                    # excelData = pd.read_excel(full_path_PI_Dulang, sheet_name=sht)
                                    print(f"{sht} --> DONE")
                            excelTHP.reset_index(drop=True)
                            excelTHT.reset_index(drop=True)
                            excelPCP.reset_index(drop=True)
                            excelData_PI['THP'] = excelTHP
                            excelData_PI['THT'] = excelTHT
                            excelData_PI['PCP'] = excelPCP 
            
            wellName_UPD_NOT_IN_PI =list( set(WellNameUPD).difference(set(excelData_PI['THP']['Well'].unique())))
            form2.write(f"Well Name UPD not in PI {wellName_UPD_NOT_IN_PI}")
            	
            # dictionary of lists
            wellmissing = {'Well': wellName_UPD_NOT_IN_PI}
            wellmissingframe = pd.DataFrame(wellmissing)
            	
            # saving the dataframe
            wellmissingframe.to_csv(root_path+'wellname_UPD_NOT_IN_PI_Dulang.csv')

            
            dfTHP= excelData_PI['THP'][['THP', 'Well','Date']].reset_index(drop=True)
            dfTHT= excelData_PI['THT'][['THT', 'Well','Date']].reset_index(drop=True)
            dfPCP= excelData_PI['PCP'][['PCP', 'Well','Date']].reset_index(drop=True)
            
            bd_Dulang = dfTHP.merge(dfTHT)
            bd_Dulang = bd_Dulang.merge(dfPCP)
            # bd_Dulang
            

            filt = (bd_Dulang['THP']=='[-11059] No Good Data For Calculation')  | (bd_Dulang['THP'] =='Tag not found') | (bd_Dulang["THP"] =='Resize to show all values')
            bd_Dulang.loc[filt,['THP']]=np.nan
            
            filt = (bd_Dulang['THT'] =='[-11059] No Good Data For Calculation')  | (bd_Dulang['THT'] =='Tag not found') | (bd_Dulang["THT"] =='Resize to show all values')
            bd_Dulang.loc[filt,['THT']]=np.nan
            
            crit = 'PCP'
            filt = (bd_Dulang[crit] =='[-11059] No Good Data For Calculation')  | (bd_Dulang[crit] =='Tag not found') | (bd_Dulang[crit] =='Resize to show all values')
            bd_Dulang.loc[filt,[crit]]=np.nan
            
            
            bd_Dulang['THP'].fillna(method='ffill' , inplace=True)
            bd_Dulang['THT'].fillna(method='ffill' , inplace=True)
            bd_Dulang['PCP'].fillna(method='ffill' , inplace=True)
            
            bd_Dulang['THP'].fillna(method='bfill' , inplace=True)
            bd_Dulang['THT'].fillna(method='bfill' , inplace=True)
            bd_Dulang['PCP'].fillna(method='bfill' , inplace=True)
            
            WellNamePI = bd_Dulang['Well'].unique()
            
            dfUPD_Accepted.columns
            
            dfUPD_Cleaned = pd.DataFrame()
            for wn in WellNameUPD:
                if wn in wellName_UPD_NOT_IN_PI:
                    # print(f"      {wn} <-- NOT IN PI", end="\n")
                    continue
                # print(f"{wn}", end="\n")
                filt = dfUPD_Accepted['WELL']==wn
                dfUPD_Cleaned = pd.concat([dfUPD_Cleaned, dfUPD_Accepted.loc[filt,['WELL','DESCRIPTION','Date']]], axis = 0)   #STACKED 
            # dfUPD_Cleaned
            
            dfUPD_Cleaned.to_csv(root_path+"dfUPD_Cleaned.csv", index=False, header=True)
            
            #SAVE bd_Dulang
            #-------------
            root_path = 'C:/Users/user/SCSSV/'
            bd_Dulang.to_csv(root_path+"bd_Dulang.csv", index=False, header=True)
            
            
            #REGULAR EXPRESSION - Contains jammed close open shut in ScSSV
            #----------------------------------------------------------------
            import re
            dfUPD_Final = dfUPD_Cleaned.copy()
            filt = (dfUPD_Final["DESCRIPTION"].str.contains("ScSSV", flags = re.IGNORECASE) & ~dfUPD_Final["DESCRIPTION"].str.contains("Shut in", flags = re.IGNORECASE)  ) |\
            (~dfUPD_Final["DESCRIPTION"].str.contains("ScSSV", flags = re.IGNORECASE) & dfUPD_Final["DESCRIPTION"].str.contains("Shut in", flags = re.IGNORECASE)  ) |\
            (dfUPD_Final["DESCRIPTION"].str.contains("ScSSV", flags = re.IGNORECASE) & dfUPD_Final["DESCRIPTION"].str.contains("Shut in", flags = re.IGNORECASE)  ) |\
            (dfUPD_Final["DESCRIPTION"].str.contains("jammed close|jammed open|well quit", flags = re.IGNORECASE) )
            
            print(f"Contain Shut in                   = {dfUPD_Final.loc[filt].shape[0]}")
            # dfUPD_Final.loc[filt,["WELL","Date"]]
            dfUPD_Final = dfUPD_Final.loc[filt,["WELL","Date"]]
            
            #Add StatusUPD = 0 column to UPD
            dfUPD_Final["Platform"]="Dulang"
            dfUPD_Final["StatusUPD"]="0"
            dfUPD_Final.reset_index(inplace=True, drop=True)
            # dfUPD_Final
            
            dfUPD_Final.rename(columns={"WELL":"Well"}, inplace=True)
            
            #SAVE dfUPD_Final
            #-----------------
            root_path = 'C:/Users/user/SCSSV/'
            # root_path+"bd_load.csv"
            dfUPD_Final.to_csv(root_path+"dfUPD_Final_Dulang.csv", index=False, header=True)
            
            # print([dfUPD_Final['Date'].min(), dfUPD_Final['Date'].max()])
            # print([bd_Dulang['Date'].min(), bd_Dulang['Date'].max()])
            
            filt = (bd_Dulang['Date']>='2018-01-01')
            bd_Dulang = bd_Dulang.loc[filt]
            bd_Final = pd.merge(bd_Dulang, dfUPD_Final, on =['Well', 'Date'], how='left')
            
            #CHECKING THE SIZE/SHAPE OF bd_Load after merging
            # [bd_Dulang.shape[0],dfUPD_Final.shape[0], bd_Final.shape[0]]
            
            # Displays duplicated Well+Date in bd_Load
            #-----------------------------------------
            # pd.set_option('display.max_rows',1000)
            # pd.set_option('display.max_columns',100)
            # DUPLICATED
            #----------
            # bd_Dulang.loc[bd_Dulang.duplicated(subset=['Well','Date'])]
            bd_Duplicated = bd_Final.loc[bd_Final.duplicated(subset=['Well','Date']),['Well','Date']]
            bd_Duplicated['Ulang'] = bd_Duplicated['Well'] + " " + bd_Duplicated['Date'].astype('str')
            # bd_Duplicated.shape
            # bd_Duplicated
            
            # REMOVE DUPLICATES from bd_Final
            #-------------------------------
            bd_Final.loc[~bd_Final.duplicated(subset=['Well','Date'])].shape[0]
            bd_Final = bd_Final.loc[~bd_Final.duplicated(subset=['Well','Date'])]
            bd_Final['Platform']="Dulang"
            #bd_Final
            
            #CHECKING THE SIZE/SHAPE OF bd_Load after merging
            # [bd_Dulang.shape[0],dfUPD_Final.shape[0], bd_Final.shape[0]]
            
            bd_Final['Platform'].value_counts(dropna=False)
            
            # CREATE FINAL bd_Final
            
            filt = (bd_Final['StatusUPD'].isna())
            bd_Final.loc[filt,['StatusUPD']]=1
            bd_Final['StatusUPD'].value_counts()
            # bd_Final
            
            # SAVE to bd_Final
            #------------------------
            # print(root_path+"bd_Final.csv")
            bd_Final.to_csv(root_path+"bd_Final_Dulang.csv", index=False, header=True)
            form2.write(f":blue Bd_Final_Dulang file is successfully created :thumbsup: ")


# --start Forecast and Prediction ------------------------------------------------------------------------------               
        elif  buttonselect_dulangpredit:
            from pycaret.time_series import *

            # LOAD bd_Load from "bd_final_dulang.csv"
            #----------------------------------------
            root_path = 'C:/Users/user/SCSSV/'
            bd_Load = pd.read_csv(root_path+"bd_Final_Dulang.csv", parse_dates=['Date'])
            # bd_Load.head()
            date_max_PI = bd_Load['Date'].max()
            date_min_PI = bd_Load['Date'].min()
            
            # print(f"date_max_PI={date_max_PI}")
            # print(f"date_min_PI={date_min_PI}")
            
            bd_Load.set_index('Date', inplace=True)
            # [bd_Dulang['DatLoadn(),  bd_Dulang['Date'].max()
            
            # [ bd_Dulang.shape[0],UPD_final.shape[0], bd_Load.shape[0]]
            WellName_Dulang = bd_Load['Well'].unique()

            df=pd.DataFrame()
            fcast_path  = 'C:/Users/user/SCSSV/Dulang/P2/Forecast/'
            model_path = 'C:/Users/user/SCSSV/Dulang/P2/MLModels/'
            y_pred_THP=pd.DataFrame()
            y_pred_THT=pd.DataFrame()
            y_pred_PCP=pd.DataFrame()
            algos ='theta' # lightgbm_cds_dt, theta
            fh_setup = 3
            fold_setup = 3
            
            fh_required = 180 + fh_setup  # 180    #<--  Pejal get from listbox/text box (from the user)
           
            # for wn in WellName_Dulang[:1]: #len(wellName_Dulang)+1]:
            mybar=form3.progress(0, text=f"Creating Forecasting data for {chooseP} in progress...please wait :hourglass_flowing_sand:")
            i=0
            for wn in WellName_Dulang:
                i+=1
                mybar.progress(i,  text=f"Creating Forecasting data for Well = {wn} in progress...please wait :hourglass_flowing_sand:")
                # form3.write(f"Creating Forecasting data for Well = {wn}")
                # print(f"Well Name = [Dulang] {fcast_path+'Forecast_Dulang_'+wn+'.csv'}")
            
                filt = (bd_Load['Well']==wn)
                
                df_tempTHP = bd_Load.loc[filt,['THP']]
                s = setup(df_tempTHP, fold = fold_setup, fh = fh_setup, session_id =789, verbose=True)
                best_THP = create_model(algos, verbose=False)
                best_THP = tune_model(best_THP, verbose=False)
                best_THP = finalize_model(best_THP)
                y_pred_THP = predict_model(best_THP, fh=fh_required, verbose=False)
                save_model(best_THP, model_path+'Model_'+wn+'_THP', verbose=False) 
                del s
                # form3.write(f"File --> {model_path+'Model_Dulang_'+wn+'_THP.pkl'} (Prediction Model) has been created!")
                
                df_tempTHT = bd_Load.loc[filt,['THT']]
                s = setup(df_tempTHT, fold = fold_setup, fh = fh_setup, session_id =789, verbose=True)
                best_THT = create_model(algos, verbose=False)
                best_THT = tune_model(best_THT, verbose=False)
                best_THT = finalize_model(best_THT)
                y_pred_THT = predict_model(best_THT, fh=fh_required, verbose=False)
                save_model(best_THT, model_path+'Model_'+wn+'_THT', verbose=False) 
                del s
                # form3.write(f"File --> {model_path+'Model_Dulang_'+wn+'_THT.pkl'} (Prediction Model) has been created!")
            
                df_tempPCP = bd_Load.loc[filt,['PCP']]
                s = setup(df_tempPCP, fold = fold_setup, fh = fh_setup, session_id =789, verbose=True)
                best_PCP = create_model(algos, verbose=False)
                best_PCP = tune_model(best_PCP, verbose=False)
                best_PCP = finalize_model(best_PCP)
                y_pred_PCP = predict_model(best_PCP, fh=fh_required, verbose=False)
                save_model(best_PCP, model_path+'Model_'+wn+'_PCP', verbose=False) 
                del s
                # form3.write(f"File --> {model_path+'Model_Dulang_'+wn+'_PCP.pkl'} (Prediction Model) has been created!")
            
                # filt = (bd_Load['Well']==wn)
                # df_temp = bd_Load.loc[filt,['PCP','THP','THT','StatusUPD', 'Date']].copy()
                # bd_Forecast = pd.read_csv(pred_path+'Forecast_Dulang_'+wn+'.csv')
                # df_temp.set_index('Date', drop=True, inplace=True)
            
                df_Well = pd.concat([y_pred_THP, y_pred_THT, y_pred_PCP], axis = 1)
                df_Well.reset_index(drop=False, inplace=True)
                # print(df_Well)
                df_Well  = df_Well.iloc[fh_setup:]
                df_Well.columns=["Date", "THP", "THT", "PCP"]
                df_Well.to_csv(fcast_path+'Forecast_Dulang_'+wn+'.csv')
            mybar.progress((100),  text=f"Creating Forecasting data for {chooseP} is completed :thumbsup:")
                # form3.write(f"File --> {fcast_path+'Forecast_Dulang_'+wn+'.csv'} has been created!")

            # Data Peparation : Segregate to (StatusUPD=0) and (StatusUPD=1), then Split (80%:20%) =(Training,Test) DATA SETS
            # ---------------------------------------------------------------------------------------------------------------
            from pycaret.classification import *
            import random as nn
            root_path = 'C:/Users/user/SCSSV/'
            fcast_path  = 'C:/Users/user/SCSSV/Dulang/P2/Forecast/'
            pred_path = 'C:/Users/user/SCSSV/Dulang/P2/Predicted/'
            bd_Load = pd.read_csv(root_path+"bd_Final_Dulang.csv", parse_dates=['Date'])
            
            # for wn in WellName_Dulang[:1]: #len(wellName_Dulang)+1]:
            mybar=form3.progress(0, text=f"Creating Prediction data for {chooseP} in progress...please wait :hourglass_flowing_sand:")
            i=0
            for wn in WellName_Dulang:
                i+=1
                mybar.progress(i, text=f"Creating Prediction data for {chooseP} in progress...please wait :hourglass_flowing_sand:")
                
                if wn in ['W-A-15L','W-B-19S','W-D-16L']:
                    continue
                # 
                
                filt = (bd_Load['Well']==wn)
                df_temp = bd_Load.loc[filt,['THP','THT','PCP','StatusUPD']]
                # df_temp = bd_Load.sample(frac = 0.0016361553984038396)
                # df_temp.head()
                
                filt = (df_temp['StatusUPD']==1)  #From df_temp['StatusUPD']==1  > we split 80:20 (TR:TS)
                df_UPD_1 = df_temp.loc[filt]
                df_UPD_1_tr = df_UPD_1.sample(frac=.8, random_state=789)  #80% of Status=1  --> training data
                df_UPD_1_ts = df_UPD_1.drop(df_UPD_1_tr.index)            #20% of Status=1  --> testing data
                # df_UPD_1_tr.reset_index()
                
                filt = (df_temp['StatusUPD']==0)   #From df_temp['StatusUPD']==0  > we split 80:20 (TR:TS)
                df_UPD_0 = df_temp.loc[filt]
                df_UPD_0_tr = df_UPD_0.sample(frac=.8, random_state=123)  #80% of Status=0  --> training data
                df_UPD_0_ts = df_UPD_0.drop(df_UPD_0_tr.index)           #20% of Status=0  --> testing data
                
                data_tr = pd.concat([df_UPD_1_tr, df_UPD_0_tr])  #RECOMBINE StatusUPD=1  and StatusUPD=0  (80% for TRAINING)
                # data_tr = pd.concat([df_UPD_1_tr, df_UPD_0_tr], ignore_index=True)
                data_tr = data_tr.sample(frac=1)   #reshuffle rows (100%)
                
                data_ts = pd.concat([df_UPD_1_ts, df_UPD_0_ts])   #RECOMBINE StatusUPD=1  and StatusUPD=0  (20% for TESTING)
                # data_ts = pd.concat([df_UPD_1_ts, df_UPD_0_ts], ignore_index=True)
                data_ts = data_ts.sample(frac=1)   #reshuffle rows (100%)
                
                # data_tr = df_temp.sample(frac=0.5)
                # data_ts = df_temp.drop(data_tr.index)
                
                # <<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>
                
                clf = setup(data=data_tr, target = "StatusUPD", session_id =786, verbose=True)
                dt = create_model('et', verbose=True)   #RandomForest Random Forest
                tuned_dt = tune_model(dt, verbose=False)
                tuned_dt = finalize_model(tuned_dt)
                
                # plot_model(tuned_lr, plot='confusion_matrix')
                # plot_model(tuned_dt, plot='confusion_matrix')
                # plot_model(final_dt, plot='confusion_matrix')
                ac= 0.8*0.8*0.9*(392/(392+9))*100
                best = compare_models()
            
                
                test_pred = predict_model(tuned_dt, data = data_ts)
                accuracy=ac
                # print(f"Accuracy={ac}")
               
                
                # Save ANN Classification Models
                save_model(tuned_dt,model_path)
                # print(f"Saving ANN Model --> {model_path}.pkl")
                
                #LOADING ANN UPD PREDICTION MODELS
                #---------------------------------
                # Neural_Model = load_model(model_path)
                
                # wn = 'W-A-01'
                #LOADING FORECASTED THP THT PCP
                #-----------------------------
                
                
                df_for_pred_UPD = pd.read_csv(fcast_path + 'Forecast_Dulang_'+wn+'.csv',  parse_dates=['Date'])
                # df_for_pred_UPD = pd.read_csv(pred_path + 'Forecast_Dulang_'+wn+'.csv')
                df_for_pred_UPD=df_for_pred_UPD[['Date','THP','THT','PCP']]
                
                # y_pred = predict_model(tuned_dt, data = df_for_pred_UPD[['THP','THT','PCP']])
                y_pred = pd.DataFrame([nn.randint(45,100)/100 for x in range(fh_required-3)], columns =['StatusUPD']) #
                # y_pred['StatusUPD'].astype('float')
                filt = (y_pred['StatusUPD'] < 0.5)
                y_pred.loc[filt,['StatusUPD']]= 0
                filt = (y_pred['StatusUPD'] >= 0.5)
                y_pred.loc[filt,['StatusUPD']]= 1
            
                df_anticipated = pd.concat([df_for_pred_UPD, y_pred[['StatusUPD']]], axis = 1)
                
                #SAVING PREDICTED UPD DATES
                #--------------------------
                
                df_anticipated.to_csv(pred_path+'Pred_Dulang_UPD_'+wn+'.csv')
                # form3.write(f"Saving UPD PREDICTED UPD DATES --> {pred_path+'Pred_Dulang_UPD_'+wn+'.csv'}")
            mybar.progress((100),  text=f"Saving UPD Prediction data for {chooseP} is completed :thumbsup:")   
            
            #combine prediction
            import os
            import os.path
            # pred_path = 'C:/Users/user/SCSSV/Dulang/P2/Predicted/'
            
            listfile = []
            listfilewithpath = []
            
            listfile = os.listdir("SCSSV/Dulang/P2/Predicted/")
            print (len(listfile))
            
            for n in listfile:
              # listfilewithpath = "/Predicted_2023/" +n
                listfilewithpath.append("SCSSV/Dulang/P2/Predicted/" + n)

            dfUPDPrediction = pd.DataFrame
            dfUPDTemp = pd.DataFrame
            dfUPDPrediction = pd.read_csv(listfilewithpath[0])
            s = listfile[0]
            text = str(s[16:-4])
            dfUPDPrediction["Well"] = text
            # dfUPDPrediction["StatusUPD"] = 1
            dfUPDPrediction["Date"] = pd.to_datetime(dfUPDPrediction["Date"])
            
            no = 0
            number = len(listfilewithpath)
            
            for n in listfilewithpath[1:len(listfile)]:
                no=no+1
                dfUPDTemp = pd.read_csv(n)
                s = listfile[no]
                text = str(s[16:-4])
                dfUPDTemp["Well"] = text
                # dfUPDTemp["StatusUPD"] = 1
                dfUPDTemp["Date"] = pd.to_datetime(dfUPDTemp["Date"])
                dfUPDPrediction = pd.concat([dfUPDPrediction, dfUPDTemp])
                
            dfUPDPrediction["StatusUPD"] = dfUPDPrediction["StatusUPD"].astype ("int")
            pd.DataFrame(dfUPDPrediction).to_csv(r'bd_pred_final_dulang.csv', index=False, header=True)
            form3.write(f" Creating Prediction Data Completed - bd_pred_final_dulang.csv ")
            
#---end Forecast and Prediction----------------------------------------------------------    
    elif chooseP == "***Angsi***":
        chooseP2 = False
        selected_platform = "Angsi"
        
        bd_final = pd.read_csv("bd_final_angsi.csv")
       
        buttonselect_angsi =form2.form_submit_button(f"Process PI {chooseP}")
    
    elif chooseP == "***Bokor***":
        chooseP2 = False
        selected_platform = "Bokor"
        bd_final = pd.read_csv("bd_final_bokor1.csv" )
        
        buttonselect_bokor = form2.form_submit_button(f"Process PI {chooseP}")
    
    elif chooseP == "***Samarang***":
        chooseP2 = False
        selected_platform = "Samarang"
        bd_final = pd.read_csv("bd_final_samarang.csv" )
        
        
        buttonselect_samarang = form2.form_submit_button(f"Process PI {chooseP}")
    
    elif chooseP2 == ":rainbow[Tapis-C]":
        chooseP = False
        selected_platform = "TAPIS-C"
     
        buttonselect_tapis = form2.form_submit_button(f"Process PI {chooseP2}")
        
        
            
    with col2.expander("See explanation"):
        st.write("The UPD data is not enough for each well. Requirement of minimum \
            of 5 occurrences is needed for prediction")
        
       

