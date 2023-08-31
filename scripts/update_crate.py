import os
import argparse
import datetime
import requests
from giturlparse import parse as ghparse
from pathlib import Path
from typing import Union, List, Dict, Tuple
import mimetypes
from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from rocrate.model.data_entity import DataEntity
from rocrate.model.contextentity import ContextEntity
from extract_metadata import (
    extract_notebook_metadata,
)

NOTEBOOK_EXTENSION = ".ipynb"

DEFAULT_LICENCE = {
    "@id": "https://spdx.org/licenses/MIT",
    "name": "MIT License",
    "@type": "CreativeWork",
    "url": "https://spdx.org/licenses/MIT.html",
}

METADATA_LICENCE = {
    "@id": "https://creativecommons.org/publicdomain/zero/1.0/",
    "name": "CC0 Public Domain Dedication",
    "@type": "CreativeWork",
    "url": "https://creativecommons.org/publicdomain/zero/1.0/",
}

PYTHON = {
    "@id": "https://www.python.org/downloads/release/python-31012/",
    "version": "3.10.12",
    "name": "Python 3.10.12",
    "url": "https://www.python.org/downloads/release/python-31012/",
    "@type": ["ComputerLanguage", "SoftwareApplication"],
}


def main(version: str):
    # Make working directory the parent of the scripts directory
    os.chdir(Path(__file__).resolve().parent.parent)

    # Get a list of paths to notebooks in the cwd
    notebooks = get_notebooks()

    # Update the crate
    update_crate(version, notebooks)


def get_notebooks() -> List[Path]:
    """Returns a list of paths to jupyter notebooks in the given directory

    Parameters:
        dir: The path to the directory in which to search.

    Returns:
        Paths of the notebooks found in the directory
    """
    files = [Path(file) for file in os.listdir()]
    is_notebook = lambda file: file.suffix == NOTEBOOK_EXTENSION
    return list(filter(is_notebook, files))


def id_ify(elements: Union[List[str], str]) -> Union[List[dict], dict]:
    """Wraps elements in a list with @id keys
    eg, convert ['a', 'b'] to [{'@id': 'a'}, {'@id': 'b'}]
    """
    # If the input is a string, make it a list
    # elements = [elements] if isinstance(elements, str) else elements
    # Nope - single elements shouldn't be lists, see: https://www.researchobject.org/ro-crate/1.1/appendix/jsonld.html
    if isinstance(elements, str):
        return {"@id": elements}
    else:
        return [{"@id": element} for element in elements]


def add_people(crate: ROCrate, authors: List[Dict]) -> List[Person]:
    """Converts a list of authors to a list of Persons to be embedded within an ROCrate

    Parameters:
        crate: The rocrate in which the authors will be created.
        authors:
            A list of author information.
            Expects a dict with at least a 'name' value ('Surname, Givenname')
            If there's an 'orcid' this will be used as the id (and converted to a uri if necessary)
    Returns:
        A list of Persons.
    """
    persons = []

    # Loop through list of authors
    for author in authors:
        # If there's no orcid, create an id from the name
        if "orcid" not in author or not author["orcid"]:
            author_id = f"#{author['name'].replace(', ', '_')}"

        # If there's an orcid but it's not a url, turn it into one
        elif not author["orcid"].startswith("http"):
            author_id = f"https://orcid.org/{author['orcid']}"

        # Otherwise we'll just use the orcid as the id
        else:
            author_id = author["orcid"]

        # Check to see if there's already an entry for this person in the crate
        author_current = crate.get(author_id)

        # If there's already an entry we'll update the existing properties
        if author_current:
            properties = author_current.properties()

            # Update the name in case it has changed
            properties.update({"name": author["name"]})

        # Otherwise set default properties
        else:
            properties = {"name": author["name"]}

        # Add/update the person record and add to the list of persons to return
        persons.append(crate.add(Person(crate, author_id, properties=properties)))

    return persons


def get_file_stats(datafile: str) -> Tuple[str, int]:
    """
    Try to get the file size and last modified date of the datafile.
    """
    if datafile.startswith("http"):
        # Process GitHub links
        if "github.com" in datafile:
            # the ghparser doesn't seem to like 'raw' urls
            datafile = datafile.replace("/raw/", "/blob/")
            gh_parts = ghparse(datafile)

            # API url to get the latest commit for this file
            gh_commit_url = f"https://api.github.com/repos/{gh_parts.owner}/{gh_parts.repo}/commits?path={gh_parts.path.split('/')[-1]}"
            try:
                response = requests.get(gh_commit_url)

                # Get the date of the last commit
                date = response.json()[0]["commit"]["committer"]["date"][:10]

            except (IndexError, KeyError):
                date = None

            # Different API endpoint for file data
            gh_file_url = f"https://api.github.com/repos/{gh_parts.owner}/{gh_parts.repo}/contents/{gh_parts.path.split('/')[-1]}"
            try:
                response = requests.get(gh_file_url)

                # Get the file size
                size = response.json()["size"]

            except KeyError:
                size = None

        else:
            # If the file is online, get size from content headers
            size = requests.head(datafile).headers.get("Content-length")
            date = None

    else:
        # Get file stats from local filesystem
        stats = Path(datafile).stat()
        size = stats.st_size
        date = datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d")

    return date, size


