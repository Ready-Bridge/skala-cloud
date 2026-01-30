package com.sk.skala.stockapi.data.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class PlayerSession {
	@NotBlank(message = "플레이어 ID는 필수입니다")
	private String playerId;
	
	@NotBlank(message = "비밀번호는 필수입니다")
	private String playerPassword;
}
