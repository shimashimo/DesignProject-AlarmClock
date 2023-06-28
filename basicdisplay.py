from machine import Pin, SPI, I2C, Timer # SPI is a class associated with the machine library. 
import utime
from utime import localtime

# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display.
from RadioClass import Radio #this is another library imported for the radio functionality of the clock


# Define columns and rows of the oled display. These numbers are the standard values. 
SCREEN_WIDTH = 128 #number of columns
SCREEN_HEIGHT = 64 #number of rows


# Initialize I/O pins associated with the oled display SPI interface
spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(21) # res stands for reset; to be connected to a free GPIO pin
spi_dc  = Pin(20) # dc stands for data/command; to be connected to a free GPIO pin
spi_cs  = Pin(17) # chip select; to be connected to the SPI chip select of the Pico 


# SPI Device ID can be 0 or 1. It must match the wiring. 
SPI_DEVICE = 0 # Because the peripheral is connected to SPI 0 hardware lines of the Pico


# initialize the SPI interface for the OLED display
oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )

# Initialize the display
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True )

# Assign pushbutton 1, 2, 3, and 4 to Pico Pin
menu_button = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
up_button = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
down_button = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
select_button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

led_onboard = machine.Pin(25, machine.Pin.OUT)

def convert_time_12hour(Dhour, ap_hour_format): #Pass in the 24 hour time
    global am_pm

    print("Convert to 12 hour called")
    print("Dhour: ", Dhour)
    print("AM or PM: ", am_pm)
    print("AM PM Boolean: ", ap_hour_format)

    # Already in 12 hour format
    if(ap_hour_format == True):
        return Dhour

    # 24 hour format - 00:00 to 11:59 is AM, 12:00 to 23:59 is PM
    # Therefore, when Dhour is between 0 and 11 = AM,
    # When Dhour between 12 and 23, PM
    if(Dhour > 12):
        print("> 12")
        am_pm = "PM"
        return (Dhour - 12)
    elif(Dhour == 12):
        print(" == 12")
        am_pm = "PM"
        return 12
    else:
        print("< 12")
        am_pm = "AM"
        return Dhour
    
def convert_to_24(Dhour, am_pm, ap_hour_format): # Pass in 12 hour time

    print("Convert to 24 hour called")
    print("Dhour: ", Dhour)
    print("AM or PM: ", am_pm)
    print("AM PM Boolean: ", ap_hour_format)
    
    # If 12 hour format is already false, don't need to convert time again because already in 24 hour format
    if(ap_hour_format == False):
        return Dhour
    
    if(am_pm == "AM" and Dhour == 12):
        print("returning 0")
        return 0
    
    elif(am_pm == "AM"):
        print("in am_pm = AM")
        return Dhour
    
    elif(am_pm == "PM" and Dhour == 12):
        print("in am_pm == pm and Dhour == 12")
        return Dhour
    
    else:
        print("am_pm == PM and returnin Dhour + 12")
        return (Dhour + 12)



def state_handler(pin):
    global count, last_time_pressed, menu_button
    new_time = utime.ticks_ms()
    if (new_time - last_time_pressed) > 200:
        count += 1
        last_time_pressed = new_time

