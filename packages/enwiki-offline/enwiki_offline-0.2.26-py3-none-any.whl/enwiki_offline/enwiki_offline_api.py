# -*- coding: utf-8 -*-
""" Parse the EnWiki all-titles File """


from functools import lru_cache
from typing import List, Optional

from baseblock import BaseObject, FileIO


class EnwikiOfflineAPI(BaseObject):

    def __init__(self):
        """ Change Log

        Created:
            9-Apr-2024
            craigtrim@gmail.com
            *   https://github.com/craigtrim/enwiki-offline/issues/1
        """
        BaseObject.__init__(self, __name__)
        self._output_path = FileIO.join_cwd('resources/enwiki')
        FileIO.exists_or_error(self._output_path)

    @lru_cache(maxsize=5192)
    def _get_file(self, entity: str) -> Optional[dict]:

        ch_path = FileIO.join(self._output_path, entity[0], entity[:2])
        if not FileIO.exists(ch_path):
            return None

        file_path = FileIO.join(ch_path, f"{entity[:3]}.json")
        if not FileIO.exists(file_path):
            return None

        return FileIO.read_json(file_path)

    @lru_cache(maxsize=2048, typed=False)
    def exists(self, entity: str) -> bool:
        """
        Checks if a Wikipedia entry exists for the specified entity by performing
        a case-insensitive search within a predefined file or database. This method
        is designed to identify exact matches only; synonyms, partial matches, and
        fuzzy searches are not supported. The search is strictly limited to entities
        that exactly match the provided string, disregarding any case differences.

        The method first processes the input entity by converting it to lowercase
        and stripping any leading or trailing whitespace to standardize the input
        for comparison. It then performs the existence check based on this processed
        entity string.

        Parameters:
        - entity (str): The name of the entity for which the Wikipedia entry existence
        check is to be performed. The search is case-insensitive, but exact matching
        is required.

        Returns:
        - bool: Returns True if an exact match for the Wikipedia entry is found; otherwise,
        returns False. The method also returns False if the processed entity string
        is less than 4 characters long, under the assumption that valid Wikipedia entries
        are unlikely to be represented by such short strings.
        """
        entity = entity.lower().strip()
        if len(entity) < 4:
            return False

        return entity in self._get_file(entity=entity)

    @lru_cache(maxsize=2048, typed=False)
    def is_ambiguous(self, entity: str) -> bool:
        """
        Determines if the specified entity is associated with multiple Wikipedia entries,
        indicating that the term is ambiguous. This method relies on an initial check
        to ascertain the existence of at least one Wikipedia entry for the entity. If such
        an entry exists, it further checks whether the number of entries exceeds one,
        which would classify the entity as ambiguous.

        The ambiguity check is based on the assumption that if multiple entries are
        associated with the same term, users or automated processes may require additional
        context or disambiguation to select the appropriate entry.

        Parameters:
        - entity (str): The name of the entity to check for ambiguity. This entity is
        checked against a collection of Wikipedia entries to determine if multiple
        entries exist for the same term.

        Returns:
        - bool: Returns True if the entity is associated with multiple Wikipedia entries,
        indicating ambiguity. If the entity does not exist or is associated with a single
        entry only, the method returns False.
        """

        if self.exists(entity):
            entity = entity.lower().strip()
            return len(self._get_file(entity=entity)[entity]) > 1

        return False

    @lru_cache(maxsize=2048, typed=False)
    def titles(self, entity: str) -> Optional[List[str]]:
        """
        Retrieves all Wikipedia titles associated with the given entity and formats
        them as fully qualified URLs to their respective Wikipedia pages. If the
        entity does not exist (i.e., no Wikipedia entry can be found for the given
        term), the method returns None.

        This method first checks for the existence of the entity in Wikipedia. If
        the entity is found, it retrieves the list of titles associated with this
        entity. Each title is then transformed into a URL pointing to the Wikipedia
        page for that title. The transformation involves replacing spaces in the
        title with underscores (as is standard in Wikipedia URLs) and prefixing the
        title with the base URL for English Wikipedia pages.

        Parameters:
        - entity (str): The name of the entity for which Wikipedia titles are to be
        retrieved. This is a string representing the term or name used to look up
        Wikipedia entries.

        Returns:
        - Optional[List[str]]: A list of strings, each a fully qualified URL to a
        Wikipedia page associated with the entity. If no entries are found for the
        entity, the method returns None.
        """

        if not self.exists(entity):
            return None

        entity = entity.lower().strip()
        values: List[str] = self._get_file(entity=entity)[entity]
        return [
            f"https://en.wikipedia.org/wiki/{value.replace(' ', '_')}"
            for value in values
        ]
