// Form handling
document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const home = document.getElementById('home').value;
            const away = document.getElementById('away').value;
            
            if (!home || !away) {
                e.preventDefault();
                alert('Please select both teams');
                return;
            }
            
            if (home === away) {
                e.preventDefault();
                alert('Home and away teams must be different');
                return;
            }
        });
    }
});

// API fetching for programmatic access
async function fetchAnalysis(home, away) {
    try {
        const response = await fetch(`/api/match?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch analysis:', error);
        return null;
    }
}

// Verification state utilities
function getVerificationBadge(state) {
    const badges = {
        'verified': '🟢',
        'assumption': '🟡',
        'unavailable': '🔴',
    };
    return badges[state] || '❓';
}

// Format odds for display
function formatOdds(odds) {
    return odds.toFixed(2);
}

// Format percentage for display
function formatPercent(value) {
    return (value * 100).toFixed(1) + '%';
}

// Export for external use
window.SoccerAnalyzer = {
    fetchAnalysis,
    getVerificationBadge,
    formatOdds,
    formatPercent,
};
