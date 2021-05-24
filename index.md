# Trove Newspaper and Gazette Harvester

The [Trove Newspaper & Gazette Harvester Harvester](https://pypi.org/project/troveharvester/) makes it easy to download large quantities of digitised articles from Trove's newspapers and gazettes. Just give it a search from the Trove web interface, and the harvester will save the metadata of all the articles in a CSV (spreadsheet) file for further analysis. You can also save the full text of every article, as well as copies of the articles as JPG images, and even PDFs. While the web interface will only show you the first 2,000 results matching your search, the Newspaper & Gazette Harvester will get **everything**.

The Jupyter notebooks in this repository use the Trove Newspaper and Gazette Harvester to download large quantities of digitised newspaper articles from Trove. There's also a few examples of how you can analyse and explore the harvested data.

The notebooks include:

* [**Using TroveHarvester to get newspaper articles in bulk**](Using-TroveHarvester-to-get-newspaper-articles-in-bulk.ipynb) — an easy introduction to the TroveHarvester tool
* [**Trove Harvester web app**](newspaper_harvester_app.ipynb) — a simple web interface to the TroveHarvester, the easiest way to harvest data from Trove (runs in Voila)
* [**Display the results of a harvest as a searchable database using Datasette**](display_harvest_results_using_datasette.ipynb) – load your harvested data into a SQLite database and explore it using Datasette
* [**Exploring your TroveHarvester data**](Exploring-your-TroveHarvester-data.ipynb) — use Pandas to analyse your data and create some visualisations
* [**Explore harvested text files**](Explore-harvested-text-files.ipynb) (experimental) — analyse the full text content of harvested articles

See the [GLAM Workbench for more details](https://glam-workbench.github.io/trove-harvester/).


## Cite as

See the GLAM Workbench or [Zenodo](https://doi.org/10.5281/zenodo.3545044) for up-to-date citation details.

----

This repository is part of the [GLAM Workbench](https://glam-workbench.github.io/).  
If you think this project is worthwhile, you might like [to sponsor me on GitHub](https://github.com/sponsors/wragge?o=esb).
