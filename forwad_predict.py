import sys
sys.path.append('/cs/anomaly/scripts/stlupdate') #search for modules in stl update folder
import fasut
import pandas as pd
import numpy as np
import io
import json
import datetime
import time
import rocksdb
import itertools
import pickle
from datetime import timedelta
from dynaconf import settings
import re
import math
import copy
from numpy import array
from tensorflow import keras
from tensorflow.keras.model import model_from_json
from sklearn.metrics import mean_absolute_error
from keras.model import load_model
from tensoflow.keras.backend import manual_variable_intialization
import gc
from icecream import ic
import common_programs.LSTMModel as lstmm
import common_programs.logscaling as Logscaling
import schemas.commonschema as cschema

pd.set_option('display.width',200) #maximum 200 display size

'''
Forward predict over 24 hrs using weak model

'''

append_str = "." #appending of strings using .(ci_name and metrics)

app = faust.App(
      'TSAnomaly_Weak_Forward_Pred', #Name of the faust application
      broker = 'kafka://kafka-devap01.ap.hedani.net;kafka://kafka-devap02.ap.hedani.net;kafka://kafka-devap03.ap.hedani.net', #no.of broker which will use to produce and consume messages(here 3 brokers are provided)
      web_port = 6098, #port no for web interface for faust application 
      producer_max_request_size = 1115728649, # maximum size of messages produced by producer
      store = 'rocksdb://', # data store used by faust(key-value pair embedded )
      topic_replication_factor = 3, # no.of replication of topic used to maintain fault tolerance system if one partiion fails
      broker_max_poll_records = 500,#maximum no.of records to be fetched in single request
      broker_heartbeat_interval = 10, #consumer sends heartbeats to broker to ensure consumer is active or unresponsive
      broker_request_timeout = 190.0,#maximum wait time by broker to get response from consumer
      broker_session_timeout = 190.0,#maximum wait time for broker after which after which it will rebalance to reassign paritions
) #  The application is designed for weak forward prediction of time series data and will interact with Kafka brokers to produce and consume messages.

app.conf.table_cleanup_interval = 60 #check for expiry of data in every 60 seconds
app.producer.buffer.max_messages = 90000 # maximum no.of msg can be buffered by producer for consumer

WEAKMODELDB = rocksdb.DB(b"/cs/anomaly/scripts/stlupdate/temp_data/v1/tables/weak_model_table_db",rocksdb.Options(create_if_missing=False),read_only = True)#object of rocksdb database and should not create new database and object has accesibility to read only mode
CLUSTERTABLEDB = rocksdb.DB(b"/cs/anomaly/scripts/stlupdate/temp_data/v1/tables/cluster_table_db",rocksdb.Options(create_if_missing=False),read_only = True)# same type object to infer the cluster table 
FORWARD_WEAK_PRED_TABLE = app.Table('forward_weak_pred_table',default = None, partitions = 1, schema = cmdls.STLTableSchema, help = "Output Created by Forward Weak Prediction")# faust table with no default value and table parition = 1 also schema -> data type of table
STRONG_TRAIN_TOPIC = app.topic('ts_anomaly_strongtrain_in',schema = csschema.postSTLschema) # This topic will be used to receive messages containing strong training data for the LSTM model.

DEBUG = false
ci_cluster = {}
lstm_refresh_time = {}
lstm_model = {}
lstm_avgstddev ={}

df_agg_pred = pd.DataFrame()
df_agg_trend = pd.DataFrame()
df_agg_season = pd.DataFrame()
df_agg_total = pd.DataFrame()

#configuration file setting (setting.toml to receieve configurations)
if(settings["downSample"]):
  n_steps_in = settings["dforward_look_back_param"] #how many past data points will be used for predictions 
  n_steps_out = settings["dforward_look_back_param"]#288(maximum window size when downsampling required(shorter time ranges))
else:
  n_steps_in = settings["forward_look_back_param"]#1440(maximum window size if downsampling is not required)
  n_steps_out = settings["forward_look_back_param"]
#summary: configuring the input and output window sizes for the LSTM model based on whether downsampling is required or not. If downsampling is required, the window sizes are set to 24 hours (288 data points), and if downsampling is not required, the window sizes are set to 24 hours at a higher resolution (1440 data points)

class DBConnection: 
    def __init__(self):
	self.stl_read_table = rocksdb.DB("/cs/anomaly/scripts/stlupdate/TSAnomalySTL-worker1-data/v1/tables/stl_input_table-0.db", rocksdb.Options(create_if_missing = False),read_only = True)
#class created for rocksdb connection

