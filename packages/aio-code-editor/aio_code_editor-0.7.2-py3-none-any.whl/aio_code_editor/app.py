import streamlit as st
from code_editor import code_editor
import os
from aio_code_editor.ui import side_bar, heading, codes_box, run_code
    
    
def run():
    # check and install numpy
    try:
        import numpy as np
    
    except ImportError:
        os.system("pip install numpy")
    # UI
    file_name = side_bar()
    heading()
    sample_code = """#Bạn viết code ở đây nhé!\nprint("AI VIET NAM XIN CHÀO!")\n"""
    codes, type = codes_box(sample_code)
    run_code(file_name, codes, type)
    
if __name__ == "__main__":
    run()