# Morphology-Generation

Implementation of the work presentented in the paper Morphology Generation for Statistical Machine Translation using Deep Learning Techniques (https://arxiv.org/abs/1610.02209)

# Run the model

In order to run the model for translation:

```

translate.py [--stdin, -f path-to-input-file] [--stdout, -o path-to-output-file]

```

Options --stdin and --stdout to read and print results using the standard IO channel. -f and -o to translate from and to a file.

# Configuration

In order to execute the code in the file config/config the following paths to dependencies are required to the be modified according to your system:

* MOSES_DIR: Path to Moses installation
* SRILM_DIR: Path to Srilm installation
* BASELINE: Path to trained Moses model





