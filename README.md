# SoftwareTopics


## Reproducibility

### Setup

The project uses [Poetry](https://python-poetry.org/) to manage dependencies. Check a quick guide to use Poetry [here](https://python-poetry.org/docs/basic-usage/).

Install the required packages by running the following command:

```bash
poetry init
```

Once the packages are installed, to reproduce the results, you can use ```make``` commands.

For example, to run the construction of the taxonomy using Wikidata (others require to download other artifacts, see below), you can run the following command:

```bash
make complete_wiki
```

or for the plots (and installing dependencies):

```bash
make setup_R
make plots
```