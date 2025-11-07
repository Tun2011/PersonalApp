import streamlit as st
import google.generativeai as genai
import time # Thêm thư viện này để tạo hiệu ứng gõ máy

# --- Cấu hình trang ---
st.set_page_config(
    page_title="Trợ lý Cá nhân",
    page_icon="🤖",
    layout="wide"
)

# --- Thanh bên (Sidebar) để nhập thông tin ---
st.sidebar.title("Cấu hình ⚙️")
st.sidebar.write("Nhập thông tin của bạn để bắt đầu.")

# Lấy API key
api_key = st.sidebar.text_input("Nhập Google API Key của bạn:", type="password")

# Lấy Tên người dùng
username = st.sidebar.text_input("Nhập tên của bạn:", "Người dùng")

# Chọn chức năng
app_mode = st.sidebar.selectbox("Chọn chức năng bạn muốn:",
                                ["Trang chủ", "Dịch thuật 📚", "Viết code 💻"])

# --- Xử lý chính ---

# 1. Chào mừng
st.title(f"Chào mừng, {username}! 👋")

# 2. Kiểm tra API Key và Cấu hình Model
if not api_key:
    st.warning("Vui lòng nhập API Key của bạn vào thanh bên trái để sử dụng các chức năng.")
    st.stop() # Dừng thực thi nếu chưa có key

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-lastest')
    st.sidebar.success("Đã kết nối với API Key!")
except Exception as e:
    st.sidebar.error(f"Lỗi kết nối API: {e}")
    st.stop()


# --- Hàm hiển thị hiệu ứng gõ máy ---
def stream_response(response_text):
    for word in response_text.split():
        yield word + " "
        time.sleep(0.05)

# 3. Chạy chức năng tương ứng
if app_mode == "Trang chủ":
    st.header("Đây là trang web tự động hóa của bạn.")
    st.write("Hãy chọn một chức năng ở thanh bên trái để bắt đầu.")
    st.image("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png", width=300)

# --- Chức năng Dịch thuật ---
elif app_mode == "Dịch thuật 📚":
    st.header("Chức năng Dịch thuật")

    col1, col2 = st.columns(2)
    with col1:
        text_to_translate = st.text_area("Nhập văn bản cần dịch:", height=200)
    with col2:
        target_language = st.text_input("Dịch sang ngôn ngữ:", "Tiếng Việt")

    if st.button("Bắt đầu dịch"):
        if text_to_translate:
            prompt = f"Dịch văn bản sau sang {target_language}. Chỉ trả về kết quả đã dịch, không thêm giải thích: {text_to_translate}"
            try:
                response = model.generate_content(prompt)
                st.subheader("Kết quả dịch:")
                # st.write(response.text) # Hiển thị ngay lập tức
                st.write_stream(stream_response(response.text)) # Hiệu ứng gõ máy
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
        else:
            st.warning("Vui lòng nhập văn bản cần dịch.")

# --- Chức năng Viết Code ---
elif app_mode == "Viết code 💻":
    st.header("Chức năng Viết Code")
    code_description = st.text_area("Mô tả code bạn muốn (ví dụ: 'viết hàm python kiểm tra số nguyên tố'):", height=150)
    
    if st.button("Tạo code"):
        if code_description:
            prompt = f"Viết một đoạn code (chỉ trả về code, không giải thích) cho yêu cầu sau: {code_description}"
            try:
                response = model.generate_content(prompt)
                st.subheader("Code được tạo:")
                st.code(response.text, language="python") # st.code để hiển thị code đẹp hơn
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")
        else:
            st.warning("Vui lòng mô tả code bạn muốn.")