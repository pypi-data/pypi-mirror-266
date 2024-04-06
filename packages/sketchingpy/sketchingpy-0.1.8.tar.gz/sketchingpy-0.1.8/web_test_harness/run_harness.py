import sys

import selenium.common.exceptions
import selenium.webdriver
import selenium.webdriver.common.by
import selenium.webdriver.common.desired_capabilities
import selenium.webdriver.support.wait

def main():
    options = selenium.webdriver.FirefoxOptions()
    options.add_argument("--headless")

    driver = selenium.webdriver.Firefox(options=options)
    driver.get('localhost:8000/example.html')

    wait = selenium.webdriver.support.wait.WebDriverWait(driver, timeout=7)
    canvas = driver.find_element(
       selenium.webdriver.common.by.By.ID,
       'sketch-canvas'
    )

    try:
        wait.until(lambda d : canvas.is_displayed())
        canvas_shown = canvas.is_displayed()
    except selenium.common.exceptions.TimeoutException:
        canvas_shown = True

    py_error = None
    try:
        py_error = driver.find_element(
            selenium.webdriver.common.by.By.CLASS_NAME,
            'py-error'
        )
    except selenium.common.exceptions.NoSuchElementException:
        pass

    error_found = py_error is not None

    driver.close()

    if (not canvas_shown) or error_found:
        print('Failed.')
        sys.exit(1)


if __name__ == '__main__':
    main()
