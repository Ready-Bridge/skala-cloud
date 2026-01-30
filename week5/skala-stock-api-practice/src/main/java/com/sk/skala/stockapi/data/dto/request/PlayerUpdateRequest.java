package com.sk.skala.stockapi.data.dto.request;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

public record PlayerUpdateRequest(
	String playerId,
	
	@NotNull(message = "플레이어 금액은 필수입니다")
	@PositiveOrZero(message = "플레이어 금액은 0 이상이어야 합니다")
	Double playerMoney
) {
}
