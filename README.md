# delivery_updates_tts
Python application that retrieves the latest status of your food delivery.
Built around Google Home and Home Assistant, with requests delivered by voice and updates provided using text-to-speech.
Note: This is intended to retrieve your only personal orders only, using the as-built updates from the delivery service.

# Usage
1. Install dependencies (recommend using virtualenv): flask, aenum, lxml, requests
2. Add custom config.json file using config_example.json as a template
3. Run: python application.py
Note: Make sure to properly using NAT'd IPs, WAN IPs, and port forwarding depending on configuration

# Example
This example uses Google Home + IFTTT/Maker + Home Assistant
1. Start Home Assistant
2. Configure delivery_updates_tts
  * Set service password
  * Set "update_url" to the google_say endpoint from Home Assistant
  * Add Caviar credentials
3. Create a new IFTTT applet
  * "This" = Google Assistant for "Say Phrase with a text ingredient" as "Where is my $ order?"
  * "That" = Maker web request
    * URL = "http://Service_IP:5035/api/getstatus?password=your_password"
      * Service_IP = The accessible IP for the delivery_updates_tts 
      * your_password = Password configured in config.json
    * Method = "POST"
    * Content type = "application/json"
    * Body = "{"service": "{{TextField}}"}"
      * TextField = The ingredient from Google Assistant
4. Start delivery_updates_tts
5. Ask Google Home "Where is my Caviar order?"
6. Google Home responds with the update from Caviar

# Limitations
* Only supported delivery service is Caviar
* Service only looks at the latest order, with an order time within the past 4 hours
