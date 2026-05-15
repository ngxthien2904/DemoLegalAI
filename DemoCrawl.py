from playwright.sync_api import sync_playwright
import time

def crawl_vbpl_documents(keyword):
    print(f"Đang khởi động trình duyệt để tìm kiếm: {keyword}...")
    
    # Khởi tạo Playwright
    with sync_playwright() as p:
        # Mở trình duyệt Chromium. Để headless=False để nhìn thấy trình duyệt đang thao tác
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        try:
            # 1. Truy cập trang chủ VBPL
            page.goto("https://vbpl.vn/", timeout=60000)
            print("Đã truy cập thành công vbpl.vn")
            
            # 2 & 3. Tìm ô tìm kiếm, nhập từ khóa và ấn Enter
            # LƯU Ý MỎNG: Hãy sửa "Tìm kiếm..." thành đúng dòng chữ mờ đang hiển thị trong ô tìm kiếm trên web.
            # Ví dụ: "Nhập từ khóa...", "Tìm kiếm văn bản...", v.v.
            placeholder_text = "Nhập từ khóa tìm kiếm..." 
            
            page.get_by_placeholder(placeholder_text).fill(keyword)
            page.get_by_placeholder(placeholder_text).press("Enter")
            
            print("Đã gửi yêu cầu tìm kiếm, đang chờ trang kết quả tải...")
            
            # 4. Chờ kết quả tải xong
            # Chú ý: Ở phần trước chúng ta đang làm dở bước lấy selector cho danh sách này
            page.wait_for_selector(".list-law", timeout=30000) 
            print("Đã tải xong trang kết quả.")
            
            # 5. Trích xuất dữ liệu
            # Chú ý: Tương tự, phần này cũng cần thay bằng selector thực tế của thẻ <a> chứa tiêu đề
            documents = page.query_selector_all(".title-law a") 
            
            print(f"\nTìm thấy {len(documents)} văn bản:")
            for doc in documents:
                title = doc.inner_text().strip()
                link = doc.get_attribute("href")
                
                # Xử lý linh hoạt trường hợp link đã có sẵn https:// hoặc chỉ là link tương đối (/)
                full_link = f"https://vbpl.vn{link}" if link and link.startswith("/") else link
                
                print("-" * 40)
                print(f"Tiêu đề: {title}")
                print(f"Link: {full_link}")
                
            # Nghỉ 2 giây để tránh bị chặn do thao tác quá nhanh
            time.sleep(2)

        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            
        finally:
            browser.close()

# Chạy thử nghiệm
if __name__ == "__main__":
    crawl_vbpl_documents("Luật Chứng khoán")