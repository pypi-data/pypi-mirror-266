from textwrap import dedent


def test_compile_query_script(catalog):
    script = dedent(
        """
        from dvcx.query import C, DatasetQuery, asUDF
        DatasetQuery("s3://bkt/dir1")
        """
    ).strip()
    result = catalog.compile_query_script(script)
    expected = dedent(
        """
        from dvcx.query import C, DatasetQuery, asUDF
        import dvcx.query.dataset
        dvcx.query.dataset.query_wrapper_print(
        DatasetQuery('s3://bkt/dir1'))
        """
    ).strip()
    assert result == expected


def test_compile_query_script_with_save(cloud_test_catalog):
    script = dedent(
        """
        from dvcx.query import C, DatasetQuery, asUDF
        DatasetQuery("s3://bkt/dir1")
        """
    ).strip()
    result = cloud_test_catalog.catalog.compile_query_script(script, save=True)
    expected = dedent(
        """
        from dvcx.query import C, DatasetQuery, asUDF
        import dvcx.query.dataset
        dvcx.query.dataset.query_wrapper_save(
        DatasetQuery('s3://bkt/dir1'))
        """
    ).strip()
    assert result == expected
