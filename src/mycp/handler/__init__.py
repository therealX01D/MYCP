from .methods import append_record

# Unimplemented handler kinds have no callable yet.
current_actions = {
    "append_record": append_record,
    "query_records": None,
    "update_record": None,
    "http_call": None,
    "prompt_template": None,
}
