#!/usr/bin/env python

import os
import ast
import ConfigParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

config = ConfigParser.ConfigParser()

config.read('checker.ini')

# The idea is that we will loop through each reservation page
# based on the data below.  When we reach one which is available,
# we will enter reservation info and take the user to checkout -
# at this point the reservation is held for 15 minutes and the user
# can enter payment details.

RETRIES = int(config.get("common", "retries"))
USERNAME = config.get("common", "username")
PASSWORD = config.get("common", "password")
NUM_RESERVATIONS = int(config.get("common", "num_reservations"))

firefoxProfile = FirefoxProfile()
firefoxProfile.set_preference('browser.migration.version', 9001)
firefoxProfile.set_preference('permissions.default.image', 2)
firefoxProfile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

def checksites():
	site_ready = False
	num_retries = 0

	# Loop through sites
	for site in SITES:

		url = url_request.format(**site)
		driver.get(url)

		# First check if this is reservable yet - refresh if it's not
		while site_ready == False:
			# avail1 is the first date box on the page - if there's an 'N' in it,
			# then the site is not yet available for reservations
			elem = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'avail1')))
			if elem.text == 'N':
				if num_retries < RETRIES:
					print('Not yet reservable, retrying...')
					num_retries += 1
					driver.refresh()
				else:
					print('Not yet reservable. Exceeded number of retries.')
					return False
			# sites are now reservable, exit while loop
			else:
				site_ready = True

		# check the border of the arrival date field - a red border indicates
		# the selection is not available. if we find a site, return the value
		try:
			border_color = driver.find_element_by_id('arrivaldate').value_of_css_property('border-top-color')
			if border_color != 'rgb(255, 72, 0)':
				return site
		except Exception as e:
			print(e)

# Error checker
def checkerrors():
	site_ready = False
	num_retries = 0
	while site_ready == False:
		error = None
		try:
			error = driver.find_element_by_css_selector('#msg1')
		except:
			pass
		if error != None:
			if num_retries < RETRIES:
				print('Site error: ' + error.text)
				num_retries += 1
				driver.refresh()
			else:
				print('Site error. Exceeded number of retries.')
				return False
		else:
			site_ready = True
	return True

for i in range(NUM_RESERVATIONS):

	count = str(i + 1)

	driver = webdriver.Firefox(firefoxProfile)
	driver.maximize_window()

	ARV_DATE = config.get("reservation_" + count, "arv_date")
	LENGTH_OF_STAY = config.get("reservation_" + count, "length_of_stay")
	NUM_OCCUPANTS = config.get("reservation_" + count, "num_occupants")
	NUM_VEHICLES = config.get("reservation_" + count, "num_vehicles")
	EQUIPMENT_TYPE = config.get("reservation_" + count, "equipment_type")
	SITES = ast.literal_eval(config.get("reservation_" + count, "sites"))

	print SITES

	url_request = 'http://www.recreation.gov/campsiteDetails.do?siteId={site_id}&contractCode=NRSO&parkId={park_id}&arvdate=' + ARV_DATE + '&lengthOfStay=' + LENGTH_OF_STAY

	# Check if sites are available yet - if not refresh

	# Find an available site
	selected_site = False
	
	selected_site = checksites()
	# if we've got a selected_site, automate the booking process

	if selected_site:
		# Click book button
		driver.find_element_by_id('btnbookdates').click()

		# Check to see if we got an error, if so refresh
		WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#contentArea')))
		noerrors = checkerrors();

		if (noerrors):
			# Enter username
			username_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#emailGroup input')))
			username_field.send_keys(USERNAME);

			# Enter password
			password_field = driver.find_element_by_css_selector('#passwrdGroup input')
			password_field.send_keys(PASSWORD);

			# Click login button
			driver.find_element_by_name('submitForm').click()

			# Check if Primary Equipment field is readonly, if not set a value
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "equip")))
			if driver.find_element_by_id('equip').is_enabled():
				driver.find_element_by_css_selector("select#equip > option[value='" + EQUIPMENT_TYPE + "']").click()

			# Set number of occupants
			driver.find_element_by_id('numoccupants').send_keys(NUM_OCCUPANTS)

			# Set number of vehicles
			driver.find_element_by_id('numvehicles').send_keys(NUM_VEHICLES)

			# Click "Yes, I have read and understood this important information"
			driver.find_element_by_id('agreement').click()

			# Click "Continue to Shopping Cart" button
			driver.find_element_by_id('continueshop').click()

			print "You have 15 minutes to complete this reservation in the browser window."
			
		else:
			print('No available sites. (L2)')
	else:
		print('No available sites. (L1)')

