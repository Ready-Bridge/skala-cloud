package com.sk.skala.stockapi.controller;

import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.sk.skala.stockapi.data.common.PagedList;
import com.sk.skala.stockapi.data.common.Response;
import com.sk.skala.stockapi.data.dto.request.StockCreateRequest;
import com.sk.skala.stockapi.data.dto.request.StockDeleteRequest;
import com.sk.skala.stockapi.data.dto.request.StockUpdateRequest;
import com.sk.skala.stockapi.data.table.Stock;
import com.sk.skala.stockapi.service.StockService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/stocks")
@RequiredArgsConstructor
@Tag(name = "Stock API", description = "주식 정보 관리 API")
public class StockController {
    
    private final StockService stockService;

    @GetMapping("/list")
    @Operation(summary = "전체 주식 목록 조회", description = "페이징을 적용하여 주식 목록을 조회합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 요청"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<PagedList> getAllStocks(
        @Parameter(description = "페이지 오프셋 (기본값: 0)", example = "0")
        @RequestParam(defaultValue = "0") Integer offset,
        @Parameter(description = "페이지당 항목 수 (기본값: 10)", example = "10")
        @RequestParam(defaultValue = "10") Integer count) {
        return stockService.getAllStocks(offset, count);
    }

    @GetMapping("/{id}")
    @Operation(summary = "개별 주식 상세 조회", description = "주식 ID로 특정 주식의 정보를 조회합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "주식을 찾을 수 없음"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Stock> getStockById(
        @Parameter(description = "주식 ID", example = "1")
        @PathVariable Long id) {
        return stockService.getStockById(id);
    }

    @PostMapping
    @Operation(summary = "주식 등록", description = "새로운 주식 정보를 등록합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "등록 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "필수 파라미터 누락 또는 중복"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Stock> createStock(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "등록할 주식 정보",
            content = @Content(schema = @Schema(implementation = StockCreateRequest.class)))
        @Valid @RequestBody StockCreateRequest request) {
        return stockService.createStock(request);
    }

    @PutMapping
    @Operation(summary = "주식 정보 수정", description = "기존 주식의 정보를 수정합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "수정 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "필수 파라미터 누락 또는 주식 미존재"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Stock> updateStock(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "수정할 주식 정보",
            content = @Content(schema = @Schema(implementation = StockUpdateRequest.class)))
        @Valid @RequestBody StockUpdateRequest request) {
        return stockService.updateStock(request);
    }

    @DeleteMapping
    @Operation(summary = "주식 삭제", description = "주식을 삭제합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "삭제 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "주식을 찾을 수 없음"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Void> deleteStock(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "삭제할 주식 정보",
            content = @Content(schema = @Schema(implementation = StockDeleteRequest.class)))
        @RequestBody StockDeleteRequest request) {
        return stockService.deleteStock(request);
    }

}
