# Import the manager for Firefox
import os
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# ==============================================================================
# --- URLS & LOCATORS: Final verified and robust locators ---
# ==============================================================================
URLS = {
    "login": "https://erp.superior.edu.pk/web/login",
    "dashboard": "https://erp.superior.edu.pk/students/dashboard",
    "attendance": "https://erp.superior.edu.pk/student/attendance",
    "results": "https://erp.superior.edu.pk/student/results",
    "invoices": "https://erp.superior.edu.pk/student/invoices",
    "timetable": "https://erp.superior.edu.pk/student/class/schedule"
}

LOCATORS = {
    "login": {
        "roll_no_field": ("id", "login"),
        "password_field": ("id", "password"),
        "login_button": ("xpath", "//button[@type='submit']")
    },

"enrolled_courses": {
    "container": ("id", "hierarchical-show"),
    "course_cards": ("xpath", "./div[contains(@class, 'uk-row-first')]"),
    
    # Locators based on the NEW HTML structure
    "course_name": ("xpath", ".//a/span[1]"), # The first span inside the link
    "credits": ("xpath", ".//a//b[normalize-space()='Credits :']/following-sibling::span"),
    "status": ("xpath", ".//a//span[contains(text(), 'progress') or contains(text(), 'Active')]"),
    "semester": ("xpath", ".//a//div[@class='uk-text-small']/span[@class='uk-text-small']")
},
    "dashboard": {
        "student_name": ("xpath", "//h2[@class='heading_b']/span[@class='uk-text-truncate']"),
        "academic_info_box": ("xpath", "//div[contains(text(), 'Academic standings:')]"),
        "credits_info_box": ("xpath", "//div[contains(text(), 'Completed Cr.')]"),
        "today_classes_box": ("xpath", "//div[contains(text(), 'Today Classes:')]")
    },
    "attendance_summary": {
        "subject_cards_container": ("id", "hierarchical-show"),
        "subject_cards": ("xpath", ".//div[@class='md-card md-card-hover']")
    },
    "attendance_detail": {
        "course_name": ("xpath", "//b[normalize-space()='Course :']/following-sibling::span"),
        "conducted_classes": ("xpath", "//b[normalize-space()='Number of classes Conducted :']/following-sibling::span"),
        "attended_classes": ("xpath", "//b[normalize-space()='Number of classes Attended :']/following-sibling::span"),
        "percentage": ("xpath", "//b[normalize-space()='Attendance Percentage:']/following-sibling::span"),
    },
    "results_summary": {
        "page_header": ("xpath", "//h3[contains(text(), 'Results')]"),
        "previous_courses_tab": ("xpath", "//a[normalize-space()='Previous Courses']"),
        "term_summary_rows": ("xpath", "//tr[contains(@class, 'table-parent-row')]")
    },
    "invoices_page": {
        "page_header": ("xpath", "//h3[contains(text(), 'Invoices List')]"),
        "table_rows": ("xpath", "//table[contains(@class, 'table_check')]/tbody/tr")
    },
    "timetable_page": {
        "header": ("xpath", "//h3[contains(text(), 'Class Schedule')]"),
        "day_groups": ("xpath", "//li[@class='cd-schedule__group']")
    }
}

