import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras import datasets, layers, models, losses, Model
from main import get_files
from keras.models import load_model

BATCH_SIZE = 32
IMAGE_SIZE = [224, 224]
NUM_CLASSES = 47
    
def train():
    train_dataset, val_dataset, test_dataset = get_files()

    base_model = tf.keras.applications.ResNet101(weights='imagenet', include_top=False, input_shape = (*IMAGE_SIZE, 3))
    base_model = tf.keras.applications.VGG16(input_shape=(*IMAGE_SIZE, 3), include_top=False, weights='imagenet')
    base_model.trainable = False

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='categorical_crossentropy',
                  metrics='accuracy')

    checkpoint_cb = tf.keras.callbacks.ModelCheckpoint("texture_model.h5",
                                                    save_best_only=True)

    early_stopping_cb = tf.keras.callbacks.EarlyStopping(patience=5,
                                                        restore_best_weights=True)

    def exponential_decay(lr0, s):
        def exponential_decay_fn(epoch):
            return lr0 * 0.1 **(epoch / s)
        return exponential_decay_fn

    exponential_decay_fn = exponential_decay(0.01, 20)

    lr_scheduler = tf.keras.callbacks.LearningRateScheduler(exponential_decay_fn)

    history = model.fit(train_dataset, batch_size=100, epochs=20, validation_data=val_dataset,
     callbacks=[checkpoint_cb, early_stopping_cb, lr_scheduler])

    def plot(history):
        fig, axs = plt.subplots(2, 1, figsize=(15, 15))
        axs[0].plot(history.history['loss'])
        axs[0].plot(history.history['val_loss'])
        axs[0].title.set_text('Training Loss vs Validation Loss')
        axs[0].set_xlabel('Epochs')
        axs[0].set_ylabel('Loss')
        axs[0].legend(['Train','Val'])
        axs[1].plot(history.history['accuracy'])
        axs[1].plot(history.history['val_accuracy'])
        axs[1].title.set_text('Training Accuracy vs Validation Accuracy')
        axs[1].set_xlabel('Epochs')
        axs[1].set_ylabel('Accuracy')
        axs[1].legend(['Train', 'Val'])
        plt.savefig('figure.png')

    plot(history)
    print(model.evaluate(test_dataset))

    model.compile(optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics='accuracy')

    model.summary()

    test_ds = test_ds.map(lambda items: (items["image"], tf.one_hot(items["label"], NUM_CLASSES)))

    test_ds = (
        test_ds
        .cache()
        .map(pad)
        .batch(BATCH_SIZE)
    ) 
    model.evaluate(test_ds)

def test():
    train_dataset, val_dataset, test_dataset = get_files()
    model = load_model('texture_model.h5')
    print(model.evaluate(test_dataset))
    model.summary()


if __name__ == "__main__":
    #train()
    test()