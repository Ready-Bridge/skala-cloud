package com.sk.skala.stockapi.data.table;

import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import com.sk.skala.stockapi.config.Error;
import com.sk.skala.stockapi.exception.ResponseException;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class PlayerStock {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;
	
	@ManyToOne(fetch = FetchType.LAZY)
	@JoinColumn(name = "player_id")
	private Player player;
	
	@ManyToOne(fetch = FetchType.LAZY)
	@JoinColumn(name = "stock_id")
	private Stock stock;
	
	private Integer quantity;

	public PlayerStock(Player player, Stock stock, Integer quantity) {
		this.player = player;
		this.stock = stock;
		this.quantity = quantity;
	}

	//수량 증가
	public void addQuantity(Integer amount) {
		if (amount == null || amount <= 0) {
			throw new ResponseException(Error.INVALID_PARAMETER, "증가 수량은 0보다 커야 합니다");
		}
		this.quantity += amount;
	}

	// 수량 감소
	public void subtractQuantity(Integer amount) {
		if (amount == null || amount <= 0) {
			throw new ResponseException(Error.INVALID_PARAMETER, "감소 수량은 0보다 커야 합니다");
		}
		if (this.quantity < amount) {
			throw new ResponseException(Error.INSUFFICIENT_QUANTITY, "보유 수량이 부족합니다");
		}
		this.quantity -= amount;
	}
}