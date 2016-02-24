from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# The idea is that we will loop through each reservation page
# based on the data below.  When we reach one which is available,
# we will enter reservation info and take the user to checkout -
# at this point the reservation is held for 15 minutes and the user
# can enter payment details.

RETRIES = 1							# Number of initial retries
ARV_DATE = '01/01/2016'				# Arrival Date in MM/DD/YYYY format
LENGTH_OF_STAY = '1'				# Number of nights
USERNAME = ''						# Recreation.gov username
PASSWORD = ''						# Recreation.gov password
NUM_OCCUPANTS = '1'					# Number of campers
NUM_VEHICLES = '1'					# Number of vehicles
EQUIPMENT_TYPE = '108060'			# EQUIPMENT TYPES:
										# 0: None
										# 108068: Caravan/Camper Van
										# 108067: Fifth Wheel
										# 108660: Pickup Camper
										# 108061: Pop up
										# 108063: RV/Motorhome
										# 108060: Tent
										# 108062: Trailer
SITES = [							# Parks & sites to search through.
	{								# See README.md for details on how
		'park_id': '70924',			# to find site IDs.
		'site_id': '204308'
	},
	{
		'park_id': '70924',
		'site_id': '204309'
	},
	{
		'park_id': '70924',
		'site_id': '205951'
	}
]

url_request = 'http://www.recreation.gov/campsiteDetails.do?siteId={site_id}&contractCode=NRSO&parkId={park_id}&arvdate=' + ARV_DATE + '&lengthOfStay=' + LENGTH_OF_STAY

driver = webdriver.Firefox()
# Check if sites are available yet - if not refresh

# Find an available site
selected_site = False

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
			if border_color == 'rgba(218, 218, 218, 1)':
				return site
		except Exception as e:
			print(e)

selected_site = checksites()

# if we've got a selected_site, automate the booking process

if selected_site:
	# Click book button
	driver.find_element_by_id('btnbookdates').click()

	# Enter username
	username_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#emailGroup input')))
	username_field.send_keys(USERNAME);

	# Enter password
	password_field = driver.find_element_by_css_selector('#passwrdGroup input')
	password_field.send_keys(PASSWORD);

	# Click login button
	driver.find_element_by_id('submitForm_submitForm').click()

	# Check if Primary Equipment field is readonly, if not set a value
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
else:
	print('No available sites.')

