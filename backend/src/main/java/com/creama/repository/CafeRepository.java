package com.creama.repository;

import com.creama.entity.Cafe;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CafeRepository extends JpaRepository<Cafe, Long> {

    @Query("SELECT DISTINCT c FROM Cafe c LEFT JOIN FETCH c.sensoryDataList")
    List<Cafe> findAllWithSensoryData();

    @Query("SELECT c FROM Cafe c LEFT JOIN FETCH c.sensoryDataList WHERE c.id = :id")
    Optional<Cafe> findByIdWithSensoryData(@Param("id") Long id);

    @Query("SELECT DISTINCT c FROM Cafe c LEFT JOIN FETCH c.sensoryDataList sd WHERE " +
            "LOWER(c.name) LIKE LOWER(:keyword) OR " +
            "LOWER(c.address) LIKE LOWER(:keyword) OR " +
            "LOWER(sd.keywords) LIKE LOWER(:keyword) OR " +
            "LOWER(sd.vibeKeywords) LIKE LOWER(:keyword) OR " +
            "LOWER(sd.recommendedFor) LIKE LOWER(:keyword)")
    List<Cafe> searchByKeyword(@Param("keyword") String keyword);
}
