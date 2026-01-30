package com.sk.skala.stockapi.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.sk.skala.stockapi.config.Error;
import com.sk.skala.stockapi.data.common.PagedList;
import com.sk.skala.stockapi.data.common.Response;
import com.sk.skala.stockapi.data.dto.request.PlayerCreateRequest;
import com.sk.skala.stockapi.data.dto.request.PlayerDeleteRequest;
import com.sk.skala.stockapi.data.dto.request.PlayerUpdateRequest;
import com.sk.skala.stockapi.data.dto.request.PlayerSession;
import com.sk.skala.stockapi.data.dto.request.StockOrder;
import com.sk.skala.stockapi.data.dto.response.PlayerLoginDto;
import com.sk.skala.stockapi.data.dto.response.PlayerStockDto;
import com.sk.skala.stockapi.data.dto.response.PlayerStockListDto;
import com.sk.skala.stockapi.data.table.Player;
import com.sk.skala.stockapi.data.table.PlayerStock;
import com.sk.skala.stockapi.data.table.Stock;
import com.sk.skala.stockapi.exception.ParameterException;
import com.sk.skala.stockapi.exception.ResponseException;
import com.sk.skala.stockapi.repository.PlayerRepository;
import com.sk.skala.stockapi.repository.PlayerStockRepository;
import com.sk.skala.stockapi.repository.StockRepository;
import com.sk.skala.stockapi.tools.PaginationTool;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PlayerService {
    
    private static final Double INITIAL_PLAYER_MONEY = 10000.0;
    
    private final StockRepository stockRepository;
    private final PlayerRepository playerRepository;
    private final PlayerStockRepository playerStockRepository;
    private final SessionHandler sessionHandler;

    public Response<PagedList> getAllPlayers(int pageNumber, int count) {
        Pageable pageable = PageRequest.of(pageNumber, count, Sort.by("playerId").ascending());
        Page<Player> page = playerRepository.findAll(pageable);
        PagedList pagedList = PaginationTool.toPagedList(page, pageNumber);
        
        return Response.success(pagedList);
    }

    public Response<PlayerStockListDto> getPlayerById(String playerId) {
        Player player = playerRepository.findById(playerId)
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Player not found"));
        
        List<PlayerStock> playerStocks = playerStockRepository.findByPlayer_PlayerId(playerId);
        List<PlayerStockDto> stockDtos = playerStocks.stream()
            .map(ps -> PlayerStockDto.builder()
                .stockId(ps.getStock().getId())
                .stockName(ps.getStock().getStockName())
                .stockPrice(ps.getStock().getStockPrice())
                .quantity(ps.getQuantity())
                .build())
            .collect(Collectors.toList());
        
        PlayerStockListDto body = PlayerStockListDto.builder()
            .playerId(player.getPlayerId())
            .playerMoney(player.getPlayerMoney())
            .stocks(stockDtos)
            .build();

        return Response.success(body);
    }

    @Transactional
    public Response<Player> createPlayer(PlayerCreateRequest request) {
        validatePlayerIdAndPassword(request.playerId(), request.playerPassword());
        
        if (playerRepository.findById(request.playerId()).isPresent()) {
            throw new ResponseException(Error.DATA_DUPLICATED, "PlayerId: " + request.playerId());
        }
        
        Player newPlayer = new Player(request.playerId(), INITIAL_PLAYER_MONEY);
        newPlayer.updatePassword(request.playerPassword());
        Player savedPlayer = playerRepository.save(newPlayer);
        
        return Response.success(savedPlayer);
    }

    public Response<PlayerLoginDto> loginPlayer(PlayerSession playerSession) {
        validatePlayerIdAndPassword(playerSession.getPlayerId(), playerSession.getPlayerPassword());
        
        Player player = playerRepository.findById(playerSession.getPlayerId())
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Player not found"));
        
        if (!player.getPlayerPassword().equals(playerSession.getPlayerPassword())) {
            throw new ResponseException(Error.NOT_AUTHENTICATED, "Invalid password");
        }
        
        sessionHandler.storeAccessToken(playerSession);
        
        PlayerLoginDto loginDto = PlayerLoginDto.from(player.getPlayerId(), player.getPlayerMoney());
        return Response.success(loginDto);
    }

    @Transactional
    public Response<Player> updatePlayer(PlayerUpdateRequest request) {
        if (request == null || request.playerId() == null || request.playerId().trim().isEmpty()) {
            throw new ParameterException("playerId");
        }
        if (request.playerMoney() == null || request.playerMoney() < 0) {
            throw new ParameterException("playerMoney");
        }

        Player existingPlayer = playerRepository.findById(request.playerId())
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Player not found"));
        
        existingPlayer.updateMoney(request.playerMoney());
        
        Player updatedPlayer = playerRepository.save(existingPlayer);
        return Response.success(updatedPlayer);
    }

    @Transactional
    public Response<Void> deletePlayer(PlayerDeleteRequest request) {
        if (request == null || request.playerId() == null || request.playerId().trim().isEmpty()) {
            throw new ParameterException("playerId");
        }
        Player existingPlayer = playerRepository.findById(request.playerId())
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Player not found"));
        
        playerRepository.delete(existingPlayer);
        return Response.success("Player deleted successfully");
    }

    @Transactional
    public Response<Void> buyPlayerStock(StockOrder order) {
        validateStockOrder(order);
        
        String playerId = sessionHandler.getPlayerId();
        Player player = playerRepository.findById(playerId)
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Player not found"));

        Stock stock = stockRepository.findById(order.getStockId())
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Stock not found"));
        
        Double totalPrice = stock.getStockPrice() * order.getQuantity();
        if (player.getPlayerMoney() < totalPrice) {
            throw new ResponseException(Error.INSUFFICIENT_FUNDS, "Insufficient balance");
        }
        
        player.subtractMoney(totalPrice);
        playerRepository.save(player);
        
        PlayerStock existingPlayerStock = playerStockRepository.findByPlayerAndStock(player, stock).orElse(null);
        
        if (existingPlayerStock != null) {
            existingPlayerStock.addQuantity(order.getQuantity());
            playerStockRepository.save(existingPlayerStock);
        } else {
            PlayerStock newPlayerStock = new PlayerStock(player, stock, order.getQuantity());
            playerStockRepository.save(newPlayerStock);
        }
        
        return Response.success("Stock purchased successfully");
    }

    @Transactional
    public Response<Void> sellPlayerStock(StockOrder order) {
        validateStockOrder(order);
        
        String playerId = sessionHandler.getPlayerId();
        Player player = playerRepository.findById(playerId)
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Player not found"));

        Stock stock = stockRepository.findById(order.getStockId())
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Stock not found"));
        
        PlayerStock playerStock = playerStockRepository.findByPlayerAndStock(player, stock)
            .orElseThrow(() -> new ResponseException(Error.INSUFFICIENT_QUANTITY, "Stock not owned"));
        
        if (playerStock.getQuantity() < order.getQuantity()) {
            throw new ResponseException(Error.INSUFFICIENT_QUANTITY, "Insufficient quantity");
        }
        
        Double totalPrice = stock.getStockPrice() * order.getQuantity();
        player.addMoney(totalPrice);
        playerRepository.save(player);
        
        if (playerStock.getQuantity().equals(order.getQuantity())) {
            playerStockRepository.delete(playerStock);
        } else {
            playerStock.subtractQuantity(order.getQuantity());
            playerStockRepository.save(playerStock);
        }
        
        return Response.success("Stock sold successfully");
    }

    private void validatePlayerIdAndPassword(String playerId, String playerPassword) {
        if (playerId == null || playerId.trim().isEmpty() ||
            playerPassword == null || playerPassword.trim().isEmpty()) {
            throw new ParameterException("playerId", "playerPassword");
        }
    }

    private void validateStockOrder(StockOrder order) {
        if (order == null || order.getStockId() == null) {
            throw new ParameterException("stockId");
        }
        if (order.getQuantity() == null || order.getQuantity() <= 0) {
            throw new ParameterException("quantity");
        }
    }

}
