package com.sk.skala.stockapi.data.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record StockUpdateRequest(
	Long id,
	
	@NotBlank(message = "주식명은 필수입니다")
	String stockName,
	
	@NotNull(message = "주식 가격은 필수입니다")
	@Positive(message = "주식 가격은 0보다 커야 합니다")
	Double stockPrice
) {
}