def up_handler(pin):
    global count, selectcount, last_time_pressed, volume, handlerhour, handlermin, handlersec
    global ap_hour_format, am_pm, Dhour, Dmin, update_time_flag
    new_time = utime.ticks_ms()
    
    print("up irq called")
    
    # Debounce
    if (new_time - last_time_pressed) > 200:
        last_time_pressed = new_time
        
        if(count == 1):
            Dhour = convert_to_24(Dhour, am_pm, ap_hour_format)
            update_time_flag = True
            ap_hour_format = False
            print("ap_hour is False")
            
        if(count == 2):
            # Increase Hour Time
            if(selectcount == 0):

                # Edit time in 12 Hour format
                if(ap_hour_format == True):
                    if(Dhour < 12):
                        Dhour = Dhour + 1
                    else:
                        # Dhour is > 12 so reset Dhour back to 1
                        Dhour = 1
                        print("After modifying time", Dhour)
                
                # Edit time in 24 hour format
                else:   
                    print("In 24 hour time update")
                    if(Dhour < 23):
                        Dhour = Dhour + 1
                        print(Dhour)
                    else:
                        # if Dhour is 24, reset back to 0
                        Dhour = 0
               
            # Increase Min Time
            elif(selectcount == 1):
                if(Dmin < 59):
                    Dmin = Dmin + 1
                else:
                    #DMin is 59, so if incremented reset back to 0
                    Dmin = 0

            # Edit AM or PM
            elif(selectcount == 2 and ap_hour_format == True):
                global am_pm
                if(am_pm == "AM"):
                    am_pm = "PM"
                else:
                    am_pm = "AM"
            
            # Set time updated flag so we know to use updated time object.
            update_time_flag = True
            
                
        if(count == 3):
            if(selectcount == 0):
                if(handlerhour < 24):
                    handlerhour = handlerhour + 1
                    print("Updating hour", handlerhour)
                else:
                    handlerhour = 0
                    
            if(selectcount == 1):
                if(handlermin < 60):
                    handlermin = handlermin + 1
                    print("Updating min", handlermin)
                else:
                    handlermin = 0
                    
            if(selectcount == 2):
                if(handlersec < 60):
                    handlersec = handlersec + 1
                    print("Updating sec", handlersec)
                else:
                    handlersec = 0
                
            
        if(count == 5):
            Settings = fm_radio.GetSettings()
            volume = Settings[1]
            print("Printing Current Volume in IRQ: %d" % volume)
            volume = volume + 1
            if ( fm_radio.SetVolume( volume ) == True ):
                fm_radio.ProgramRadio()
            else:
                print( "Invalid volume level( Range is 0 to 15 )" )
            last_time_pressed = new_time

def down_handler(pin):
    global count, selectcount, last_time_pressed, volume, handlerhour, handlermin, handlersec
    global ap_hour_format, Dhour, Dmin, update_time_flag
    new_time = utime.ticks_ms()
    
    print("down irq called")
    
    if (new_time - last_time_pressed) > 200:
        last_time_pressed = new_time
        
        if(count == 1):
            Dhour = convert_time_12hour(Dhour, ap_hour_format)
            update_time_flag = True
            ap_hour_format = True
            print("ap_hour is True")

        if(count == 2):
            if(selectcount == 0):
                print("Before modifying time", Dhour)
                if(ap_hour_format == True):
                    if(Dhour > 1):
                        Dhour = Dhour - 1
                    else:
                        # Dhour is 1 so reset Dhour back to 12
                        Dhour = 12
                        print("After modifying time", Dhour)
                else:
                    print("In 24 hour time update")
                    if(Dhour > 0):
                        Dhour = Dhour - 1
                        print(Dhour)
                    else:
                        # if Dhour is 0, reset back to 23
                        Dhour = 23
                        
            # Decrease Minutes Time
            elif(selectcount == 1):
                if(Dmin > 0):
                    Dmin = Dmin - 1
                else:
                    #DMin is 0, so if decremented rollback to 59
                    Dmin = 59
            
            # Edit AM or PM
            elif(selectcount == 2 and ap_hour_format == True):
                global am_pm
                if(am_pm == "AM"):
                    am_pm = "PM"
                else:
                    am_pm = "AM"

            update_time_flag = True
            
        if(count == 5):
            Settings = fm_radio.GetSettings()
            volume = Settings[1]
            print("Printing Current Volume in IRQ: %d" % volume)
            volume = volume - 1
            if ( fm_radio.SetVolume( volume ) == True ):
                fm_radio.ProgramRadio()
            else:
                print( "Invalid volume level( Range is 0 to 15 )" )
            last_time_pressed = new_time
   
def select_handler(pin):
    global count, selectcount, last_time_pressed
    new_time = utime.ticks_ms()
    
    # print("select irq called")
    
    if (new_time - last_time_pressed) > 200:
        last_time_pressed = new_time
        
        if(count == 2):
            selectcount += 1
            # print("select count is: ", selectcount)
        
        #If in set time setting and select button is presses increase select counter
        if(count == 3):
            selectcount = selectcount + 1
            print("select count in state 3 is: ", selectcount)
        
        if(count == 5):
            Settings = fm_radio.GetSettings()
            frequency = Settings[2]
            print("Printing Current Frequency in IRQ: %d" % frequency)
            frequency = frequency + 1
            if ( fm_radio.SetFrequency( frequency ) == True ):
                fm_radio.ProgramRadio()
            else:
                print( "Invalid volume level( Range is 0 to 15 )" )
            last_time_pressed = new_time
   
   
   
