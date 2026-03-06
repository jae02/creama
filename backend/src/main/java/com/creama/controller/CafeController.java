package com.creama.controller;

import com.creama.dto.CafeDTO;
import com.creama.service.CafeService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cafes")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class CafeController {

    private final CafeService cafeService;

    @GetMapping
    public ResponseEntity<List<CafeDTO>> getAllCafes() {
        return ResponseEntity.ok(cafeService.getAllCafes());
    }

    @GetMapping("/{id}")
    public ResponseEntity<CafeDTO> getCafeById(@PathVariable Long id) {
        return ResponseEntity.ok(cafeService.getCafeById(id));
    }

    /**
     * 키워드 검색
     * GET /api/cafes/search?q=빈티지
     */
    @GetMapping("/search")
    public ResponseEntity<List<CafeDTO>> searchCafes(@RequestParam(name = "q", required = false) String query) {
        return ResponseEntity.ok(cafeService.searchCafes(query));
    }

    /**
     * 위치 기반 가까운 카페 추천
     * GET /api/cafes/nearby?lat=37.5&lng=127.0&limit=10
     */
    @GetMapping("/nearby")
    public ResponseEntity<List<CafeDTO>> getNearbyCafes(
            @RequestParam Double lat,
            @RequestParam Double lng,
            @RequestParam(defaultValue = "10") int limit) {
        return ResponseEntity.ok(cafeService.getNearbyCafes(lat, lng, limit));
    }
}
