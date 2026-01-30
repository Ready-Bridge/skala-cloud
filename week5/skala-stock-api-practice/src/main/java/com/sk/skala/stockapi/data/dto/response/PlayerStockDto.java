package com.sk.skala.stockapi.data.dto.response;

import lombok.Builder;

// Player가 보유한 주식 정보
@Builder
public record PlayerStockDto (
    Long stockId,
    String stockName,
    Double stockPrice,
    Integer quantity
){

}
