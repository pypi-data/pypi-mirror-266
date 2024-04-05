from setuptools import setup

import loss_balancer_tf

setup(
    name="loss-balancer-tf",
    author="anime-song",
    description="Implementation of Encodec loss balancer in tensorflow",
    license="MIT license",
    version="0.0.3",
    install_requires=["tensorflow"],
    packages=["loss_balancer_tf"]
)
