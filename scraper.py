import requests
from bs4 import BeautifulSoup


def open_web(url, timeout=10):
    """Fetch page and return text or empty string on error."""
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception:
        return ""


def get_all_links(html_text, poisk, progress_callback=None, max_categories=None):
    """Compatibility API: collect links and titles and return two lists.

    This function is a wrapper around `get_all_links_stream` and
    accumulates found items into `links` and `glava` lists.

    RU: Совместимый API: собирает ссылки и заголовки и возвращает два списка.

    RU: Эта функция теперь является обёрткой над `get_all_links_stream` и
    RU: аккумулирует найденные элементы в списки `links` и `glava`.

    Args:
        html_text: HTML string of the page to scan.
        poisk: substring to match in hrefs.
        progress_callback: optional; callable(processed, total, found)
        max_categories: optional limit on number of categories.

    Returns: (links, glava)
    """
    links, glava = [], []
    for link, title in get_all_links_stream(
        html_text,
        poisk,
        progress_callback=progress_callback,
        max_categories=max_categories,
    ):
        links.append(link)
        glava.append(title)
    return links, glava


def get_all_links_stream(html_text, poisk, progress_callback=None, max_categories=None):
    """Streaming variant: yields (link, title) as found.

    RU: Вариант потоковой выдачи: возвращает (link, title) по мере нахождения.

    Args:
        html_text: HTML of the starting page
        poisk: substring to match in href
        progress_callback: optional callable(processed, total, found)
        max_categories: optional int to stop after this many found
    Yields:
        (link, title)
    """
    soup = BeautifulSoup(html_text, "html.parser")
    href_link = soup.find_all("a")
    lp = len(poisk) + 5

    total = len(href_link)
    processed = 0
    found = 0

    for tag in href_link:
        processed += 1
        a = tag.get("href")
        if not a:
            if progress_callback:
                try:
                    progress_callback(processed, total, found)
                except Exception:
                    pass
            continue

        a = a.strip()
        la = len(a)

        if poisk in a.rstrip("/") and la >= lp and a:
            # try to expand via _dop
            # RU: попытка расширить путь через функцию _dop (сбор "хлебных крошек")
            new_links, new_glava = _dop(a, poisk)
            if new_links and new_glava:
                for nl, ng in zip(new_links, new_glava):
                    found += 1
                    yield (nl, ng)
                    if progress_callback:
                        try:
                            progress_callback(processed, total, found)
                        except Exception:
                            pass
                    if max_categories and found >= max_categories:
                        return
            else:
                # fallback: yield the link/text from current tag
                # RU: fallback: выдаём ссылку/текст из текущего тега
                found += 1
                yield (a, tag.text.strip())
                if progress_callback:
                    try:
                        progress_callback(processed, total, found)
                    except Exception:
                        pass
                if max_categories and found >= max_categories:
                    return

        if progress_callback:
            try:
                progress_callback(processed, total, found)
            except Exception:
                pass


def _dop(url, poisk):
    """Helper: extract `url` and collect links from `a.breads` elements.

    RU: Helper: извлечь `url` и собрать ссылки из элементов `a.breads`.
    """
    links = []
    glava = []
    http_txt = open_web(url)
    if not http_txt:
        return links, glava

    soup = BeautifulSoup(http_txt, "lxml")
    v = soup.find_all("a", class_="breads")
    po = len(poisk) + 1

    for b in v:
        a = b.get("href")
        if a:
            a = a.strip()
            if len(a) >= po and a != url:
                links.append(a)
                glava.append(b.text.strip())

    return links, glava


def get_page_data(html, gl):
    """Parse page and return list of dicts representing rows (blok).

    RU: Анализ страницы и возврат списка словарей, представляющих строки (блок).
    """
    soup = BeautifulSoup(html, "lxml")
    job_name = soup.find_all("td", class_="tdwrap")
    blok = []
    blok.append({"№": "", "Наименование": gl, "Цена": "", "Ед. изм": ""})

    for index, tag in enumerate(job_name, start=1):
        name_job = tag.text.strip() if tag.text else ""
        ed = [e.text.strip() for e in tag.findNextSiblings() if e.text]
        ed += [""] * (2 - len(ed))
        blok.append(
            {"№": index, "Наименование": name_job, "Цена": ed[0], "Ед. изм": ed[1]}
        )

    return blok
