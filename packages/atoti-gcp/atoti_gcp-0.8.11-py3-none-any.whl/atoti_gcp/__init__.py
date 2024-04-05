"""Plugin to load CSV and parquet files from Google Cloud Storage into Atoti tables.

This package is required to load files with GCP paths starting with ``gs://``.

Authentication is handled by the underlying GCS SDK for Java library.
Automatic credentials retrieval is explained in `their documentation <https://cloud.google.com/docs/authentication/production#automatically>`__.

Example:
    >>> table = session.read_csv("gs://atoti-anonymous/city.csv", keys=["city"])
    >>> table.head().sort_index()
            value
    city
    London  200.0
    Paris   100.0

"""
