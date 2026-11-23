from mycp.registry import SQLiteRecordStore,SQLiteConfig,RecordQuery,RecordInput,RecordReturn


def test_append_and_query(tmp_path):
    store = SQLiteRecordStore(SQLiteConfig((tmp_path / "t.db")))
    
    store.append(RecordInput("notes","default", {"text": "I prefer dark mode"}))
    store.append(RecordInput("notes","default",  {"text": "My cat is called Miso"}))
    
    all_notes = store.query(RecordQuery("notes","default"))
    assert [r.data["text"] for r in all_notes] == ["My cat is called Miso", "I prefer dark mode"]

    hits = store.query(RecordQuery("notes","default",  text="dark"))
    assert len(hits) == 1 and "dark mode" in hits[0].data["text"]


def test_users_and_collections_are_isolated(tmp_path):
    store = SQLiteRecordStore(SQLiteConfig((tmp_path / "t.db")))
    store.append(RecordInput("notes","alice", {"text": "secret"}))
    assert store.query(RecordQuery("notes", "bob" )) == []
    assert store.query(RecordQuery("other", "alice")) == []


def test_like_wildcards_are_escaped(tmp_path):
    store = SQLiteRecordStore(SQLiteConfig((tmp_path / "t.db")))
    store.append(RecordInput("notes","default",  {"text": "100% done"}))
    store.append(RecordInput("notes","default",  {"text": "nothing here"}))
    assert len(store.query(RecordQuery("notes","default", text="%"))) == 1


def test_concurrent_appends_from_many_threads(tmp_path):
    import threading

    store = SQLiteRecordStore(SQLiteConfig((tmp_path / "t.db")))
    errors = []

    def worker(n):
        try:
            for i in range(25):
                store.append(RecordInput("notes","default",  {"text": f"thread {n} note {i}"}))
        except Exception as exc:  # pragma: no cover - failure path
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    records = store.query(RecordQuery("notes","default",limit=200))
    assert len(records) == 200
    assert len({r.id for r in records}) == 200


def test_data_survives_close_and_reopen(tmp_path):
    path = SQLiteConfig((tmp_path / "t.db"))
    store = SQLiteRecordStore(path)
    store.append(RecordInput("notes","default",  {"text": "persisted"}))
    store.close()
    store.close()  # idempotent

    reopened = SQLiteRecordStore(path)
    assert reopened.query("notes","default")[0].data["text"] == "persisted"
    reopened.close()
