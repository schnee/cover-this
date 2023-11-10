from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx

def get_remote_ip() -> str:
    """Get remote ip."""

    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip

def _get_session():
    ctx = get_script_run_ctx()
    session_id = ctx.session_id
    return session_id

import streamlit as st

st.markdown("Title")
st.markdown(f"The remote ip is {get_remote_ip()}")
st.markdown(f"The Streamlit session id is {_get_session()}")