import sqlite3
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- CẤU HÌNH ĐƯỜNG DẪN  ---
GECKO_PATH = r"C:\Users\NHU\OneDrive\Documents\VSC\MNM\Selenium\geckodriver.exe"
FIREFOX_BINARY = r"C:\Program Files\Mozilla Firefox\firefox.exe"
DB_NAME = "longchau_db.sqlite"

# --- 1. KHỞI TẠO DATABASE ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tạo bảng products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            url TEXT PRIMARY KEY,
            id TEXT,
            name TEXT,
            price REAL,
            original_price REAL,
            unit TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- 2. CÁC HÀM XỬ LÝ DỮ LIỆU ---
def clean_price(price_text):
    """Chuyển '150.000đ' -> 150000.0"""
    if not price_text: return 0
    clean = re.sub(r'[^\d]', '', price_text) 
    try: return float(clean)
    except: return 0

def extract_unit(name):
    """Lấy đơn vị từ tên sản phẩm"""
    name_lower = name.lower()
    units = ["hộp", "chai", "lọ", "vỉ", "tuýp", "gói", "viên"]
    for u in units:
        if u in name_lower:
            return u.title() 
    return "Khác"

# --- 3. CHƯƠNG TRÌNH CHÍNH ---
def run_scraper():
    # Setup Database
    init_db()
    conn = sqlite3.connect(DB_NAME) 
    cursor = conn.cursor()

    ser = Service(GECKO_PATH)
    options = webdriver.FirefoxOptions()
    options.binary_location = FIREFOX_BINARY
    driver = webdriver.Firefox(options=options, service=ser)

    # Truy cập 
    url = 'https://nhathuoclongchau.com.vn/thuc-pham-chuc-nang/vitamin-khoang-chat'
    driver.get(url)
    time.sleep(2)

    body = driver.find_element(By.TAG_NAME, "body")
    
    print("Đang tải thêm sản phẩm...")
    for k in range(10): 
        try:
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "Xem thêm" in button.text and "sản phẩm" in button.text:
                    driver.execute_script("arguments[0].click();", button) 
                    time.sleep(2)
                    break 
        except:
            pass
            
    # Cuộn trang từ từ
    for i in range(50):
        body.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.1)

    # BẮT ĐẦU CÀO
    # Tìm tất cả nút "Chọn mua"
    buy_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Chọn mua')]")
    print(f"Tìm thấy {len(buy_buttons)} sản phẩm khả dụng.")

    count = 0
    for bt in buy_buttons:
        # if count >= 60: break 

        try:
            # --- Logic Leo thang (Traversal) ---
            parent_div = bt
            # Quay ngược 3 cấp để lấy thẻ bao quanh sản phẩm
            for _ in range(3):
                parent_div = parent_div.find_element(By.XPATH, "./..")

            # --- Lấy dữ liệu từ parent_div ---
            
            # 1. Tên sản phẩm & URL (Tìm thẻ <a>)
            try:
                a_tag = parent_div.find_element(By.TAG_NAME, "a")
                p_name = a_tag.get_attribute("title")
                if not p_name: # Dự phòng nếu title rỗng
                    p_name = parent_div.find_element(By.TAG_NAME, "h3").text
                
                p_url = a_tag.get_attribute("href")
            except:
                continue 

            # 2. Giá bán 
            try:
                price_raw = parent_div.find_element(By.CLASS_NAME, "text-blue-5").text
                price = clean_price(price_raw)
            except:
                price = 0

            # 3. Giá gốc 
            try:
                # Tìm thẻ có style gạch ngang hoặc class chứa line-through
                orig_raw = parent_div.find_element(By.CSS_SELECTOR, ".line-through").text
                original_price = clean_price(orig_raw)
            except:
                original_price = price # Nếu ko có giá cũ thì bằng giá mới

            # 4. ID & Unit
            try:
                p_id = p_url.split('/')[-1].replace('.html', '')
            except:
                p_id = f"unknown_{int(time.time())}"
            
            unit = extract_unit(p_name)

            # --- LƯU TỨC THI VÀO SQLITE ---
            sql = '''
                INSERT OR IGNORE INTO products 
                (url, id, name, price, original_price, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(sql, (p_url, p_id, p_name, price, original_price, unit))
            conn.commit()
            
            print(f"Đã lưu: {p_name[:30]}... | {price}")
            count += 1

        except Exception as e:
            continue

    driver.quit()
    conn.close()
    print("\n--- Dữ liệu đã lưu vào file longchau_db.sqlite ---")

if __name__ == "__main__":
    run_scraper()

import sqlite3
import pandas as pd

# Kết nối DB
conn = sqlite3.connect("longchau_db.sqlite")

def run_query(title, query):
    print(f"\n--- {title} ---")
    try:
        df = pd.read_sql_query(query, conn)
        if df.empty:
            print("(Không có dữ liệu thỏa mãn)")
        else:
            print(df)
    except Exception as e:
        print(f"Lỗi SQL: {e}")

# =========================================================
#  NHÓM 1: KIỂM TRA CHẤT LƯỢNG DỮ LIỆU (BẮT BUỘC)
# =========================================================

# 1. Kiểm tra trùng lặp (Dựa trên URL)
run_query("1. Kiểm tra bản ghi trùng lặp (URL)", 
    """
    SELECT url, COUNT(*) as so_luong_trung
    FROM products 
    GROUP BY url 
    HAVING so_luong_trung > 1
    """)

# 2. Kiểm tra dữ liệu thiếu (Giá = 0 hoặc NULL)
run_query("2. Số lượng sản phẩm thiếu giá (Price is NULL or 0)", 
    """
    SELECT COUNT(*) as so_sp_loi_gia 
    FROM products 
    WHERE price IS NULL OR price = 0
    """)

# 3. Kiểm tra giá bất thường (Giá bán > Giá gốc)
run_query("3. Sản phẩm có Giá bán > Giá gốc (Logic sai)", 
    """
    SELECT name, price, original_price 
    FROM products 
    WHERE price > original_price AND original_price > 0
    """)

# 4. Kiểm tra định dạng (Các Unit duy nhất)
run_query("4. Danh sách các Đơn vị tính (Unit) duy nhất", 
    """
    SELECT DISTINCT unit FROM products
    """)

# 5. Tổng số lượng bản ghi
run_query("5. Tổng số sản phẩm đã cào được", 
    """
    SELECT COUNT(*) as tong_so_san_pham FROM products
    """)


# =========================================================
#  NHÓM 2: KHẢO SÁT VÀ PHÂN TÍCH (BỔ SUNG)
# =========================================================

# 6. Sản phẩm giảm giá nhiều nhất (Số tiền VNĐ)
run_query("6. Top 10 sản phẩm có mức giảm giá (VNĐ) cao nhất", 
    """
    SELECT name, price, original_price, (original_price - price) as giam_vnd
    FROM products 
    WHERE original_price > price
    ORDER BY giam_vnd DESC 
    LIMIT 10
    """)

# 7. Sản phẩm đắt nhất
run_query("7. Sản phẩm có giá bán cao nhất", 
    """
    SELECT name, price, unit 
    FROM products 
    ORDER BY price DESC 
    LIMIT 1
    """)

# 8. Thống kê theo đơn vị
run_query("8. Số lượng sản phẩm theo từng Đơn vị tính", 
    """
    SELECT unit, COUNT(*) as so_luong 
    FROM products 
    GROUP BY unit
    ORDER BY so_luong DESC
    """)

# 9. Tìm kiếm sản phẩm "Vitamin C"
run_query("9. Tìm kiếm sản phẩm chứa từ khóa 'Vitamin C'", 
    """
    SELECT name, price 
    FROM products 
    WHERE name LIKE '%Vitamin C%'
    """)

# 10. Lọc theo khoảng giá (100k - 200k)
run_query("10. Sản phẩm có giá từ 100.000 đến 200.000 VNĐ", 
    """
    SELECT name, price 
    FROM products 
    WHERE price BETWEEN 100000 AND 200000
    LIMIT 10
    """)


# =========================================================
#  NHÓM 3: CÁC TRUY VẤN NÂNG CAO (TÙY CHỌN)
# =========================================================

# 11. Sắp xếp giá từ thấp đến cao
run_query("11. Sắp xếp sản phẩm theo Giá tăng dần (Top 5 rẻ nhất)", 
    """
    SELECT name, price 
    FROM products 
    WHERE price > 0
    ORDER BY price ASC 
    LIMIT 5
    """)

# 12. Phần trăm giảm giá cao nhất
# Công thức: (Giá gốc - Giá bán) / Giá gốc * 100
run_query("12. Top 5 sản phẩm có % Giảm giá cao nhất", 
    """
    SELECT name, price, original_price,
           ROUND(((original_price - price) * 100.0 / original_price), 1) as phan_tram_giam
    FROM products
    WHERE original_price > price
    ORDER BY phan_tram_giam DESC
    LIMIT 5
    """)

# 13. Xóa bản ghi trùng lặp (Giữ lại 1 bản ghi duy nhất)
# Sử dụng ROWID để giữ lại bản ghi đầu tiên nhập vào
print("\n" + "="*60)
print("13. Thực hiện Xóa bản ghi trùng lặp...")
try:
    delete_query = """
    DELETE FROM products
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM products
        GROUP BY url
    )
    """
    cursor = conn.cursor()
    cursor.execute(delete_query)
    conn.commit()
    print(f"   -> Đã thực hiện lệnh xóa. (Số dòng bị xóa: {cursor.rowcount})")
except Exception as e:
    print(f"Lỗi khi xóa: {e}")

# 14. Phân tích nhóm giá (Case When)
run_query("14. Phân bố sản phẩm theo nhóm giá", 
    """
    SELECT 
        CASE 
            WHEN price < 50000 THEN 'Dưới 50k'
            WHEN price BETWEEN 50000 AND 100000 THEN '50k - 100k'
            ELSE 'Trên 100k'
        END as phan_khuc_gia,
        COUNT(*) as so_luong
    FROM products
    WHERE price > 0
    GROUP BY phan_khuc_gia
    """)

# 15. URL không hợp lệ
run_query("15. Các sản phẩm lỗi URL (NULL hoặc Rỗng)", 
    """
    SELECT * FROM products 
    WHERE url IS NULL OR url = ''
    """)

conn.close()