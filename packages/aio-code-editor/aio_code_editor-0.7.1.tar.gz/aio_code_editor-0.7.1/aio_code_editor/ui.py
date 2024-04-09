import streamlit as st
from code_editor import code_editor
from aio_code_editor.css import info_bar_input, info_bar_output, output_btns, input_btns
import subprocess
from aio_code_editor.until import check_code, write_code
import os
import sys
import importlib

environ = os.environ.copy()
environ['PYTHONIOENCODING'] = 'utf-8'

def side_bar():
    with st.sidebar:
        st.markdown("## :heartbeat: :heartbeat: Hướng dẫn  :heartbeat: :heartbeat:")
        st.markdown("1. Đặt tên file (không bắt buộc)")
        st.markdown("2. Viết mã Python vào ô bên dưới")
        st.markdown("3. Nhấn nút **Run** để thực thi mã")
        st.markdown("4. Kết quả sẽ hiển thị ở ô bên dưới")
        st.markdown("5. Bạn có thể tải file Python bằng cách nhấn vào nút **Save file**")
        
        file_name = st.text_input("Tên file:", "st_test.py")
        st.write("Chill chút nhỉ? ^^")
        st.audio("https://cdn.pixabay.com/audio/2023/01/10/audio_5f83ba4572.mp3", format="audio/mp3")
        st.audio("https://cdn.pixabay.com/audio/2023/04/30/audio_6b3a512606.mp3", format="audio/mp3")
        st.audio("https://ia800209.us.archive.org/12/items/ECHOSAXEND/ECHOSAXEND.mp3", format="audio/mp3")
        
        return file_name
    
def heading():
    col_1, col_2, col_3 = st.columns([0.2, 0.5, 0.4])
    with col_2:
        st.title("AIO Code Editor")
    with col_3:
        st.image("https://ia800202.us.archive.org/30/items/shark_202403/shark.png", width=150)

def codes_box(sample_code, min_raw=5, max_raw=20, type_out="python", file_name="st_test.py"):
    response_dict = code_editor(sample_code, buttons=input_btns, height=[min_raw, max_raw], info= info_bar_input)
    codes = response_dict["text"]
    # get lines number of sample_code
    line_nums = len(sample_code.split('\n'))    
    res_type = response_dict["type"]
    # st.write(sample_code)
    if type_out=="plot":
        write_code(sample_code, file_name)
    return codes, res_type, response_dict, line_nums

def output_box(response_dict, results, min_raw=5, max_raw=20, err=0):
    num_rows = response_dict['cursor']['row']
    if num_rows<min_raw:
        code_editor(results, buttons=output_btns, height= [min_raw, min_raw], info=info_bar_output)
    elif num_rows>=max_raw:
        code_editor(results, buttons=output_btns, height= [max_raw, max_raw] , info=info_bar_output)
             
    elif num_rows>=min_raw and num_rows<=max_raw:
        code_editor(results, buttons=output_btns, height= [int(num_rows)+1-err, max_raw], info=info_bar_output)

def run_plot(file_name, codes, res_type, download=False):
    if check_code(codes):  
        if res_type == "":
            # Hiển thị button đownload file
            if download:
                st.download_button(
                    label="Save file",
                    data=open(file_name, 'rb').read(),
                    file_name= file_name,
                    mime="text/plain")
            # Thực thi file Python và lấy đầu ra và lỗi (nếu có)
            module_name  = file_name.split(".")[0]
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
        elif res_type == "submit":
            # Lưu mã vào file Python
            write_code(codes, file_name)
            # Hiển thị button đownload file
            if download:
                st.download_button(
                    label="Save file",
                    data=open(file_name, 'rb').read(),
                    file_name= file_name,
                    mime="text/plain")
            # Thực thi file Python và lấy đầu ra và lỗi (nếu có)
            module_name  = file_name.split(".")[0]
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])
            else:
                importlib.import_module(module_name)
        
                
def run_code(file_name, codes, res_type, response_dict, download=False):
    if check_code(codes):     
        if res_type == "submit":
            # Lưu mã vào file Python
            write_code(codes, file_name)
            # Hiển thị button đownload file
            if download:
                st.download_button(
                    label="Save file",
                    data=open(file_name, 'rb').read(),
                    file_name= file_name,
                    mime="text/plain")
            
            # Thực thi file Python và lấy đầu ra và lỗi (nếu có)
            result = subprocess.run(['python', file_name], encoding="utf-8", env=environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Hiển thị kết quả trong output_box
            if result.stderr == "":
                output_box(response_dict, result.stdout)
            elif result.stdout == "":
                output_box(response_dict, result.stderr, err=1)
            else:
                output_box(response_dict, f"{result.stdout}\n{result.stderr}", err=1)
    else:
        st.error("Mã của bạn có thể nguy hiểm, vui lòng kiểm tra lại!")

def code_io(sample=''' ''', l=1, r=1, min_raw=5, max_raw=20, download=False, key=None, type_out="python" ):
    col1, col2 = st.columns([l, r])
    with col1:
        if type_out == "plot":
            codes, res_type, response_dict, line_nums = codes_box(sample, min_raw, max_raw, type_out="plot",file_name="st_test.py")
        else:
            codes, res_type, response_dict, line_nums = codes_box(sample, min_raw, max_raw)

    with col2:
        if res_type=="" and type_out=="python":
            if line_nums<min_raw:
                line_nums = min_raw
            elif line_nums>=max_raw:
                line_nums = max_raw
            if type_out=="plot":
                run_plot(file_name="st_test.py", codes=codes, res_type=res_type, download=download)
            else:
                code_editor("", buttons=output_btns, height= [line_nums, max_raw] , info=info_bar_output, key=key)

        else:
            if type_out=="python":
                run_code(file_name="st_test.py", codes=codes, res_type=res_type, response_dict=response_dict, download=download)
            elif type_out=="plot":
                run_plot(file_name="st_test.py", codes=codes, res_type=res_type, download=download)