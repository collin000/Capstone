import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify, request
from time import sleep
import board
import busio

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)

# define variables

robotStatus = {'motor1': 0, 'motor2': 0}
lastAction = "stop"

# motor control functions

try:
    # define an Adafruit Motor kit object

    from adafruit_motorkit import MotorKit

    kit = MotorKit(i2c=board.I2C())
    print('Adafruit Motor kit library available.')


    def set_speeds(power_left, power_right):
        
        print(power_left, power_right)

        kit.motor1.throttle = power_right
        kit.motor2.throttle = power_right
        kit.motor3.throttle = power_left
        kit.motor4.throttle = power_left


    def stop_motors():

        set_speeds(0, 0)

except ImportError:

    def set_speeds(power_left, power_right):
        print('Left: {}, Right: {}'.format(power_left, power_right))
        sleep(0.1)


    def stop_motors():
        print('Motors stopping')

# define the Web app

app = Flask(__name__)

# setup the GPIOs pins used

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Display back light pin, this could be a LED instead
display = 26

# Define display pin as output
GPIO.setup(display, GPIO.OUT)

# and turn it off
GPIO.output(display, GPIO.LOW)


# Web routes ie. index.html and the setting motor speeds ie. /motors/forward

# site index page

@app.route("/")
def index():
    templateData = {
        'title': 'Wifi Robot',
    }
    return render_template('index2.html', **templateData)


# motor control is /motor then the action /forward or /left

@app.route("/<deviceName>/<action>/")
def action(deviceName, action):
    global robotStatus, lastAction

    if deviceName == 'motor' and lastAction != action:
        print(f"action: {action}")
        if action == "off":
            robotStatus["motor1"] = 0
            robotStatus["motor2"] = 0
            stop_motors()

        if action == "forward":
            robotStatus["motor1"] = 1
            robotStatus["motor2"] = 1

        if action == "backward":
            robotStatus["motor1"] = -1
            robotStatus["motor2"] = -1

        if action == "left":
            robotStatus["motor1"] = -1
            robotStatus["motor2"] = 1

        if action == "right":
            robotStatus["motor1"] = 1
            robotStatus["motor2"] = -1

        # set motor speeds
        set_speeds(robotStatus["motor1"], robotStatus["motor2"])

    lastAction = action
    print(f"last action: {lastAction}")

    return jsonify(robotStatus)

if __name__ == "__main__":
    app.run(host='172.61.58.132', port=5080, debug=False)  # debug switched off and port 5080
