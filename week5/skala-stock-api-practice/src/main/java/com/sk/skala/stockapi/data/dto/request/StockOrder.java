package com.sk.skala.stockapi.data.dto.request;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class StockOrder {
	@NotNull(message = "주식 ID는 필수입니다")
	private Long stockId;
	
	@NotNull(message = "수량은 필수입니다")
	@Positive(message = "수량은 0보다 커야 합니다")
	private Integer quantity;
}
