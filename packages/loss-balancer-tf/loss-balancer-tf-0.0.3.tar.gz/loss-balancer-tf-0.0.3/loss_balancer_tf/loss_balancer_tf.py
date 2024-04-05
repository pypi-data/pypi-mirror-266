import tensorflow as tf
import typing as tp

# 元の実装: https://github.com/facebookresearch/encodec/blob/main/encodec/balancer.py
class LossBalancer():
    def __init__(self,
                 weights: tp.Dict[str, float],
                 rescale_grads: bool=True,
                 total_norm: float=1.0,
                 epsilon: float=1e-12,
                 ema_decay: float=0.999,
                 per_batch_item: bool=True):
        self.loss_weights = weights
        self.rescale_grads = rescale_grads
        self.total_norm = total_norm
        self.epsilon = epsilon
        self.ema_decay = ema_decay
        self.per_batch_item = per_batch_item

        self.total = tf.Variable(tf.zeros(len(self.loss_weights)), trainable=False)
        self.fix = tf.Variable(tf.zeros(len(self.loss_weights)), trainable=False)
        self.keys_to_indices = {k: i for i, k in enumerate(self.loss_weights)}

    def _update(self, metrics: tp.Dict[str, tp.Any], weight: float = 1) -> tp.Dict[str, float]:
        for key, value in metrics.items():
            if tf.reduce_any(tf.math.is_nan(value)):
                continue
            idx = self.keys_to_indices[key]
            self.total[idx].assign(self.total[idx] * self.ema_decay + weight * value)
            self.fix[idx].assign(self.fix[idx] * self.ema_decay + weight)
        return {key: self.total[self.keys_to_indices[key]] / self.fix[self.keys_to_indices[key]]
                    for key in metrics.keys()}

    def gradient(self, loss_dict: tp.Dict[str, tf.Tensor], tape: tf.GradientTape, output: tf.Tensor, trainable_variables):
        total_weights = sum(list(self.loss_weights.values()))
        ratios = {k: w / total_weights for k, w in self.loss_weights.items()}

        norms = {}
        grads = {}
        for name, loss in loss_dict.items():
            gradients = tape.gradient(loss, output)

            if self.per_batch_item:
                axis = tuple(range(1, len(gradients.shape)))
                if len(gradients.shape) == 1:
                    axis = None

                norms[name] = tf.reduce_mean(tf.norm(gradients, axis=axis))
            else:
                norms[name] = tf.norm(gradients)

            grads[name] = gradients

        avg_norms = self._update(norms)
        metrics = {}
        total = sum(avg_norms.values())
        for k, v in avg_norms.items():
            metrics[f'ratio_{k}'] = v / total

        out_grad = None
        for name, grad in grads.items():
            if self.rescale_grads:
                scale = ratios[name] * self.total_norm / (self.epsilon + avg_norms[name])
                scaled_grad = tf.multiply(grad, scale)
            else:
                weight = self.loss_weights[name]
                scaled_grad = tf.multiply(grad, weight)

            if out_grad is None:
                out_grad = scaled_grad
            else:
                out_grad = out_grad + scaled_grad

        out_grad = tape.gradient(output, trainable_variables, output_gradients=out_grad)
        return out_grad, metrics


def test():
    x = tf.Variable([0.0], trainable=True)
    one = tf.constant([1.0])
    minus_one = tf.constant([-1.0])

    balancer_no_rescale = LossBalancer(weights={'1': 1, '2': 1}, rescale_grads=False)
    with tf.GradientTape(persistent=True) as tape:
        loss_1 = tf.reduce_mean(tf.abs(x - one))
        loss_2 = 100 * tf.reduce_mean(tf.abs(x - minus_one))
        losses = {'1': loss_1, '2': loss_2}
    grads_no_rescale, _ = balancer_no_rescale.gradient(losses, tape, x, x)
    assert tf.abs(grads_no_rescale - tf.constant(99.0)) < 1e-5


    balancer_rescale = LossBalancer(weights={'1': 1, '2': 1}, rescale_grads=True)
    with tf.GradientTape(persistent=True) as tape:
        loss_1 = tf.reduce_mean(tf.abs(x - one))
        loss_2 = 100 * tf.reduce_mean(tf.abs(x - minus_one))
        losses = {'1': loss_1, '2': loss_2}
    grads_rescale, _ = balancer_rescale.gradient(losses, tape, x, x)

    assert tf.abs(grads_rescale) < 1e-5

if __name__ == '__main__':
    test()