def add_files(crate: ROCrate, datafiles) -> List:
    """
    Add data files to the crate.
    Tries to extract some basic info about files (size, date) before adding them.
    """
    file_entities = []

    # Loop through list of datafiles
    for datafile in datafiles:
        # Check if file exists (or is a url)
        if Path(datafile).exists() or datafile.startswith("http"):
            # Get date and size info
            date, size = get_file_stats(datafile)

            # Check to see if there's already an entry for this file in the crate
            file_entity = crate.get(datafile)

            # If there's already an entry for this file, we'll keep it's properties
            # but modify the date, size etc later
            if file_entity:
                properties = file_entity.properties()

            # Otherwise we'll define default properties for a new file entity
            else:
                name = datafile.split("/")[-1]
                properties = {
                    "@id": datafile,
                    "@type": ["File", "Dataset"],
                    "name": name,
                }

                # Guess the encoding type from extension
                encoding = mimetypes.guess_type(datafile)[0]
                if encoding:
                    properties["encodingFormat"] = encoding

            # Add/update modified date
            if date:
                properties["dateModified"] = date

            # Add/update file size
            if size:
                properties["contentSize"] = size

            # If it's a web link add today's date to indicate when it was last accessed
            if datafile.startswith("http"):
                properties["sdDatePublished"] = datetime.datetime.now().strftime(
                    "%Y-%m-%d"
                )

            # Add/update the file entity and add to the list of file entities
            file_entities.append(crate.add_file(datafile, properties=properties))

    return file_entities


def add_action(
    crate: ROCrate, notebook: DataEntity, input_files: List, output_files: List
) -> None:
    """
    Links a notebook and associated datafiles through a CreateAction.
    """
    # Create an action id from the notebook name
    action_id = f"{notebook.id.replace('.ipynb', '')}_run"

    # Get a list of dates from the output files
    dates = [f.properties()["dateModified"] for f in output_files]

    # Find the latest date to use as the endDate for the action
    try:
        last_date = sorted(dates)[-1]
    
    # There's no dates (or no output files)
    except IndexError:

        # Use the date the notebook was last modified
        last_date, _ = get_file_stats(notebook.id)

    # Check to see if this action is already in the crate
    action_current = crate.get(action_id)
    if action_current:
        # Remove current files from existing action entity
        properties = {"object": [], "result": []}
    else:
        # Default properties for new action
        properties = {
            "@type": "CreateAction",
            "instrument": id_ify(notebook.id),
            "actionStatus": {"@id": "http://schema.org/CompletedActionStatus"},
            "name": f"Run of notebook: {notebook.id}",
        }

    # Set endDate to latest file modification date
    properties["endDate"] = last_date

    # Add or update action
    action_new = crate.add(ContextEntity(crate, action_id, properties=properties))

    # Add input files to action
    for input in input_files:
        action_new.append_to("object", input)

    # Add output files to action
    for output in output_files:
        action_new.append_to("result", output)


def add_notebook(crate: ROCrate, notebook: Path) -> None:
    """Adds notebook information to an ROCRate.

    Parameters:
        crate: The rocrate to update.
        notebook: The notebook to add to the rocrate
    """
    # Get the crate root
    root = crate.get("./").properties()

    # Extract embedded metadata from the notebook
    notebook_metadata = extract_notebook_metadata(
        notebook,
        {
            "name": notebook.name,
            "author": [],
            "description": "",
            "object": [],
            "result": [],
        },
    )

    # Check if this notebook is already in the crate
    nb_current = crate.get(notebook.name)

    # If there's an entry for this notebook, we'll update it
    if nb_current:
        # Get current properties of the notebook
        properties = nb_current.properties()

        # If details have changed in notebook metadata they should be updated in the crate
        properties.update(
            {
                "name": notebook_metadata["name"],
                "description": notebook_metadata["description"],
                "author": [],
            }
        )
    else:
        # Default properties for a new notebook
        properties = {
            "@type": ["File", "SoftwareSourceCode"],
            "name": notebook_metadata["name"],
            "description": notebook_metadata["description"],
            "programmingLanguage": id_ify(PYTHON["@id"]),
            "encodingFormat": "application/x-ipynb+json",
            "conformsTo": id_ify(
                "https://purl.archive.org/textcommons/profile#Notebook"
            ),
            "codeRepository": root["url"],
        }

    # Add input files from 'object' property
    input_files = add_files(crate, notebook_metadata["object"])

    # Add output files from 'result' property
    output_files = add_files(crate, notebook_metadata["result"])

    # Add or update the notebook entity
    # (if there's an existing entry it will be overwritten)
    nb_new = crate.add_file(notebook, properties=properties)

    # Add a CreateAction that links the notebook run with the input and output files
    add_action(crate, nb_new, input_files, output_files)

    # If the notebook has author info, add people to crate
    if notebook_metadata["author"]:
        # Add people referenced in notebook metadata
        persons = add_people(crate, notebook_metadata["author"])

        # If people are not already attached to notebook, append them to the author property
        for person in persons:
            if person not in nb_current["author"]:
                nb_new.append_to("author", person)

    # Otherwise add crate root authors to notebook
    else:
        nb_new.append_to("author", root["author"])


