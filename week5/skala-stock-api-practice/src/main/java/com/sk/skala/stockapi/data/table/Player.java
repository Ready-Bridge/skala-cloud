package com.sk.skala.stockapi.data.table;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import com.sk.skala.stockapi.config.Error;
import com.sk.skala.stockapi.exception.ResponseException;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Player {

	@Id
	private String playerId;
	
	private String playerPassword;
	
	private Double playerMoney;

	public Player(String playerId, Double playerMoney) {
		this.playerId = playerId;
		this.playerMoney = playerMoney;
	}

	public void updatePassword(String playerPassword) {
		if (playerPassword == null || playerPassword.length() < 4) {
			throw new ResponseException(Error.INVALID_PARAMETER, "비밀번호는 최소 4자 이상이어야 합니다");
		}
		this.playerPassword = playerPassword;
	}

	// money 증가
	public void addMoney(Double amount) {
		if (amount == null || amount <= 0) {
			throw new ResponseException(Error.INVALID_PARAMETER, "증가 금액은 0보다 커야 합니다");
		}
		this.playerMoney += amount;
	}

	// money 감소
	public void subtractMoney(Double amount) {
		if (amount == null || amount <= 0) {
			throw new ResponseException(Error.INVALID_PARAMETER, "감소 금액은 0보다 커야 합니다");
		}
		if (this.playerMoney < amount) {
			throw new ResponseException(Error.INSUFFICIENT_FUNDS, "플레이어 잔액 부족");
		}
		this.playerMoney -= amount;
	}

	public void updateMoney(Double newAmount) {
		if (newAmount == null || newAmount < 0) {
			throw new ResponseException(Error.INVALID_PARAMETER, "금액은 0 이상이어야 합니다");
		}
		this.playerMoney = newAmount;
	}
}
