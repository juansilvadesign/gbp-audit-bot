"""
Unit tests for the Geogrid calculation service.
"""
import pytest
import math

from app.services.geogrid import (
    generate_geogrid,
    estimate_credits,
    calculate_visibility_score,
    calculate_average_rank,
    get_rank_color,
    count_top3,
    count_top10,
    calculate_scan_stats,
    GridPoint,
    ScanStats
)


class TestGenerateGeogrid:
    """Tests for the generate_geogrid function."""
    
    def test_grid_3x3_generates_9_points(self):
        """A 3x3 grid should generate exactly 9 points."""
        points = generate_geogrid(-22.9711, -43.1825, 2.0, 3)
        assert len(points) == 9
    
    def test_grid_5x5_generates_25_points(self):
        """A 5x5 grid should generate exactly 25 points."""
        points = generate_geogrid(-22.9711, -43.1825, 5.0, 5)
        assert len(points) == 25
    
    def test_grid_7x7_generates_49_points(self):
        """A 7x7 grid should generate exactly 49 points."""
        points = generate_geogrid(-22.9711, -43.1825, 10.0, 7)
        assert len(points) == 49
    
    def test_center_point_is_at_center_coordinates(self):
        """The center point should have coordinates close to the input center."""
        center_lat, center_lng = -22.9711, -43.1825
        points = generate_geogrid(center_lat, center_lng, 2.0, 3)
        
        # Center point in a 3x3 grid is at index 4 (row 1, col 1)
        center_point = points[4]
        
        assert center_point.x == 1
        assert center_point.y == 1
        assert abs(center_point.latitude - center_lat) < 0.0001
        assert abs(center_point.longitude - center_lng) < 0.0001
    
    def test_center_point_in_5x5_grid(self):
        """The center point in a 5x5 grid should be at index 12."""
        center_lat, center_lng = -23.5505, -46.6333
        points = generate_geogrid(center_lat, center_lng, 5.0, 5)
        
        # Center point in a 5x5 grid is at index 12 (row 2, col 2)
        center_point = points[12]
        
        assert center_point.x == 2
        assert center_point.y == 2
        assert abs(center_point.latitude - center_lat) < 0.0001
        assert abs(center_point.longitude - center_lng) < 0.0001
    
    def test_grid_points_are_equidistant(self):
        """Points should be equidistant from each other."""
        center_lat, center_lng = -22.9711, -43.1825
        radius_km = 2.0
        points = generate_geogrid(center_lat, center_lng, radius_km, 3)
        
        # Expected step in km
        expected_step_km = (radius_km * 2) / 2  # 2km for a 3x3 grid with 2km radius
        
        # Check horizontal distance between first two points in a row
        point_0 = points[0]  # Top-left
        point_1 = points[1]  # Top-center
        
        # Approximate distance using simple calculation
        lng_diff_deg = abs(point_1.longitude - point_0.longitude)
        meters_per_lng_deg = 111111 * math.cos(math.radians(center_lat))
        distance_m = lng_diff_deg * meters_per_lng_deg
        distance_km = distance_m / 1000
        
        assert abs(distance_km - expected_step_km) < 0.1  # Within 100m tolerance
    
    def test_invalid_grid_size_raises_error(self):
        """Grid size must be 3, 5, or 7."""
        with pytest.raises(ValueError, match="Grid size must be 3, 5, or 7"):
            generate_geogrid(-22.9711, -43.1825, 2.0, 4)
        
        with pytest.raises(ValueError, match="Grid size must be 3, 5, or 7"):
            generate_geogrid(-22.9711, -43.1825, 2.0, 9)
    
    def test_negative_radius_raises_error(self):
        """Radius must be positive."""
        with pytest.raises(ValueError, match="Radius must be positive"):
            generate_geogrid(-22.9711, -43.1825, -1.0, 3)
    
    def test_excessive_radius_raises_error(self):
        """Radius must not exceed 50km for accuracy."""
        with pytest.raises(ValueError, match="must not exceed 50km"):
            generate_geogrid(-22.9711, -43.1825, 100.0, 3)
    
    def test_labels_are_correct(self):
        """Each point should have the correct label format."""
        points = generate_geogrid(-22.9711, -43.1825, 2.0, 3)
        
        assert points[0].label == "Ponto_0_0"
        assert points[4].label == "Ponto_1_1"
        assert points[8].label == "Ponto_2_2"
    
    def test_copacabana_example_from_docs(self):
        """Test the example from math.md documentation."""
        # Example: Grade 3x3 em Copacabana com raio de 2km
        points = generate_geogrid(-22.9711, -43.1825, 2, 3)
        
        assert len(points) == 9
        # All latitudes should be around -22.9711 (±0.02)
        for p in points:
            assert -23.0 < p.latitude < -22.9
            assert -43.25 < p.longitude < -43.1


