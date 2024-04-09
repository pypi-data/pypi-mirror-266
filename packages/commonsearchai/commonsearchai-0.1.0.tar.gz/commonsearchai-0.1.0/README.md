# CommonSearchAI

package containing common function for using Azure Search AI

This package contains the following functions:

-   create_search_index this function create an index with the following SearchFields
    -   chunk_id
    -   parent_id
    -   chunk
    -   title
    -   vector

-   create_search_datasource this function create a datasource from a blob container

-   create_search_skillset this function create a skillset to manage a chunked file

-   create_search_indexer this function create an indexer to be launched using a blob
    datasource to fill the index

