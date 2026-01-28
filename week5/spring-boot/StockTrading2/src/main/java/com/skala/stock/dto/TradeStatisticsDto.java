package com.skala.stock.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TradeStatisticsDto {
    private Long userId;
    private Long totalTradeCount;       // 총 거래 횟수
    private Long buyCount;              // 매수 횟수
    private Long sellCount;             // 매도 횟수
    private Long totalBuyAmount;        // 총 매수 금액
    private Long totalSellAmount;       // 총 매도 금액
    private Long totalBuyQuantity;      // 총 매수 수량
    private Long totalSellQuantity;     // 총 매도 수량
}
