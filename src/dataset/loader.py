import re
import asyncio
import numpy as np
import pandas as pd
from utils import load_df_cache, get_outpoints
from lbry import filtered_outpoints

# Create dataframes from dataset chunk
class Dataset_chunk_loader:
    def __init__(self):
        self.load()

    def load(self):
        self.valid = True
        self.df_streams = self.load_streams_data()
        self.df_channels = self.load_channels_data()
        # Not enough data to process dataset chunk
        if self.df_streams.empty or self.df_channels.empty:
            self.valid = False

    # Load streams dataframe
    def load_streams_data(self):
        df_streams = load_df_cache("df_streams")
        if not df_streams.empty:
            df_streams = self.prepare_streams_data(df_streams)
        return df_streams

    # Load channels dataframe
    def load_channels_data(self):
        df_channels = load_df_cache("df_channels")
        if not df_channels.empty:
            df_channels = self.prepare_channels_data(df_channels)
        return df_channels

    # Initial preparation of streams dataframe
    def prepare_streams_data(self, df):
        df_streams = df.copy()
        # Generate and append outpoints
        df_streams["outpoint"] = (
            df_streams["transaction_hash_id"] + ":" + df_streams["vout"].astype(str)
        )
        # Filter blocked content
        if filtered_outpoints and len(filtered_outpoints) > 0:
            filter_mask = ~df_streams.outpoint.isin(filtered_outpoints)
            df_streams = df_streams.loc[filter_mask]

        # Remove irrelevant columns
        df_streams = df_streams.drop(
            ["transaction_hash_id", "vout", "outpoint"], axis=1
        )

        return df_streams

    def prepare_channels_data(self, df):
        df_channels = df.copy()
        # Filters
        filter_mask = df_channels.channel_title.notnull() & (
            df_channels.channel_title.str.len() > 0
        )
        df_channels = df_channels.loc[filter_mask]
        # Format channel title
        df_channels["channel_title"] = df_channels["channel_title"].astype("string")
        return df_channels
