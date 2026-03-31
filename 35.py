# Prompt 35

import tensorflow as tf
import tensorflow_federated as tff

# Define a simple federated learning model
def create_federated_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10)
    ])
    return tff.learning.from_keras_model(
        model,
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
    )

# Simulate a federated dataset
emnist_train, emnist_test = tff.simulation.datasets.emnist.load_data()

def preprocess(dataset):
    def batch_format_fn(element):
        return (tf.cast(element['pixels'], tf.float32) / 255., tf.cast(element['label'], tf.int64))
    return dataset.batch(20).map(batch_format_fn)

federated_train_data = [preprocess(emnist_train.create_tf_dataset_for_client(client))
                         for client in emnist_train.client_ids]
federated_test_data = preprocess(emnist_test.create_tf_dataset_for_client(emnist_test.client_ids[0]))

# Define the federated learning process
iterative_process = tff.learning.build_federated_averaging_process(
    create_federated_model,
    client_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.02),
    server_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=1.0)
)

# Initialize the federated learning process
state = iterative_process.initialize()

# Run the federated learning process
for round_num in range(1, 11):
    state, metrics = iterative_process.next(state, federated_train_data)
    print('round {:2d}, metrics={}'.format(round_num, metrics))