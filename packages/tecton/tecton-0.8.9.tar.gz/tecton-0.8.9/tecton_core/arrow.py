import pyarrow.dataset


# These are kwargs for the pyarrow.dataset.ParquetFileFormat.make_write_options function. They are "unwrapped" like this
# because some other APIs (e.g. pyarrow.parquet.write_to_dataset, which is in turn called by
# pandas.DataFrame.to_parquet) also accept write options in kwargs format but not FileWriteOptions format.
PARQUET_WRITE_OPTIONS_KWARGS = {
    "version": "2.4",
    "data_page_version": "1.0",
}

PARQUET_WRITE_OPTIONS = pyarrow.dataset.ParquetFileFormat().make_write_options(**PARQUET_WRITE_OPTIONS_KWARGS)
