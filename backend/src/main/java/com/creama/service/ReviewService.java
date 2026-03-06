package com.creama.service;

import com.creama.dto.ReviewDTO;
import com.creama.entity.Cafe;
import com.creama.entity.Review;
import com.creama.repository.CafeRepository;
import com.creama.repository.ReviewRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ReviewService {

    private final ReviewRepository reviewRepository;
    private final CafeRepository cafeRepository;

    @Value("${app.upload.dir:/app/uploads}")
    private String uploadDir;

    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

    @Transactional(readOnly = true)
    public List<ReviewDTO> getReviewsByCafeId(Long cafeId) {
        return reviewRepository.findByCafeIdOrderByCreatedAtDesc(cafeId).stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    @Transactional
    public ReviewDTO createReview(Long cafeId, String nickname, String content, MultipartFile image) {
        Cafe cafe = cafeRepository.findById(cafeId)
                .orElseThrow(() -> new RuntimeException("카페를 찾을 수 없습니다. id: " + cafeId));

        String imageUrl = null;
        if (image != null && !image.isEmpty()) {
            imageUrl = saveImage(image);
        }

        Review review = Review.builder()
                .cafe(cafe)
                .nickname(nickname)
                .content(content)
                .imageUrl(imageUrl)
                .createdAt(LocalDateTime.now())
                .build();

        return convertToDTO(reviewRepository.save(review));
    }

    private String saveImage(MultipartFile file) {
        try {
            Path uploadPath = Paths.get(uploadDir);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            String originalFilename = file.getOriginalFilename();
            String ext = "";
            if (originalFilename != null && originalFilename.contains(".")) {
                ext = originalFilename.substring(originalFilename.lastIndexOf("."));
            }
            String filename = UUID.randomUUID().toString() + ext;

            Path filePath = uploadPath.resolve(filename);
            Files.copy(file.getInputStream(), filePath);

            return "/uploads/" + filename;
        } catch (IOException e) {
            throw new RuntimeException("이미지 업로드 실패", e);
        }
    }

    private ReviewDTO convertToDTO(Review review) {
        return ReviewDTO.builder()
                .id(review.getId())
                .cafeId(review.getCafe().getId())
                .nickname(review.getNickname())
                .content(review.getContent())
                .imageUrl(review.getImageUrl())
                .createdAt(review.getCreatedAt().format(FORMATTER))
                .build();
    }
}
