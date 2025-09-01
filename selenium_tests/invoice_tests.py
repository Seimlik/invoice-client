from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

invoice_number = "12345"
expected_price = "1456879.00"


def create_invoice(driver, invoice_number):
    # kliknutí na tlačítko "Nová faktura"
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn-success"))
    ).click()

    # čekání na načtení pole čísla faktury
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.NAME, "invoiceNumber")))

    # vyplnění čísla faktury
    invoice_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "invoiceNumber"))
    )
    invoice_input.send_keys(invoice_number)

    # výběr prodávajícího
    seller_select = Select(driver.find_element(By.NAME, "seller"))
    WebDriverWait(driver, 50).until(lambda d: len(seller_select.options) > 1)
    seller_select.select_by_index(1)

    # výběr kupujícího
    buyer_select = Select(driver.find_element(By.NAME, "buyer"))
    WebDriverWait(driver, 50).until(lambda d: len(buyer_select.options) > 1)
    buyer_select.select_by_index(2)

    # vyplnění polí s čekáním
    issued_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "issued"))
    )
    issued_input.send_keys("01012000")

    due_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "dueDate"))
    )
    due_input.send_keys("01012001")

    product_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "product"))
    )
    product_input.send_keys("Testovací produkt")

    price_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "price"))
    )
    price_input.send_keys(expected_price)

    dph_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "dph"))
    )
    dph_input.send_keys("21")

    note_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "note"))
    )
    note_input.send_keys("Poznámka k faktuře")

    # odeslání formuláře
    print("👉 Klikám na tlačítko 'Uložit'")
    save_button = WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input.btn.btn-primary[value='Uložit']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
    driver.execute_script("arguments[0].click();", save_button)


def verify_invoice(driver, invoice_number, expected_price):
    try:
        invoice_row = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//tr[td[normalize-space()='{invoice_number}']]"))
        )
    except TimeoutException:
        assert False, f"Test selhal: Faktura s číslem {invoice_number} nebyla nalezena!"

    price_element = invoice_row.find_element(By.XPATH, ".//td[position()=last()-1]")
    actual_price = price_element.text.strip()

    assert actual_price == expected_price, f"Test selhal: Faktura nemá správnou cenu! Očekáváno: {expected_price}, Nalezeno: {actual_price}"

    print("Test prošel! Faktura byla úspěšně přidána do seznamu.")


def delete_invoice(driver, invoice_number):
    try:
        invoice_row = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//tr[td[normalize-space()='{invoice_number}']]"))
        )

        delete_button = invoice_row.find_element(By.XPATH, ".//button[contains(text(),'Odstranit')]")
        delete_button.click()

        print(f"Faktura {invoice_number} byla úspěšně smazána.")

    except TimeoutException:
        print(f"Chyba: Faktura {invoice_number} nebyla nalezena pro smazání.")

    except Exception as e:
        print(f"Chyba při mazání faktury: {e}")


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    driver.get("http://localhost:3000")
    driver.maximize_window()

    create_invoice(driver, invoice_number)
    verify_invoice(driver, invoice_number, expected_price)

except Exception as e:
    print(e)

finally:
    delete_invoice(driver, invoice_number)
    driver.quit()