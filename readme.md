# EDNA

EDNA is an end-to-end streaming toolkit for ingesting, processing, and emitting streaming data. It is based on our prior work with [LITMUS](https://ieeexplore.ieee.org/abstract/document/6971222),
[ASSED](https://dl.acm.org/doi/abs/10.1145/3328905.3329510), and [EventMapper](https://arxiv.org/abs/2001.08700) and incorporates a slew of improvements and features for streaming analytics, fault tolerance, and end-to-end management.


EDNA's initial use was a test-bed for studying concept drift detection and recovery in multimedia datasets. Over time, it has grown to a toolkit for stream analytics. We are continuing to work on it to mature it for production clusters. To that end, this repo hosts an alpha version.


We have described EDNA in our paper, [EDNA-COVID: A Large-Scale Covid-19 Dataset Collected with the EDNA Streaming Toolkit](https://arxiv.org/abs/2010.04084). There are also a set of tutorials in the **Setup** folder we use to introduce the toolkit to students in the Real-Time Systems course at Georgia Tech. We have also released a dataset for COVID-19 collected with EDNA at the [EDNA-COVID](https://github.com/asuprem/EDNA-Covid-Tweets) repository.

To cite the paper, please use:

```
@article{edna,
  title={EDNA-COVID: A Large-Scale Covid-19 Dataset Collected with the EDNA Streaming Toolkit},
  author={Suprem, Abhijit and Pu, Calton},
  journal={arXiv preprint},
  year={2020}
}
```
