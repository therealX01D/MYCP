from mycp.registry import SQLiteRecordStore


def test_append_and_query(tmp_path):
    store = SQLiteRecordStore(tmp_path / "t.db")
    store.append("default", "notes", {"text": "I prefer dark mode"})
    store.append("default", "notes", {"text": "My cat is called Miso"})

    all_notes = store.query("default", "notes")
    assert [r.data["text"] for r in all_notes] == ["My cat is called Miso", "I prefer dark mode"]

    hits = store.query("default", "notes", text="dark")
    assert len(hits) == 1 and "dark mode" in hits[0].data["text"]


def test_users_and_collections_are_isolated(tmp_path):
    store = SQLiteRecordStore(tmp_path / "t.db")
    store.append("alice", "notes", {"text": "secret"})
    assert store.query("bob", "notes") == []
    assert store.query("alice", "other") == []


def test_like_wildcards_are_escaped(tmp_path):
    store = SQLiteRecordStore(tmp_path / "t.db")
    store.append("default", "notes", {"text": "100% done"})
    store.append("default", "notes", {"text": "nothing here"})
    assert len(store.query("default", "notes", text="%")) == 1


def test_concurrent_appends_from_many_threads(tmp_path):
    import threading

    store = SQLiteRecordStore(tmp_path / "t.db")
    errors = []

    def worker(n):
        try:
            for i in range(25):
                store.append("default", "notes", {"text": f"thread {n} note {i}"})
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    records = store.query("default", "notes", limit=200)
    assert len(records) == 200
    assert len({r.id for r in records}) == 200


def test_data_survives_close_and_reopen(tmp_path):
    path = tmp_path / "t.db"
    store = SQLiteRecordStore(path)
    store.append("default", "notes", {"text": "persisted"})
    store.close()
    store.close()  # idempotent

    reopened = SQLiteRecordStore(path)
    assert reopened.query("default", "notes")[0].data["text"] == "persisted"
    reopened.close()
