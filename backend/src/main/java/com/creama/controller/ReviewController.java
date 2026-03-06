package com.creama.controller;

import com.creama.dto.ReviewDTO;
import com.creama.service.ReviewService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/cafes/{cafeId}/reviews")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ReviewController {

    private final ReviewService reviewService;

    @GetMapping
    public ResponseEntity<List<ReviewDTO>> getReviews(@PathVariable Long cafeId) {
        return ResponseEntity.ok(reviewService.getReviewsByCafeId(cafeId));
    }

    @PostMapping
    public ResponseEntity<ReviewDTO> createReview(
            @PathVariable Long cafeId,
            @RequestParam String nickname,
            @RequestParam String content,
            @RequestParam(required = false) MultipartFile image) {
        return ResponseEntity.ok(reviewService.createReview(cafeId, nickname, content, image));
    }
}
