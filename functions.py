from RadioClass import Radio

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
    
    
def trigger_alarm(handlerhour, handlermin, handlersec, Dhour, Dmin, Dsec, ap_hour_format, alarm_am_pm="DE", am_pm="DE"):
    
    if(ap_hour_format == True and handlerhour == Dhour and handlermin == Dmin and handlersec == Dsec and alarm_am_pm == am_pm):
        print(ap_hour_format)
        print(alarm_am_pm)
        print(am_pm)
        return True
    elif(handlerhour == Dhour and handlermin == Dmin and handlersec == Dsec):
        return True
    else:
        return False
    
def formatTimeZero(Dhour, Dmin, Dsec, oled, cur_hour, cur_min, cur_sec):
    if(Dhour < 10):
        oled.text("0", 32, 28)
        oled.text(cur_hour.format(Dhour), 40, 28)
    else:
        oled.text(cur_hour.format(Dhour), 32, 28)

    oled.text(":", 48, 28)
    
    if(Dmin < 10):
        oled.text("0", 56, 28)
        oled.text(cur_min.format(Dmin), 64, 28)
    else:
        oled.text(cur_min.format(Dmin), 56, 28)
    
    oled.text(":", 72, 28)
    
    if(Dsec < 10):
        oled.text("0", 80, 28)
        oled.text(cur_sec.format(Dsec), 88, 28)
    else:
        oled.text(cur_sec.format(Dsec), 80, 28)
    