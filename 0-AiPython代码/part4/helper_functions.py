#import gradio as gr
import os

from openai import OpenAI
from dotenv import load_dotenv
import ipywidgets as widgets
from IPython.display import display, HTML
import io
import csv
import pandas as pd 
import base64

parent_dir = os.path.dirname(os.getcwd())
# Get the OpenAI API key from the .env file
env_path = os.path.join( parent_dir, '.env')
load_dotenv(env_path, override=True)
# print(f"✅ 已加载 .env: {env_path}")

# 模型url
base_url = os.getenv('BASE_URL')
# 模型apikey
api_key = os.getenv('API_KEY')
# 模型名称
model_name = os.getenv('MODEL_NAME')

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

def print_llm_response(prompt):
    """This function takes as input a prompt, which must be a string enclosed in quotation marks,
    and passes it to OpenAI's GPT3.5 model. The function then prints the response of the model.
    """
    try:
        if not isinstance(prompt, str):
            raise ValueError("Input must be a string enclosed in quotes.")
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful but terse AI assistant who gets straight to the point.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        response = completion.choices[0].message.content
        print(response)
    except TypeError as e:
        print("Error:", str(e))


def get_llm_response(prompt):
    """This function takes as input a prompt, which must be a string enclosed in quotation marks,
    and passes it to OpenAI's GPT3.5 model. The function then saves the response of the model as
    a string.
    """
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful but terse AI assistant who gets straight to the point.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
    )
    response = completion.choices[0].message.content
    return response


def get_chat_completion(prompt, history):
    history_string = "\n\n".join(["\n".join(turn) for turn in history])
    prompt_with_history = f"{history_string}\n\n{prompt}"
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful but terse AI assistant who gets straight to the point.",
            },
            {"role": "user", "content": prompt_with_history},
        ],
        temperature=0.0,
    )
    response = completion.choices[0].message.content
    return response


def display_html(html):
    display(HTML(html))

def read_journal(file_path):
    f = open(file_path, "r")
    journal = f.read()
    f.close()
    
    return journal


def create_download_link(file_path, description):
    with open(file_path, 'rb') as file:
        file_data = file.read()
        encoded_data = base64.b64encode(file_data).decode()
        href = f'<a href="data:text/html;base64,{encoded_data}" download="{file_path}">{description}</a>'
        return HTML(href)


def read_csv_dict(csv_file_path):
    """This function takes a csv file and loads it as a dict."""

    # Initialize an empty list to store the data
    data_list = []

    # Open the CSV file
    with open(csv_file_path, mode='r') as file:
        # Create a CSV reader object
        csv_reader = csv.DictReader(file)
    
        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Append the row to the data list
            data_list.append(row)

    # Convert the list to a dictionary
    data_dict = {i: data_list[i] for i in range(len(data_list))}
    return data_dict


def upload_txt_file():
    """
    Uploads a text file and saves it to the specified directory.
    
    Args:
        directory (str): The directory where the uploaded file will be saved. 
        Defaults to the current working directory.
    """
    # Create the file upload widget
    upload_widget = widgets.FileUpload(
        accept='.txt',  # Accept text files only
        multiple=False  # Do not allow multiple uploads
    )
    # Impose file size limit
    output = widgets.Output()

    # Function to handle file upload
    def handle_upload(change):
        with output:
            output.clear_output()
            # Read the file content
            content = upload_widget.value[0]['content']
            name = upload_widget.value[0]['name']
            size_in_kb = len(content) / 1024
            
            if size_in_kb > 3:
                print(f"Your file is too large, please upload a file that doesn't exceed 3KB.")
                return
		    
            # Save the file to the specified directory
            with open(name, 'wb') as f:
                f.write(content)
            # Confirm the file has been saved
            print(f"The {name} file has been uploaded.")

    # Attach the file upload event to the handler function
    upload_widget.observe(handle_upload, names='value')

    display(upload_widget, output)


def read_journal(journal_file):
    f = open(journal_file, "r")
    journal = f.read() 
    f.close()
    return journal

def create_download_link(file_path, description):
    with open(file_path, 'rb') as file:
        file_data = file.read()
        encoded_data = base64.b64encode(file_data).decode()
        href = f'<a href="data:text/html;base64,{encoded_data}" download="{file_path}">{description}</a>'
        return HTML(href)

