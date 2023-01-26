from model import CVAE, Encoder, Decoder
from randomforest import *
from utils import *

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
print('Tensorflow: %s' % tf.__version__)  # print version

new_model = True
find_dimensions = True
parent_dir = 'data_binary_watermark'
sub_dir = 'my_model'


def train_a_model(train_params):
    from train import load_data, sample_inputs, initialize_training, train_model
    check_dir(train_params.name)

    model = CVAE(
        latent_dim=train_params.latent_dim,
        batch_size=train_params.batch_size,
        image_size=train_params.image_size
    )

    test_set, train_set = load_data(train_params)
    log_lists, test_sample, test_label = sample_inputs(
        model, Encoder, Decoder, test_set, train_params
    )
    pbar, e_loss_record, r_loss_record, k_loss_record = initialize_training(train_params)
    model, test_sample, test_label = train_model(
        model=model,
        test_set=test_set,
        train_set=train_set,
        test_sample=test_sample,
        test_label=test_label,
        pbar=pbar,
        k_loss_record=k_loss_record,
        r_loss_record=r_loss_record,
        e_loss_record=e_loss_record,
        params=train_params
    )
    return model, test_set, train_set


if __name__ == "__main__":
    from train import load_data, TrainParams
    if new_model:
        check_params = TrainParams(
            parent_dir=parent_dir,
            name=sub_dir,
            epochs=75,
            batch_size=32,
            image_size=32,
            latent_dim=32,
            num_examples_to_generate=16,
            learning_rate=0.001
            # show_latent_gif=True
        )
        cvae, test_ds, train_ds = train_a_model(check_params)
    # else:
    #     load_params = TrainParams(
    #         parent_dir=parent_dir,
    #         name=sub_dir,
    #         epochs=2,
    #         batch_size=16,
    #         image_size=128,
    #         latent_dim=32,
    #         num_examples_to_generate=16,
    #         learning_rate=0.001
    #         # show_latent_gif=True
    #     )
    #     cvae, test_ds, train_ds = load_data(parent_dir)

    if find_dimensions:
        # Get arrays of encoded data from model
        train_encodings, train_labels, train_files, split_train_encodings, _ = get_encoding(cvae, train_ds)
        test_encodings, test_labels, test_files, _, _ = get_encoding(cvae, test_ds)

        # Run arrays through random forest regression to figure out if any can separate the labels
        valuable_encodings, forest_model = random_forest(
            train_encodings,
            train_labels,
            test_encodings,
            test_labels,
            check_params
        )
        show_split(split_train_encodings, valuable_encodings, forest_model, check_params)
        save_tree(forest_model, check_params)
