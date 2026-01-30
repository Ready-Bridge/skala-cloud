package com.sk.skala.stockapi.data.dto.response;

public record PlayerLoginDto(
    String playerId,
    Double playerMoney
) {
    public static PlayerLoginDto from(String playerId, Double playerMoney) {
        return new PlayerLoginDto(playerId, playerMoney);
    }
}
