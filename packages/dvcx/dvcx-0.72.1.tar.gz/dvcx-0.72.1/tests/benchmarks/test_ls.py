def test_ls(bench_dvcx, tmp_dir, bucket):
    bench_dvcx("ls", bucket, "--aws-anon")