# Initialize time for button last pressed for debouncing button
last_time_pressed = 0

menu_button.irq(trigger=machine.Pin.IRQ_RISING, handler=state_handler)
up_button.irq(trigger=machine.Pin.IRQ_RISING, handler=up_handler)
down_button.irq(trigger=machine.Pin.IRQ_RISING, handler=down_handler)
select_button.irq(trigger=machine.Pin.IRQ_RISING, handler=select_handler)


# Initialize State Counter
count = 0

# Track 12 or 24 hour format - Default 24 hour
ap_hour_format = False

# Track whether AM or PM - Default AM
am_pm = "DE"
   
# Initialize Select Counter
selectcount = 0

# Creating an uninitialized timer
settimer = Timer()

handlersec = 0
handlermin = 0
handlerhour = 0

# Set flag for if alarm is going off
alarm = False

# Set flag for update to true
update_time_flag = False

rtc = machine.RTC()

while True:
    
    # Clear the buffer
    oled.fill(0)
    
    # Update Time object if updated
    if(update_time_flag == True):
        print("In updated time")
        print(Dhour)
        updated_time_vals = (Dyear, Dmonth, Dday, Dweekday, Dhour, Dmin, Dsec, Dsubseconds)
        rtc.datetime(updated_time_vals)

        # Needs time to set RTC? This fixed alternating Dhour bug
        utime.sleep_ms(10)

        update_time_flag = False
    
    timeObj = rtc.datetime()

    # print(timeObj)
        
    Dyear, Dmonth, Dday, Dweekday, Dhour, Dmin, Dsec, Dsubseconds = (timeObj)  
    cur_time = "{}:{}:{}"
    cur_date = "{}/{}/{}"
    cur_hour = "{}"
    cur_min = "{}"
    cur_sec = "{}"

    #Home state
    if(count == 0):
        
        fm_radio = Radio( 100.3, 0, True )
        
        #Display Time and Date on Home screen
        oled.text(cur_time.format(Dhour, Dmin, Dsec), 30, 10)
        oled.text(cur_date.format(Dday, Dmonth, Dyear), 25, 20)

        if(ap_hour_format == True):
            oled.text(am_pm, 100, 10)
        
        # Update the text on the screen
        oled.text("Count is: %4d" % count, 0, 50 ) # Print the value stored in the variable Count. #line of text is 7 pixels

        # Slow Output
        # utime.sleep_ms(50)
    
    #24 or 12 state
    elif(count == 1):

        fm_radio = Radio( 100.3, 0, True )
        oled.text("24 or 12", 25, 32 )
        oled.text("Count is: %4d" % count, 0, 50 )
            
        oled.text(cur_time.format(Dhour, Dmin, Dsec), 30, 10)
        if(ap_hour_format == True):
            oled.text(am_pm, 100, 10)

        # Slow Output
        # utime.sleep_ms(250)
        
    #Set/Edit time state
    elif(count == 2):
        fm_radio = Radio( 100.3, 0, True )
        
        # Check if 12 hour or 24 hour
        # if(ap_hour_format == True):
            # Dhour = convert_time_12hour(timeObj)
        
        
        # Blink the Hours to show minutes editing is selected
        if(selectcount == 0):
            
            oled.text("Set/Edit Time", 10, 10)

            # Buffer is cleared from the beginning of the While True loop,
            # and we want to display the current selection as off but show the min and sec
            # Once buffer is cleared, it will only display what is told after that ( in between oled.fill(0) and oled.show() )
            if(Dhour < 10):
                oled.text("0", 44, 30, 0)
                oled.text(cur_hour.format(Dhour), 52, 30, 0)
            else:
                oled.text(cur_hour.format(Dhour), 44, 30, 0)
                
            oled.text(":", 60, 30)
            
            if(Dmin < 10):
                oled.text("0", 68, 30)
                oled.text(cur_min.format(Dmin), 76, 30)
            else:
                oled.text(cur_min.format(Dmin), 68, 30)
            # oled.text(cur_sec.format(Dsec), 80, 30)

            if(ap_hour_format == True):
                oled.text(am_pm, 86, 30)

            oled.show()
            utime.sleep_ms(500)
            
            
            # Clear the buffer, ( i.e blank display )
            # tell to display the hour, min and sec
            oled.fill(0)
            oled.text("Set/Edit Time", 10, 10)


            if(Dhour < 10):
                oled.text("0", 44, 30, 1)
                oled.text(cur_hour.format(Dhour), 52, 30, 1)
            else:
                oled.text(cur_hour.format(Dhour), 44, 30, 1)

            oled.text(":", 60, 30)

            if(Dmin < 10):
                oled.text("0", 68, 30)
                oled.text(cur_min.format(Dmin), 76, 30)
            else:
                oled.text(cur_min.format(Dmin), 68, 30)
            # oled.text(cur_sec.format(Dsec), 80, 30)

            if(ap_hour_format == True):
                # print(am_pm)
                oled.text(am_pm, 86, 30)

            oled.show()
            utime.sleep_ms(500)
            
            
            
        # Blink the Mins to show minutes editing is selected
        elif(selectcount == 1):
            
            # print("In Mins Edit")
            oled.text("Set/Edit Time", 10, 10)
            
            # oled.fill(0)
            if(Dhour < 10):
                oled.text("0", 44, 30)
                oled.text(cur_hour.format(Dhour), 52, 30)
            else:
                oled.text(cur_hour.format(Dhour), 44, 30)
            
            oled.text(":", 60, 30)

            if(Dmin < 10):
                oled.text("0", 68, 30, 0)
                oled.text(cur_min.format(Dmin), 76, 30, 0)
            else:
                oled.text(cur_min.format(Dmin), 68, 30, 0)

            # oled.text(cur_sec.format(Dsec), 80, 30)

            if(ap_hour_format == True):
                oled.text(am_pm, 86, 30)

            oled.show()
             
            utime.sleep_ms(500)
            
            
            # Clear the buffer, ( i.e blank display )
            # tell to display the hour, min and sec
            oled.fill(0)

            oled.text("Set/Edit Time", 10, 10)

            if(Dhour < 10):
                oled.text("0", 44, 30)
                oled.text(cur_hour.format(Dhour), 52, 30)
            else:
                oled.text(cur_hour.format(Dhour), 44, 30)

            oled.text(":", 60, 30)

            if(Dmin < 10):
                oled.text("0", 68, 30, 1)
                oled.text(cur_min.format(Dmin), 76, 30, 1)
            else:
                oled.text(cur_min.format(Dmin), 68, 30, 1)
            
            # oled.text(cur_sec.format(Dsec), 80, 30)

            if(ap_hour_format == True):
                oled.text(am_pm, 86, 30)

            oled.show()
            utime.sleep_ms(500)
            
        # Edit Seconds
