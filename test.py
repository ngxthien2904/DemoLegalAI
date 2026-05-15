import time
import random
from playwright.sync_api import sync_playwright

# --- CẤU HÌNH THÔNG SỐ TRANG VBPL ---
# Đường dẫn danh mục văn bản mới nhất (hoặc đường dẫn tìm kiếm của bạn)
TARGET_URL = "https://vbpl.vn" 

# Các Selector đặc thù dựa trên cấu trúc giao diện của vbpl.vn
ROW_SELECTOR = "ul.lItem -> li, table.table-vbpq tr" # Định vị dòng chứa văn bản
# Do vbpl.vn thường dùng cấu trúc danh sách hoặc bảng tùy theo trang, 
# Dưới đây là cấu trúc bóc tách chuẩn cho trang tìm kiếm/danh mục của VBPL:
LIST_ITEM_SELECTOR = "div.vbpq-item, ul.lItem > li" 
# --------------------------------------------

def get_random_user_agent():
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
    ]
    return random.choice(ua_list)

def extract_vbpl_data(page):
    """Hàm trích xuất dữ liệu văn bản từ trang hiện tại"""
    # Đợi danh sách văn bản hiển thị trên giao diện
    page.wait_for_selector(".vbpq-item, .lItem, .table", timeout=15000)
    
    # Tìm tất cả các khối văn bản pháp luật trên trang
    items = page.locator("div.vbpq-item").all()
    if not items:
        # Thử với cấu trúc bảng hoặc danh sách dạng cũ nếu cấu trúc trang thay đổi
        items = page.locator("ul.lItem > li").all()

    print(f"[+] Tìm thấy {len(items)} văn bản trên trang này.")
    
    for index, item in enumerate(items, 1):
        try:
            # 1. Lấy tiêu đề / Trích yếu văn bản (thường nằm trong thẻ a)
            title_element = item.locator("p.title a, h2.title a, a").first
            title = title_element.inner_text().strip()
            link = title_element.get_attribute("href")
            full_link = f"https://vbpl.vn{link}" if link and link.startswith("/") else link

            # 2. Lấy các thông tin thuộc tính (Số ký hiệu, Ngày ban hành...)
            # VBPL thường để thông tin này trong các thẻ p hoặc span bên dưới tiêu đề
            attributes = item.locator("p.attributes, div.description").inner_text().strip()
            
            print(f"\n--- Văn bản {index} ---")
            print(f"Tiêu đề: {title}")
            print(f"Thuộc tính: {attributes}")
            print(f"Liên kết chi tiết: {full_link}")
            
        except Exception as e:
            continue

def run_vbpl_scraper():
    with sync_playwright() as p:
        # Khởi chạy trình duyệt thật (Đặt headless=False để kiểm tra quá trình chạy trực quan)
        browser = p.chromium.launch(headless=False) 
        
        context = browser.new_context(
            user_agent=get_random_user_agent(),
            viewport={"width": 1366, "height": 768},
            locale="vi-VN"
        )
        
        page = context.new_page()
        
        try:
            print(f"[*] Đang kết nối tới {TARGET_URL}...")
            page.goto(TARGET_URL, timeout=60000, wait_until="networkidle")
            
            # Nếu trang chủ yêu cầu nhấn vào danh mục "Văn bản mới" hoặc "Tìm kiếm"
            # Bạn có thể điều hướng trực tiếp bằng click hoặc giữ nguyên URL mục tiêu
            time.sleep(3) 
            
            print("[*] Đang tiến hành cào dữ liệu trang đầu tiên...")
            extract_vbpl_data(page)
            
            # --- XỬ LÝ PHÂN TRANG ĐỘNG (NEXT PAGE) ---
            # Tìm nút chuyển trang (thường có chữ 'Tiếp', '>' hoặc class 'next')
            next_button = page.locator("a:has-text('Tiếp'), a.next, li.next a").first
            
            if next_button.is_visible():
                print("[*] Phát hiện nút chuyển trang. Đang chuyển sang Trang 2...")
                next_button.click()
                
                # Chờ đợi trang mới tải xong hoàn toàn dữ liệu động
                page.wait_for_load_state("networkidle")
                time.sleep(random.uniform(2, 4))
                
                print("[*] Đang cào dữ liệu Trang 2...")
                extract_vbpl_data(page)
            else:
                print("[-] Không tìm thấy nút chuyển trang hoặc chỉ có 1 trang duy nhất.")
                
        except Exception as e:
            print(f"[!] Lỗi: {e}")
            page.screenshot(path="vbpl_error.png")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run_vbpl_scraper()