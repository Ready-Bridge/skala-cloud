package com.skala.stock.aop;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.springframework.stereotype.Component;

import java.util.Arrays;

@Slf4j
@Aspect
@Component
@RequiredArgsConstructor
public class ExecutionTimeAspect {

    private final ObjectMapper objectMapper;

    @Around("execution(public * com.skala.stock..*Controller.*(..))")
    public Object logExecutionTime(ProceedingJoinPoint joinPoint) throws Throwable {
        long start = System.currentTimeMillis();

        String methodName = joinPoint.getSignature().toShortString();
        String params = stringifyArgs(joinPoint.getArgs());
        log.info("[API REQUEST] {} | Params: {} - 시작", methodName, params);

        Object result = joinPoint.proceed();

        long end = System.currentTimeMillis();
        long duration = end - start;
        
        log.info("[API RESPONSE] {} - 완료 (소요 시간: {} ms)", methodName, duration);
        return result;
    }

    // JSON 직렬화 실패 시 기본 toString 배열 출력
    private String stringifyArgs(Object[] args) {
        try {
            return objectMapper.writeValueAsString(args);
        } catch (Exception e) {
            return Arrays.toString(args);
        }
    }
}
