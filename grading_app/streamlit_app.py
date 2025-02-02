import streamlit as st
import os
from typing import Dict
import tempfile
from grading_app.input.file_processor import FileProcessor
from grading_app.grading.schema_loader import load_grading_schema
from grading_app.models.ai_models import AIGrader, ConsensusGrader
from grading_app.grading.grader import AssignmentGrader

def initialize_grading_system(api_key: str) -> AssignmentGrader:
    """Initialize the grading system with the provided API key."""
    os.environ["OPENAI_API_KEY"] = api_key
    
    models = [
        AIGrader(model_name="gpt-4"),
        AIGrader(model_name="gpt-3.5-turbo"),
    ]
    consensus_grader = ConsensusGrader(models)
    return AssignmentGrader(consensus_grader)

def main():
    st.title("Assignment Grading System")
    
    # API Key Input (with secure handling)
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
        st.session_state.grader = None
    
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.openai_api_key,
            help="Enter your OpenAI API key here"
        )
        
        if api_key != st.session_state.openai_api_key:
            st.session_state.openai_api_key = api_key
            if api_key:
                try:
                    st.session_state.grader = initialize_grading_system(api_key)
                    st.success("API key configured successfully!")
                except Exception as e:
                    st.error(f"Error configuring API key: {str(e)}")
                    st.session_state.grader = None
    
    if not st.session_state.openai_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        return
    
    # File Upload Section
    st.header("Upload Assignments")
    uploaded_file = st.file_uploader(
        "Upload ZIP file containing assignments",
        type=["zip"],
        help="Upload a ZIP file containing the assignments to grade"
    )
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            zip_path = tmp_file.name
        
        try:
            # Process the uploaded file
            processor = FileProcessor()
            contents = processor.extract_from_zip(zip_path)
            
            # Display file contents and grade each submission
            st.header("Grading Results")
            
            for filename, content in contents.items():
                with st.expander(f"Assignment: {filename}"):
                    st.text_area("Content", content, height=200)
                    
                    if st.button(f"Grade {filename}"):
                        with st.spinner("Grading submission..."):
                            try:
                                # Load schema (using assignment_id=1 for demo)
                                schema = load_grading_schema("1")
                                
                                # Grade the submission
                                grade_result = st.session_state.grader.grade_assignment(
                                    content,
                                    schema
                                )
                                
                                # Display results
                                st.subheader("Grading Results")
                                st.metric("Total Points", f"{grade_result.total_points:.1f}/100")
                                st.metric("Confidence Score", f"{grade_result.overall_confidence:.2f}")
                                
                                if grade_result.needs_review:
                                    st.warning("This submission needs manual review")
                                
                                # Display individual criterion grades
                                st.subheader("Detailed Breakdown")
                                for criterion_name, grade in grade_result.criterion_grades.items():
                                    with st.expander(f"Criterion: {criterion_name}"):
                                        st.write(f"Points: {grade.points:.1f}")
                                        st.write(f"Confidence: {grade.confidence:.2f}")
                                        st.write("Explanation:", grade.explanation)
                                
                            except Exception as e:
                                st.error(f"Error grading submission: {str(e)}")
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
        finally:
            # Cleanup temporary file
            os.unlink(zip_path)
    
    # Display statistics if available
    if hasattr(st.session_state, 'graded_count'):
        st.sidebar.header("Statistics")
        st.sidebar.metric("Assignments Graded", st.session_state.graded_count)

if __name__ == "__main__":
    main() 