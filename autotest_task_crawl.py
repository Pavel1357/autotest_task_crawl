from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urlparse, urljoin


# ожидание полной загрузки страницы
def wait_for_page_load(driver, timeout=10):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


# получение времени загрузки страницы
def get_load_time(driver):
    timing = driver.execute_script("return window.performance.timing")
    load_time = timing["loadEventEnd"] - timing["navigationStart"]
    return load_time if load_time > 0 else None


# рекурсивный краулер с ограничением по домену и строгой глубиной
def crawl(driver, url, base_domain, max_depth, max_pages, visited=None, results=None, depth=0):
    if visited is None:
        visited = set()

    if results is None:
        results = []

    if depth >= max_depth or url in visited or len(results) >= max_pages:
        return

    try:
        driver.get(url)
        wait_for_page_load(driver)

        load_time = get_load_time(driver)
        visited.add(url)

        if load_time:
            results.append((url, load_time))

        print("  " * depth + f"[{depth}] {url} | Load time: {load_time} ms")

        # собираем ссылки и идем рекурсивно
        links = driver.find_elements(By.TAG_NAME, "a")
        hrefs = [link.get_attribute("href") for link in links if link.get_attribute("href")]

        for href in hrefs:
            if not href.startswith("http"):
                href = urljoin(url, href)

            host = urlparse(href).netloc
            if (host == base_domain or host.endswith("." + base_domain)) and href not in visited:
                if depth + 1 < max_depth:
                    crawl(driver, href, base_domain, max_depth, max_pages, visited, results, depth + 1)

    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")

    return results


if __name__ == "__main__":
    start_url = input("Введите URL-адрес сайта: ").strip()
    max_depth = int(input("Введите максимальную глубину обхода: ").strip())
    max_pages = int(input("Введите максимальное количество страниц: ").strip())

    base_domain = urlparse(start_url).netloc

    driver = webdriver.Chrome()

    try:
        results = crawl(driver, start_url, base_domain, max_depth, max_pages)
    finally:
        driver.quit()

    results.sort(key=lambda x: x[1], reverse=True)

    print("\nТоп страниц по времени загрузки:")
    for url, t in results:
        print(f"{t} ms -> {url}")