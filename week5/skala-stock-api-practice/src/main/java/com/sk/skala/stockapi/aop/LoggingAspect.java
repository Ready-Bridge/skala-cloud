package com.sk.skala.stockapi.aop;

import java.lang.reflect.Method;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import com.sk.skala.stockapi.config.ApplicationProperties;
import com.sk.skala.stockapi.config.Constant;
import com.sk.skala.stockapi.config.Error;
import com.sk.skala.stockapi.data.common.ApiLog;
import com.sk.skala.stockapi.data.common.Response;
import com.sk.skala.stockapi.tools.HostInfo;
import com.sk.skala.stockapi.tools.JsonTool;
import com.sk.skala.stockapi.tools.StringTool;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Aspect
@Component
@Slf4j
@RequiredArgsConstructor
public class LoggingAspect {
	private final ApplicationProperties applicationProperties;

	@Around("@annotation(org.springframework.web.bind.annotation.GetMapping) ||"
			+ " @annotation(org.springframework.web.bind.annotation.PostMapping) ||"
			+ " @annotation(org.springframework.web.bind.annotation.PutMapping) ||"
			+ " @annotation(org.springframework.web.bind.annotation.DeleteMapping)")
	public Object logAround(ProceedingJoinPoint joinPoint) throws Throwable {

		if (isSkipLogging(joinPoint)) {
			return joinPoint.proceed();
		}

		String controller = joinPoint.getSignature().getDeclaringTypeName() + "." + joinPoint.getSignature().getName();
		ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
		HttpServletRequest request = attributes.getRequest();
		
		long timestamp = System.currentTimeMillis();
		ApiLog.ApiLogBuilder logBuilder = ApiLog.builder()
			.timestamp(timestamp)
			.remoteAddress(getRemoteAddress(request))
			.apiHost(HostInfo.getHostname())
			.apiUrl(request.getRequestURI())
			.apiMethod(request.getMethod())
			.apiController(controller)
			.requestParams(request.getQueryString());

		try {
			String contentType = request.getContentType();
			if (contentType != null && Constant.TEXT_TYPES.contains(contentType.toLowerCase())) {
				String body = JsonTool.toString(joinPoint.getArgs());
				logBuilder.requestBody(body);
			}

			Object result = joinPoint.proceed();
			if (result instanceof Response) {
				String body = JsonTool.toString(result);
				logBuilder.responseBody(body);
			}

			ApiLog apiLog = logBuilder
				.apiResult(Constant.RESULT_SUCCESS)
				.elapsedTime(System.currentTimeMillis() - timestamp)
				.build();
			log.info("{}: {}", applicationProperties.getName(), JsonTool.toString(apiLog));
			return result;
		} catch (Exception e) {
			Response response = Response.error(Error.SYSTEM_ERROR.getCode(), e.getMessage());

			ApiLog apiLog = logBuilder
				.apiResult(Constant.RESULT_FAIL)
				.responseBody(JsonTool.toString(response))
				.elapsedTime(System.currentTimeMillis() - timestamp)
				.build();
			log.info("{}: {}", applicationProperties.getName(), JsonTool.toString(apiLog));
			throw e;
		}
	}

	private boolean isSkipLogging(ProceedingJoinPoint joinPoint) {
		try {
			Method method = getMethodFromJoinPoint(joinPoint);
			if (method != null) {
				if (method.isAnnotationPresent(SkipLogging.class)
						|| method.getDeclaringClass().isAnnotationPresent(SkipLogging.class)) {
					return true;
				}
			}
		} catch (NoSuchMethodException e) {
			log.error("MaskingAspect.shouldSkipMasking: {}", e.getMessage());
		}
		return false;
	}

	private Method getMethodFromJoinPoint(ProceedingJoinPoint joinPoint) throws NoSuchMethodException {
		String methodName = joinPoint.getSignature().getName();
		Class<?> targetClass = joinPoint.getTarget().getClass();
		Class<?>[] parameterTypes = ((org.aspectj.lang.reflect.MethodSignature) joinPoint.getSignature())
				.getParameterTypes();
		return targetClass.getMethod(methodName, parameterTypes);
	}

	String getRemoteAddress(HttpServletRequest request) {
		String address = request.getHeader("X-Forwarded-For");
		if (StringTool.isEmpty(address)) {
			return request.getRemoteAddr();
		} else {
			String[] values = address.split(",");
			return values[0].trim();
		}
	}
}
