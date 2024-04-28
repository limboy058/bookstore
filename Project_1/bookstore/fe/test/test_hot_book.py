from fe.bench.run import run_hot_one_test


def test_bench():
    try:
        run_hot_one_test
        pass
    except Exception as e:
        assert 200 == 100, "test_hot_book过程出现异常"
