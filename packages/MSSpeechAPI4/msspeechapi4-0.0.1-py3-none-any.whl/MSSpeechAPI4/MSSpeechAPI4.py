import urllib.parse
import requests
import pygame
import os

output_directory = os.getcwd()
def download_file(url, filename):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Write the content of the response to a file
        with open(os.path.join(output_directory, filename), 'wb') as f:
            f.write(response.content)
    else:
        print("Failed to download file from URL")

def Say(string, voice, pitch2, speed2):
    # String to encode
    input_string = string
    input_voice = voice
    pitch = str(pitch2)
    speed = str(speed2)

    # Encode the string
    encoded_string = urllib.parse.quote(input_string)
    encoded_voice = urllib.parse.quote(input_voice)

    urli = "https://tetyys.com/SAPI4/SAPI4?text=" + encoded_string + "&voice=" + encoded_voice + "&pitch=" + pitch + "&speed=" + speed

    # URL of the WAV file
    wav_url = urli
    # Name of the downloaded file
    wav_filename = "audio.wav"

    # Download the WAV file
    download_file(wav_url, wav_filename)

    # Initialize pygame mixer
    pygame.mixer.init()

    # Load the WAV file
    pygame.mixer.music.load(output_directory + "/" + wav_filename)
    
    # Play the WAV file
    pygame.mixer.music.play()

    # Wait until the music finishes playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.quit()

    os.remove(output_directory + "/" + wav_filename)

