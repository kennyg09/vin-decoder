import ttkbootstrap as tb
import requests, pprint
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.tooltip import ToolTip


root = tb.Window(themename="superhero")

def vin_check(vin):
    # Check format of VIN
    if vin.isalnum() and len(vin) == 17:
        return True
    else:
        return False

def title_keys(d):
    result = {}
    for key, value in d.items():
        upper_key = key.title()
        result[upper_key] = result.get(upper_key,value)
    return result


def veh_clean(d):
    result = []
    for key, value in d.items():
        if key in ['ModelYear','Make','Model','VIN','Manufacturer','BodyClass']:

            result.append (f'{key} - {value}\n')
            #result[key] = value
    return result

def safty_clean(d):
    result = {}
    for key, value in d.items():
        if key in [ 'ActiveSafetySysNote',
        'AdaptiveCruiseControl',
        'AdaptiveDrivingBeam',
        'AdaptiveHeadlights',
        'AdditionalErrorText',
        'AirBagLocCurtain',
        'AirBagLocFront',
        'AirBagLocKnee',
        'AirBagLocSeatCushion',
        'AirBagLocSide',
        'AutoReverseSystem',
        'AutomaticPedestrianAlertingSound',
        'BlindSpotIntervention',
        'BlindSpotMon',
        'ChargerLevel',
        'ChargerPowerKW',
        'DriverAssist',
        'EVDriveUnit',
        'ElectrificationLevel',
        'ForwardCollisionWarning',
        'LaneCenteringAssistance',
        'LaneDepartureWarning',
        'LaneKeepSystem',
        'OtherRestraintSystemInfo',
        'ParkAssist',
        'PedestrianAutomaticEmergencyBraking',
        'Pretensioner',
        'RearAutomaticEmergencyBraking',
        'RearCrossTrafficAlert',
        'RearVisibilitySystem',
        'SAEAutomationLevel',
        'SAEAutomationLevel_to',
        'SemiautomaticHeadlampBeamSwitching',]:

            result[key] = value
    return result

def list_data(dic):
    convert_list=[]
    for key, value in dic.items():
        convert_list.append(f'{key} - {value}\n')
    return convert_list



def process_input():
    safty_box.delete(1.0, tb.END)
    veh_info_body.delete(1.0, tb.END)
    response_box.delete(1.0, tb.END)
    user_input = input_box.get()

    if not vin_check(user_input):
        response_box.insert(tb.END, "Error: Invalid VIN format. VIN must be 17 alphanumeric characters.")
        input_box.delete(0, tb.END)
        return

    # Disable input while processing
    input_box.configure(state='disabled')
    vin_button.configure(state='disabled')
    
    # Show loading message
    response_box.insert(tb.END, "Loading data from NHTSA API...\n")
    root.update_idletasks()

    # Get data from database
    response = get_data(user_input)
    
    # Re-enable input
    input_box.configure(state='normal')
    vin_button.configure(state='normal')
    
    # Clear the loading message
    response_box.delete(1.0, tb.END)

    # Check for errors in response
    if "Error" in response:
        response_box.insert(tb.END, f"Error: {response['Error']}")
        input_box.delete(0, tb.END)
        return

    veh_list = veh_clean(response)
    safty_list = safty_clean(response)
    safty_new = list_data(safty_list)
    cleanlist = list_data(response)

    for item in safty_new:
        safty_box.insert(tb.END, item)

    for item in veh_list:
        veh_info_body.insert(tb.END, item)

    for item in cleanlist:
        response_box.insert(tb.END, item)

    input_box.delete(0, tb.END)


def get_data(vin):
    try:
        url = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/'
        post_fields = {'format': 'json', 'data':vin}
        r = requests.post(url, data=post_fields, timeout=10)  # Add timeout
        r.raise_for_status()  # Raise an exception for bad status codes
        data = r.json()
        results = data.get('Results', [])
        
        if not results:
            return {"Error": "No data returned from API"}
            
        df = results[0]
        cl = {k: v for k, v in df.items() if v and v != "Not Applicable"}
        return cl
        
    except requests.exceptions.RequestException as e:
        return {"Error": f"API Request failed: {str(e)}"}
    except (KeyError, IndexError, ValueError) as e:
        return {"Error": f"Error processing API response: {str(e)}"}

def clear_all():
    input_box.delete(0, tb.END)
    safty_box.delete(1.0, tb.END)
    veh_info_body.delete(1.0, tb.END)
    response_box.delete(1.0, tb.END)
    input_box.focus()


root.title("VIN Look up")
root.geometry("1500x800")


for i in range(3):
    root.columnconfigure(i, weight=1)
root.rowconfigure(0, weight=1)

# column 1
col1 = tb.Frame(root, padding=5)
col1.grid(row=0, column=0, sticky=NSEW)

input_vin = tb.LabelFrame(col1, text='Enter Vehicle Identification Number (VIN)', padding=10)
input_vin.pack(fill=BOTH, expand=YES,side=TOP,)

vin_info = tb.Label(input_vin, text="Enter a 17-character VIN to decode vehicle information", bootstyle="secondary")
vin_info.pack(pady=(0,5))

input_box = tb.Entry(input_vin,)
input_box.bind("<Return>",lambda e: process_input())
ToolTip(input_box, "Enter a 17-character Vehicle Identification Number")
input_box.focus()
input_box.pack(pady=5,side=TOP, padx=5)

button_frame = tb.Frame(input_vin)
button_frame.pack(pady=5, side=TOP, padx=5)

vin_button = tb.Button(button_frame, text="VIN Lookup", command=process_input, bootstyle="primary")
ToolTip(vin_button, "Click to decode the VIN")
vin_button.pack(pady=5, side=LEFT, padx=5)

clear_button = tb.Button(button_frame, text="Clear All", command=clear_all, bootstyle="secondary")
ToolTip(clear_button, "Click to clear all fields")
clear_button.pack(pady=5, side=LEFT, padx=5)


veh_info = tb.LabelFrame(col1, text='Basic Vehicle Information', padding=10)
veh_info.pack(fill=BOTH, expand=YES,side=BOTTOM,)

veh_info_header = tb.Frame(veh_info, padding=5)
veh_info_header.pack(fill=X)

lbl = tb.Label(veh_info,)
lbl.pack(side=LEFT, fill=X)

veh_info_body = tb.Text(master=veh_info,wrap=WORD, height=10, width=80)
veh_info_body.pack(fill=BOTH, expand=YES)

veh_info.rowconfigure(0, weight=1)
veh_info.columnconfigure(0, weight=0)


col2 = tb.Frame(root, padding=10)
col2.grid(row=0, column=1, sticky=NSEW)

safty_lable = tb.LabelFrame(col2, text='Safety Features & Equipment', padding=10)
safty_lable.pack(fill=BOTH, expand=YES,side=BOTTOM,)

safty_info = tb.Label(safty_lable, text="Displays vehicle safety features and equipment", bootstyle="secondary")
safty_info.pack(pady=(0,5))

safty_box = ScrolledText(safty_lable,width=100, height=100, padding=10, autohide=True,)
safty_box.pack()


col3 = tb.Frame(root, padding=10)
col3.grid(row=0, column=2, sticky=NSEW)

response_lable = tb.LabelFrame(col3, text='Complete Vehicle Details', padding=10)
response_lable.pack(fill=BOTH, expand=YES,side=BOTTOM,)

response_info = tb.Label(response_lable, text="Shows all available information for the vehicle", bootstyle="secondary")
response_info.pack(pady=(0,5))

response_box = ScrolledText(response_lable,width=100, height=100, padding=10, autohide=True)
response_box.pack()






root.mainloop()
