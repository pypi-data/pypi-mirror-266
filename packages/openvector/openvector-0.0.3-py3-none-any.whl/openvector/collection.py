from .query_result import QueryResult

class Collection:
    def __init__(self, name: str):
        self._name = name
        self._documents = []

    def add(self, documents: list):
        self._documents = documents

    def query(self, query_texts: list = None) -> QueryResult:
      """Performs a query and returns a QueryResult object.

      Args:
          query_texts: A list of query strings. If None, returns an empty result.

      Returns:
          QueryResult: An object containing the query results.
      """

      result = QueryResult()
      if query_texts is None:
          return result
      result.documents = ['Hello world', 'How are you?']
      return result
