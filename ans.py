app.agent(STRONG_TRAIN_TOPIC)
#handles operations in async while consuming messages from kafka topic: Strong_TRAIN_TOPIC
async def agent_weakpred_job(stream):
    async for stream_item in stream.events():  #iterates over the kafka topic stream

        all_partitions_processed = False

        for partition in range(0, settings["num_partitions"]):
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
            for each_key, each_val in clusterit:
                if each_key == b'unique' or each_key == b'__faust\x00offset__':
                    continue

                tseries = each_key.decode('UTF-8') #timeseries-name
                model_name = str(each_val.decode().split(",")[0]) #model name(cluster name)
                ci_list.append(tseries.split(".")[0]) # appends the cluster identifier by splitting the timeseries name
                mname[tseries] = model_name #assosiates the time series with its corresponding model name(cluster_name)

                #group time series under their respective clusters
                if model_name in columnlist:
                    columnlist[model_name.append(tseries)]
                else:
                    columnlist[model_name] = [tseries]

            for key, val in columnlist.items():
                #Creating DataFrames for Each Model
                df_agg_pred[key] = pd.DataFrame()
                df_agg_trend[key] = pd.DataFrame()
                df_agg_season[key] = pd.DataFrame()

                # Processing Data for Each Model
                # The rest of your code for processing data for each model goes here

                # Assuming you have some code here to process the data in each model

            # Set the flag to True if this is the last partition to process
            if partition == settings["num_partitions"] - 1:
                all_partitions_processed = True

            # Break the loop if all partitions have been processed
            if all_partitions_processed:
                break
