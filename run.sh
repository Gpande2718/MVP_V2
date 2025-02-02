#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
cd grading_app
streamlit run streamlit_app.py 