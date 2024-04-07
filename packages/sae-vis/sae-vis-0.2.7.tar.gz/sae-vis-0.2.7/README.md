This codebase was designed to replicate Anthropic's sparse autoencoder visualisations, which you can see [here](https://transformer-circuits.pub/2023/monosemantic-features/vis/a1.html). The codebase provides 2 different views: a **feature-centric view** (which is like the one in the link, i.e. we look at one particular feature and see things like which tokens fire strongest on that feature) and a **prompt-centric view** (where we look at once particular prompt and see which features fire strongest on that prompt according to a variety of different metrics).

Install with `pip install sae-vis`. Link to PyPI page [here](https://pypi.org/project/sae-vis/).

**Important note** - this repo has recently been significantly restructured. The recent changes include:

- The ability to view multiple features on the same page (rather than just one feature at a time)
- D3-backed visualisations (which can do things like add lines to histograms as you hover over tokens)
- More freedom to customize exactly what the visualisation looks like (we provide full cutomizability, rather than just being able to change certain parameters)

[Here](https://drive.google.com/drive/folders/1sAF3Yv6NjVSjo4wu2Tmu8kMh8it6vhIb?usp=sharing) is a link to a Google Drive folder containing 3 files:

- [**User Guide**](https://docs.google.com/document/d/1QGjDB3iFJ5Y0GGpTwibUVsvpnzctRSHRLI-0rm6wt_k/edit?usp=drive_link), which covers the basics of how to use the repo (the core essentials haven't changed much from the previous version, but there are significantly more features)
- [**Dev Guide**](https://docs.google.com/document/d/10ctbiIskkkDc5eztqgADlvTufs7uzx5Wj8FE_y5petk/edit?usp=sharing), which we recommend for anyone who wants to understand how the repo works (and make edits to it)
- [**Demo**](https://colab.research.google.com/drive/1oqDS35zibmL1IUQrk_OSTxdhcGrSS6yO?usp=drive_link), which is a Colab notebook that gives a few examples

In the demo Colab, we show the two different types of vis which are supported by this library:

1. **Feature-centric vis**, where you look at a single feature and see e.g. which sequences in a large dataset this feature fires strongest on.

<img src="https://raw.githubusercontent.com/callummcdougall/computational-thread-art/master/example_images/misc/sae-snip-1B.png" width="800">

2. **Prompt-centric vis**, where you input a custom prompt and see which features score highest on that prompt, according to a variety of possible metrics.

<img src="https://raw.githubusercontent.com/callummcdougall/computational-thread-art/master/example_images/misc/sae-snip-2.png" width="800">