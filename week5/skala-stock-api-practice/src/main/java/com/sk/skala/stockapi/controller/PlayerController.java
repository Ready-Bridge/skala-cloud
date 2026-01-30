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
import com.sk.skala.stockapi.data.dto.request.PlayerCreateRequest;
import com.sk.skala.stockapi.data.dto.request.PlayerDeleteRequest;
import com.sk.skala.stockapi.data.dto.request.PlayerSession;
import com.sk.skala.stockapi.data.dto.request.PlayerUpdateRequest;
import com.sk.skala.stockapi.data.dto.request.StockOrder;
import com.sk.skala.stockapi.data.dto.response.PlayerLoginDto;
import com.sk.skala.stockapi.data.dto.response.PlayerStockListDto;
import com.sk.skala.stockapi.data.table.Player;
import com.sk.skala.stockapi.service.PlayerService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/players")
@RequiredArgsConstructor
@Tag(name = "Player API", description = "플레이어 정보 및 주식 거래 API")
public class PlayerController {
    
    private final PlayerService playerService;

    @GetMapping("/list")
    @Operation(summary = "전체 플레이어 목록 조회", description = "페이징을 적용하여 플레이어 목록을 조회합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "잘못된 요청"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<PagedList> getAllPlayers(
        @Parameter(description = "페이지 오프셋 (기본값: 0)", example = "0")
        @RequestParam(value = "offset", defaultValue = "0") int offset,
        @Parameter(description = "페이지당 항목 수 (기본값: 10)", example = "10")
        @RequestParam(value = "count", defaultValue = "10") int count) {
        return playerService.getAllPlayers(offset, count);
    }

    @GetMapping("/{playerId}")
    @Operation(summary = "플레이어 상세 조회", description = "플레이어 ID로 플레이어 정보와 보유 주식 목록을 조회합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "조회 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "플레이어를 찾을 수 없음"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<PlayerStockListDto> getPlayerById(
        @Parameter(description = "플레이어 ID", example = "user123")
        @PathVariable String playerId) {
        return playerService.getPlayerById(playerId);
    }

    @PostMapping
    @Operation(summary = "플레이어 등록", description = "새로운 플레이어를 등록합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "등록 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "필수 파라미터 누락 또는 중복"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Player> createPlayer(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "등록할 플레이어 정보",
            content = @Content(schema = @Schema(implementation = PlayerCreateRequest.class)))
        @Valid @RequestBody PlayerCreateRequest request) {
        return playerService.createPlayer(request);
    }

    @PostMapping("/login")
    @Operation(summary = "플레이어 로그인", description = "플레이어가 로그인합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "로그인 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "필수 파라미터 누락 또는 인증 실패"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<PlayerLoginDto> loginPlayer(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "플레이어 로그인 정보",
            content = @Content(schema = @Schema(implementation = PlayerSession.class)))
        @Valid @RequestBody PlayerSession playerSession) {
        return playerService.loginPlayer(playerSession);
    }

    @PutMapping
    @Operation(summary = "플레이어 정보 수정", description = "플레이어 정보를 수정합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "수정 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "플레이어를 찾을 수 없음"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Player> updatePlayer(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "수정할 플레이어 정보",
            content = @Content(schema = @Schema(implementation = PlayerUpdateRequest.class)))
        @Valid @RequestBody PlayerUpdateRequest request) {
        return playerService.updatePlayer(request);
    }

    @DeleteMapping
    @Operation(summary = "플레이어 삭제", description = "플레이어를 삭제합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "삭제 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "플레이어를 찾을 수 없음"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Void> deletePlayer(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "삭제할 플레이어 정보",
            content = @Content(schema = @Schema(implementation = PlayerDeleteRequest.class)))
        @RequestBody PlayerDeleteRequest request) {
        return playerService.deletePlayer(request);
    }

    @PostMapping("/buy")
    @Operation(summary = "주식 매수", description = "플레이어가 주식을 매수합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "매수 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "매수 실패 (잔액 부족 등)"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Void> buyPlayerStock(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "주식 매수 정보",
            content = @Content(schema = @Schema(implementation = StockOrder.class)))
        @Valid @RequestBody StockOrder order) {
        return playerService.buyPlayerStock(order);
    }

    @PostMapping("/sell")
    @Operation(summary = "주식 매도", description = "플레이어가 주식을 매도합니다")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "매도 성공",
            content = @Content(schema = @Schema(implementation = Response.class))),
        @ApiResponse(responseCode = "400", description = "매도 실패 (보유 수량 부족 등)"),
        @ApiResponse(responseCode = "500", description = "서버 오류")
    })
    public Response<Void> sellPlayerStock(
        @io.swagger.v3.oas.annotations.parameters.RequestBody(description = "주식 매도 정보",
            content = @Content(schema = @Schema(implementation = StockOrder.class)))
        @Valid @RequestBody StockOrder order) {
        return playerService.sellPlayerStock(order);
    }

}