def download_file():
    """
    Creates a widget to download a file from the working directory.
    """
    # Text input to specify the file name
    file_name_input = widgets.Text(
        value='',
        placeholder='Enter file name',
        description='File:',
        disabled=False
    )
    
    # Button to initiate the download
    download_button = widgets.Button(
        description='Download',
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Download the specified file',
        icon='download' # (FontAwesome names without the `fa-` prefix)
    )
    
    # Output widget to display the download link
    output = widgets.Output()

    def on_button_click(b):
        with output:
            output.clear_output()
            file_name = file_name_input.value
            if (not file_name.startswith('.') and not file_name.startswith('_')):
                try:
                    download_link = create_download_link(file_name, 'Click here to download your file')
                    display(download_link)
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Please enter a valid file name.")
    
    # Attach the button click event to the handler
    download_button.on_click(on_button_click)
    
    # Display the widgets
    display(widgets.HBox([file_name_input, download_button]), output)
    
def list_files_in_directory(directory='.'):
    """
    Lists all non-hidden files in the specified directory.
    
    Args:
        directory (str): The directory to list files from. Defaults to the current working directory.
    """
    try:
        files = [f for f in os.listdir(directory) if (not f.startswith('.') and not f.startswith('_'))]
        for file in files:
            print(file)
    except Exception as e:
        print(f"An error occurred: {e}")



def display_table(data):
    df = pd.DataFrame(data)

    # Display the DataFrame as an HTML table
    display(HTML(df.to_html(index=False)))


def celsius_to_fahrenheit(celsius):
    fahrenheit = celsius * 9 / 5 + 32 
    print(f"{celsius}°C is equivalent to {fahrenheit:.2f}°F")


def beautiful_barh(labels, values):
	# Create the bar chart
	plt.figure(figsize=(9, 5))
	bars = plt.barh(labels, values, color = plt.cm.tab20.colors)

	for bar in bars:
		plt.text(bar.get_width()/2,   # X coordinate 
			 bar.get_y() + bar.get_height()/2,  # Y coordinate 
			 f'${bar.get_width() / 1e9:.1f}B',  # Text label 
			 ha='center', va='center', color='w', fontsize=10, fontweight = "bold")
			 
	# Customizing the x-axis to display values in billions
	def billions(x, pos):
		"""The two args are the value and tick position"""
		return f'${x * 1e-9:.1f}B'

	formatter = FuncFormatter(billions)
	plt.gca().xaxis.set_major_formatter(formatter)


	# Inverting the y-axis to have the highest value on top
	plt.gca().invert_yaxis()


def display_map():
    # Define the bounding box for the continental US
    us_bounds = [[24.396308, -125.0], [49.384358, -66.93457]]
    # Create the map centered on the US with limited zoom levels
    m = folium.Map(
	    location=[37.0902, -95.7129],  # Center the map on the geographic center of the US
	    zoom_start=5,  # Starting zoom level
	    min_zoom=4,  # Minimum zoom level
	    max_zoom=10,
	    max_bounds=True,
	    control_scale=True  # Maximum zoom level
	)

    # Set the bounds to limit the map to the continental US
    m.fit_bounds(us_bounds)
    # Add a click event to capture the coordinates
    m.add_child(folium.LatLngPopup())
    title_html = '''
	<div style="
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%; 
	height: 50px; 
	border:0px solid grey; 
	z-index:9999; 
	font-size:30px;
	padding: 5px;
	background-color:white;
	text-align: center;
	">
	&nbsp;<b>Click to view coordinates</b>
	</div>
	'''
	
    m.get_root().html.add_child(folium.Element(title_html))

    # Display the map
    return m
    
def get_forecast(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"

    # Make the request to get the grid points
    response = requests.get(url)
    data = response.json()
    # Extract the forecast URL from the response
    forecast_url = data['properties']['forecast']

    # Make a request to the forecast URL for the selected location
    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()
    
    daily_forecast = forecast_data['properties']['periods']
    return daily_forecast

    
def celsius_to_fahrenheit(celsius):
    fahrenheit = celsius * 9 / 5 + 32 
    print(f"{celsius}°C is equivalent to {fahrenheit:.2f}°F")
    
