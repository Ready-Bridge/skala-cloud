# password.py
import re

def is_valid_password(password: str) -> bool:
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,}$'
    return bool(re.match(pattern, password))


if __name__ == "__main__":
    pw = input("비밀번호 입력: ")
    if is_valid_password(pw):
        print("유효한 비밀번호입니다.")
    else:
        print("유효하지 않은 비밀번호입니다.")