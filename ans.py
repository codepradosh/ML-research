import time

app.agent(STRONG_TRAIN_TOPIC)
# handles operations in async while consuming messages from kafka topic: Strong_TRAIN_TOPIC
async def agent_weakpred_job(stream):
    async for stream_item in stream.events():  # iterates over the kafka topic stream

        total_time_all_partitions = 0.0  # Variable to store the total time for all partitions

        for partition in range(0, settings["num_partitions"]):

            # Record the start time for the current partition
            start_time_partition = time.time()

            df_agg_pred = pd.DataFrame()
            df_agg_trend = pd.DataFrame()
            df_agg_season = pd.DataFrame()
            df_agg_total = pd.DataFrame()

            # Rest of your code for processing data in each partition goes here

            # Assuming you have some code here to process the data in each partition

            # Record the end time for the current partition
            end_time_partition = time.time()

            # Calculate the time taken to complete the current partition
            time_taken_partition = end_time_partition - start_time_partition

            # Add the time taken for the current partition to the total time for all partitions
            total_time_all_partitions += time_taken_partition

        # Print the total time taken for all partitions
        print("Total time for all partitions:", total_time_all_partitions)