#def aggregate_data():
@app.agent(STRONG_TRAIN_TOPIC)
#handles operations in async while consuming messages from kafka topic: Strong_TRAIN_TOPIC
async def agent_weakpred_job(stream):
  async for stream_item in stream.events():  #iterates over the kafka topic stream
    class DBConnection:
       def __init__(self):
          self.stl_read_table = rocksdb.DB("/cs/anomaly/scripts/stlupdate/TSAnomalySTL-worker1-data/v1/tables/stl_input_table-0.db", rocksdb.Options(create_if_missing = False),read_only = True)
# creates an agent function agent_weakpred_job that consumes messages from the Kafka topic STRONG_TRAIN_TOPIC. 
#For each message consumed, it creates a database connection to a RocksDB database using the DBConnection class
    df_agg_pred = pd.DataFrame()
    df_agg_trend = pd.DataFrame()
    df_agg_season = pd.DataFrame()
    df_agg_total = pd.DataFrame()

    clusterit = CLUSTERTABLEDB.iteritems()  #iterator to iterate over clustertabledatabse
    modelit = WEAKMODELDB.iteritems() #iterator to iterate over weakmodel DB database
    clusterit.seek_to_first() # indexes reset to first record
    modelit.seek_to_first() # indexes reset to first record
    
    #intialising dictionaries and lists
    df_agg_pred = {}
    df_agg_trend = {}
    df_agg_season = {}
    columnlist = {}
    mname = {}
    lstm_model = {}
    ci_list = []
    # Processing Data from the Cluster Table
    #The loop extracts the each_key (time series) and each_val (model name) from the cluster table.
    for each_key, each_val in clusterit:
      if(each_key == b'unique' or each_key == b'__faust\x00offset__'):
        continue

      tseries = each_key.decode('UTF-8') #timeseries-name
      model_name = str(each_val.decode().split(",")[0]) #model name(cluster name)
      ci_list.append(tseries.split(".")[0]) # appends the cluster identifier by splitting the timeseries name
      #mname[tseries] = "Cluster_" + model_name
      #model_name = "Cluster__" + model_name
      mname[tseries] = model_name #assosiates the time series with its corresponding model name(cluster_name)

      #modellist = set(ci_cluster[ciname]['modelName']).to_string(index = False).replace(","").splitlines())
      #print(model_name,tseries)

      #group time series under their respective clusters
      if(model_name in columnlist):
        columnlist[model_name.append(tseries)]
      else:
        columnlist[model_name] = [tseries]

  for key,val in columnlist.items():
    #Creating DataFrames for Each Model
    df_agg_pred[key] = pd.DataFrame()
    df_agg_trend[key] = pd.DataFrame()
    df_agg_season[key] = pd.DataFrame()

    # Processing Data for Each Model

    value_dict = {}
    keylist = []
    for each_configitem in settings["ModelstringList"]:
      tempstr = key + "." + each_configitem
      #tempstr = "Cluster_" + key + "." + each_configitem
      print("tempstr{}".format(tempstr))
      keylist.append(tempstr.encode('UTF-8'))
    value_list = WEAKMODELDB.multi_get(keylist)
    value_dict = {}
    for each_key in value_list.keys():
      keystr = each_key.decode('UTF8').split(".")[1]
      valuestr = value_list[each_key]
      value_dict[keystr] = valuestr

    print("Weak_Forward_prediction: eachmodel, Keystring and type {} {} {}".format(key,keystr,type(value_dict[keystr])))
    weight_array = pickle.loads(value_dict["modelweight"])  #weights of LSTM model
    wtsize_array = pickle.loads(value_dict["modellayers"])  #layer sizes of the model
    modelrefreshtime = value_dict["refreshtime"].decode('UTF-8') #model refresh time is converted to unix time
    d_temp = datetime.datetime.strptime(modelrefreshtime, "%Y-%m-%d %H:%M:%S")
    lstm_refresh_time[key] = time.mktime(d_temp.timetuple())
    #lstm_avgstddev[eachmodel] = pd.read_json(value_dict["errorstddev"],orient = 'spilt')
    #lstm_avgstddev[eachmodel] = lstm_avgstddev[eachmodel].T
    #lstm_avgstddev[eachmodel] = lstm_avgstdev[eachmodel][df_data_pred.columns]
    #print("Weak_Forward_Prediction":lstm_avgstddev for eachmodel {} {} {}".format(eachmodel,ciname))
    #print(lstm_avgstddev[eachmmodel])

    # LSTM model is reconstructed using model_from_json with the configuration loaded from value_dict.
    lstm_model[key] = model_from_json(value_dict["modelconfig"].decode('UTF-8'))
    j = 0
    segments = [weight_array[wtsize_array[i-1]:wtsize_array[i],] for i in range(1,len(wtsize_array))]
    for each_layer in lstm_model[key].layers:
      each_layer.set_weights(segments[j])
      j +=1

    lstm_model[key].compile(optimizer='adam', loss = 'mse') #model compiled with optimser and mean square error function
    print(lstm_model[key].summary())
    del weight_array, wtsize_array,value_dict,value_list,modelrefreshtime

  df_agg_pred["unclassified"] = pd.DataFrame()
  df_agg_trend["unclassified"] = pd.DataFrame()
  df_agg_season["unclassified"] = pd.DataFrame()

