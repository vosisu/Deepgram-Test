#---CODE---test example
#error: Could not open socket: 'Version' object is not callable
# Example filename: main.py
import os
import httpx
from dotenv import load_dotenv
import threading
import keys as keys #API key in file
import websockets

from deepgram import (
    Deepgram,
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)

load_dotenv()

# URL for the realtime streaming audio you would like to transcribe
URL = "http://stream.live.vc.bbcmedia.co.uk/bbc_world_service"

API_KEY = os.getenv(keys.deepgram) #API key in file

def main():
    try:
        # STEP 1: Create a Deepgram client using the API key
        deepgram = DeepgramClient(API_KEY)
        print('step1')

        # STEP 2: Create a websocket connection to Deepgram
        dg_connection = deepgram.listen.websocket()
        print ('step2')

        # STEP 3: Define the event handlers for the connection
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            print(f"speaker: {sentence}")

        def on_metadata(self, metadata, **kwargs):
            print(f"\n\n{metadata}\n\n")

        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")
        print ('step3')

        # STEP 4: Register the event handlers
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        print ('step4')

        # STEP 5: Configure Deepgram options for live transcription
        options = LiveOptions(
            model="nova-2", 
            language="en-US", 
            smart_format=True,
            )
        print ('step5')
        
        # STEP 6: Start the connection
        dg_connection.start(options)
        print ('step6')

        # STEP 7: Create a lock and a flag for thread synchronization
        lock_exit = threading.Lock()
        exit = False
        print ('step7')

        # STEP 8: Define a thread that streams the audio and sends it to Deepgram
        def myThread():
            with httpx.stream("GET", URL) as r:
                for data in r.iter_bytes():
                    lock_exit.acquire()
                    if exit:
                        break
                    lock_exit.release()

                    dg_connection.send(data)
        print ('step8')

        # STEP 9: Start the thread
        myHttp = threading.Thread(target=myThread)
        myHttp.start()
        print ('step9')

        # STEP 10: Wait for user input to stop recording
        input("Press Enter to stop recording...\n\n")
        print ('step10')

        # STEP 11: Set the exit flag to True to stop the thread
        lock_exit.acquire()
        exit = True
        lock_exit.release()
        print ('step11')

        # STEP 12: Wait for the thread to finish
        myHttp.join()
        print ('step12')
        # STEP 13: Close the connection to Deepgram
        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

if __name__ == "__main__":
    main()