# ==============================================================================
#                          UPDATED SCRAPER CLASS
# ==============================================================================
class EnhancedErpScraper:
    def __init__(self, roll_no, password):
        # This code will now work on BOTH your local machine and Streamlit Cloud
        print("--- Initializing new Selenium Firefox Driver instance ---")
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # --- This is the environment-aware logic ---
        # Check if the app is running on Streamlit's servers
        if "STREAMLIT_SERVER_RUNNING" in os.environ:
            # If on Streamlit Cloud, it's a Linux environment
            print("--- Running in Streamlit Cloud environment ---")
            # We explicitly point to the Firefox binary installed via packages.txt
            options.binary_location = '/usr/bin/firefox-esr'
        else:
            # If running locally, you don't need to set the binary_location
            print("--- Running in local environment ---")

        # webdriver-manager automatically downloads and manages the correct geckodriver
        # This replaces your hardcoded "geckodriver.exe"
        service = FirefoxService(GeckoDriverManager().install())
        
        self.driver = webdriver.Firefox(service=service, options=options)
        
        # The rest of your __init__ method
        self.roll_no = roll_no
        self.password = password
        self.erp_data = {'roll_no': roll_no}
        print("--- Driver instance created successfully ---")

    def _get_locator(self, key_path):
        keys = key_path.split('.')
        value = LOCATORS
        for key in keys: value = value[key]
        return (getattr(By, value[0].upper()), value[1])

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): print("\n--- Browser Closed ---"); self.driver.quit()


    def _login(self):
        print("--- 1. Logging In ---")
        self.driver.get(URLS["login"])
        
        # Fill in login form
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(self._get_locator("login.roll_no_field"))).send_keys(self.roll_no)
        self.driver.find_element(*self._get_locator("login.password_field")).send_keys(self.password)
        self.driver.find_element(*self._get_locator("login.login_button")).click()
        
        # --- START: ROBUST LOGIN CHECK ---
        try:
            # After clicking login, wait for the student name to prove we are on the dashboard
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located(self._get_locator("dashboard.student_name"))
            )
            print("    - ✅ Login Successful!")
            
        except TimeoutException:
            # If the student name doesn't appear, login has failed.
            error_message = "Login Failed: An unknown error occurred."
            
            try:
                # Look for a specific error alert. You may need to adjust this locator.
                # Assuming the error message is in a div with class 'alert-danger'.
                alert_element = self.driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger')]")
                error_message = f"Login Failed: {alert_element.text.strip()}"
                
            except NoSuchElementException:
                # If there's no specific error message, it's likely just wrong credentials.
                error_message = "Login Failed: Invalid credentials or the page timed out."

            # --- THIS IS THE DEPLOYMENT-READY CHANGE ---
            # Only save a screenshot if running locally, not on Streamlit Cloud.
            if "STREAMLIT_SERVER_RUNNING" not in os.environ:
                try:
                    self.driver.save_screenshot("login_failure_screenshot.png")
                    print("    - A screenshot 'login_failure_screenshot.png' has been saved for local debugging.")
                except Exception as e:
                    print(f"    - Could not save screenshot: {e}")
            # --- END OF CHANGE ---
            
            print(f"    - ❌ {error_message}")
            
            # Raise a clean exception that the main app can catch and display
            raise Exception(error_message)

    def _scrape_dashboard(self):
        print("--- 2. Scraping Dashboard ---")
        try:
            self.driver.get(URLS["dashboard"])
            profile_data = {}

            # Wait for the student name to ensure the page's JS has loaded
            name_element = WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located(self._get_locator("dashboard.student_name"))
            )
            profile_data['student_name'] = name_element.text
            
            # --- ACADEMIC INFO: Find and safely parse ---
            try:
                academic_text = self.driver.find_element(*self._get_locator("dashboard.academic_info_box")).text
                standing_match = re.search(r"Academic standings:\s*(\w+)", academic_text)
                profile_data['academic_standing'] = standing_match.group(1) if standing_match else "Not Found"
                
                semester_match = re.search(r"Semester:\s*(\w+)", academic_text)
                profile_data['semester'] = semester_match.group(1) if semester_match else "Not Found"

                cgpa_match = re.search(r"CGPA:\s*([\d.]+)", academic_text)
                profile_data['cgpa'] = cgpa_match.group(1) if cgpa_match else "Not Found"
            except NoSuchElementException:
                print("    - Could not find academic info box.")
                profile_data.update({'academic_standing': 'Not Found', 'semester': 'Not Found', 'cgpa': 'Not Found'})

            # --- CREDITS INFO: Find and safely parse ---
            try:
                credits_text = self.driver.find_element(*self._get_locator("dashboard.credits_info_box")).text
                completed_match = re.search(r"Completed Cr\. / Total Cr:\s*([\d.]+)", credits_text)
                profile_data['completed_credits'] = completed_match.group(1) if completed_match else "Not Found"
                
                inprogress_match = re.search(r"Inprogress Cr :\s*([\d.]+)", credits_text)
                profile_data['inprogress_credits'] = inprogress_match.group(1) if inprogress_match else "Not Found"
            except NoSuchElementException:
                print("    - Could not find credits info box.")
                profile_data.update({'completed_credits': 'Not Found', 'inprogress_credits': 'Not Found'})

            # --- TODAY'S CLASSES: Find and safely parse ---
            try:
                classes_text = self.driver.find_element(*self._get_locator("dashboard.today_classes_box")).text
                profile_data['today_classes'] = classes_text.split(":")[-1].strip()
            except NoSuchElementException:
                print("    - Could not find today's classes box.")
                profile_data['today_classes'] = 'Not Found'

            self.erp_data['profile'] = profile_data
            print("    - Dashboard scraped successfully.")
        except Exception as e:
            print(f"    - ⚠️ An unexpected error occurred while scraping dashboard: {e}")
            if 'profile' not in self.erp_data:
                self.erp_data['profile'] = {'student_name': 'Unknown_Student_ERROR'}

    def _scrape_attendance(self):
        print("--- 3. Scraping Attendance ---")
        try:
            self.driver.get(URLS["attendance"])
            # Wait for the container of the cards, which is more reliable
            cards_container = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self._get_locator("attendance_summary.subject_cards_container")))
            subject_cards = cards_container.find_elements(*self._get_locator("attendance_summary.subject_cards"))
            subject_urls = [card.find_element(By.TAG_NAME, 'a').get_attribute('href') for card in subject_cards]
            
            records = []
            for url in subject_urls:
                self.driver.get(url)
                # Wait for the actual data to appear, not just the page header
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self._get_locator("attendance_detail.course_name")))
                details = {
                    "course_name": self.driver.find_element(*self._get_locator("attendance_detail.course_name")).text.strip(),
                    "conducted": self.driver.find_element(*self._get_locator("attendance_detail.conducted_classes")).text.strip(),
                    "attended": self.driver.find_element(*self._get_locator("attendance_detail.attended_classes")).text.strip(),
                    "percentage": self.driver.find_element(*self._get_locator("attendance_detail.percentage")).text.strip()
                }
                records.append(details)
            self.erp_data['attendance'] = records
            print(f"    - Scraped attendance for {len(records)} courses.")
        except Exception as e:
            print(f"    - ⚠️ Error scraping attendance: {e}")

    
    def _scrape_results(self):
        print("--- 4. Scraping Results ---")
        try:
            self.driver.get(URLS["results"])
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self._get_locator("results_summary.page_header")))
            
            previous_courses_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(self._get_locator("results_summary.previous_courses_tab"))
            )
            previous_courses_tab.click()
            
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self._get_locator("results_summary.term_summary_rows"))
            )
            
            all_results = []
            current_semester_data = None
            
            all_rows = self.driver.find_elements(By.XPATH, "//table[contains(@class, 'table_tree')]/tbody/tr")

            for row in all_rows:
                row_class = row.get_attribute("class")
                
                if "table-parent-row" in row_class:
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    if len(cols) >= 6:
                        current_semester_data = {
                            "term": cols[0].text.strip(),
                            "gpa": cols[4].text.strip(),
                            "cgpa": cols[5].text.strip(),
                            "courses": []
                        }
                        all_results.append(current_semester_data)

                elif "table-child-row" in row_class and current_semester_data:
                    cols = row.find_elements(By.TAG_NAME, 'td')
                    if len(cols) == 4:
                        # --- FIX: Use .get_attribute('textContent') for hidden elements ---
                        course_detail = {
                            "course_name": cols[0].get_attribute('textContent').strip(),
                            "credits": cols[1].get_attribute('textContent').strip(),
                            "marks_obtained": cols[2].get_attribute('textContent').strip(),
                            "final_grade": cols[3].get_attribute('textContent').strip()
                        }
                        current_semester_data["courses"].append(course_detail)
            
            self.erp_data['semester_results'] = all_results
            print(f"    - Scraped detailed results for {len(all_results)} semesters.")
            
        except Exception as e:
            print(f"    - ⚠️ Error scraping results: {e}")




    def _scrape_invoices(self):
        print("--- 5. Scraping Invoices ---")
        try:
            self.driver.get(URLS["invoices"])
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self._get_locator("invoices_page.page_header")))
            rows = self.driver.find_elements(*self._get_locator("invoices_page.table_rows"))
            
            total_balance = 0.0
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 9:
                    try:
                        balance_float = float(cols[8].text.strip())
                        total_balance += balance_float
                    except ValueError: continue
            
            self.erp_data['financials'] = {"total_remaining_balance": total_balance}
            print(f"    - Calculated total remaining balance: {total_balance}")
        except Exception as e:
            print(f"    - ⚠️ Error scraping invoices: {e}")


    def _scrape_timetable(self):
        print("--- 6. Scraping Time Table ---")
        try:
            self.driver.get(URLS["timetable"])
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self._get_locator("timetable_page.header")))
            
            groups = self.driver.find_elements(*self._get_locator("timetable_page.day_groups"))
            timetable = {}
            
            for group in groups:
                day = group.find_element(By.XPATH, ".//div[@class='cd-schedule__top-info']/span").text
                timetable[day] = []
                
                events = group.find_elements(By.XPATH, ".//li[@class='cd-schedule__event']")
                
                for event in events:
                    anchor = event.find_element(By.TAG_NAME, 'a')
                    
                    # --- START: MODIFIED LOGIC ---
                    
                    # 1. Get the raw text, replacing newlines with a clear delimiter
                    full_details_string = anchor.text.replace('\n', ' | ')
                    
                    # 2. Prepare default values
                    course_name = full_details_string  # Default to the full string
                    venue = "N/A"
                    
                    # 3. Parse the string
                    try:
                        parts = [p.strip() for p in full_details_string.split('|')]
                        
                        if len(parts) > 0:
                            course_name = parts[0]  # The first part is the course name
                        
                        if len(parts) > 2:
                            venue = parts[2]  # The third part is the venue
                            
                    except Exception as e:
                        print(f"    - Could not parse event string: '{full_details_string}'. Error: {e}")

                    # 4. Append the structured dictionary to the timetable
                    timetable[day].append({
                        "time": f"{anchor.get_attribute('data-start')} - {anchor.get_attribute('data-end')}",
                        "details": course_name, # The cleaned course name
                        "venue": venue          # The extracted venue
                    })
                    
                    # --- END: MODIFIED LOGIC ---

            self.erp_data['timetable'] = timetable
            print(f"    - Found schedule for {len(timetable)} days.")
        except Exception as e:
            print(f"    - ⚠️ Error scraping timetable: {e}")


    def _scrape_enrolled_courses(self):
        print("--- 7. Scraping Enrolled Courses (Final Production Version) ---")
        try:
            self.driver.get(URLS["dashboard"])
            container_locator = (By.ID, "hierarchical-show")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(container_locator))
            
            course_cards = self.driver.find_elements(By.CSS_SELECTOR, "#hierarchical-show a")
            enrolled_courses = []
            
            print(f"    - Found {len(course_cards)} course cards. Parsing with final logic...")

            for card in course_cards:
                try:
                    # 1. Get the raw text content from the card. This is our single source of truth.
                    full_text_raw = card.get_attribute("textContent").strip()
                    if not full_text_raw:
                        continue
                        
                    # 2. Split the text into clean lines to get name, code, etc.
                    lines = [line.strip() for line in full_text_raw.split('\n') if line.strip()]
                    if not lines:
                        continue

                    # 3. Extract positional and labeled data with safety checks.
                    course_name = lines[0] if len(lines) > 0 else 'N/A'
                    course_code = lines[1] if len(lines) > 1 else 'N/A'
                    credits = 'N/A'
                    try:
                        credits_index = lines.index('Credits :')
                        if len(lines) > credits_index + 1:
                            credits = lines[credits_index + 1]
                    except ValueError:
                        pass

                    # 4. Normalize the raw text to handle all whitespace and newlines for status detection.
                    #    This is the key fix for "Grading in progress".
                    normalized_text = ' '.join(full_text_raw.split())

                    # 5. Check for status keywords in the NORMALIZED text. This is guaranteed to work.
                    status = 'N/A' # Default
                    if 'Active Class' in normalized_text:
                        status = 'Active Class'
                    elif 'Grading in progress' in normalized_text:
                        status = 'Grading in progress'

                    # 6. Append the final, correct data structure.
                    enrolled_courses.append({
                        'course_name': course_name,
                        'course_code': course_code,
                        'credits': credits,
                        'status': status
                    })

                except Exception as e:
                    print(f"    - Could not parse one course card. Skipping. Error: {e}")
                    
            self.erp_data['enrolled_courses'] = enrolled_courses
            print(f"    - Successfully parsed {len(enrolled_courses)} courses.")

        except Exception as e:
            print(f"    - ⚠️ FATAL Error during enrolled course scraping: {e}")
    def scrape_all_data(self):
        try:
            self._login()
            scraping_tasks = [
                self._scrape_dashboard, self._scrape_attendance, self._scrape_results,
                self._scrape_invoices, self._scrape_timetable,self._scrape_enrolled_courses
            ]
            for task in scraping_tasks:
                task()
            return self.erp_data
        except Exception as e:
            print(f"❌ A critical error occurred: {e}")
            self.driver.save_screenshot("critical_error_screenshot.png")
            return {"error": str(e)}
