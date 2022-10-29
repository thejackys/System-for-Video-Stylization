import tensorflow as tf
from .net import fst_net
import numpy as np
import os

CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), 'checkpoint')

class FST:
    def __init__(self):
        self.styles = ['la_muse', 'rain_princess', 'scream', 'udnie', 'wave', 'wreck']
        pass
    def _run(self, contents, style_type):
        g = tf.Graph()
        with g.as_default(), g.device('/CPU:0'), tf.compat.v1.Session() as sess:
            img_placeholder = tf.compat.v1.placeholder(tf.float32, shape=contents.shape, name='img_placeholder')
            preds = fst_net.net(img_placeholder)
            saver = tf.compat.v1.train.Saver()
            saver.restore(sess, os.path.join(CHECKPOINT_DIR, style_type+'.ckpt'))
            results = sess.run(preds, feed_dict={img_placeholder:contents.astype(np.float32)})
            results = np.clip(results, 0, 255).astype(np.uint8)
        return results

    def transform(self, contents, style_type, same_shape=False):
        if not same_shape:
            results = []
            for content in contents:
                content = content[np.newaxis, :, :, :]
                results.append(self._run(content, style_type)[0])
        else:
            contents = np.array(contents)
            results = self._run(contents, style_type)
        return results

if __name__ == '__main__':
    from PIL import Image
    input_dir = os.path.join(os.path.dirname(__file__), 'image/content/')
    output_dir = os.path.join(os.path.dirname(__file__), 'image/result/')
    files = os.listdir(input_dir)

    content = [np.array(Image.open(os.path.join(input_dir, name))) for name in files]
    style_type = 'la_muse'

    fst = FST()
    result = fst.transform(content, style_type)
    for index, name in enumerate(files):
        Image.fromarray(result[index]).save(os.path.join(output_dir, 'fst_'+name))
