package com.creama.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "sensory_data")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SensoryData {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cafe_id", nullable = false)
    private Cafe cafe;

    // Taste Metrics (0.0 - 5.0)
    @Column(nullable = false)
    private Double acidity; // 산미

    @Column(nullable = false)
    private Double body; // 바디감

    @Column(nullable = false)
    private Double sweetness; // 단맛

    @Column(nullable = false)
    private Double bitterness; // 쓴맛

    @Column(nullable = false)
    private Double aroma; // 향

    // Vibe Metrics (0 - 100)
    @Column(name = "noise_level", nullable = false)
    private Integer noiseLevel; // 0: 도서관 -> 100: 시장

    @Column(nullable = false)
    private Integer lighting; // 0: 무드/어둠 -> 100: 밝음/작업

    @Column(nullable = false)
    private Integer comfort; // 0: 딱딱한 의자 -> 100: 소파

    // 신규 Vibe 필드
    @Column(name = "music_genre", length = 50)
    private String musicGenre; // Jazz, Lo-fi, Acoustic, K-Pop, None 등

    @Column(name = "crowdedness")
    private Integer crowdedness; // 0: 한산 -> 100: 혼잡

    @Column(name = "has_concent")
    private Boolean hasConcent; // 콘센트 유무

    @Column(name = "has_wifi")
    private Boolean hasWifi; // 와이파이 유무

    @Column(name = "has_parking")
    private Boolean hasParking; // 주차 가능 여부

    @Column(name = "seat_types", columnDefinition = "TEXT")
    private String seatTypes; // JSON: ["소파","바","테라스","개인석"]

    @Column(name = "vibe_keywords", columnDefinition = "TEXT")
    private String vibeKeywords; // JSON: ["빈티지","모던","아늑한","힙한"]

    @Column(name = "recommended_for", columnDefinition = "TEXT")
    private String recommendedFor; // JSON: ["데이트","작업","모임","혼카페","사진"]

    // Tags (JSON stored as text) — 기존 유지
    @Column(columnDefinition = "TEXT")
    private String keywords; // JSON array: ["Roastery", "Date", "Jazz"]
}
