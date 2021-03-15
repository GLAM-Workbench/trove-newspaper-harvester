# Trove Newspaper and Gazette Harvester

The Jupyter notebooks in this repository use the Trove Harvester to download large quantities of digitised newspaper articles from Trove. There's also a few examples of how you can analyse and explore the harvested data.

The notebooks include:

* [**Trove Harvester web app**](newspaper_harvester_app.ipynb) — a simple web interface to the TroveHarvester, the easiest way to harvest data from Trove (runs in Appmode)
* [**Using TroveHarvester to get newspaper articles in bulk**](Using-TroveHarvester-to-get-newspaper-articles-in-bulk.ipynb) — an easy introduction to the TroveHarvester tool
* [**Exploring your TroveHarvester data**](Exploring-your-TroveHarvester-data.ipynb) — use Pandas to analyse your data and create some visualisations
* [**Explore harvested text files**](Explore-harvested-text-files.ipynb) — analyse the full text content of harvested articles

If you haven't used Jupyter notebooks before, you might want to try the Getting Started notebook. It introduces some basic concepts using data from the National Museum of Australia.

See the [GLAM Workbench for more details](https://glam-workbench.github.io/trove-harvester/).

<!-- START RUN INFO -->

## Run these notebooks

There are a number of different ways to use these notebooks. Binder is quickest and easiest, but it doesn't save your data. I've listed the options below from easiest to most complicated (requiring more technical knowledge).

### Using Binder

[![Launch on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/GLAM-Workbench/trove-newspaper-harvester/master)

Click on the button above to launch the notebooks in this repository using the [Binder](https://mybinder.org/) service (it might take a little while to load). This is a free service, but note that sessions will close if you stop using the notebooks, and no data will be saved. Make sure you download any changed notebooks or harvested data that you want to save.

### Using Reclaim Cloud

[![Launch on Reclaim Cloud](https://glam-workbench.github.io/images/launch-on-reclaim-cloud.svg)](https://app.my.reclaim.cloud/?manifest=https://raw.githubusercontent.com/GLAM-Workbench/trove-newspaper-harvester/master/reclaim-manifest.jps)

[Reclaim Cloud](https://reclaim.cloud/) is a paid hosting service, aimed particularly at supported digital scholarship in hte humanities. Unlike Binder, the environments you create on Reclaim Cloud will save your data – even if you switch them off! To run this repository on Reclaim Cloud for the first time:

* Create a [Reclaim Cloud](https://reclaim.cloud/) account and log in.
* Click on the button above to start the installation process.
* A dialogue box will ask you to set a password, this is used to limit access to your Jupyter installation.
* Sit back and wait for the installation to complete!
* Once the installation is finished click on the 'Open in Browser' button of your newly created environment (note that you might need to wait a few minutes before everything is ready).

See the GLAM Workbench for more details.

### Using Docker

You can use Docker to run a pre-built computing environment on your own computer. It will set up everything you need to run the notebooks in this repository. This is free, but requires more technical knowledge – you'll have to install Docker on your computer, and be able to use the command line.

* Install [Docker Desktop](https://docs.docker.com/get-docker/).
* Create a new directory for this repository and open it from the command line.
* From the command line, run the following command:  
  ```
  docker run -p 8888:8888 --name trove-newspaper-harvester -v "$PWD":/home/jovyan/work wragge/trove-newspaper-harvester repo2docker-entrypoint jupyter lab --ip 0.0.0.0 --NotebookApp.token='' --LabApp.default_url='/lab/tree/index.md'
  ```
* It will take a while to download and configure the Docker image. Once it's ready you'll see a message saying that Jupyter Notebook is running.
* Point your web browser to `http://127.0.0.1:8888`

See the GLAM Workbench for more details.

### Setting up on your own computer

If you know your way around the command line and are comfortable installing software, you might want to set up your own computer to run these notebooks.

Assuming you have recent versions of Python and Git installed, the steps might be something like:

* Create a virtual environment, eg: `python -m venv trove-harvester`
* Open the new directory" `cd trove-harvester`
* Activate the environment `source bin/activate`
* Clone the repository: `git clone https://github.com/GLAM-Workbench/trove-newspaper-harvester.git notebooks`
* Open the new `notebooks` directory: `cd notebooks`
* Install the necessary Python packages: `pip install -r requirements.txt`
* Run Jupyter: `jupyter lab`

See the GLAM Workbench for more details.

<!-- END RUN INFO -->

## Cite as

See the GLAM Workbench or [Zenodo](https://doi.org/10.5281/zenodo.3545044) for up-to-date citation details.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3545044.svg)](https://doi.org/10.5281/zenodo.3545044)

----

This repository is part of the [GLAM Workbench](https://glam-workbench.github.io/).  
If you think this project is worthwhile, you might like [to support me on Patreon](https://www.patreon.com/timsherratt).
