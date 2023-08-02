##Author : Pradosh Priyadarshan

import faust 
import json
import pandas as pd
import numpy as np
import io 
import datetime
import time 
import random 
import datetime import timedelta
from dynaconf import settings





import mlmodel_classes as mlclasses
import mlmodel_classes.common_models as cmdls
import mlmodel_classes.LSTModel as lstmm
import rocksdb
import pickle
from base 64 import b64decode, b64encode
from tensorflow.keras.models import model_from_json 

pd.set_option('display_width', 200)

''' 

This agent is a stream processing a predict if increasing data point from earlier prediction step.
Need to decide further if Models for Specific clusters should be copied on every server, Possibly yes, to make predictios efficient.

e.g.
STREAM_IN_TOPIC has new data point for key=ci_name

Currently time series is assumed to be time zone agnoistic so, None Timezone is appled. This needs to be reviewed carefully. 
Time series is downsampled, log scaled, if key is already found then value is retrieved from table i.e. database and new dataframe appended. 
Vlue is converted back into JSON and new value pushed into table against the same key. 
Key = CI_NAME

Final value expected here is 
key = value in JSON

Agent concurrency may not be possible sie we want to maintin table and need to keep predicting and send message to next topic for strong prediction.
Anomaly score is reconfirmed as anomalous using Markov Chain model i.e. probability matrix.

'''

app = faust.App(
	'TSAnomaly_standalone_StrongPred', 
	broker= 'kafka://localhost:9092',
	web_port=6096,
	producer_max_request_size=15728640,
	store='rocksdb://',
)


STREAM_IN_TOPIC = app.topic('ts_anomaly_weakpred_out',schema=cmdls.WeakPredschema)
STREAM_IN_CONFIRMED_TOPIC = app.topic('ts_anomaly_weakpred_confirmed',schema=cmdls.WeakPredschema)

ANOMALYVIEW = app.Table('anomaly_view_count', default=int,partitions-1).tumbling(timedelta(minutes=30),expires=timedelta(hours=1),key_index=True).relative_to_field(cmdls.WeakPredObservation.ts)
ANOMALYLIST = app.Table('anomaly_list',default=list,partitions=1).tumbling(timedelta(minutes=30),expires=timedelta(hours=1),key_index=True).relative_to_field(cmdls.WeakPredObservation.ts)


tempnparr = {}
metricstime = {}
metrics = {}




min_anomaly_observations = settings["min_anomally_observations_d"]



async def send_to_topic(topic_name,ci_name,valueindex,df_columns):
	df_temp = pd.DataFrame()
	df_temp.at[0. 'df_columons'] = df_columns
	df_temp = df_temp.iloc[0.:len(df_temp.columns)]
	temp_str = json.loads(df_temp.to.json(orient='index',data_format='iso'))
	await topic_name.send(key=ci_name,value=temp_str)



@app.agent(STREAM_IN_TOPIC)
async def agent_strongpred_counter(stream):
	async for stream_itme in stream.events():
		ci_name = stream_item.key 
		value_metricstime =int(stream_item,value.df_columnnos)

		ANOMALYVIEW[ci_name] += 1

		tempnparr[ci_name] = []

		if (ANOMALYVIEW[ci_name].value() > 1):
			metrics[ci_name] = ANOMALYLIST(ci_name).value()
			metrics[ci_name].append(tempnparr[ci_name])
			[metricstime[ci_name].append(x) for x in metrics[ci_name] if x is not in metricstime[ci_name]]
			ANOMALYLIST(ci_name) = metricstime[ci_name]
			ano_list = ANOMALYLIST[ci_name].value()
			ANOMALYVIEW[ci_name] = len(ano_list)
		else:
			metricstime[ci_name].append(tempnparr[ci_name])
			ANOMALYLIST[ci_name] = metricstime[ci_name]

		print("printing metricstime for server {}".format(ci_name))
		print(ANOMALYLIST[ci_name].value(),ANOMALYVIEW[ci_name],value())

		if(ANOMALYVIEW[ci_name],value() >= min_anomaly_observations):
			print("fag7_strongpred: Anomaly points more than minimum observations for ci_came {} {}".format(ci_name,ANOMALYVIEW[ci_name].value()))
			ANOMALYVIEW[ci_name] = 0

			for each_observation in ANOMALYLIST[ci_name].value():

			df_temp = pd.DataFrame()
			df_temp.at[0,'ts'] = each_observation[0]
			df_temp.at[0,'df_columnnos'] = each_observation[1]
			df_temp = df_temp.iloc[0,:len(df_temp_columns)]
			temp_str = json.loads(df_temp.to_json(orient='index',data_format='iso'))
			await STREAM_IN_CONFIRMED_TOPIC.send(key=ci_name,value=temp_str)

			
        else
:        	continue


















metricstime[ci_name].extend(x for x in metrics[ci_name] if x not in metricstime[ci_name])
