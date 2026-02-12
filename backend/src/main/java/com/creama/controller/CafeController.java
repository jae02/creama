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
@CrossOrigin(origins = "*") // For local development
public class CafeController {

    private final CafeService cafeService;

    @GetMapping
    public ResponseEntity<List<CafeDTO>> getAllCafes() {
        return ResponseEntity.ok(cafeService.getAllCafes());
    }
}