#         elif(selectcount == 2):
#             
#             oled.text(cur_min.format(Dmin), 55, 30)
#             oled.text(cur_hour.format(Dhour), 30, 30)
#             oled.text(cur_sec.format(Dsec), 80, 30, 0)
#             oled.show()
#             
#             utime.sleep_ms(500)
#             
#             
#             # Clear the buffer, ( i.e blank display )
#             # tell to display the hour, min and sec
#             oled.fill(0)
#             oled.text(cur_min.format(Dmin), 55, 30)
#             oled.text(cur_hour.format(Dhour), 30, 30)
#             
#             oled.text(cur_sec.format(Dsec), 80, 30, 1)
# 
#             oled.show()
#             utime.sleep_ms(500)

        # Edit AM/PM (Only editable when in 12 hour format)
        elif(selectcount == 2 and ap_hour_format == True):
            
            oled.fill(0)

            oled.text("Set/Edit Time", 10, 10)

            if(Dhour < 10):
                oled.text("0", 44, 30)
                oled.text(cur_hour.format(Dhour), 52, 30)
            else:
                oled.text(cur_hour.format(Dhour), 44, 30)
            
            oled.text(":", 60, 30)

            if(Dmin < 10):
                oled.text("0", 68, 30)
                oled.text(cur_min.format(Dmin), 76, 30)
            else:
                oled.text(cur_min.format(Dmin), 68, 30)

            # oled.text(cur_sec.format(Dsec), 80, 30)

            oled.text(am_pm, 86, 30, 0)

            oled.show()
             
            utime.sleep_ms(500)
            
            
            # Clear the buffer, ( i.e blank display )
            # tell to display the hour, min and sec
            oled.fill(0)

            oled.text("Set/Edit Time", 10, 10)

            if(Dhour < 10):
                oled.text("0", 44, 30)
                oled.text(cur_hour.format(Dhour), 52, 30)
            else:
                oled.text(cur_hour.format(Dhour), 44, 30)

            oled.text(":", 60, 30)

            if(Dmin < 10):
                oled.text("0", 68, 30)
                oled.text(cur_min.format(Dmin), 76, 30)
            else:
                oled.text(cur_min.format(Dmin), 68, 30)
            
            # oled.text(cur_sec.format(Dsec), 80, 30)

            oled.text(am_pm, 86, 30, 1)

            oled.show()
            utime.sleep_ms(500)
        


        elif(selectcount > 1 and ap_hour_format == False):
            selectcount = 0
        elif(selectcount > 2 and ap_hour_format == True):
            selectcount = 0
            
        # Skip rest of while loop, go to next iteration
        continue
        
    
    #Set alarm state
    elif(count == 3):
        fm_radio = Radio( 100.3, 0, True )

        

        # #oled.text("Alarm State", 25, 30 )
        # oled.text("Count is: %4d" % count, 0, 50 )
        # #If inputted time == cur_time, then make sound?
        
        # #in the up handler make a variable called handlersec that increases by one with push of the button
        # oled.text("%d" % handlerhour, 30, 30, 0)
        # if(selectcount == 0 ):
        #     oled.text(str(handlerhour), 30, 30, 0)
        # elif(selectcount == 1):
        #     oled.text(str(handlermin), 30, 30, 0)
        # elif(selectcount == 2):
        #     oled.text(str(handlersec), 30, 30, 0)
        # elif(selectcount > 2):
        #     selectcount = 0
            
        
        # #convert to ms
        # second = handlersec * 1000
        
        # minute = handlermin * 60 * 1000
        
        # hour = handlerhour * 60 * 60 * 1000

        
        
        #def mycallback():
        
        #settimer.init(mode = Timer.ONESHOT, period = (second + minute + hour), callback = mycallback )
        
        
        
        
    #Snooze or off state
        ## can probably combine this state with alarm state. If the alarm flag is True, then if menu_button pressed snooze, select_button for off?
    elif(count == 4):
        fm_radio = Radio( 100.3, 0, False )
        oled.text("Snooze State", 25, 30 )
        oled.text("Count is: %4d" % count, 0, 50 )
        
    #Radio State
    elif(count == 5):
        oled.text("Count is: %4d" % count, 0, 50 )
        
        #If the mute status is false the radio will play outside of radio setting, ie the radio setting is turns on the radio
        #If the mute status is true the radio will not play after radio setting has been clicked thorugh
        #fm_radio = Radio( 107.3, 0, True )
        Settings = fm_radio.GetSettings()
        
        
        current_zero = Settings [0]
        oled.text("Zero: %d" % current_zero, 0, 10 )
        
        current_volume = Settings[1]
        oled.text("Volume: %d" % current_volume, 0, 20 )
        
        current_frequency = Settings [2]
        oled.text("Frequency: %.1f" % current_frequency, 0, 30 )
        
        current_third = Settings [3]
        oled.text("Third: %d" % current_third, 0, 40 )
        

    elif(count > 5):
        count = 0

        # Reset Select Counter
        selectcount = 0

# Draw box below the text
    #oled.rect( 0, 50, 128, 5, 1  )        

    # Transfer the buffer to the screen
    oled.show()
        
    