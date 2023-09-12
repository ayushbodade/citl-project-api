import requests

# Set the API URL
base_url = 'http://localhost:5000'  # Replace with your server URL if needed

# Upload a file
files = {'file': open('/home/ayush/Desktop/projects/working/tests/sample.pdf', 'rb')}
upload_response = requests.post(f'{base_url}/upload', files=files)

if upload_response.status_code == 200:
    file_path = upload_response.json().get('file_path')

    # Ask a question
    data = {
        'file_path': file_path,
        'prompt': 'What is the main topic of this report?'
    }
    ask_response = requests.post(f'{base_url}/ask', data=data)

    if ask_response.status_code == 200:
        response_data = ask_response.json()
        print('Response:', response_data['response'])
    else:
        print('Error:', ask_response.text)
else:
    print('Error:', upload_response.text)