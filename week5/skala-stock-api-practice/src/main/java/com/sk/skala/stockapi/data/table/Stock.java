package com.sk.skala.stockapi.data.table;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import com.sk.skala.stockapi.config.Error;
import com.sk.skala.stockapi.exception.ResponseException;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Stock {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;
	
	private String stockName;

	private Double stockPrice;

	public Stock(String stockName, Double stockPrice) {
		this.stockName = stockName;
		this.stockPrice = stockPrice;
	}

	// 주식 이름 변경
	public void updateStockName(String stockName) {
		if (stockName == null || stockName.trim().isEmpty()) {
			throw new ResponseException(Error.INVALID_PARAMETER, "stockName은 필수입니다");
		}
		this.stockName = stockName;
	}

	// 주가 업데이트
	public void updateStockPrice(Double stockPrice) {
		if (stockPrice == null || stockPrice <= 0) {
			throw new ResponseException(Error.INVALID_PARAMETER, "주가는 0보다 커야 합니다");
		}
		this.stockPrice = stockPrice;
	}
}
