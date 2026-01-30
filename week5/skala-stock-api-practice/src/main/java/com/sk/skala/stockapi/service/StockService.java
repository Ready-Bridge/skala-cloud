package com.sk.skala.stockapi.service;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.sk.skala.stockapi.config.Error;
import com.sk.skala.stockapi.data.common.PagedList;
import com.sk.skala.stockapi.data.common.Response;
import com.sk.skala.stockapi.data.dto.request.StockCreateRequest;
import com.sk.skala.stockapi.data.dto.request.StockDeleteRequest;
import com.sk.skala.stockapi.data.dto.request.StockUpdateRequest;
import com.sk.skala.stockapi.data.table.Stock;
import com.sk.skala.stockapi.exception.ParameterException;
import com.sk.skala.stockapi.exception.ResponseException;
import com.sk.skala.stockapi.repository.StockRepository;
import com.sk.skala.stockapi.tools.PaginationTool;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class StockService {
    
    private final StockRepository stockRepository;

    public Response<PagedList> getAllStocks(int pageNumber, int count) {
        Pageable pageable = PageRequest.of(pageNumber, count, Sort.by("id").ascending());
        Page<Stock> page = stockRepository.findAll(pageable);
        PagedList pagedList = PaginationTool.toPagedList(page, pageNumber);
        
        return Response.success(pagedList);
    }
    
    public Response<Stock> getStockById(Long stockId) {
        Stock stock = stockRepository.findById(stockId)
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Stock ID: " + stockId));
        
        return Response.success(stock);
    }

    @Transactional
    public Response<Stock> createStock(StockCreateRequest request) {
        validateStockRequest(request.stockName(), request.stockPrice());
        
        if (stockRepository.findByStockName(request.stockName()).isPresent()) {
            throw new ResponseException(Error.DATA_DUPLICATED, "Stock Name: " + request.stockName());
        }
        
        Stock savedStock = stockRepository.save(new Stock(request.stockName(), request.stockPrice()));
        
        return Response.success(savedStock);
    }

    @Transactional
    public Response<Stock> updateStock(StockUpdateRequest request) {
        if (request == null || request.id() == null) {
            throw new ParameterException("id");
        }
        validateStockRequest(request.stockName(), request.stockPrice());
    
        Stock existingStock = stockRepository.findById(request.id())
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Stock ID: " + request.id()));
        
        existingStock.updateStockName(request.stockName());
        existingStock.updateStockPrice(request.stockPrice());
        Stock updatedStock = stockRepository.save(existingStock);
        
        return Response.success(updatedStock);
    }

    @Transactional
    public Response<Void> deleteStock(StockDeleteRequest request) {
        if (request == null || request.id() == null) {
            throw new ParameterException("id");
        }
        Stock existingStock = stockRepository.findById(request.id())
            .orElseThrow(() -> new ResponseException(Error.DATA_NOT_FOUND, "Stock ID: " + request.id()));
        
        stockRepository.delete(existingStock);
        
        return Response.success("Stock deleted successfully");
    }

    private void validateStockRequest(String stockName, Double stockPrice) {
        if (stockName == null || stockName.trim().isEmpty()) {
            throw new ParameterException("stockName");
        }
        if (stockPrice == null || stockPrice <= 0) {
            throw new ParameterException("stockPrice");
        }
    }
}