def remove_deleted_files(crate: ROCrate) -> None:
    """
    Loops through File entities checking to see if they exist in local filesystem.
    If they don't then they're removed from the crate.
    """
    file_ids = []
    for action in crate.get_by_type("CreateAction"):
        for file_type in ["object", "result"]:
            try:
                file_ids += [o["@id"] for o in action.properties()[file_type]]
            except KeyError:
                pass

    # Loop through File entities
    for f in crate.get_by_type("File"):
        # If they don't exist and they're not urls, then delete
        if not Path(f.id).exists() and not f.id.startswith("http"):
            crate.delete(f)
        # If they're not referenced in CreateActions then delete
        if f.id not in file_ids and not f.id.endswith(".ipynb"):
            crate.delete(f)



def remove_unreferenced_authors(crate: ROCrate) -> None:
    """
    Compares the current Person entities with those referenced by the "author" property.
    Removes Person entities that are not authors.
    """
    # Get authors from root
    authors = crate.get("./")["author"]

    # Loop through all File entities, extracting authors
    for file_ in crate.get_by_type("File"):
        try:
            authors += file_["author"]
        except KeyError:
            pass
    # Loop though Person entities checking against authors
    for person in crate.get_by_type("Person"):
        # If Person is not an author, delete them
        if not person in authors:
            crate.delete(person)


def add_update_action(crate: ROCrate, version: str) -> None:
    """
    Adds an UpdateAction to the crate when the repo version is updated.
    """
    # Create an id for the action using the version number
    action_id = f"create_version_{version.replace('.', '_')}"

    # Set basic properties for action
    properties = {
        "@type": "UpdateAction",
        "endDate": datetime.datetime.now().strftime("%Y-%m-%d"),
        "name": f"Create version {version}",
        "actionStatus": {"@id": "http://schema.org/CompletedActionStatus"},
    }

    # Create entity
    crate.add(ContextEntity(crate, action_id, properties=properties))


def add_context_entity(crate: ROCrate, entity: Dict) -> None:
    """
    Adds a ContextEntity to the crate.

    Parameters:
        crate: the current ROCrate
        entity: A JSONLD ready dict containing "@id" and "@type" values
    """
    crate.add(ContextEntity(crate, entity["@id"], properties=entity))


def update_crate(version: str, notebooks: List[Path]) -> None:
    """Creates a parent crate in the supplied directory.

    Parameters:
        version: The version of the repository
        notebooks: The notebooks to include in the crate
    """
    # Load existing crate from cwd
    crate = ROCrate(source="./")

    # If this is a new version, change version number and add UpdateAction
    if version:
        crate.update_jsonld(
            {
                "@id": "./",
                "version": version,
                "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
            }
        )
        add_update_action(crate, version)

    # Add licence to root
    crate.license = id_ify(DEFAULT_LICENCE["@id"])
    add_context_entity(crate, DEFAULT_LICENCE)

    # Add licence to metadata
    crate.update_jsonld(
        {
            "@id": "ro-crate-metadata.json",
            "license": id_ify(METADATA_LICENCE["@id"]),
        }
    )
    add_context_entity(crate, METADATA_LICENCE)

    # Add Python for programming language
    add_context_entity(crate, PYTHON)

    # Process notebooks
    for notebook in notebooks:
        add_notebook(crate, notebook)

    # Remove files from crate if they're no longer in the repo
    remove_deleted_files(crate)

    # Remove authors from crate if they're not referenced by any entities
    remove_unreferenced_authors(crate)

    # Save the crate
    crate.write(".")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", type=str, help="New version number", required=False
    )
    args = parser.parse_args()
    main(args.version)