class TestEstimateCredits:
    """Tests for the estimate_credits function."""
    
    def test_3x3_grid_costs_9_credits(self):
        assert estimate_credits(3) == 9
    
    def test_5x5_grid_costs_25_credits(self):
        assert estimate_credits(5) == 25
    
    def test_7x7_grid_costs_49_credits(self):
        assert estimate_credits(7) == 49
    
    def test_invalid_grid_size_raises_error(self):
        with pytest.raises(ValueError):
            estimate_credits(4)


class TestCalculateVisibilityScore:
    """Tests for the visibility score calculation."""
    
    def test_all_rank_1_is_100_percent(self):
        """All positions at rank 1 should give maximum visibility."""
        ranks = [1, 1, 1, 1, 1, 1, 1, 1, 1]
        score = calculate_visibility_score(ranks, 3)
        assert score == 100.0
    
    def test_all_not_found_is_0_percent(self):
        """All positions not found should give 0% visibility."""
        ranks = [None, None, None, None, None, None, None, None, None]
        score = calculate_visibility_score(ranks, 3)
        assert score == 0.0
    
    def test_mixed_ranks_gives_intermediate_score(self):
        """Mixed ranks should give a score between 0 and 100."""
        ranks = [1, 2, 3, 5, 8, 10, 15, None, None]
        score = calculate_visibility_score(ranks, 3)
        assert 0 < score < 100


class TestCalculateAverageRank:
    """Tests for the average rank calculation."""
    
    def test_single_rank(self):
        assert calculate_average_rank([5]) == 5.0
    
    def test_multiple_ranks(self):
        assert calculate_average_rank([1, 2, 3, 4, 5]) == 3.0
    
    def test_ignores_none_values(self):
        assert calculate_average_rank([1, 2, 3, None, None]) == 2.0
    
    def test_all_none_returns_none(self):
        assert calculate_average_rank([None, None, None]) is None


class TestGetRankColor:
    """Tests for the rank color coding."""
    
    def test_rank_1_to_3_is_green(self):
        assert get_rank_color(1) == "green"
        assert get_rank_color(2) == "green"
        assert get_rank_color(3) == "green"
    
    def test_rank_4_to_10_is_yellow(self):
        assert get_rank_color(4) == "yellow"
        assert get_rank_color(7) == "yellow"
        assert get_rank_color(10) == "yellow"
    
    def test_rank_11_plus_is_red(self):
        assert get_rank_color(11) == "red"
        assert get_rank_color(15) == "red"
        assert get_rank_color(20) == "red"
    
    def test_none_is_red(self):
        assert get_rank_color(None) == "red"


class TestCountTop3:
    """Tests for the count_top3 function (esqueleto.md KPI)."""
    
    def test_all_top3(self):
        """All positions in top 3 should return full count."""
        ranks = [1, 2, 3, 1, 2, 3, 1, 2, 3]
        assert count_top3(ranks) == 9
    
    def test_none_top3(self):
        """No positions in top 3 should return 0."""
        ranks = [5, 8, 10, 15, None]
        assert count_top3(ranks) == 0
    
    def test_mixed_ranks(self):
        """Mixed ranks should count only top 3."""
        ranks = [1, 2, 3, 5, 8, None]
        assert count_top3(ranks) == 3
    
    def test_esqueleto_example(self):
        """Match the esqueleto.md example: top3_count = len([r for r in ranks if r <= 3])"""
        ranks = [1, 3, 5, 7, 2, 10, 15, None, None]
        assert count_top3(ranks) == 3  # Only 1, 3, 2 are in top 3


class TestCountTop10:
    """Tests for the count_top10 function."""
    
    def test_all_top10(self):
        ranks = [1, 5, 10, 3, 8]
        assert count_top10(ranks) == 5
    
    def test_none_top10(self):
        ranks = [11, 15, 20, None]
        assert count_top10(ranks) == 0
    
    def test_mixed_ranks(self):
        ranks = [1, 5, 10, 11, 15, None]
        assert count_top10(ranks) == 3


class TestCalculateScanStats:
    """Tests for the calculate_scan_stats function (esqueleto.md format)."""
    
    def test_returns_scan_stats_object(self):
        ranks = [1, 2, 3, 5, 8, 10, 12, None, None]
        stats = calculate_scan_stats(ranks, 3)
        assert isinstance(stats, ScanStats)
    
    def test_stats_match_individual_functions(self):
        """ScanStats should match individual function results."""
        ranks = [1, 2, 3, 5, 8, 10, 12, None, None]
        stats = calculate_scan_stats(ranks, 3)
        
        assert stats.arp == calculate_average_rank(ranks)
        assert stats.top3 == count_top3(ranks)
        assert stats.top10 == count_top10(ranks)
        assert stats.visibility_score == calculate_visibility_score(ranks, 3)
        assert stats.total_points == 9
    
    def test_esqueleto_format(self):
        """Stats should be in the format expected by esqueleto.md AI analysis."""
        ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # All found, average 5
        stats = calculate_scan_stats(ranks, 3)
        
        assert stats.arp == 5.0
        assert stats.top3 == 3
        assert stats.total_points == 9

