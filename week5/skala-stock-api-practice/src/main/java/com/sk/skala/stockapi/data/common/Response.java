package com.sk.skala.stockapi.data.common;

import com.sk.skala.stockapi.config.Error;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class Response<T> {
	public static final int SUCCESS = 0;
	public static final int FAIL = 1;

	private int result;
	private int code;
	private String message;
	private T body;

	public static <T> Response<T> success(T body) {
		return Response.<T>builder()
			.result(SUCCESS)
			.body(body)
			.build();
	}

	public static <T> Response<T> success(String message) {
		return Response.<T>builder()
			.result(SUCCESS)
			.message(message)
			.build();
	}

	public static <T> Response<T> error(Error error) {
		return Response.<T>builder()
			.result(FAIL)
			.code(error.getCode())
			.message(error.getMessage())
			.build();
	}

	public static <T> Response<T> error(int code, String message) {
		return Response.<T>builder()
			.result(FAIL)
			.code(code)
			.message(message)
			.build();
	}
}
