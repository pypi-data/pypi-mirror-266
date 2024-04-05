def test_version(bench_dvcx):
    bench_dvcx("--help", rounds=100)
