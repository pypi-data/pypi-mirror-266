import os
import streamlit.components.v1 as components

import streamlit as st

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component(
        "input_field_component",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("input_field_component", path=build_dir)

def input_field(text, key=None):
    """Create a new instance of the custom input field component.

    Parameters
    ----------
    text: str
        The sentence or phrase with [G_A_P] tokens indicating where the input fields should be.
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    list of str
        A list containing the user inputs for each custom-styled text input field.
    """
    # Adjusting the 'default' argument to reflect the change in return value structure
    user_inputs = _component_func(text=text, key=key, default=[])

    return user_inputs

with st.form("my_f"):

    s = input_field("I love [G_A_P] [G_A_P]!")
    if st.form_submit_button("Submit"):
        st.write(s)