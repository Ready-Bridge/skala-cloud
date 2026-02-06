import { shallowReactive } from "vue";

export const userRef = shallowReactive({
  name: "홍길동",
  address: {
    city: "서울",
    zip: "12345",
  },
});

export function updateName(newName) {
  userRef.name = newName;
}

export function updateCity(newCity) {
  userRef.address.city = newCity;
}
