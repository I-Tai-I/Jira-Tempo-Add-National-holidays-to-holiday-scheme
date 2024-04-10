import datetime
import holidays
import requests
import json

def add_holidays_to_scheme(tempo_api_token:str, tempo_holiday_scheme_ID:str, nation:str="dk", years_to_add:int=10):
    """ Adds national holidays of {nation} to {tempo_holiday_scheme_ID} for the next {years_to_add} years.
    
        Args: 
            - tempo_api_token:          string token from Jira tempo API integration. (Go to https://{your-jira-account}.atlassian.net/plugins/servlet/ac/io.tempo.jira/tempo-app#!/configuration/api-integration to create an API token)
            - tempo_holiday_scheme_ID:  string with ID of the holiday scheme that needs updating.
            - nation:                   string country code of the national holidays you want imported.
            - years_to_add:             int number of how many future years you want to add holidays to, including the current year.
            
        returns: dict of added and existing holidays, each list of tuples containing date and name of holiday, for added and already existing holidays respectively.
    """
    # Create a range of years for the next 10 years
    current_year = datetime.datetime.now().year
    years = range(current_year, current_year + years_to_add)

    # Create an instance of Danish holidays
    danish_holidays = holidays.country_holidays(nation) #holidays.Denmark(years=years, language="dk")
    url = f"https://api.tempo.io/4/holiday-schemes/{tempo_holiday_scheme_ID}/holidays"

    status_dict = {'added': [], 'existing': []}
    # Iterate through each year and print out the holidays
    for year in years:
        existing_holidays = requests.get(url+"?year="+str(year), headers={"Authorization": f"Bearer {tempo_api_token}",'Content-Type': 'application/json'}).json()['results']
        eh_dates = [eh['date'] for eh in existing_holidays]
        print(f"Holidays already in {year}:")
        for eh in existing_holidays:
          print(f"\t{eh['date']}: {eh['name']}")
        print(f"Holidays in {year}:")
        for date, name in sorted(danish_holidays.items()):
            if date.year == year:
                if any(str(date) == str(fixed_d) for fixed_d in eh_dates):
                    status_dict['existing'].append((date,name))
                    print(f"\t{date}: {name} (Already there, not added)")
                else:
                    json_data = json.dumps({
                        "date": str(date),
                        "description": "Autoimported with Tai's Jira Holiday Importer",
                        "durationSeconds": 86400,
                        "name": name,
                        "type": "FLOATING"
                    })
                    added_holiday = requests.post(url, data=json_data, headers={"Authorization": f"Bearer {tempo_api_token}",'Content-Type': 'application/json'})
                    status_dict['added'].append((date,name))
                    print(f"\t{date}: {name} ({added_holiday})")
        print("\n")
    return status_dict