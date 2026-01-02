# echo.py
from password import is_valid_password

print("=== Echo Program ===")
print("사용 가능한 명령어:")
print("  아무 문장이나 입력 → 그대로 출력")
print("  !password        → 비밀번호 유효성 검사")
print("  !quit            → 프로그램 종료")
print("====================")

while True:
    text = input(">> ")

    if text == "!quit":
        print("프로그램을 종료합니다.")
        break

    elif text == "!password":
        pw = input("비밀번호 입력: ")
        if is_valid_password(pw):
            print("✅ 유효한 비밀번호입니다.")
        else:
            print("❌ 유효하지 않은 비밀번호입니다.")

    else:
        print(text)