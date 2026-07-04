from zoo_keeper.core import seeding


def test_same_root_same_sequence():
    a = seeding.RNGStreams(seeding.root_key("desk", "desk", 0, "0.1.0"))
    b = seeding.RNGStreams(seeding.root_key("desk", "desk", 0, "0.1.0"))
    assert [a.stream("dims").random() for _ in range(5)] == \
           [b.stream("dims").random() for _ in range(5)]


def test_streams_independent():
    s = seeding.RNGStreams("root")
    assert s.stream("dims").random() != s.stream("wear").random()


def test_stream_cached_not_reset():
    s = seeding.RNGStreams("root")
    first = s.stream("x").random()
    second = s.stream("x").random()
    assert first != second  # continues, doesn't restart


def test_seed_changes_everything():
    a = seeding.RNGStreams(seeding.root_key("p", "desk", 0, "0.1.0"))
    b = seeding.RNGStreams(seeding.root_key("p", "desk", 1, "0.1.0"))
    assert a.stream("dims").random() != b.stream("dims").random()


def test_short_hash_stable():
    assert seeding.short_hash("abc") == seeding.short_hash("abc")
    assert len(seeding.short_hash("abc")) == 6
