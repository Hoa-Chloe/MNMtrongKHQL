import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
import os
import pandas as pd 
import unicodedata # Thư viện quan trọng để chuẩn hóa font chữ lạ

######################################################
## I. CẤU HÌNH DATABASE
######################################################
DB_FILE = 'Painters_Data.db'
TABLE_NAME = 'painters_info'

if os.path.exists(DB_FILE):
    try: os.remove(DB_FILE)
    except: pass

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    birth TEXT,
    death TEXT,
    nationality TEXT,
    url TEXT UNIQUE
);
""")
conn.commit()

######################################################
## II. DANH SÁCH & MAPPING
######################################################
VALID_NATIONALITIES = [
    "American", "French", "Italian", "German", "Dutch", "English", "British", "Spanish", 
    "Russian", "Austrian", "Swiss", "Belgian", "Flemish", "Japanese", "Chinese", 
    "Mexican", "Canadian", "Australian", "Swedish", "Norwegian", "Danish", "Finnish",
    "Polish", "Hungarian", "Czech", "Portuguese", "Greek", "Irish", "Scottish", "Welsh",
    "Indian", "Korean", "Vietnamese", "Brazilian", "Argentine", "Chilean", "Cuban",
    "Turkish", "Egyptian", "Iranian", "Netherlandish", "Venetian", "Florentine", 
    "Neapolitan", "Roman", "Sienese", "Milanese", "Bolognese", "Prussian", "Bavarian",
    "Soviet", "Ukrainian", "Belarusian", "South African", "New Zealand", "Israeli",
    "Bahamian", "Filipino", "Thai", "Indonesian", "Malaysian", "Romani"
]

COUNTRY_MAP = {
    "United States": "American", "USA": "American", "UK": "British",
    "Netherlands": "Dutch", "Holland": "Dutch", "France": "French", "Germany": "German", 
    "Italy": "Italian", "Spain": "Spanish", "Russia": "Russian", "Austria": "Austrian",
    "Switzerland": "Swiss", "Belgium": "Belgian", "Japan": "Japanese", "China": "Chinese", 
    "Mexico": "Mexican", "Canada": "Canadian", "Australia": "Australian", "Sweden": "Swedish", 
    "Norway": "Norwegian", "Denmark": "Danish", "Finland": "Finnish", "Poland": "Polish",
    "Hungary": "Hungarian", "Greece": "Greek", "Ireland": "Irish", "Scotland": "Scottish", 
    "Wales": "Welsh", "India": "Indian", "Vietnam": "Vietnamese", "Brazil": "Brazilian", 
    "Argentina": "Argentine", "Turkey": "Turkish", "Egypt": "Egyptian", "Iran": "Iranian"
}

######################################################
## III. HÀM HỖ TRỢ 
######################################################

def normalize_text(text):
    """Biến đổi mọi ký tự lạ về dạng chuẩn ASCII"""
    if not text: return ""
    # Chuyển đổi unicode 
    text = unicodedata.normalize("NFKD", text)
    return text

def extract_years_greedy(text):
    """
    Tìm tất cả các năm trong chuỗi.
    Trả về list các năm tìm thấy.
    """
    # Tìm số có 3 hoặc 4 chữ số
    matches = re.findall(r'\b(\d{3,4})\b', text)
    valid_years = []
    for m in matches:
        # Lọc rác: Năm phải từ 900 đến 2025
        if 900 < int(m) < 2030:
            valid_years.append(m)
    return valid_years

def clean_nationality_context(text):
    """
    Ưu tiên tìm quốc tịch đứng cạnh chữ 'painter/artist'.
    Khắc phục lỗi: Károly Ferenczy (Hungarian sinh tại Áo) -> Lấy Hungarian.
    """
    if not text: return ""
    text_lower = text.lower()
    
    found_nat = ""
    
    # 1. Tìm ưu tiên: [Nationality] painter/artist
    for nat in VALID_NATIONALITIES:
        pattern = r'\b' + re.escape(nat.lower()) + r'\s+(?:male\s+|female\s+)?(?:painter|artist|sculptor)'
        if re.search(pattern, text_lower):
            return nat # Trả về ngay
            
    # 2. Nếu không thấy cụm từ ghép, tìm xuất hiện thông thường
    for nat in VALID_NATIONALITIES:
        if re.search(r'\b' + re.escape(nat) + r'\b', text, re.IGNORECASE):
            if not found_nat: found_nat = nat
            
    # 3. Check Mapping (Country -> Nationality)
    if not found_nat:
        for country, mapped_nat in COUNTRY_MAP.items():
             if re.search(r'\b' + re.escape(country) + r'\b', text, re.IGNORECASE):
                 return mapped_nat
                 
    return found_nat

def get_data_v5(driver):
    birth, death, nat = "", "", ""
    
    # --- 1. LẤY DỮ LIỆU TỪ TEXT (Ưu tiên số 1) ---
    try:
        summary_elem = driver.find_element(By.XPATH, "//div[@class='mw-parser-output']/p[not(@class='mw-empty-elt')][1]")
        raw_text = summary_elem.text
        clean_text = normalize_text(raw_text)
        
        # A. XỬ LÝ NĂM 
        # Tìm nội dung trong ngoặc đơn đầu tiên
        paren_match = re.search(r'\((.*?)\)', clean_text)
        if paren_match:
            content = paren_match.group(1)
            years = extract_years_greedy(content)
            
            if len(years) >= 2:
                birth = years[0]
                death = years[1]
            elif len(years) == 1:
                if "born" in content.lower() or "b." in content.lower():
                    birth = years[0]
                elif "died" in content.lower() or "d." in content.lower():
                    death = years[0]
        
        # B. XỬ LÝ QUỐC TỊCH 
        nat = clean_nationality_context(clean_text)

    except: pass

    # --- 2. FALLBACK: CATEGORIES ---
    try:
        cat_text = normalize_text(driver.find_element(By.ID, "catlinks").text)
        
        # Fallback Năm
        if not birth and "births" in cat_text:
            birth_match = re.search(r'(\d{3,4}) births', cat_text)
            if birth_match: birth = birth_match.group(1)
            
        if not death and "deaths" in cat_text:
            death_match = re.search(r'(\d{3,4}) deaths', cat_text)
            if death_match: death = death_match.group(1)
            
        # Fallback Quốc tịch
        if not nat:
            nat = clean_nationality_context(cat_text)
    except: pass

    # --- 3. FALLBACK: INFOBOX ---
    if not birth or not death or not nat:
        try:
            rows = driver.find_elements(By.XPATH, "//table[contains(@class,'infobox')]//tr")
            for row in rows:
                txt = normalize_text(row.text) # Chuẩn hóa
                if not birth and ("born" in txt.lower() or "b." in txt.lower()): 
                    years = extract_years_greedy(txt)
                    if years: birth = years[0]
                if not death and ("died" in txt.lower() or "d." in txt.lower()):
                     years = extract_years_greedy(txt)
                     if years: death = years[-1] # Lấy số cuối cùng
                if not nat and "nationality" in txt.lower():
                    nat = clean_nationality_context(txt)
        except: pass

    return birth, death, nat

######################################################
## IV. MAIN LOOP
######################################################
driver = webdriver.Chrome()

try:
    for i in range(65, 91): # F
        char = chr(i)
        url_list = f"https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22{char}%22"
        print(f"\n>>> ĐANG XỬ LÝ: {char}")
        driver.get(url_list)
        time.sleep(2)

        # Lấy Link
        all_links = []
        try:
            content_div = driver.find_element(By.CLASS_NAME, "mw-parser-output")
            ul_tags = content_div.find_elements(By.TAG_NAME, "ul")
            for ul in ul_tags:
                li_tags = ul.find_elements(By.TAG_NAME, "li")
                if len(li_tags) > 1: 
                    for tag in li_tags:
                        try:
                            a = tag.find_element(By.TAG_NAME, "a")
                            link = a.get_attribute("href")
                            if link and "/wiki/" in link:
                                forbidden = ["List_of", "Category:", "Special:", "File:", "Help:", "Portal:", "Talk:"]
                                if not any(x in link for x in forbidden):
                                    all_links.append(link)
                        except: pass
        except: pass
        
        all_links = list(set(all_links))
        print(f"--> Tìm thấy {len(all_links)} họa sĩ.")

        count = 0
        for p_link in all_links:
            count += 1
            try:
                driver.get(p_link)
                try: name = driver.find_element(By.ID, "firstHeading").text
                except: name = "Unknown"

                # --- GỌI HÀM ---
                b, d, n = get_data_v5(driver)

                sql = f"INSERT OR IGNORE INTO {TABLE_NAME} (name, birth, death, nationality, url) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(sql, (name, b, d, n, p_link))
                conn.commit()
                
                print(f" [{count:03}] {name[:20]:<22} | B: {b:<4} | D: {d:<4} | Nat: {n}")

            except: pass

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
    conn.close()
    
    # Check kết quả
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    print("\n--- KẾT QUẢ KIỂM TRA ---")
    print(df.head(20))
    conn.close()

