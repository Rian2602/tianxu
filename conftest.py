"""Root conftest — exclude non-test directories from pytest collection."""
collect_ignore_glob = ["claude/*", ".agents/*", ".opencode/*"]
