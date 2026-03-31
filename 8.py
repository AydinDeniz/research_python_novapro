# Prompt 8

import dask.dataframe as dd
import dask
from dask.distributed import Client

# Initialize Dask client for parallel processing
client = Client(n_workers=4, threads_per_worker=2, memory_limit='2GB')

# Load large dataset using Dask
data_path = 'large_dataset.csv'
ddf = dd.read_csv(data_path)

# Display initial data to understand structure
print(ddf.head())

# Perform groupby operation
groupby_result = ddf.groupby('category').sum()

# Perform a join operation
another_dataset_path = 'another_large_dataset.csv'
another_ddf = dd.read_csv(another_dataset_path)
joined_result = ddf.merge(another_ddf, on='common_column', how='inner')

# Perform aggregation
aggregation_result = ddf.groupby('category').agg({'value':'mean'})

# Define a custom transformation function
def custom_transformation(df):
    df['new_column'] = df['value'] * 2
    return df

# Apply the custom transformation
transformed_result = ddf.map_partitions(custom_transformation)

# Save results to files
groupby_result.to_csv('groupby_result.csv', single_file=True)
joined_result.to_csv('joined_result.csv', single_file=True)
aggregation_result.to_csv('aggregation_result.csv', single_file=True)
transformed_result.to_csv('transformed_result.csv', single_file=True)

# Demonstrate scalability by increasing the number of workers and re-running operations
client.restart(n_workers=8, threads_per_worker=4, memory_limit='4GB')

# Re-run operations with increased resources
groupby_result_scaled = ddf.groupby('category').sum()
joined_result_scaled = ddf.merge(another_ddf, on='common_column', how='inner')
aggregation_result_scaled = ddf.groupby('category').agg({'value':'mean'})
transformed_result_scaled = ddf.map_partitions(custom_transformation)

# Save scaled results to files
groupby_result_scaled.to_csv('groupby_result_scaled.csv', single_file=True)
joined_result_scaled.to_csv('joined_result_scaled.csv', single_file=True)
aggregation_result_scaled.to_csv('aggregation_result_scaled.csv', single_file=True)
transformed_result_scaled.to_csv('transformed_result_scaled.csv', single_file=True)

# Additional complex operations to demonstrate further scalability
complex_operation_result = ddf.groupby('category').apply(lambda df: df[df['value'] > df['value'].mean()])
complex_operation_result.to_csv('complex_operation_result.csv', single_file=True)

# More custom transformations
def another_custom_transformation(df):
    df['another_new_column'] = df['value'] ** 2
    return df

another_transformed_result = ddf.map_partitions(another_custom_transformation)
another_transformed_result.to_csv('another_transformed_result.csv', single_file=True)

# Chaining operations to show complex workflows
chained_result = ddf.groupby('category').sum().merge(another_ddf.groupby('category').mean(), on='category')
chained_result.to_csv('chained_result.csv', single_file=True)

# Final cleanup
client.shutdown()