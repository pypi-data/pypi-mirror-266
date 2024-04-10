# enwiki-offline

## Functions
```python
def exists(entity: str) -> bool
```
Performs a case insensitive search and returns True if a Wikipedia entry exists for the input entity.  Synonyms, Partial and Fuzzy searches are not supported.  Exact matches only.

```python
def is_ambiguous(entity: str) -> bool
```
Returns True if multiple Wikipedia entries exist for this term.

```python
def titles(entity: str) -> Optional[List[str]]
```
Returns all Wikipedia Titles for this input entity.

## Use Existing Data
Scroll down to the `DVC` section and use the `dvc pull` command to access the data.

## Parsing Wikipedia Titles
The latest enwiki file can be downloaded from https://dumps.wikimedia.org/enwiki/

You only need to do this if
1. You don't want to refresh from DVC
2. You have a different version of the enwiki file
```sh
poetry run python drivers/parse_enwiki_all_titles.py "/path/to/file/enwiki-20240301-all-titles"
```

## DVC (Data Version Control)

### Initialize DVC and Configure S3 Remote
In your project root, initialize DVC if you haven't already, and configure your S3 bucket as the remote storage. Replace `enwikioffline` with your actual S3 bucket name if it's different. Run:

```shell
dvc init
dvc remote add -d myremote s3://enwikioffline
dvc remote modify myremote profile enwiki_offline
```

This setup:
- Initializes DVC in your project.
- Adds your S3 bucket as the default remote storage.
- Configures DVC to use the `enwiki_offline` AWS profile for S3 operations.

### Track and Push Data with DVC
To track the resources folder and push it to S3, execute:
```shell
dvc add resources
git add resources.dvc .gitignore
git commit -m "Track resources folder with DVC"
dvc push
```

This process:
- Tracks the `resources` folder with DVC, creating a .dvc file.
- Commits the DVC files to Git.
- Pushes the data to your S3 bucket using the configured AWS profile.

### Pull Data with DVC
To retrieve the data managed by DVC, use:
```sh
dvc pull
```
This command pulls the data from S3 into your local `resources` folder, based on the current DVC setup and the latest `resources.dvc` file in your repository.
