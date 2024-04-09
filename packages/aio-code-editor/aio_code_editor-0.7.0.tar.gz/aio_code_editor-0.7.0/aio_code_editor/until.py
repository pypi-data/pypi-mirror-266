import streamlit as st

# Ngăn chặn việc thực thi mã nguy hiểm
black_list = ["os", "sys", "subprocess", "shutil", "importlib"]  
def check_code(codes):
    for line in codes.split('\n'):
        if 'import' in line:
            if any([True for x in black_list if x in line]):
                return False
   
    return True

def write_code(codes, file_name="st-test.py"):
    # save code to file
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(codes)
    