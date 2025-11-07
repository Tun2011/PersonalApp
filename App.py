# --- 1. Import các thư viện cần thiết ---
import streamlit as st
import google.generativeai as genai
import time

# Thêm thư viện để đọc PDF
try:
    from PyPDF2 import PdfReader
except ImportError:
    print("Vui lòng cài PyPDF2: py -m pip install PyPDF2")

# --- 2. Cấu hình trang (Phải là lệnh đầu tiên của Streamlit) ---
st.set_page_config(
    page_title="Trợ lý Cá nhân",
    page_icon="🤖",
    layout="wide"
)

# --- 3. Các hàm trợ giúp ---

def stream_response(response_text):
    """Hiển thị văn bản với hiệu ứng gõ máy."""
    for word in response_text.split():
        yield word + " "
        time.sleep(0.05)

def get_pdf_text(pdf_docs_list):
    """Trích xuất văn bản từ danh sách các tệp PDF được tải lên."""
    text = ""
    for pdf in pdf_docs_list:
        try:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text
        except Exception as e:
            st.error(f"Lỗi khi đọc tệp PDF: {e}")
    return text

# --- 4. Giao diện Thanh bên (Sidebar) ---
st.sidebar.title("Cấu hình & Chức năng ⚙️")

# <--- ĐÂY LÀ CODE CŨ ĐÃ KHÔI PHỤC ---
# Yêu cầu API Key ở thanh bên
api_key = st.sidebar.text_input("Nhập Google API Key của bạn:", type="password")

# Chọn chức năng
app_mode = st.sidebar.selectbox("Chọn chức năng bạn muốn:",
                                ["Trang chủ", "Dịch thuật & Code 📚", "Viết code (Đơn giản) 💻"])


# --- 5. Cấu hình API và Model ---

# Đặt tiêu đề chính
st.title("Trợ lý AI Tự động hóa 🚀")

# Kiểm tra API Key (được nhập từ sidebar)
if not api_key:
    st.warning("Vui lòng nhập API Key của bạn vào thanh bên trái để bắt đầu.")
    st.stop() # Dừng thực thi nếu chưa có key

# Cấu hình model
try:
    genai.configure(api_key=api_key)
    # Sử dụng model bạn đã chọn
    model = genai.GenerativeModel('gemini-flash-latest') 
    st.sidebar.success("Đã kết nối với API Key!")
except Exception as e:
    st.sidebar.error(f"Lỗi kết nối API: {e}")
    st.stop()

# --- 6. Logic xử lý cho từng trang ---

# --- Trang chủ ---
if app_mode == "Trang chủ":
    st.header("Chào mừng đến với Trợ lý AI của bạn.")
    st.write("Hãy chọn một chức năng ở thanh bên trái để bắt đầu.")
    st.image("https.streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=400)

# --- Chức năng Dịch thuật & Code (Nâng cao) ---
elif app_mode == "Dịch thuật & Code 📚":
    st.header("Chức năng Dịch thuật (Văn bản & PDF)")
    st.write("Bạn có thể dịch văn bản gõ tay HOẶC tải lên tệp PDF.")

    if "pdf_translated" not in st.session_state:
        st.session_state.pdf_translated = False
    if "original_pdf_text" not in st.session_state:
        st.session_state.original_pdf_text = ""

    col1, col2 = st.columns(2)
    with col1:
        text_to_translate = st.text_area("Nhập văn bản cần dịch:", height=200)
    with col2:
        uploaded_pdf = st.file_uploader("Hoặc tải lên tệp PDF để dịch:", type="pdf")
    
    target_language = st.text_input("Dịch sang ngôn ngữ:", "Tiếng Việt")

    if st.button("Bắt đầu dịch"):
        st.session_state.pdf_translated = False
        st.session_state.original_pdf_text = ""
        
        input_text_for_translation = ""
        is_pdf_upload = False

        if uploaded_pdf is not None:
            with st.spinner("Đang đọc tệp PDF..."):
                raw_text = get_pdf_text([uploaded_pdf])
            
            if not raw_text:
                st.error("Không thể trích xuất văn bản từ tệp PDF này. Tệp có thể là hình ảnh.")
                st.stop()
                
            input_text_for_translation = raw_text
            st.session_state.original_pdf_text = raw_text
            is_pdf_upload = True
        
        elif text_to_translate:
            input_text_for_translation = text_to_translate
        
        else:
            st.warning("Vui lòng nhập văn bản hoặc tải lên tệp PDF.")
            st.stop()

        with st.spinner(f"Đang dịch sang {target_language}..."):
            prompt = f"Dịch văn bản sau đây sang {target_language}. Chỉ trả về kết quả đã dịch, không thêm giải thích: \n\n{input_text_for_translation}"
            try:
                response = model.generate_content(prompt)
                st.subheader("Kết quả dịch:")
                st.write_stream(stream_response(response.text))
                
                if is_pdf_upload:
                    st.session_state.pdf_translated = True
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra khi dịch: {e}")

    if st.session_state.get("pdf_translated", False):
        st.divider()
        st.subheader("Tác vụ tiếp theo 🚀")
        st.write("AI đã ghi nhớ nội dung tệp PDF gốc bạn vừa tải lên.")
        
        if st.button("Bạn có muốn viết code theo yêu cầu của file PDF này không?"):
            original_text = st.session_state.original_pdf_text
            
            with st.spinner("Đang phân tích PDF và viết code..."):
                code_prompt = f"""
                Dựa trên các yêu cầu kỹ thuật trong tài liệu sau đây, hãy viết một đoạn code mẫu. 
                Chỉ trả về các khối code, không cần giải thích dài dòng.

                Tài liệu:
                ---
                {original_text}
                ---
                """
                try:
                    code_response = model.generate_content(code_prompt)
                    st.subheader("Code được tạo từ PDF:")
                    st.code(code_response.text) 
                except Exception as e:
                    st.error(f"Có lỗi xảy ra khi tạo code: {e}")

# --- Chức năng Viết Code (Đơn giản) ---
elif app_mode == "Viết code (Đơn giản) 💻":
    st.header("Chức năng Viết Code")
    code_description = st.text_area("Mô tả code bạn muốn (ví dụ: 'viết hàm python kiểm tra số nguyên tố'):", height=150)
    
    if st.button("Tạo code"):
        if code_description:
            with st.spinner("Đang viết code..."):
                prompt = f"Viết một đoạn code (chỉ trả về code, không giải thích) cho yêu cầu sau: {code_description}"
                try:
                    response = model.generate_content(prompt)
                    st.subheader("Code được tạo:")
                    st.code(response.text)
                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")
        else:
            st.warning("Vui lòng mô tả code bạn muốn.")