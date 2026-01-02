import scraper


def test_get_page_data_basic():
    html = '''
    <html><body>
    <table>
      <tr><td class="tdwrap">Job 1</td><td>100</td><td>unit</td></tr>
      <tr><td class="tdwrap">Job 2</td><td>200</td><td>m2</td></tr>
    </table>
    </body></html>
    '''
    blok = scraper.get_page_data(html, "Category Title")
    assert isinstance(blok, list)
    # first row is header/section title
    assert blok[0]["Наименование"] == "Category Title"
    # entries parsed from td.tdwrap
    assert blok[1]["Наименование"] == "Job 1"
    assert blok[1]["Цена"] == "100"
    assert blok[1]["Ед. изм"] == "unit"
    assert blok[2]["Наименование"] == "Job 2"
