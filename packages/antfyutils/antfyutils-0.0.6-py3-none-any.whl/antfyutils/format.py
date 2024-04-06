from datetime import timedelta
from datetime import timedelta

def td_to_en(td: timedelta) -> str:  
    days = td.days  
    hours = td.seconds // 3600  
    minutes = (td.seconds // 60) % 60  
    seconds = td.seconds % 60  
      
    result = []  
    if days > 0:  
        result.append(f"{days} days")  
    if hours > 0:  
        result.append(f"{hours} hours")  
    if minutes > 0:  
        result.append(f"{minutes} minutes")  
    if seconds > 0:  
        result.append(f"{seconds} seconds")  
      
    return " ".join(result)  

def seconds_to_time(seconds):  
    seconds = int(seconds)
    if seconds < 0:  
        return "Time cannot be negative"  
    elif seconds == 0:  
        return "0 seconds"  
    else:  
        hours = seconds // 3600  
        minutes = (seconds % 3600) // 60  
        remaining_seconds = seconds % 60  
          
        if hours > 0:  
            return f"{hours} hours {minutes} minutes {remaining_seconds} seconds"  
        elif minutes > 0:  
            return f"{minutes} minutes {remaining_seconds} seconds"  
        else:  
            return f"{remaining_seconds} seconds"  


def td转中文(td: timedelta)->str:  
    days = td.days  
    hours = td.seconds // 3600  
    minutes = (td.seconds // 60) % 60  
    seconds = td.seconds % 60  
      
    result = []  
    if days > 0:  
        result.append(f"{days}天")  
    if hours > 0:  
        result.append(f"{hours}小时")  
    if minutes > 0:  
        result.append(f"{minutes}分钟")  
    if seconds > 0:  
        result.append(f"{seconds}秒")  
      
    return " ".join(result)  

def 秒转时间(seconds):  
    seconds = int(seconds)
    if seconds < 0:  
        return "时间不能是负数"  
    elif seconds == 0:  
        return "0秒"  
    else:  
        hours = seconds // 3600  
        minutes = (seconds % 3600) // 60  
        remaining_seconds = seconds % 60  
          
        if hours > 0:  
            return f"{hours}小时{minutes}分{remaining_seconds}秒"  
        elif minutes > 0:  
            return f"{minutes}分{remaining_seconds}秒"  
        else:  
            return f"{remaining_seconds}秒"  