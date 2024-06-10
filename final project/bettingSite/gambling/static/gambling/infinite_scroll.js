document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('bets-container');
    const loading = document.getElementById('loading');
    const sortBySelect = document.getElementById('sort_by');

    let page = 1;
    let hasNext = true;
    let isLoading = false;

    async function fetchBets() {
        if (isLoading || !hasNext) return;
        isLoading = true;
        loading.style.display = 'block';

        const sortBy = sortBySelect.value;
        const response = await fetch(`/api/bets/?sort_by=${sortBy}&page=${page}`);
        const data = await response.json();

        data.bets.forEach(bet => {
            const betDiv = document.createElement('div');
            betDiv.className = 'col-md-4 mb-4';
            betDiv.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">${bet.name}</h5>
                        <p class="card-text">${bet.description}</p>
                        <p class="card-text">Bets Sold: ${bet.tickets_sold}</p>
                        <a href="/bets/${bet.id}/" class="btn btn-primary">View Details</a>
                    </div>
                </div>
            `;
            container.appendChild(betDiv);
        });

        hasNext = data.has_next;
        page += 1;
        isLoading = false;
        loading.style.display = 'none';
    };

    window.addEventListener('scroll', () => {
        if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 100 && hasNext) {
            fetchBets();
        }
    });

    sortBySelect.addEventListener('change', () => {
        container.innerHTML = '';
        page = 1;
        hasNext = true;
        fetchBets();
    });

    fetchBets();
});
