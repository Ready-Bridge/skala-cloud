//export default function isNotEmpty(value, fieldName) // default 붙이면 import 시 이름 바꿀 수 있음

export function isNotEmpty(value, fieldName) {
    if (!value.trim()) {
        alert(`${fieldName} 항목을 입력하세요.`);
        return false;
    }
    return true;
}