import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  
from webdriver_manager.chrome import ChromeDriverManager  

def sinta_login():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get("https://sinta.kemdikbud.go.id/logins")

    try:
        username = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        password = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )

        username.send_keys("igit.sabda@fmipa.unila.ac.id")  
        password.send_keys("1G1t01011996")  

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Login')]"))
        )
        login_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "navbar-brand"))
        )

        print("Login berhasil!")
        return driver

    except Exception as e:
        print(f"Login gagal: {e}")
        driver.quit()
        return None


def scrape_sinta_publications():
    driver = sinta_login()
    if not driver:
        print("Tidak bisa login, hentikan scraping.")
        return

    base_url = "https://sinta.kemdikbud.go.id/affiliations/profile/398/?page={}&view=googlescholar"

    title_list, year_list, author_list, pub_list, cited_list, url_list = ([] for _ in range(6))

    for page in range(4171, 5005): 
        print(f"Scraping halaman {page}...")
        driver.get(base_url.format(page))
        time.sleep(5)  

        soup = BeautifulSoup(driver.page_source, "lxml")

        articles = soup.find_all("div", class_="ar-list-item")

        if not articles:
            print(f"Tidak ada artikel di halaman {page}, kemungkinan struktur berubah atau akses dibatasi.")
            continue

        for article in articles:
            try:
                title = article.find("div", class_="ar-title").find("a").text.strip()
                year = article.find("a", class_="ar-year").text.strip()
                author = article.select_one(".ar-meta a[href]").text.strip()
                pub = article.find("a", class_="ar-pub").text.strip()
                cited = article.find("a", class_="ar-cited").text.strip() if article.find("a", class_="ar-cited") else "0"
                url = article.find("div", class_="ar-title").find("a")["href"]

                # Simpan ke list
                title_list.append(title)
                year_list.append(year)
                author_list.append(author)
                pub_list.append(pub)
                cited_list.append(cited)
                url_list.append(url)

            except Exception as e:
                print(f"Error mengambil data artikel: {e}")
                continue  

    driver.quit()

    df = pd.DataFrame({
        "Title": title_list,
        "Year": year_list,
        "Author": author_list,
        "Publication": pub_list,
        "Cited": cited_list,
        "URL": url_list
    })

    df.to_csv("sinta_publications.csv", index=False)
    print("Scraping selesai! Data disimpan di sinta_publications.csv")


scrape_sinta_publications()
