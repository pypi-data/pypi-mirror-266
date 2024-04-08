# Packaged AOT Series Framework in PyTorch

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/decoupling-features-in-hierarchical/semi-supervised-video-object-segmentation-on-15)](https://paperswithcode.com/sota/semi-supervised-video-object-segmentation-on-15?p=decoupling-features-in-hierarchical)
[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/associating-objects-with-scalable/video-object-segmentation-on-youtube-vos)](https://paperswithcode.com/sota/video-object-segmentation-on-youtube-vos?p=associating-objects-with-scalable)
[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/associating-objects-with-scalable/semi-supervised-video-object-segmentation-on-18)](https://paperswithcode.com/sota/semi-supervised-video-object-segmentation-on-18?p=associating-objects-with-scalable)
[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/associating-objects-with-scalable/semi-supervised-video-object-segmentation-on-1)](https://paperswithcode.com/sota/semi-supervised-video-object-segmentation-on-1?p=associating-objects-with-scalable)
[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/associating-objects-with-scalable/visual-object-tracking-on-davis-2017)](https://paperswithcode.com/sota/visual-object-tracking-on-davis-2017?p=associating-objects-with-scalable)
[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/associating-objects-with-scalable/visual-object-tracking-on-davis-2016)](https://paperswithcode.com/sota/visual-object-tracking-on-davis-2016?p=associating-objects-with-scalable)


## Intro
This repository is a wrapper for packaging around the AOT series framework:
- **DeAOT**: Decoupling Features in Hierarchical Propagation for Video Object Segmentation (NeurIPS 2022, Spotlight) [[OpenReview](https://openreview.net/forum?id=DgM7-7eMkq0)][[PDF](https://arxiv.org/pdf/2210.09782.pdf)]
<img src="aot/source/overview_deaot.png" width="90%"/>

- **AOT**: Associating Objects with Transformers for Video Object Segmentation (NeurIPS 2021, Score 8/8/7/8) [[OpenReview](https://openreview.net/forum?id=hl3v8io3ZYt)][[PDF](https://arxiv.org/abs/2106.02638)]
<img src="aot/source/overview.png" width="90%"/>

An extension of AOT, [AOST](https://arxiv.org/abs/2203.11442) (under review), is available now. AOST is a more robust and flexible framework, supporting run-time speed-accuracy trade-offs.


## Citations
Please consider citing the related paper(s) from the original authors in your publications if it helps your research.
```
@article{yang2021aost,
  title={Scalable Video Object Segmentation with Identification Mechanism},
  author={Yang, Zongxin and Miao, Jiaxu and Wei, Yunchao and Wang, Wenguan and Wang, Xiaohan and Yang, Yi},
  journal={TPAMI},
  year={2024}
}
@inproceedings{xu2023video,
  title={Video object segmentation in panoptic wild scenes},
  author={Xu, Yuanyou and Yang, Zongxin and Yang, Yi},
  booktitle={IJCAI},
  year={2023}
}
@inproceedings{yang2022deaot,
  title={Decoupling Features in Hierarchical Propagation for Video Object Segmentation},
  author={Yang, Zongxin and Yang, Yi},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2022}
}
@inproceedings{yang2021aot,
  title={Associating Objects with Transformers for Video Object Segmentation},
  author={Yang, Zongxin and Wei, Yunchao and Yang, Yi},
  booktitle={Advances in Neural Information Processing Systems (NeurIPS)},
  year={2021}
}
```

## License
This project is released under the BSD-3-Clause license. See [LICENSE](LICENSE) for additional details.
