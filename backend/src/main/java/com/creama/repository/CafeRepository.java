package com.creama.repository;

import com.creama.entity.Cafe;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CafeRepository extends JpaRepository<Cafe, Long> {

    @Query("SELECT c FROM Cafe c LEFT JOIN FETCH c.sensoryDataList")
    List<Cafe> findAllWithSensoryData();
}
