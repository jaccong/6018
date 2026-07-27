import datetime

if __name__ == "__main__":
    now = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('[ %m/%d %H:%M ]')
    with open("time.txt", 'w', encoding='utf-8') as file:
        file.write("自动更新,#genre#\n")
        file.write(f"{now},https://jaccong0520.serv00.net/da.mp4\n")
