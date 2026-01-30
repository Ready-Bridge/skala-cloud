package com.sk.skala.stockapi.data.dto.response;

import lombok.Builder;
import java.util.List;

// Player가 보유한 주식 목록 조회 응답
@Builder
public record PlayerStockListDto (
    String playerId,
    Double playerMoney,
    List<PlayerStockDto> stocks
){

}