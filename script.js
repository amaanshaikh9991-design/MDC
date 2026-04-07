document.addEventListener('DOMContentLoaded', () => {
    
    // --- Navbar Scroll Effect ---
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // --- Load Initial Movies ---
    const movieGrid = document.getElementById('movieGrid');
    if (movieGrid) {
        fetchMovies('/api/movies');
    }

    // --- Search Functionality ---
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    if (searchInput && searchResults) {   // ✅ FIX: added safety check
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value;

            if (query.length > 2) {
                fetch(`/api/search?q=${encodeURIComponent(query)}`) // ✅ FIX: encode URL
                    .then(res => res.json())
                    .then(data => {
                        searchResults.innerHTML = '';

                        if (data.length > 0) {
                            searchResults.style.display = 'block';

                            data.forEach(movie => {
                                const div = document.createElement('div');
                                div.className = 'search-item';
                                div.textContent = movie.title;

                                div.onclick = () => {
                                    openModal(movie.title);
                                    searchResults.style.display = 'none';
                                    searchInput.value = '';
                                };

                                searchResults.appendChild(div);
                            });
                        } else {
                            searchResults.style.display = 'none';
                        }
                    })
                    .catch(err => console.error(err)); // ✅ FIX: error handling
            } else {
                searchResults.style.display = 'none';
            }
        });

        // Close search dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

    // --- Modal Logic ---
    const modal = document.getElementById('movieModal');
    const closeModal = document.querySelector('.close-modal');
    let currentMovieTitle = '';

    if (closeModal && modal) {   // ✅ FIX: null safety
        closeModal.onclick = () => modal.style.display = 'none';

        window.onclick = (e) => {
            if (e.target === modal) modal.style.display = 'none'; // ✅ FIX: strict check
        };
    }

    // --- Recommendation Logic ---
    const btnRecommend = document.getElementById('btnRecommend');
    const recSection = document.getElementById('recommendationSection');
    const closeRec = document.getElementById('closeRec');

    if (btnRecommend && recSection) {   // ✅ FIX: null safety
        btnRecommend.addEventListener('click', () => {
            if (!currentMovieTitle) return;
            
            fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: currentMovieTitle })
            })
            .then(res => res.json())
            .then(data => {
                const recGrid = document.getElementById('recGrid');

                if (!recGrid) return; // ✅ FIX

                document.getElementById('recSourceTitle').textContent = currentMovieTitle;
                recGrid.innerHTML = '';
                
                if (data.length > 0) {
                    data.forEach(movie => {
                        recGrid.appendChild(createMovieCard(movie));
                    });

                    recSection.classList.remove('hidden');
                    recSection.scrollIntoView({ behavior: 'smooth' });
                }
            })
            .catch(err => console.error(err)); // ✅ FIX
        });
    }

    if (closeRec && recSection) {
        closeRec.addEventListener('click', () => {
            recSection.classList.add('hidden');
        });
    }

    // --- Helper Functions ---

    function fetchMovies(url) {
        if (!movieGrid) return;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                movieGrid.innerHTML = '';

                data.forEach(movie => {
                    movieGrid.appendChild(createMovieCard(movie));
                });
            })
            .catch(err => {
                movieGrid.innerHTML = '<p>Error loading movies.</p>';
                console.error(err);
            });
    }

    function createMovieCard(movie) {
        const card = document.createElement('div');
        card.className = 'movie-card';

        const posterUrl = `https://via.placeholder.com/300x450/333333/FFFFFF?text=${encodeURIComponent(movie.title)}`;
        
        card.innerHTML = `
            <div class="card-poster">
                <img src="${posterUrl}" alt="${movie.title}">
            </div>
            <div class="card-info">
                <h4>${movie.title}</h4>
                <div class="card-meta">
                    <span>${movie.year}</span>
                    <span class="rating">⭐ ${movie.rating}</span>
                </div>
            </div>
        `;
        
        card.addEventListener('click', () => openModal(movie.title));
        return card;
    }

    function openModal(title) {
        fetch(`/api/details?title=${encodeURIComponent(title)}`)
            .then(res => res.json())
            .then(movie => {
                if (!movie || !movie.title) return; // ✅ FIX
                
                currentMovieTitle = movie.title;

                document.getElementById('modalTitle').textContent = movie.title;
                document.getElementById('modalYear').textContent = movie.year;
                document.getElementById('modalRating').textContent = `⭐ ${movie.rating}`;
                document.getElementById('modalGenre').textContent = movie.genre;
                document.getElementById('modalDirector').textContent = movie.director;
                
                const posterUrl = `https://via.placeholder.com/400x600/333333/FFFFFF?text=${encodeURIComponent(movie.title)}`;
                document.getElementById('modalImg').src = posterUrl;
                
                if (modal) modal.style.display = 'flex'; // ✅ FIX
            })
            .catch(err => console.error(err)); // ✅ FIX
    }

    // --- Category Filter ---
    const catBtns = document.querySelectorAll('.cat-btn');

    catBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            catBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const filter = btn.getAttribute('data-filter');

            if (filter === 'all') {
                fetchMovies('/api/movies');
            } else {
                fetch('/api/movies')
                    .then(res => res.json())
                    .then(data => {
                        const filtered = data.filter(m => 
                            m.genre && m.genre.toLowerCase().includes(filter.toLowerCase()) // ✅ FIX: safer filtering
                        );

                        movieGrid.innerHTML = '';
                        filtered.forEach(m => movieGrid.appendChild(createMovieCard(m)));
                    })
                    .catch(err => console.error(err)); // ✅ FIX
            }
        });
    });

});