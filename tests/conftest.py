def pytest_addoption(parser):
    parser.addoption(
        "--rewrite-readme",
        action="store_true",
        default=False,
        help="Rewrite README on error",
    )
