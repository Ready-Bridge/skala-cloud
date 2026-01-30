package com.sk.skala.stockapi;

import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;

import com.sk.skala.stockapi.config.Error;
import com.sk.skala.stockapi.data.common.Response;
import com.sk.skala.stockapi.exception.ParameterException;
import com.sk.skala.stockapi.exception.ResponseException;

import lombok.extern.slf4j.Slf4j;

@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

	@ExceptionHandler(value = MethodArgumentNotValidException.class)
	public @ResponseBody Response<?> takeMethodArgumentNotValidException(MethodArgumentNotValidException e) {
		String errorMessage = e.getBindingResult()
			.getFieldErrors()
			.stream()
			.map(error -> error.getField() + ": " + error.getDefaultMessage())
			.reduce((m1, m2) -> m1 + ", " + m2)
			.orElse("검증 실패");
		
		log.error("GlobalExceptionHandler.MethodArgumentNotValidException: {}", errorMessage);
		return Response.error(Error.INVALID_PARAMETER.getCode(), errorMessage);
	}

	@ExceptionHandler(value = Exception.class)
	public @ResponseBody Response<?> takeException(Exception e) {
		log.error("GlobalExceptionHandler.Exception: {}", e.getMessage());
		return Response.error(Error.SYSTEM_ERROR.getCode(), e.getMessage());
	}

	@ExceptionHandler(value = NullPointerException.class)
	public @ResponseBody Response<?> takeNullPointerException(Exception e) {
		log.error("GlobalExceptionHandler.NullPointerException: {}", e.getMessage());
		e.printStackTrace();
		return Response.error(Error.SYSTEM_ERROR.getCode(), e.getMessage());
	}

	@ExceptionHandler(value = SecurityException.class)
	public @ResponseBody Response<?> takeSecurityException(SecurityException e) {
		log.error("GlobalExceptionHandler.SecurityException: {}", e.getMessage());
		return Response.error(Error.NOT_AUTHENTICATED.getCode(), e.getMessage());
	}

	@ExceptionHandler(value = ParameterException.class)
	public @ResponseBody Response<?> takeParameterException(ParameterException e) {
		return Response.error(e.getCode(), e.getMessage());
	}

	@ExceptionHandler(value = ResponseException.class)
	public @ResponseBody Response<?> takeResponseException(ResponseException e) {
		return Response.error(e.getCode(), e.getMessage());
	}
}