#Start Reading the Data from STL Input table
  dconnection = DBConnection()
  it = dconnection.stl_read_table.iteritems() #iterator for the STL table
  it.seek_to_first() #iterator moved to first

  count = 0  #track of processed records

  # Processing Data from the STL Input Table;
  for each_key, each_val in it :
    if(each_key == b'__faust\x00offset__'):
      continue


    ci_name = each_key.decode('utf-8').replace('"'.'')
    vt_val = each_val.decode('utf-8')
    df_temp, df_tmp = pd.DataFrame(), pd.DataFrame()

    print("Weak_Forward_prediction: Processing start for {}".format(ci_name))
    #Data sclicing and aggregation:
    if(vt_val):
      df_tmp = pd.read_json(json.loads(vt_val),orient = 'spilt')
      print(df_tmp.tail())
      if("ts" in df_tmp.columns):
        df_tmp = df_tmp.set_index('ts')
      else:
        df_tmp = df_tmp.rename_axis('ts')


      df_tmp = df_tmp.set_index(pd.to__datetime(df_tmp.index,infer_datetime_format=True).tz_localize(tz =settings["localize_totz"]))
      df_tmp.columns = list(map(lamda x : x.split(append_str, 1)[0], df_tmp.columns))

      df_tmp = df_tmp.astype('float32')
      row,column = df_tmp.shape()
      print(row,column)


      if column < settings["min_number_of_stl_columns"] and not column & settings["number_of_stl_frames"] == 0:
        print("Data set for server {} has only {} column or not divisible by minimum number of stl frames".format(ci_name,column))
        continue

      print("Weak_Forward_prediction: Start load the DataFrame for server {}".format(ci_name))
      each_frame_length = int(column/settings["number_of_stl_frames"])
      df_temp = np.array_split(df_tmp,settings["number_of_stl_frames"],axis = 1)
      df_columns = list(df_temp[0].columns)
      print("Column names are : {}".format(','.join(df_columns)))


      df_tmp_test = df_temp[0]
      df_tmp_trend = df_temp[1]
      df_tmp_season = df_temp[2]

      df_tmp_trend.columns = df_tmp_test.columns 
      df_tmp_season.columns = df_tmp_test.columns 

    else:
      print("Weak_Forward_prediction: Key not found {}".format(ci_name))
      continue

    #check last index and go back by couple of hours to ensure majority of CI's have values          
    df_pred_last_index = df_tmp.iloc[-1:].set_index
    #df_pred_last_index = df_pred_last_index - timedelta(hours = 2)

    #we take double the look_back_param to ensure majority of CI's have values after merging
    df_test = df_tmp_test.loc[:df_pred_last_index.values[0]].tail(n_steps_in)
    df_trend = df_tmp_trend.loc[:df_pred_last_index.values[0]].tail(n_steps_in)
    df_season = df_tmp_season.loc[:df_pred_last_index.values[0]].tail(n_steps_in)
    print(df_test,df_trend,df_season)
    #df_residual = df_tmp_residual.loc[:df_pred_last_index.values[0]].tail(2*settings["look_back_param"])

    df_pred = df_test - df_season

    #print("Weak_Forward_Prediction: Printing shape of df_pred,df_trend for ci_name {} {} {}",format(df_pred.shape,df_trend.shape,ci_name))
    new_timeseries_name = []
    for metrics in df_pred.columns:
      new_timeseries_name.append(ci_name + "."+ metrics)

    df_pred.columns = new_timeseries_name
    df_trend.columns = new_timeseries_name
    df_season.columns = new_timeseries_name


    where_to = ""
    skip_flag = int(0)
    for colname in df_pred.columns:
      if colname in mname.keys():
        where_to = mname[colname]
        print("where_to {}".format(where_to))
        skip_flag = 0

      else:
        skip_flag = 1
        continue

        #where_to = "unclassified"
        #print("Weak_forward_prediction: Timeseries {} is unclassified for ci name {}".format(colname,ci_name))
      if(not df_agg_pred[where_to].empty):
        df_agg_pred[where_to] = pd.merge(df_agg_pred[where_to],df_pred[colname],left_index = True, right_index = True, how = 'outer')
      else:
        df_agg_pred[where_to] = df_pred[colname]


      if(not df_agg_trend[where_to].empty):
         df_agg_trend[where_to] = pd.merge(df_agg_trend[where_to],df_trend[colname],left_index = True, right_index = True, how = 'outer')
       else:
        df_agg_trend[where_to] = df_trend[colname]


      if(not df_agg_season[where_to].empty):
         df_agg_season[where_to] = pd.merge(df_agg_season[where_to],df_season[colname],left_index = True, right_index = True, how = 'outer')
       else:
        df_agg_season[where_to] = df_season[colname]   
    
    if(skip_flag < 1):
      skip_flag = 0
      df_agg_pred[where_to] = df_agg_pred[where_to].ffill().bfill().tail(n_steps_in)
      df_agg_trend[where_to] = df_agg_trend[where_to].ffill().bfill().tail(n_steps_in)
      df_agg_season[where_to] = df_agg_season[where_to].ffill().bfill().tail(n_steps_in)
    print(df_agg_pred[where_to],df_trend[where_to],df_season[where_to])
    

    del df_pred,df_trend,df_agg_season
    count += 1
    print("Weak_Forward_prediction: Completed processing for ci_name {} {}".format(ci_name,count))


  
  df_agg_yhat = pd.DataFrame()
  for keys in df_agg_pred.keys():
      print(keys, df_agg_pred[keys],df_agg_trend[keys],df_agg_season[keys])
      df_agg_pred[where_to] = df_agg_pred[where_to].ffill().bfill().tail(n_steps_in)
      df_agg_trend[where_to] = df_agg_trend[where_to].ffill().bfill().tail(n_steps_in)
      df_agg_season[where_to] = df_agg_season[where_to].ffill().bfill().tail(n_steps_in)
      if(len(df_agg_season[keys]) < n_steps_in):
          print("Weak_Forward_prediction : Not enough data to process model {}".format(keys))
          continue

      #df_agg_pred[keys] = df_agg_pred[keys].astype('float16')
      #df_agg_trend[keys] = df_agg_trend[keys].astype('float16')
      #df_agg_season[keys] = df_agg_season[keys].astype('float16')

      df_agg_pred[keys] = df_agg_pred[keys] - df_agg_season[keys]

      if(keys in lstm_model):
        t_now = datetime.datetime.now().timestamp()
        t_diff = abs(t_now - lstm_refresh_time[keys])
        if(t_diff > settings["WeakModelStaleSeconds"]):
          print("Weak_Forward_Prediction: model for keys {} in memory stale, going to reload assuming training would have completed by this time".format(keys))

      
      yhat_df = pd.DataFrame()
      #Bug fixed if only one column is part of dataframe, then it was coming as a series. So converting series into Dataframe...
      if(isinstace(df_agg_pred[keys],pd.Series)):
        df_agg_pred[keys] = df_agg_pred[keys].to_frame(name = df_agg_pred[keys].name)

      if(isinstace(df_agg_trend[keys],pd.Series)):
        df_agg_trend[keys] = df_agg_trend[keys].to_frame(name = df_agg_trend[keys].name)

      yhat_df = lstmm.predictscores(df_agg_pred[keys],df_agg_trend(keys),n_steps_in,n_steps_out,modelName= lstm_model[keys],reconstruct_model = False, forward_predict = True)
      print(yhat_df)
      print("Weak_Forward_prediction: Processed forward prediction of model {} in Weak Prediction ..".format(keys))
      print(app.monitor.events_s)
      if(not df_agg_yhat.empty):
        df_agg_yhat = pd.merge(df_agg_yhat,yhat_df,left_index = True, right_index = True, how = 'outer')

      else: 
        df_agg_yhat = yhat_df

  df_agg_yhat = df_agg_yhat.rename_axis('ts').reset_index()
  df_agg_yhat.set_index('ts',inplace = True)

  dfs = {filter_name : df_agg_yhat.filter(like = filter_name) for filter_name in ci_list }
  dfs_final = {filter_name: dfs[filter_name].rename(columns = dict(zip(dfs[filter_name].columns.tolist(),[x.split(".")[1] for x in dfs[filter_name].columns]))) for filter_name in ci_list}
  print(dfs_final)


  fwd_keylist = set(FORWARD_WEAK_PRED_TABLE.keys())

  for df_keys in dfs_final.keys():
    df_tmp = pd.DataFrame
    if(df_keys in fwd_keylist):
      #del FORWARD_WEAL_PRED_TABLE[df_keys]
      vt_val = FORWARD_WEAK_PRED_TABLE[df_keys]
      df_tmp = pd.read_json(vt_val,orient = "spilt")
      df_tmp = df_tmp.set_index(pd.to__datetime(df_tmp.index,infer_datetime_format = True).tz_localize(tz=settings("localize_totz")))
      df_tmp = df_tmp.iloc[-3*n_steps_out:]
    
    if(not df_tmp.empty):
      df_tmp = pd.concat([df_tmp,dfs_final[df_keys]], axis = 0, ignore_index = False)
    else:
      df_tmp = dfs.final[df_keys]

    df_tmp = df_tmp.sort_index()
    df_tmp = df_tmp[~df_tmp.index.duplicated(keep = 'first')]
    tmp_str = df_tmp.to_json(orient = 'spilt',date_format = 'iso')
    print("Weak_Forward_Prediction: Going to push new value of df_tmp to Table")
    print(df_tmp.shape)
    if(not df_tmp.shape):
      FORWARD_WEAK_PRED_TABLE[df_keys] = tmp_str
    del df_tmp, tmp_str
  sys.exit()
  break
  time.sleep(86000)   






