from datetime import datetime

class hour:
    now = datetime.now()
    current_time = now.strftime("%Y-%M-%d %H:%M:%S")


def computelog(header, msg, footer):
    print("="*50)
    print(f"{header}")
    print("="*50)
    print(f"{hour.current_time} Début de l'execution de la fonction")
    print(f"{msg}")
    print(f"{hour.current_time} {footer}")
