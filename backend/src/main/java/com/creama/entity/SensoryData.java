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
    private Integer noiseLevel; // 0: Library -> 100: Market

    @Column(nullable = false)
    private Integer lighting; // 0: Dark/Mood -> 100: Bright/Work

    @Column(nullable = false)
    private Integer comfort; // 0: Hard Chair -> 100: Sofa

    // Tags (JSON stored as text)
    @Column(columnDefinition = "TEXT")
    private String keywords; // JSON array: ["Roastery", "Date", "Jazz"]
}