"""Summary for the forward_predict: 



Step 1:

Import Required Libraries: The script starts by importing necessary Python libraries, including Faust (faust), Pandas (pd), and RocksDB (rocksdb).

Step 2:
Kafka Broker Configuration: The Kafka broker configuration is provided, specifying the brokers' URLs to connect to the Kafka cluster.

Step 3:

Faust Application Initialization: An instance of the Faust application (app) is created with relevant configurations, such as the name, broker details, topic replication factor, etc.

Step 4:
Data Preprocessing Parameters: The script defines some data preprocessing parameters, such as look-back parameters (n_steps_in and n_steps_out) for LSTM input and output sequences.

Step 5:
Load Model and Data: The script loads the pre-trained LSTM model and necessary data from databases (WEAKMODELDB and CLUSTERTABLEDB) to use for predictions.

Step 6:
Stream Processing: The script uses the Faust decorator @app.agent(STRONG_TRAIN_TOPIC) to define an agent function agent_weakpred_job. This agent function consumes data from the Kafka topic (STRONG_TRAIN_TOPIC) and processes each stream item.

Step 7:
Database Connection: For each stream item, the script creates a database connection to the RocksDB database (stl_read_table) using the DBConnection class.

Step 8:
Data Aggregation: Data is aggregated into df_agg_pred, df_agg_trend, and df_agg_season DataFrames, organized based on clusters or models.

Step 9 :
LSTM Model Preparation: The LSTM model's weights and architecture are loaded from the database (WEAKMODELDB). The model is then reconstructed and compiled using the 'adam' optimizer and mean squared error (mse) loss function.

Step 10:
Data Preprocessing from STL Input Table: Data is read from the STL input table and preprocessed by setting the 
index as a DatetimeIndex, converting columns to float32 data type, and adjusting column names.

Step 11:
Data Slicing and Aggregation: The data is sliced and aggregated based on the look-back parameter (n_steps_in). 
This step prepares the input and target sequences for LSTM prediction.

Step 12:
Weak Forward Prediction: The script performs weak forward prediction for each cluster/model using the LSTM model. It predicts future values for the input sequences and stores the predictions in the df_agg_yhat DataFrame.

Step 13:
Data Storage in Forward Weak Prediction Table: The weak forward prediction results are stored in the Forward Weak Prediction Table (FORWARD_WEAK_PRED_TABLE).

Step 14:
Data Processing for Other Clusters/Models: The above steps are repeated for other clusters/models in the stream.

Step 15:
Data Formatting for Output: The script formats the prediction results and stores them in dfs_final.

Step 16:
Final Data Storage: The final prediction results are stored in the Forward Weak Prediction Table (FORWARD_WEAK_PRED_TABLE) for each cluster/model.

Question: Currently code is taking data from one partition of kafka stream if we use for 8 paritions what should be the changes done: 

Ans: FORWARD_WEAK_PRED_TABLE = app.Table('forward_weak_pred_table',default = None, partitions = 1, schema = cmdls.STLTableSchema, help = "Output Created by Forward Weak Prediction")# faust table with no default value and table parition = 1 also schema -> data type of table


FORWARD_WEAK_PRED_TABLE = app.Table('forward_weak_pred_table', default=None, partitions=8, schema=cmdls.STLTableSchema, help="Output Created by Forward Weak Prediction")







