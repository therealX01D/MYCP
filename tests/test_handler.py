from mycp.handler import current_actions
from mycp.handler.methods import append_record
from mycp.registry import RecordQuery, SQLiteConfig, SQLiteRecordStore


def test_append_record_action_uses_supplied_store(tmp_path):
    store = SQLiteRecordStore(SQLiteConfig(filepath=tmp_path / "actions.db"))
    try:
        action = current_actions["append_record"]
        assert action is append_record
        record = action("workouts", {"minutes": 30}, store)
        assert record.collection == "workouts"
        assert record.user_id == "default"
        assert record.data == {"minutes": 30}
        assert store.query(RecordQuery("workouts", "default")) == [record]
    finally:
        store.close()
