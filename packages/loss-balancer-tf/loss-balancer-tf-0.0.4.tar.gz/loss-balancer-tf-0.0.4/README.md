# loss-balancer-tf

Encodec の lossbalancer の tensorflow での実装です。

# Installation

```sh
pip install loss-balancer-tf
```

# Usage

```py
class Trainer():
    def __init__(self,
        recon_loss_weight: float = 1.0,
        feature_loss_weight: float = 3.0,
        generator_loss_weight: float = 3.0):

        # 各ロスの重みを設定
        self.loss_balancer = LossBalancer(weights={
            "mel": recon_loss_weight,
            "feat": feature_loss_weight,
            "gen": generator_loss_weight,
        })

    @tf.function
    def train_step(self, input_data):
        x_batch_train, _ = input_data

        # 勾配を複数回計算するため persistent=Trueが必須です
        with tf.GradientTape(persistent=True) as gen_tape:
            g_fake, _, _, mel_loss, original_inputs = self.generator(x_batch_train, training=True)

            losses = [tf.reduce_mean(tf.abs(tf.cast(real, tf.float32) - tf.cast(fake, tf.float32)))
                    for real, fake in zip(real_intermediates, fake_intermediates)]
            feature_loss = tf.reduce_sum(losses)
            recon_loss = mel_loss

            g_loss = self.generator_loss(fake_pred)

        # 計算したロスをロスバランサーに渡し勾配を計算します
        scaled_gen_grads, scaled_metrics = self.loss_balancer.gradient(
            loss_dict={
                "mel": recon_loss,
                "feat": feature_loss,
                "gen": g_loss
            },
            tape=gen_tape,
            output=g_fake,
            trainable_variables=self.generator.trainable_variables)
        self.generator_optimizer.apply_gradients(zip(scaled_gen_grads, self.generator.trainable_variables))

        metrics = {
            "g_loss": g_loss,
            "feature_loss": feature_loss,
            "mel_loss": recon_loss,
        }
        metrics.update(scaled_metrics)
        return metrics
```
