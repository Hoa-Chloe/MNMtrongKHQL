from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

# ======================================================
# 1. HÀM LÀM SẠCH VĂN BẢN 
# ======================================================
def clean_text(text):
    if not text: return "N/A"
    # Xóa các chú thích kiểu [1], [2], [a]...
    text = re.sub(r'\[.*?\]', '', text)
    # Thay thế xuống dòng bằng dấu " | " 
    text = text.replace('\n', ' | ')
    return text.strip()

# ======================================================
# 2. KHỞI TẠO VÀ LẤY LINK
# ======================================================
driver = webdriver.Chrome()
url_goc = "https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_tr%C6%B0%E1%BB%9Dng_%C4%91%E1%BA%A1i_h%E1%BB%8Dc_t%E1%BA%A1i_Vi%E1%BB%87t_Nam"
data_list = []

print("--- ĐANG LẤY DANH SÁCH LINK ---")
driver.get(url_goc)

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "wikitable")))
    elements = driver.find_elements(By.CSS_SELECTOR, "table.wikitable td a")
    
    # Dùng set để lọc trùng lặp ngay lập tức
    uni_links = list({
        e.get_attribute("href") for e in elements 
        if e.get_attribute("href") and "/wiki/" in e.get_attribute("href") and "redlink=1" not in e.get_attribute("href")
    })
    print(f"-> Tìm thấy {len(uni_links)} trường.")
except Exception as e:
    print("Lỗi lấy link:", e)
    uni_links = []

# ======================================================
# 3. CHẠY VÒNG LẶP QUÉT DỮ LIỆU
# ======================================================
# LIMIT = 10

count = 0
for link in uni_links:
    # if LIMIT != -1 and count >= LIMIT: break
    count += 1
    
    print(f"[{count}] Đang cào: {link}")
    
    try:
        driver.get(link)
        
        info = {
            "Tên trường": "N/A",
            "Tên lãnh đạo": "N/A",
            "Hotline": "N/A",
            "Website": "N/A"
        }
        
        # --- A. LẤY TÊN TRƯỜNG ---
        try:
            info["Tên trường"] = driver.find_element(By.TAG_NAME, "h1").text
        except: pass

        # --- B. QUÉT INFOBOX (BẢNG THÔNG TIN) ---
        rows = driver.find_elements(By.CSS_SELECTOR, "table.infobox tr")
        
        for row in rows:
            try:
                header = row.find_element(By.TAG_NAME, "th").text.lower()
                content = row.find_element(By.TAG_NAME, "td").text
                
                # 1. TÌM LÃNH ĐẠO (Hiệu trưởng / Giám đốc / Viện trưởng)
                if any(x in header for x in ["hiệu trưởng", "giám đốc", "viện trưởng", "chủ nhiệm khoa"]):
                    clean_content = clean_text(content)
                    if info["Tên lãnh đạo"] == "N/A":
                        info["Tên lãnh đạo"] = clean_content
                    else:
                        info["Tên lãnh đạo"] += f" | {clean_content}"

                # 2. TÌM HOTLINE (Điện thoại)
                elif any(x in header for x in ["điện thoại", "hotline"]):
                    info["Hotline"] = clean_text(content)
                
                # 3. TÌM WEBSITE
                elif any(x in header for x in ["website", "trang web", "url"]):
                    info["Website"] = clean_text(content)

            except:
                continue

        data_list.append(info)

    except Exception as e:
        print(f"Lỗi link {link}: {e}")

# ======================================================
# 4. XUẤT FILE EXCEL
# ======================================================
driver.quit()

if data_list:
    df = pd.DataFrame(data_list)

    df = df[["Tên trường", "Tên lãnh đạo", "Hotline", "Website"]]
    
    file_name = 'DanhSachDH_Clean.xlsx'
    df.to_excel(file_name, index=False)
    print(f"\n--- XONG! Đã lưu dữ liệu vào '{file_name}' ---")
    print(df.head())
else:
    print("Không thu thập được dữ liệu nào.")