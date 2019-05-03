# Scavenger
A Python full text search and indexing library

### Table of Contents

1. [Description](#description)

2. [Use Case](#use-case)


###  Description
Scavenger is a Python search library. It focuses on full text search and supports scoring through TF-IDF or BM25. The index is persistently stored in a SQLite DB and cached using Redis.

###  Use Case
Scavenger is best used for full text search in read heavy situations with small document collections. It precalculates the scores for every document word on commit and when loading the DB data onto Redis, making commits expensive but reading very fast.
