package com.sk.skala.stockapi.data.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record PlayerCreateRequest(
	@NotBlank(message = "플레이어 ID는 필수입니다")
	@Size(min = 3, max = 20, message = "플레이어 ID는 3자 이상 20자 이하여야 합니다")
	String playerId,
	
	@NotBlank(message = "비밀번호는 필수입니다")
	@Size(min = 4, max = 20, message = "비밀번호는 4자 이상 20자 이하여야 합니다")
	String playerPassword
) {
}
